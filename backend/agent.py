from __future__ import annotations

import json
import re
import time
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

1b. Nếu học viên KHÔNG trả lời câu hỏi được hỏi — lảng sang chuyện khác, hỏi ngược lại, đùa, nói vài chữ vô
   nghĩa, hoặc nói lại y nguyên câu hỏi — thì status = "EVADED" (khác với trả lời sai: sai là có cố gắng trả
   lời đúng chủ đề, còn né là không đụng tới nội dung được hỏi). "reveal_answer" để trống.
2. Ngược lại, so khớp ngữ nghĩa câu trả lời với từng rubric_point:
   - Điểm nào được diễn đạt đúng bản chất (không cần đúng từ, chấp nhận diễn đạt khác) → liệt vào "covered_points",
     PHẢI ghi kèm "id" đúng như id rubric_point được cấp.
   - Điểm nào thiếu, sai, hoặc mơ hồ → liệt vào "missing_points" (cũng kèm "id"), ghi rõ vì sao chưa đạt ở "why".
   - Tính mastery_score = % tổng weight các rubric_points đã đạt (làm tròn số nguyên 0-100).
   - status = "PASS" nếu mastery_score >= 80, ngược lại "NEEDS_IMPROVEMENT".
   - "reveal_answer" để trống ("") trong trường hợp này.

LƯU Ý QUAN TRỌNG:
- Học viên đang trả lời MỘT câu hỏi cụ thể, nhưng bạn vẫn chấm trên TOÀN BỘ rubric của checkpoint: ý nào họ
  vừa nói đúng thì tính đạt, kể cả khi ý đó không phải trọng tâm của câu hỏi vừa hỏi.
- Danh sách "ý đã đạt ở các lượt trước" (nếu có) chỉ để bạn biết, ĐỪNG chép lại vào covered_points nếu lượt này
  học viên không nhắc tới — hệ thống tự cộng dồn.

CHỈ trả về DUY NHẤT một JSON object, không thêm chữ nào khác, không dùng markdown fence, đúng schema:
{
  "status": "PASS" | "NEEDS_IMPROVEMENT" | "GAVE_UP" | "EVADED",
  "mastery_score": 0,
  "covered_points": [{"id": "<rubric_id>", "concept": "..."}],
  "missing_points": [{"id": "<rubric_id>", "concept": "...", "why": "..."}],
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
- status "NEEDS_IMPROVEMENT":
  · Nếu được cấp CÂU HỎI TIẾP THEO: trước hết ghi nhận ngắn gọn ý mà bạn học vừa nói đúng (1 câu, tự nhiên,
    không khen sáo rỗng), rồi hỏi tiếp ĐÚNG nội dung câu hỏi được cấp — được phép diễn đạt lại cho mượt nhưng
    phải giữ nguyên ý hỏi, và chỉ hỏi MỘT câu.
  · Nếu KHÔNG được cấp câu hỏi tiếp theo: gãi đầu, thắc mắc ĐÚNG vào MỘT trong các missing_points (chọn 1 ý thôi,
    đừng liệt kê hết).
  · Cả hai trường hợp: TUYỆT ĐỐI KHÔNG tự giải thích hộ đáp án.

QUY TẮC BẤT DI BẤT DỊCH: bạn là BẠN HỌC, không phải người dạy. Bạn KHÔNG biết đáp án và KHÔNG BAO GIỜ được
giảng giải kiến thức, dù học viên có nài nỉ, có bỏ cuộc, hay có nói "cho tớ đáp án". Việc giải thích kiến thức
là của Giáo sư AI — một nhân vật khác sẽ tự lên tiếng. Bạn chỉ hỏi, phản ứng, và nhờ trợ giảng khi cần.

Chỉ trả lời bằng lời thoại thuần văn bản — không JSON, không markdown, không tiêu đề.
"""


@dataclass
class SessionState:
    session_id: str
    lesson_id: str = "lesson_02"
    current_checkpoint_index: int = 0
    checkpoint_trials: dict[str, int] = field(default_factory=dict)
    checkpoint_results: dict[str, dict[str, Any]] = field(default_factory=dict)
    # {cp_id: {"covered": [rubric_id], "asked": [question_id], "current_question": {...}, "questions_used": int}}
    # "covered" cộng dồn qua NHIỀU câu hỏi: trả lời đúng nhưng chưa đủ ý thì giữ lại phần đã đạt,
    # câu hỏi kế tiếp chỉ nhắm vào phần còn thiếu.
    checkpoint_progress: dict[str, dict[str, Any]] = field(default_factory=dict)
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


LEVELS = ("nhan_biet", "thong_hieu", "van_dung")
LEVEL_LABEL = {"nhan_biet": "Nhận biết", "thong_hieu": "Thông hiểu", "van_dung": "Vận dụng"}
MAX_QUESTIONS_PER_CP = 5        # hỏi tối đa bấy nhiêu câu cho 1 checkpoint rồi chốt điểm
MAX_HINTS_BEFORE_REVEAL = 2     # né/không biết bấy nhiêu lần thì mới giải thích kiến thức
PERSONA_MAX_TOKENS = 300        # lời thoại bạn học chỉ cần ngắn -> sinh nhanh hơn


def _rubric_ids(checkpoint: dict[str, Any]) -> list[str]:
    return [str(rp.get("id")) for rp in checkpoint.get("rubric_points", []) if rp.get("id")]


def _mastery_from_covered(checkpoint: dict[str, Any], covered: list[str]) -> int:
    """% mức nắm bài = tổng weight các rubric_point đã đạt (cộng dồn qua nhiều câu hỏi) / tổng weight."""
    points = checkpoint.get("rubric_points") or []
    total = sum(float(rp.get("weight", 0) or 0) for rp in points)
    if total <= 0:
        return 100 if covered else 0
    got = sum(float(rp.get("weight", 0) or 0) for rp in points if str(rp.get("id")) in set(covered))
    return int(round(got / total * 100))


def _match_rubric_id(checkpoint: dict[str, Any], covered_point: dict[str, Any]) -> str | None:
    """Tìm rubric_point ứng với một 'covered_point' do Agent 3 trả về.

    Ưu tiên khớp theo "id". Model đôi khi quên field này (chỉ trả "concept"), nên có thêm bước khớp
    mềm theo tên khái niệm — không có bước này thì ý học viên nói đúng vẫn bị tính là còn thiếu.
    """
    rubric = checkpoint.get("rubric_points") or []
    rid = str(covered_point.get("id") or "").strip()
    valid = {str(rp.get("id")) for rp in rubric if rp.get("id")}
    if rid in valid:
        return rid

    concept = (covered_point.get("concept") or "").strip().lower()
    if not concept:
        return None
    for rp in rubric:
        rp_concept = (rp.get("concept") or "").strip().lower()
        if not rp_concept:
            continue
        if concept == rp_concept or concept in rp_concept or rp_concept in concept:
            return str(rp.get("id"))
        # khớp theo tỉ lệ từ chung, đủ để bắt các cách diễn đạt lệch nhau đôi chút
        a, b = set(concept.split()), set(rp_concept.split())
        if a and b and len(a & b) / min(len(a), len(b)) >= 0.6:
            return str(rp.get("id"))
    return None


def _new_progress() -> dict[str, Any]:
    return {"covered": [], "asked": [], "current_question": None, "questions_used": 0, "hints_given": 0}


def _pick_next_question(
    checkpoint: dict[str, Any],
    progress: dict[str, Any],
    *,
    progressed: bool = False,
    opening: bool = False,
) -> dict[str, Any] | None:
    """Chọn câu hỏi kế tiếp: ưu tiên câu nhắm đúng ý CÒN THIẾU, độ khó tăng dần khi học viên vừa tiến bộ.

    opening=True (câu đầu tiên của checkpoint): lúc này chưa đạt ý nào nên câu nào cũng "nhắm vào ý còn thiếu";
    chọn theo ĐỘ KHÓ THẤP NHẤT để mở màn nhẹ nhàng, thay vì chọn câu phủ nhiều ý nhất (thường là câu khó).
    """
    bank = checkpoint.get("question_bank") or []
    if not bank:
        return None

    asked = set(progress.get("asked") or [])
    candidates = [q for q in bank if q.get("id") not in asked]
    if not candidates:
        return None

    missing = set(_rubric_ids(checkpoint)) - set(progress.get("covered") or [])
    current = progress.get("current_question") or {}
    last_level = current.get("level")
    if last_level in LEVELS:
        target_idx = min(LEVELS.index(last_level) + (1 if progressed else 0), len(LEVELS) - 1)
    else:
        target_idx = 0   # câu đầu tiên của checkpoint luôn bắt đầu từ mức dễ nhất

    def rank(q: dict[str, Any]) -> tuple[int, int, int]:
        overlap = len(set(q.get("targets") or []) & missing)
        level_idx = LEVELS.index(q["level"]) if q.get("level") in LEVELS else 0
        if opening:
            return (level_idx, -overlap, 0)
        return (-overlap, abs(level_idx - target_idx), level_idx)

    return sorted(candidates, key=rank)[0]


# Bạn học bí thì nhờ trợ giảng chứ không tự giảng — mấy câu này cố định để khỏi tốn thêm một lượt gọi LLM.
_BUDDY_HANDOVER = (
    "Thôi phần này tớ cũng mù tịt, để tớ nhờ trợ giảng nói giúp hai đứa mình nhé.",
    "Ừ tớ cũng chưa nắm được, gọi trợ giảng ra giải thích cho chắc nha.",
    "Tớ chịu luôn, nhờ trợ giảng nói lại cho cả hai đứa cùng hiểu vậy.",
)


def _build_hint(
    checkpoint: dict[str, Any],
    progress: dict[str, Any],
    missing_ids: list[str],
    *,
    level: int,
) -> str:
    """Gợi ý tăng dần — KHÔNG phải đáp án.

    Lần 1: chỉ hướng người học vào khái niệm còn thiếu và chỗ đọc lại trong slide.
    Lần 2: cụ thể hơn, lấy 'hint' của chính câu hỏi hoặc tiêu chí rubric để mở đường.
    """
    by_id = {str(rp.get("id")): rp for rp in checkpoint.get("rubric_points", [])}
    target = by_id.get(missing_ids[0]) if missing_ids else None
    citation = checkpoint.get("source_citation") or ""
    page = checkpoint.get("pdf_page")

    if level <= 1:
        concept = (target or {}).get("concept") or checkpoint.get("title", "phần này")
        where = f" (xem lại slide trang {page})" if page else (f" ({citation})" if citation else "")
        return f"Thử nghĩ theo hướng: {concept}{where}. Cậu nhớ được ý nào trước cũng được, nói thử xem."

    # Mức 2: thu hẹp phạm vi, KHÔNG được đọc "criteria" của rubric — criteria viết theo kiểu
    # "câu trả lời phải có X, Y, Z" nên nói ra là lộ nguyên đáp án, người học hết việc để nghĩ.
    question_hint = (progress.get("current_question") or {}).get("hint") or ""
    if question_hint:
        return question_hint

    remaining = [by_id[rid].get("concept", "") for rid in missing_ids if rid in by_id]
    if len(remaining) > 1:
        names = ", ".join(c for c in remaining if c)
        return (f"Phần này còn {len(remaining)} ý chưa nói tới: {names}. "
                f"Cậu chọn một ý bất kỳ và nói bằng lời của cậu xem, không cần đúng hết đâu.")

    concept = (target or {}).get("concept") or checkpoint.get("title", "")
    return (f"Thu hẹp lại nhé: chỉ cần nói ngắn gọn \"{concept}\" là gì và dùng để làm gì, "
            f"một hai câu thôi cũng được.")


def _start_checkpoint(state: "SessionState", checkpoint: dict[str, Any]) -> tuple[dict[str, Any], str]:
    """Mở một checkpoint: đặt lại tiến trình và lấy câu hỏi đầu tiên (mức dễ nhất)."""
    progress = _new_progress()
    question = _pick_next_question(checkpoint, progress, opening=True)
    if question:
        progress["asked"].append(question["id"])
        progress["current_question"] = question
        progress["questions_used"] = 1
        opening = question["question"]
    else:
        opening = checkpoint.get("student_starter_message") or f"Cậu giải thích giúp tớ phần \"{checkpoint.get('title', '')}\" với!"
    state.checkpoint_progress[checkpoint["id"]] = progress
    state.checkpoint_trials[checkpoint["id"]] = 0
    return progress, opening


def _build_evaluator_prompt(
    checkpoint: dict[str, Any],
    user_explanation: str,
    trials_used: int,
    *,
    question: dict[str, Any] | None = None,
    covered_before: list[str] | None = None,
) -> str:
    rubric_lines = "\n".join(
        f'- id="{p.get("id")}" (weight={p.get("weight", 30)}): {p.get("concept")} — {p.get("criteria", "")}'
        for p in checkpoint.get("rubric_points", [])
    ) or "- (checkpoint không có rubric_points cụ thể, tự đánh giá theo tiêu đề checkpoint)"

    asked_block = ""
    if question:
        asked_block = (
            f"\nCÂU HỎI VỪA HỎI HỌC VIÊN (mức {question.get('level', '?')}):\n"
            f"\"{question.get('question', '')}\"\n"
            f"Ý cần có trong câu trả lời cho riêng câu này: {question.get('expected_points', '(không ghi rõ)')}\n"
        )

    covered_block = ""
    if covered_before:
        covered_block = (
            "\nÝ HỌC VIÊN ĐÃ ĐẠT Ở CÁC LƯỢT TRƯỚC (hệ thống tự cộng dồn, chỉ để bạn tham khảo): "
            + ", ".join(covered_before) + "\n"
        )

    return f"""CHECKPOINT: {checkpoint.get('title')}

RUBRIC_POINTS (tiêu chí phải đạt):
{rubric_lines}
{asked_block}{covered_block}

ĐÁP ÁN THAM KHẢO (đối chiếu, và dùng làm cơ sở cho reveal_answer nếu cần):
{checkpoint.get('correction', '')}

LƯỢT THỬ HIỆN TẠI: {trials_used}/3

CÂU TRẢ LỜI CỦA HỌC VIÊN:
\"\"\"{user_explanation}\"\"\"
"""


def _build_persona_prompt(
    checkpoint: dict[str, Any],
    user_explanation: str,
    verdict: dict[str, Any],
    *,
    next_question: dict[str, Any] | None = None,
    hint: str | None = None,
) -> str:
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

{("GỢI Ý CẦN ĐƯA CHO HỌC VIÊN (diễn đạt lại bằng lời của cậu bạn học, KHÔNG nói đáp án):" + chr(10) + hint) if hint else ""}
{("CÂU HỎI TIẾP THEO CẦN HỎI (bám đúng ý học viên còn thiếu — hãy hỏi lại bằng lời của cậu bạn học, giữ nguyên ý):" + chr(10) + '"' + next_question.get("question", "") + '"' + chr(10) + "Gợi ý có thể lồng vào nếu thấy cần: " + (next_question.get("hint") or "(không có)")) if next_question else "KHÔNG có câu hỏi tiếp theo cho lượt này."}

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


def _fallback_persona_text(verdict: dict[str, Any], hint: str | None = None) -> str:
    status = verdict.get("status")
    if status == "HINT":
        return f"Không sao, từ từ thôi. {hint or 'Cậu thử nhớ lại phần này trong slide xem sao?'}"
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

        state = SessionState(
            session_id=session_id,
            lesson_id=lesson_id,
            current_checkpoint_index=0,
            checkpoint_trials={},
            checkpoint_results={},
            messages=[],
            completed=False,
        )

        if first_cp:
            _, starter_msg = _start_checkpoint(state, first_cp)
        else:
            starter_msg = "Sẵn sàng ôn bài!"

        state.messages.append({"role": "assistant", "content": starter_msg})
        return state, starter_msg

    def get_current_checkpoint(self, state: SessionState) -> dict[str, Any] | None:
        checkpoints = self.get_lesson_checkpoints(state.lesson_id)
        if 0 <= state.current_checkpoint_index < len(checkpoints):
            return checkpoints[state.current_checkpoint_index]
        return None

    # --------------------------------------------------------------- Agent 3
    def _run_evaluator(
        self,
        checkpoint: dict[str, Any],
        user_explanation: str,
        trials_used: int,
        *,
        question: dict[str, Any] | None = None,
        covered_before: list[str] | None = None,
    ) -> dict[str, Any]:
        started = time.perf_counter()
        try:
            response = self.provider.complete(
                [
                    {"role": "system", "content": EVALUATOR_SYSTEM_PROMPT},
                    {"role": "user", "content": _build_evaluator_prompt(
                        checkpoint, user_explanation, trials_used,
                        question=question, covered_before=covered_before,
                    )},
                ],
                tools=None,
                model=self.model,
                temperature=0.1,
            )
            verdict = _parse_json_object(response.text or "")
            if verdict is None or verdict.get("status") not in ("PASS", "NEEDS_IMPROVEMENT", "GAVE_UP", "EVADED"):
                raise ValueError(f"Agent 3 không trả JSON hợp lệ: {response.text!r}")
            verdict.setdefault("covered_points", [])
            verdict.setdefault("missing_points", [])
            verdict.setdefault("reveal_answer", "")
            verdict.setdefault("mastery_score", 0)
            print(f"⏱ Giáo sư AI chấm xong sau {time.perf_counter() - started:.1f}s")
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
    def _run_persona(
        self,
        checkpoint: dict[str, Any],
        user_explanation: str,
        verdict: dict[str, Any],
        *,
        next_question: dict[str, Any] | None = None,
        hint: str | None = None,
    ) -> str:
        started = time.perf_counter()
        try:
            response = self.provider.complete(
                [
                    {"role": "system", "content": PERSONA_SYSTEM_PROMPT},
                    {"role": "user", "content": _build_persona_prompt(
                        checkpoint, user_explanation, verdict, next_question=next_question, hint=hint,
                    )},
                ],
                tools=None,
                model=self.model,
                temperature=0.6,
            )
            text = (response.text or "").strip()
            if not text:
                raise ValueError("Agent 2 trả lời rỗng")
            print(f"⏱ Bạn học trả lời xong sau {time.perf_counter() - started:.1f}s")
            return text
        except Exception as exc:
            print(f"⚠️ Agent 2 (Minh AI) lỗi ({exc}), dùng câu trả lời mẫu dự phòng.")
            text = _fallback_persona_text(verdict, hint)
            if next_question and verdict.get("status") == "NEEDS_IMPROVEMENT":
                text = f"{text}\n\n{next_question.get('question', '')}"
            return text

    def _run_persona_stream(
        self,
        checkpoint: dict[str, Any],
        user_explanation: str,
        verdict: dict[str, Any],
        *,
        next_question: dict[str, Any] | None = None,
        hint: str | None = None,
    ):
        """Sinh lời thoại theo từng đoạn. Provider nào không hỗ trợ stream thì trả nguyên cục một lần."""
        messages = [
            {"role": "system", "content": PERSONA_SYSTEM_PROMPT},
            {"role": "user", "content": _build_persona_prompt(
                checkpoint, user_explanation, verdict, next_question=next_question, hint=hint,
            )},
        ]
        streamer = getattr(self.provider, "stream", None)
        if streamer is None:
            yield self._run_persona(checkpoint, user_explanation, verdict,
                                    next_question=next_question, hint=hint)
            return

        got_any = False
        started = time.perf_counter()
        try:
            for piece in streamer(messages, model=self.model, temperature=0.6,
                                  max_tokens=PERSONA_MAX_TOKENS):
                if piece:
                    if not got_any:
                        print(f"⏱ Chữ đầu tiên của bạn học sau {time.perf_counter() - started:.1f}s")
                    got_any = True
                    yield piece
        except Exception as exc:
            print(f"⚠️ Agent 2 (Minh AI) lỗi khi stream ({exc}).")
            if not got_any:
                yield self._run_persona(checkpoint, user_explanation, verdict,
                                        next_question=next_question, hint=hint)
            return

        if not got_any:
            yield self._run_persona(checkpoint, user_explanation, verdict,
                                    next_question=next_question, hint=hint)

    # ------------------------------------------------------------------ 1 lượt
    def _process_turn(self, state: SessionState, user_input: str) -> dict[str, Any] | None:
        """Chấm điểm và cập nhật trạng thái phiên — KHÔNG gọi persona.

        Tách riêng để dùng chung cho cả lượt trả một cục (/api/chat) lẫn lượt stream
        (/api/chat/stream): phần chấm xong là đẩy ngay cho UI, lời thoại chảy sau.
        Trả None nếu buổi học đã kết thúc.
        """
        current_cp = self.get_current_checkpoint(state)
        if not current_cp:
            return None

        cp_id = current_cp["id"]
        progress = state.checkpoint_progress.setdefault(cp_id, _new_progress())
        state.checkpoint_trials[cp_id] = state.checkpoint_trials.get(cp_id, 0) + 1
        trials_used = state.checkpoint_trials[cp_id]
        state.messages.append({"role": "user", "content": user_input})

        asked_question = progress.get("current_question")
        covered_before = list(progress.get("covered") or [])

        verdict = self._run_evaluator(
            current_cp, user_input, trials_used,
            question=asked_question, covered_before=covered_before,
        )

        # --- Cộng dồn ý đã đạt qua NHIỀU câu hỏi (đúng nhưng chưa đủ thì giữ lại phần đã đúng) ---
        rubric_ids = _rubric_ids(current_cp)
        newly_covered = []
        for c in verdict.get("covered_points", []):
            rid = _match_rubric_id(current_cp, c)
            if rid and rid not in covered_before and rid not in newly_covered:
                newly_covered.append(rid)
        progress["covered"] = covered_before + newly_covered
        progressed = bool(newly_covered)
        missing_ids = [rid for rid in rubric_ids if rid not in progress["covered"]]
        mastery = _mastery_from_covered(current_cp, progress["covered"])

        verdict["mastery_score"] = mastery
        if rubric_ids:
            by_id = {str(rp.get("id")): rp for rp in current_cp.get("rubric_points", [])}
            why_by_id = {str(m.get("id")): m.get("why", "") for m in verdict.get("missing_points", [])}
            verdict["missing_points"] = [
                {"id": rid, "concept": by_id[rid].get("concept", ""), "why": why_by_id.get(rid, "")}
                for rid in missing_ids if rid in by_id
            ]

        has_bank = bool(current_cp.get("question_bank"))
        next_question: dict[str, Any] | None = None
        hint_text: str | None = None

        professor_message = None
        buddy_line = None

        if verdict["status"] in ("GAVE_UP", "EVADED"):
            # Không biết / lảng tránh: gợi ý vài lần đã, hết lượt gợi ý mới giải thích kiến thức.
            if progress["hints_given"] < MAX_HINTS_BEFORE_REVEAL:
                progress["hints_given"] += 1
                hint_text = _build_hint(current_cp, progress, missing_ids or rubric_ids,
                                        level=progress["hints_given"])
                verdict["status"] = "HINT"
                verdict["reveal_answer"] = ""
                advance_checkpoint = False
                # Gợi ý là việc của Giáo sư AI; bạn học không nói gì ở lượt này (đỡ luôn 1 lượt gọi LLM).
                professor_message = hint_text
            else:
                verdict["status"] = "GAVE_UP"
                verdict["reveal_answer"] = verdict.get("reveal_answer") or current_cp.get("correction", "")
                advance_checkpoint = True
                professor_message = verdict["reveal_answer"]
                buddy_line = _BUDDY_HANDOVER[state.current_checkpoint_index % len(_BUDDY_HANDOVER)]
        elif rubric_ids and not missing_ids:
            verdict["status"] = "PASS"
            advance_checkpoint = True
        elif has_bank:
            if progress["questions_used"] >= MAX_QUESTIONS_PER_CP:
                if mastery >= 80:
                    verdict["status"] = "PASS"
                else:
                    verdict["status"] = "GAVE_UP"
                    verdict["reveal_answer"] = current_cp.get("correction", "")
                    professor_message = verdict["reveal_answer"]
                    buddy_line = _BUDDY_HANDOVER[state.current_checkpoint_index % len(_BUDDY_HANDOVER)]
                advance_checkpoint = True
            else:
                next_question = _pick_next_question(current_cp, progress, progressed=progressed)
                if next_question:
                    progress["asked"].append(next_question["id"])
                    progress["current_question"] = next_question
                    progress["questions_used"] += 1
                    verdict["status"] = "NEEDS_IMPROVEMENT"
                    advance_checkpoint = False
                else:
                    if mastery >= 80:
                        verdict["status"] = "PASS"
                    else:
                        verdict["status"] = "GAVE_UP"
                        verdict["reveal_answer"] = current_cp.get("correction", "")
                        professor_message = verdict["reveal_answer"]
                        buddy_line = _BUDDY_HANDOVER[state.current_checkpoint_index % len(_BUDDY_HANDOVER)]
                    advance_checkpoint = True
        else:
            # Checkpoint chưa có ngân hàng câu hỏi -> giữ luật 3 lượt thử như trước.
            if verdict["status"] == "NEEDS_IMPROVEMENT" and trials_used >= 3:
                verdict["status"] = "GAVE_UP"
                verdict["reveal_answer"] = current_cp.get("correction", "")
                professor_message = verdict["reveal_answer"]
                buddy_line = _BUDDY_HANDOVER[state.current_checkpoint_index % len(_BUDDY_HANDOVER)]
            advance_checkpoint = verdict["status"] in ("PASS", "GAVE_UP")

        state.checkpoint_results[cp_id] = {**verdict, "trials": trials_used,
                                           "questions_used": progress["questions_used"]}

        next_checkpoint_title = None
        next_question_text = None
        if advance_checkpoint:
            state.current_checkpoint_index += 1
            next_cp = self.get_current_checkpoint(state)
            if next_cp:
                next_checkpoint_title = next_cp["title"]
                _, next_question_text = _start_checkpoint(state, next_cp)
            else:
                state.completed = True

        current_question = progress.get("current_question") or {}
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
            "covered_count": len(progress.get("covered") or []),
            "rubric_total": len(rubric_ids),
            "hint": hint_text or "",
            "hints_given": progress.get("hints_given", 0),
            "max_hints": MAX_HINTS_BEFORE_REVEAL,
        }

        question_info = None
        if not advance_checkpoint:
            question_info = {
                "id": current_question.get("id"),
                "level": current_question.get("level"),
                "level_label": LEVEL_LABEL.get(current_question.get("level", ""), ""),
                "index": progress.get("questions_used") or trials_used,
                "max": MAX_QUESTIONS_PER_CP if has_bank else 3,
                "has_bank": has_bank,
            }

        return {
            "checkpoint": current_cp,
            "verdict": verdict,
            "hint": hint_text,
            "next_question": next_question,
            "advance_checkpoint": advance_checkpoint,
            "next_checkpoint_title": next_checkpoint_title,
            "next_question_text": next_question_text,
            "latest_evaluation": latest_evaluation,
            "question_info": question_info,
            "trials_used": trials_used,
            "professor_message": professor_message,
            "buddy_line": buddy_line,
        }

    @staticmethod
    def _completed_payload() -> dict[str, Any]:
        return {
            "assistant_text": "Buổi học đã hoàn thành! Bạn có thể xem bảng báo cáo tổng kết.",
            "latest_evaluation": None,
            "checkpoint_id": None,
            "checkpoint_title": None,
            "trials_used": 0,
            "advance_checkpoint": False,
            "next_checkpoint_title": None,
            "next_question": None,
            "current_question": None,
            "professor_message": "",
            "completed": True,
        }

    def chat_step(self, state: SessionState, user_input: str) -> dict[str, Any]:
        """Xử lý 1 lượt và trả về nguyên cục (không stream) — giữ nguyên giao diện API cũ."""
        ctx = self._process_turn(state, user_input)
        if ctx is None:
            return self._completed_payload()

        # Lượt nào do Giáo sư AI nói (gợi ý / giải thích) thì bạn học không cần sinh lời thoại —
        # vừa đúng vai, vừa bớt hẳn một lượt gọi LLM ở đúng những lượt hay chậm nhất.
        if ctx["professor_message"]:
            assistant_text = ctx["buddy_line"] or ""
        else:
            assistant_text = self._run_persona(
                ctx["checkpoint"], user_input, ctx["verdict"],
                next_question=ctx["next_question"], hint=ctx["hint"],
            )
        if assistant_text:
            state.messages.append({"role": "assistant", "content": assistant_text})
        if ctx["professor_message"]:
            state.messages.append({"role": "assistant", "content": f"[Giáo sư AI] {ctx['professor_message']}"})

        return {
            "assistant_text": assistant_text,
            "professor_message": ctx["professor_message"] or "",
            "latest_evaluation": ctx["latest_evaluation"],
            "checkpoint_id": ctx["checkpoint"]["id"],
            "checkpoint_title": ctx["checkpoint"]["title"],
            "trials_used": ctx["trials_used"],
            "advance_checkpoint": ctx["advance_checkpoint"],
            "next_checkpoint_title": ctx["next_checkpoint_title"],
            "next_question": ctx["next_question_text"],
            "current_question": ctx["question_info"],
            "completed": state.completed,
        }

    def chat_step_stream(self, state: SessionState, user_input: str):
        """Như chat_step nhưng đẩy kết quả chấm ra trước, rồi stream lời thoại theo từng đoạn.

        Sinh ra các cặp (tên_sự_kiện, dữ liệu): "evaluation" -> "delta"* -> "done".
        """
        ctx = self._process_turn(state, user_input)
        if ctx is None:
            payload = self._completed_payload()
            yield "evaluation", {k: payload[k] for k in
                                 ("latest_evaluation", "advance_checkpoint", "current_question", "completed")}
            yield "delta", {"text": payload["assistant_text"]}
            yield "done", payload
            return

        professor_message = ctx["professor_message"]
        will_stream = not professor_message

        yield "evaluation", {
            "latest_evaluation": ctx["latest_evaluation"],
            "advance_checkpoint": ctx["advance_checkpoint"],
            "next_checkpoint_title": ctx["next_checkpoint_title"],
            "current_question": ctx["question_info"],
            "checkpoint_id": ctx["checkpoint"]["id"],
            "buddy_line": ctx["buddy_line"] or "",
            "professor_message": professor_message or "",
            "will_stream": will_stream,
            "completed": False,
        }

        if not will_stream:
            # Giáo sư AI đã nói phần nội dung; bạn học chỉ có câu bàn giao ngắn (hoặc không nói gì).
            assistant_text = ctx["buddy_line"] or ""
            if assistant_text:
                state.messages.append({"role": "assistant", "content": assistant_text})
            state.messages.append({"role": "assistant", "content": f"[Giáo sư AI] {professor_message}"})
        else:
            chunks: list[str] = []
            for piece in self._run_persona_stream(
                ctx["checkpoint"], user_input, ctx["verdict"],
                next_question=ctx["next_question"], hint=ctx["hint"],
            ):
                chunks.append(piece)
                yield "delta", {"text": piece}

            assistant_text = "".join(chunks).strip() or _fallback_persona_text(ctx["verdict"], ctx["hint"])
            state.messages.append({"role": "assistant", "content": assistant_text})

        yield "done", {
            "assistant_text": assistant_text,
            "professor_message": professor_message or "",
            "buddy_line": ctx["buddy_line"] or "",
            "latest_evaluation": ctx["latest_evaluation"],
            "checkpoint_id": ctx["checkpoint"]["id"],
            "checkpoint_title": ctx["checkpoint"]["title"],
            "trials_used": ctx["trials_used"],
            "advance_checkpoint": ctx["advance_checkpoint"],
            "next_checkpoint_title": ctx["next_checkpoint_title"],
            "next_question": ctx["next_question_text"],
            "current_question": ctx["question_info"],
            "completed": state.completed,
        }
