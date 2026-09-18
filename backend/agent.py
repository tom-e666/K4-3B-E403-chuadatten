from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from .providers.base import Provider, ToolCall
from .tools import TOOL_FUNCTIONS, TOOLS_DECLARATIONS
from .tools._shared import load_lessons_data, get_checkpoint_by_id, get_lesson_by_id

DEFAULT_SYSTEM_PROMPT = """Bạn là 'Minh AI' - một bạn học cùng lớp trong chương trình AI20k, đang cùng người học (User) ôn tập kiến thức các bài giảng AI thực chiến.

MỤC TIÊU & PHƯƠNG PHÁP (Feynman Reverse Tutoring):
- Bạn đóng vai một người học đang gặp khúc mắc, có những hiểu lầm ngây ngô (misconceptions) và cần người dùng đóng vai 'người thầy' giảng giải lại cho bạn.
- Bạn xưng hô tự nhiên, thân thiện: "tớ - cậu" hoặc "mình - bạn".
- QUY TẮC BẮT BUỘC: Khi người dùng gửi lời giải thích, bạn PHẢI LUÔN LUÔN GỌI TOOL `grade_explanation` để kiểm tra độ chính xác và độ bao phủ kiến thức của người dùng.
- Sau khi nhận kết quả từ tool:
  + Nếu kết quả `status == 'PASS'`: Bạn tỏ ra hào hứng, gật gù cảm ơn vì đã hiểu ra bản chất, chốt lại 1 ý cốt lõi và vui vẻ bảo bạn học chuyển sang câu hỏi tiếp theo.
  + Nếu kết quả `status == 'NEEDS_IMPROVEMENT'`: Bạn gãi đầu, thắc mắc về đúng điểm mà người dùng giải thích còn thiếu hoặc còn mơ hồ (dựa vào `missing_points` hoặc `bot_guidance` từ tool). Tuyệt đối KHÔNG đưa ra đáp án thay người học!
- TUYỆT ĐỐI KHÔNG tự trả lời hay giải thích bài thay người dùng. Mục đích là để người dùng tự diễn đạt kiến thức bằng lời của mình.
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


class FeynmanAgent:
    def __init__(
        self,
        provider: Provider,
        *,
        model: str | None = None,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        max_tool_rounds: int = 4,
    ) -> None:
        self.provider = provider
        self.model = model
        self.system_prompt = system_prompt
        self.max_tool_rounds = max_tool_rounds
        self.tools = TOOLS_DECLARATIONS

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
            messages=[
                {"role": "assistant", "content": starter_msg}
            ],
            completed=False
        )
        return state, starter_msg

    def get_current_checkpoint(self, state: SessionState) -> dict[str, Any] | None:
        checkpoints = self.get_lesson_checkpoints(state.lesson_id)
        if 0 <= state.current_checkpoint_index < len(checkpoints):
            return checkpoints[state.current_checkpoint_index]
        return None

    def execute_tool_call(self, call: ToolCall) -> dict[str, Any]:
        func = TOOL_FUNCTIONS.get(call.name)
        if not func:
            return {"error": "unknown_tool", "message": f"Không có tool '{call.name}'"}
        try:
            result = func(**call.args)
        except Exception as exc:
            result = {"error": type(exc).__name__, "message": str(exc)}
        return {"tool": call.name, "args": call.args, "result": result}

    def chat_step(self, state: SessionState, user_input: str) -> dict[str, Any]:
        """
        Xử lý 1 lượt tin nhắn của người học:
        1. Cập nhật lượt thử của Checkpoint hiện tại
        2. Chạy Tool Calling loop để model gọi grade_explanation
        3. Cập nhật state nếu checkpoint được PASS hoặc đạt max trials
        4. Trả về phản hồi cho UI
        """
        current_cp = self.get_current_checkpoint(state)
        if not current_cp:
            return {
                "assistant_text": "Buổi học đã hoàn thành! Bạn có thể xem bảng báo cáo tổng kết.",
                "state": state,
                "completed": True,
                "latest_evaluation": None
            }

        cp_id = current_cp["id"]
        state.checkpoint_trials[cp_id] = state.checkpoint_trials.get(cp_id, 0) + 1

        state.messages.append({"role": "user", "content": user_input})

        working_messages = [
            {"role": "system", "content": f"{self.system_prompt}\n\nTHÔNG TIN BÀI HỌC HIỆN TẠI (Bài: {state.lesson_id}):\n- Checkpoint: {current_cp['title']} (ID: {cp_id})\n- Lượt thử của học viên: {state.checkpoint_trials[cp_id]}/3."},
            *state.messages
        ]

        latest_evaluation = None
        tool_events = []

        for _ in range(self.max_tool_rounds):
            try:
                response = self.provider.complete(working_messages, self.tools, model=self.model, temperature=0.2)
            except Exception as exc:
                print(f"⚠️ Provider API bị lỗi ({exc}), tự động chuyển sang chế độ đánh giá rubric trực tiếp.")
                from .tools.evaluator import grade_explanation
                latest_evaluation = grade_explanation(cp_id, user_input)
                state.checkpoint_results[cp_id] = {
                    **latest_evaluation,
                    "trials": state.checkpoint_trials[cp_id]
                }
                if latest_evaluation.get("status") == "PASS":
                    assistant_text = f"À tớ hiểu rồi! Cậu giải thích rất chuẩn và đúng trọng tâm ({latest_evaluation.get('mastery_score')}%), cảm ơn cậu nhiều nha!"
                else:
                    missing_str = ", ".join(m.get("concept", "") for m in latest_evaluation.get("missing_points", []))
                    assistant_text = f"Ủa tớ vẫn chưa rõ lắm, hình như còn thiếu phần [{missing_str or 'khái niệm cốt lõi'}]. Cậu giải thích thêm cho tớ được không?"
                state.messages.append({"role": "assistant", "content": assistant_text})
                break

            calls = response.tool_calls

            if not calls:
                assistant_text = response.text or "Tớ đang suy nghĩ câu trả lời..."
                state.messages.append({"role": "assistant", "content": assistant_text})
                break

            # Ghi nhận tool calls vào messages
            call_summaries = [{"name": c.name, "args": c.args} for c in calls]
            working_messages.append({
                "role": "assistant",
                "content": f"{response.text or ''}\n\n[TOOL CALLS]: {json.dumps(call_summaries, ensure_ascii=False)}"
            })

            round_results = []
            for call in calls:
                event = self.execute_tool_call(call)
                round_results.append(event)
                tool_events.append(event)
                if call.name == "grade_explanation" and "result" in event:
                    latest_evaluation = event["result"]
                    state.checkpoint_results[cp_id] = {
                        **latest_evaluation,
                        "trials": state.checkpoint_trials[cp_id]
                    }

            working_messages.append({
                "role": "user",
                "content": f"[TOOL RESULTS]:\n{json.dumps(round_results, ensure_ascii=False)}"
            })
        else:
            assistant_text = "Tớ đã nghe cậu giải thích rồi, cảm ơn cậu nhiều nhé!"
            state.messages.append({"role": "assistant", "content": assistant_text})

        # Xử lý chuyển Checkpoint nếu đạt hoặc hết lượt
        advance_checkpoint = False
        next_checkpoint_title = None

        if latest_evaluation:
            is_passed = latest_evaluation.get("status") == "PASS"
            trials_used = state.checkpoint_trials[cp_id]

            if is_passed or trials_used >= 3:
                advance_checkpoint = True
                state.current_checkpoint_index += 1
                next_cp = self.get_current_checkpoint(state)
                if next_cp:
                    next_checkpoint_title = next_cp["title"]
                    # Thêm câu hỏi tiếp theo của Bot vào cuộc trò chuyện
                    next_starter = f"\n\n👉 **Chuyển sang phần tiếp theo ({next_cp['title']})**:\n{next_cp.get('student_starter_message', '')}"
                    state.messages[-1]["content"] += next_starter
                    assistant_text = state.messages[-1]["content"]
                    state.checkpoint_trials[next_cp["id"]] = 0
                else:
                    state.completed = True
                    assistant_text += "\n\n🎉 **Chúc mừng bạn! Chúng ta đã hoàn thành tất cả các mục bài học của buổi ôn tập hôm nay!**"
                    state.messages[-1]["content"] = assistant_text

        return {
            "assistant_text": assistant_text,
            "latest_evaluation": latest_evaluation,
            "tool_events": tool_events,
            "checkpoint_id": cp_id,
            "checkpoint_title": current_cp["title"],
            "trials_used": state.checkpoint_trials[cp_id],
            "advance_checkpoint": advance_checkpoint,
            "next_checkpoint_title": next_checkpoint_title,
            "completed": state.completed
        }
