from __future__ import annotations

from typing import Any, Callable

from .lookup_lesson import lookup_lesson_point
from .evaluator import grade_explanation
from .reporter import generate_session_report

TOOL_FUNCTIONS: dict[str, Callable[..., Any]] = {
    "lookup_lesson_point": lookup_lesson_point,
    "grade_explanation": grade_explanation,
    "generate_session_report": generate_session_report,
}

TOOLS_DECLARATIONS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "lookup_lesson_point",
            "description": "Tra cứu kiến thức chuẩn, danh sách rubric criteria và các hiểu lầm phổ biến của một Checkpoint bài học.",
            "parameters": {
                "type": "object",
                "properties": {
                    "checkpoint_id": {
                        "type": "string",
                        "description": "Mã định danh checkpoint (ví dụ: 'cp1_self_attention', 'cp2_multi_head_attention', 'cp3_positional_encoding')."
                    }
                },
                "required": ["checkpoint_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "grade_explanation",
            "description": "Chấm điểm và phân tích câu giải thích của học viên so với tiêu chuẩn của Checkpoint (trả về % Mastery, điểm đạt/hổng, và hướng dẫn phản hồi cho bạn học).",
            "parameters": {
                "type": "object",
                "properties": {
                    "checkpoint_id": {
                        "type": "string",
                        "description": "Mã định danh checkpoint đang chấm."
                    },
                    "user_explanation": {
                        "type": "string",
                        "description": "Toàn bộ văn bản giải thích mà học viên vừa gửi."
                    }
                },
                "required": ["checkpoint_id", "user_explanation"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_session_report",
            "description": "Tổng kết phiên học sau khi qua các checkpoints: tính điểm trung bình, danh sách concept đã đạt và concept cần ôn tập.",
            "parameters": {
                "type": "object",
                "properties": {
                    "session_results": {
                        "type": "array",
                        "items": {
                            "type": "object"
                        },
                        "description": "Danh sách kết quả đánh giá của các checkpoints trong phiên."
                    }
                },
                "required": ["session_results"]
            }
        }
    }
]

__all__ = ["TOOL_FUNCTIONS", "TOOLS_DECLARATIONS", "lookup_lesson_point", "grade_explanation", "generate_session_report"]

