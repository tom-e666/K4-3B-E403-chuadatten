from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

from .providers.base import Provider
from .tools._shared import load_lessons_data, get_lesson_by_id

# ============================================================================
# Agent 3 — "Giáo sư AI": chấm điểm bằng so khớp NGỮ NGHĨA (không từ khóa cứng),
# và tự phát hiện khi học viên bỏ cuộc để trả lời thẳng đáp án.
# ============================================================================
EVALUATOR_SYSTEM_PROMPT = """Bạn là 'Giáo sư AI' — một AI chuyên môn, khách quan, đóng vai giám khảo chấm bài
trong hệ thống ôn tập Feynman Reverse Tutoring. Bạn KHÔNG lộ diện với học viên — bạn chỉ phân tích và trả về
JSON để hệ thống xử lý tiếp, một AI khác (persona bạn học) sẽ đọc JSON này rồi mới nói chuyện với học viên.

Nhiệm vụ: đọc lời giải thích của học viên, so sánh về mặt Ý NGHĨA (không phải khớp từ khóa) với danh sách
rubric_points (tiêu chí) của checkpoint hiện tại, rồi phán đoán:

1. Nếu học viên có dấu hiệu BỎ CUỘC / xin hàng — ví dụ nói "không biết", "chịu", "chịu thua", "bó tay", "pass",
   "cho em đáp án", "em không nhớ", "thua rồi", ... → status = "GAVE_UP". Điền "reveal_answer" bằng lời giải
   thích ĐẦY ĐỦ, CHÍNH XÁC, dễ hiểu cho đúng khái niệm đó (dựa trên rubric_points + đáp án tham khảo được cấp).
2. Ngược lại, so khớp ngữ nghĩa câu trả lời với từng rubric_point:
   - Điểm nào được diễn đạt đúng bản chất (không cần đúng từ, chấp nhận diễn đạt khác) → liệt vào "covered_points".
   - Điểm nào thiếu, sai, hoặc mơ hồ → liệt vào "missing_points", ghi rõ vì sao chưa đạt ở "why".
   - Tính mastery_score = % tổng weight các rubric_points đã đạt (làm tròn số nguyên 0-100).
   - status = "PASS" nếu mastery_score >= 80, ngược lại "NEEDS_IMPROVEMENT".
   - "reveal_answer" để trống ("") trong trường hợp này.

CHỈ trả về DUY NHẤT một JSON object, không thêm chữ nào khác, không dùng markdown fence, đúng schema:
{
  "status": "PASS" | "NEEDS_IMPROVEMENT" | "GAVE_UP",
  "mastery_score": 0,
  "covered_points": [{"concept": "..."}],
  "missing_points": [{"concept": "...", "why": "..."}],
  "reveal_answer": ""
}
"""

# ============================================================================
# Agent 2 — "Minh AI" (Bot Ngu): CHỈ diễn đạt lại phán quyết của Agent 3 bằng
# lời thoại tự nhiên, đúng tính cách bạn học đang nhờ giảng lại bài.
# ============================================================================
PERSONA_SYSTEM_PROMPT = """Bạn là 'Minh AI' - một bạn học cùng lớp trong chương trình AI20k, đang nhờ người dùng
(User) giảng lại kiến thức cho mình theo kỹ thuật Feynman. Xưng hô tự nhiên "tớ - cậu" hoặc "mình - bạn". Đừng
nhắc tới việc bạn là AI, đang bị chấm điểm, hay các từ như 'checkpoint'/'rubric'.

Bạn nhận một PHÁN QUYẾT có sẵn từ Giáo sư AI (không hiển thị cho học viên) — nhiệm vụ của bạn CHỈ là diễn đạt
lại phán quyết đó bằng đúng 1 lượt lời thoại, theo tính cách:
- status "PASS": hào hứng, gật gù, chốt lại đúng 1 ý cốt lõi vừa học được, cảm ơn bạn học.
- status "NEEDS_IMPROVEMENT": gãi đầu, thắc mắc ĐÚNG vào MỘT trong các missing_points được cấp (chọn 1 ý thôi,
  đừng liệt kê hết) — TUYỆT ĐỐI KHÔNG tự giải thích hộ đáp án.
- status "GAVE_UP": thông cảm nhẹ nhàng trước ("không sao đâu, để tớ nói cho cậu nghe nhé"), rồi trình bày lại
  đúng nội dung reveal_answer bằng giọng văn tự nhiên của một người bạn, không phải giọng giáo trình khô khan.

Chỉ trả lời bằng lời thoại thuần văn bản — không JSON, không markdown, không tiêu đề.
"""


@dataclass
class SessionState:
    session_id: str
    lesson_id: str = "lesson_02"
    current_checkpoint_index: int = 0
    checkpoint_trials: dict[str, int] = field(default_factory=dict)
    checkpoint_results: dict[str, dict[str, Any]] = field(default_factory=dict)
    messages: list[dict[str, str]] = field(default_factory=list)
    completed: bool = False


def _parse_json_object(text: str) -> dict[str, Any] | None:
    """Trích JSON object đầu tiên trong text — chịu được model bọc thêm ```json ... ``` hoặc lời dẫn thừa."""
    if not text:
        return None
    cleaned = re.sub(r"^```(json)?\s*|\s*```$", "", text.strip())
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start == -1 or end == -1 or end < start:
        return None
    try:
        return json.loads(cleaned[start:end + 1])
    except json.JSONDecodeError:
        return None


def _build_evaluator_prompt(checkpoint: dict[str, Any], user_explanation: str, trials_used: int) -> str:
    rubric_lines = "\n".join(
        f'- id="{p.get("id")}" (weight={p.get("weight", 30)}): {p.get("concept")} — {p.get("criteria", "")}'
        for p in checkpoint.get("rubric_points", [])
    ) or "- (checkpoint không có rubric_points cụ thể, tự đánh giá theo tiêu đề checkpoint)"

    return f"""CHECKPOINT: {checkpoint.get('title')}

RUBRIC_POINTS (tiêu chí phải đạt):
{rubric_lines}

ĐÁP ÁN THAM KHẢO (đối chiếu, và dùng làm cơ sở cho reveal_answer nếu cần):
{checkpoint.get('correction', '')}

LƯỢT THỬ HIỆN TẠI: {trials_used}/3

CÂU TRẢ LỜI CỦA HỌC VIÊN:
\"\"\"{user_explanation}\"\"\"
"""


def _build_persona_prompt(checkpoint: dict[str, Any], user_explanation: str, verdict: dict[str, Any]) -> str:
    verdict_json = json.dumps(
        {
            "status": verdict.get("status"),
            "missing_points": verdict.get("missing_points", []),
            "reveal_answer": verdict.get("reveal_answer", ""),
            "mastery_score": verdict.get("mastery_score", 0),
        },
        ensure_ascii=False,
    )
    return f"""CHECKPOINT ĐANG HỌC: {checkpoint.get('title')}

CÂU TRẢ LỜI VỪA RỒI CỦA NGƯỜI DÙNG:
\"\"\"{user_explanation}\"\"\"

PHÁN QUYẾT TỪ GIÁO SƯ AI (không hiển thị cho người dùng, chỉ để bạn phản ứng đúng):
{verdict_json}

Hãy trả lời NGƯỜI DÙNG bằng đúng 1 lượt lời thoại, theo tính cách đã mô tả.
"""


def _fallback_verdict(status: str, mastery_score: int = 0) -> dict[str, Any]:
    return {
        "status": status,
        "mastery_score": mastery_score,
        "covered_points": [],
        "missing_points": [],
        "reveal_answer": "",
    }


def _fallback_persona_text(verdict: dict[str, Any]) -> str:
    status = verdict.get("status")
    if status == "PASS":
        return f"À tớ hiểu rồi! Cậu giải thích rất chuẩn và đúng trọng tâm ({verdict.get('mastery_score', 0)}%), cảm ơn cậu nhiều nha!"
    if status == "GAVE_UP":
        answer = verdict.get("reveal_answer") or "phần này khá khó, để tớ tìm hiểu thêm rồi nói lại với cậu sau nhé."
        return f"Không sao đâu, để tớ nói cho cậu nghe nhé: {answer}"
    missing_str = ", ".join(m.get("concept", "") for m in verdict.get("missing_points", []))
    return f"Ủa tớ vẫn chưa rõ lắm, hình như còn thiếu phần [{missing_str or 'khái niệm cốt lõi'}]. Cậu giải thích thêm cho tớ được không?"


class FeynmanAgent:
    def __init__(
        self,
        provider: Provider,
        *,
        model: str | None = None,
    ) -> None:
        self.provider = provider
        self.model = model

    def get_lesson_checkpoints(self, lesson_id: str) -> list[dict[str, Any]]:
        lesson = get_lesson_by_id(lesson_id) or load_lessons_data(lesson_id)
        return lesson.get("checkpoints", [])

    def start_session(self, session_id: str = "default_session", lesson_id: str = "lesson_02") -> tuple[SessionState, str]:
        """Khởi tạo một phiên học mới theo lesson_id, trả về state và câu mở đầu của Bot Ngu."""
        checkpoints = self.get_lesson_checkpoints(lesson_id)
        first_cp = checkpoints[0] if checkpoints else None
        starter_msg = first_cp.get("student_starter_message", "Chào bạn! Cùng ôn bài nhé.") if first_cp else "Sẵn sàng ôn bài!"

        state = SessionState(
            session_id=session_id,
            lesson_id=lesson_id,
            current_checkpoint_index=0,
            checkpoint_trials={first_cp["id"]: 0} if first_cp else {},
            checkpoint_results={},
            messages=[{"role": "assistant", "content": starter_msg}],
            completed=False,
        )
        return state, starter_msg

    def get_current_checkpoint(self, state: SessionState) -> dict[str, Any] | None:
        checkpoints = self.get_lesson_checkpoints(state.lesson_id)
        if 0 <= state.current_checkpoint_index < len(checkpoints):
            return checkpoints[state.current_checkpoint_index]
        return None

    # --------------------------------------------------------------- Agent 3
    def _run_evaluator(self, checkpoint: dict[str, Any], user_explanation: str, trials_used: int) -> dict[str, Any]:
        try:
            response = self.provider.complete(
                [
                    {"role": "system", "content": EVALUATOR_SYSTEM_PROMPT},
                    {"role": "user", "content": _build_evaluator_prompt(checkpoint, user_explanation, trials_used)},
                ],
                tools=None,
                model=self.model,
                temperature=0.1,
            )
            verdict = _parse_json_object(response.text or "")
            if verdict is None or verdict.get("status") not in ("PASS", "NEEDS_IMPROVEMENT", "GAVE_UP"):
                raise ValueError(f"Agent 3 không trả JSON hợp lệ: {response.text!r}")
            verdict.setdefault("covered_points", [])
            verdict.setdefault("missing_points", [])
            verdict.setdefault("reveal_answer", "")
            verdict.setdefault("mastery_score", 0)
            return verdict
        except Exception as exc:
            print(f"⚠️ Agent 3 (Giáo sư AI) lỗi ({exc}), rơi về chấm rule-based dự phòng.")
            from .tools.evaluator import grade_explanation
            fallback = grade_explanation(checkpoint["id"], user_explanation)
            if fallback.get("error"):
                return _fallback_verdict("NEEDS_IMPROVEMENT")
            return {
                "status": fallback.get("status", "NEEDS_IMPROVEMENT"),
                "mastery_score": fallback.get("mastery_score", 0),
                "covered_points": fallback.get("covered_points", []),
                "missing_points": fallback.get("missing_points", []),
                "reveal_answer": "",
            }

    # --------------------------------------------------------------- Agent 2
    def _run_persona(self, checkpoint: dict[str, Any], user_explanation: str, verdict: dict[str, Any]) -> str:
        try:
            response = self.provider.complete(
                [
                    {"role": "system", "content": PERSONA_SYSTEM_PROMPT},
                    {"role": "user", "content": _build_persona_prompt(checkpoint, user_explanation, verdict)},
                ],
                tools=None,
                model=self.model,
                temperature=0.6,
            )
            text = (response.text or "").strip()
            if not text:
                raise ValueError("Agent 2 trả lời rỗng")
            return text
        except Exception as exc:
            print(f"⚠️ Agent 2 (Minh AI) lỗi ({exc}), dùng câu trả lời mẫu dự phòng.")
            return _fallback_persona_text(verdict)

    def chat_step(self, state: SessionState, user_input: str) -> dict[str, Any]:
        """
        Xử lý 1 lượt tin nhắn của học viên bằng 2 lệnh gọi AI tách biệt:
        1. Agent 3 ('Giáo sư AI') chấm điểm ngữ nghĩa / phát hiện bỏ cuộc.
        2. Agent 2 ('Minh AI') diễn đạt lại phán quyết đó thành lời thoại.
        Sau đó cập nhật tiến độ checkpoint và trả kết quả cho UI.
        """
        current_cp = self.get_current_checkpoint(state)
        if not current_cp:
            return {
                "assistant_text": "Buổi học đã hoàn thành! Bạn có thể xem bảng báo cáo tổng kết.",
                "latest_evaluation": None,
                "checkpoint_id": None,
                "checkpoint_title": None,
                "trials_used": 0,
                "advance_checkpoint": False,
                "next_checkpoint_title": None,
                "completed": True,
            }

        cp_id = current_cp["id"]
        state.checkpoint_trials[cp_id] = state.checkpoint_trials.get(cp_id, 0) + 1
        trials_used = state.checkpoint_trials[cp_id]
        state.messages.append({"role": "user", "content": user_input})

        verdict = self._run_evaluator(current_cp, user_input, trials_used)

        # Hết 3 lượt vẫn chưa đạt (và chưa tự nhận bỏ cuộc) -> ép công bố đáp án, giống hành vi cũ.
        if verdict["status"] == "NEEDS_IMPROVEMENT" and trials_used >= 3:
            verdict = {**verdict, "status": "GAVE_UP", "reveal_answer": current_cp.get("correction", "")}

        assistant_text = self._run_persona(current_cp, user_input, verdict)
        state.messages.append({"role": "assistant", "content": assistant_text})
        state.checkpoint_results[cp_id] = {**verdict, "trials": trials_used}

        advance_checkpoint = verdict["status"] in ("PASS", "GAVE_UP")
        next_checkpoint_title = None
        if advance_checkpoint:
            state.current_checkpoint_index += 1
            next_cp = self.get_current_checkpoint(state)
            if next_cp:
                next_checkpoint_title = next_cp["title"]
                state.checkpoint_trials[next_cp["id"]] = 0
            else:
                state.completed = True

        latest_evaluation = {
            "checkpoint_id": cp_id,
            "checkpoint_title": current_cp["title"],
            # "status" FE-facing chỉ có 2 giá trị (PASS/NEEDS_IMPROVEMENT) để khớp UI hiện có —
            # PASS thật và GAVE_UP đều coi là "qua checkpoint" phía FE; chi tiết thật nằm ở "outcome".
            "status": "PASS" if advance_checkpoint else "NEEDS_IMPROVEMENT",
            "outcome": verdict["status"].lower(),
            "mastery_score": verdict.get("mastery_score", 0),
            "threshold": 80,
            "covered_points": verdict.get("covered_points", []),
            "missing_points": verdict.get("missing_points", []),
            "reveal_answer": verdict.get("reveal_answer", ""),
            "source_citation": current_cp.get("source_citation", ""),
        }

        return {
            "assistant_text": assistant_text,
            "latest_evaluation": latest_evaluation,
            "checkpoint_id": cp_id,
            "checkpoint_title": current_cp["title"],
            "trials_used": trials_used,
            "advance_checkpoint": advance_checkpoint,
            "next_checkpoint_title": next_checkpoint_title,
            "completed": state.completed,
        }
