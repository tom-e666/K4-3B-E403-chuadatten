from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.env_loader import load_lab_env
load_lab_env(PROJECT_ROOT)

from backend.providers import make_provider
from backend.providers.base import Provider
from backend.tools._shared import load_slides_from_pdf, get_checkpoint_by_id, load_lessons_data

PROFESSOR_EVALUATOR_SYSTEM_PROMPT = """Bạn là "Giáo sư AI" - một chuyên gia giảng dạy cao cấp trong chương trình AI20k, nắm vững toàn bộ tri thức của bài giảng từ slide PDF.

Nhiệm vụ của bạn:
Đánh giá câu trả lời / giải thích của học viên (User) đối với một Checkpoint kiến thức cụ thể. Dựa trên tri thức chuẩn của các trang Slide bài giảng và bộ Tiêu chí chấm điểm (Rubric Points) cùng các Hiểu lầm phổ biến (Misconceptions).

BẠN CẦN THỰC HIỆN ĐÁNH GIÁ VÀ TRẢ VỀ KẾT QUẢ THEO ĐÚNG ĐỊNH DẠNG JSON SAU:
{
  "mastery_score": 85,
  "status": "PASS",
  "covered_points": [
    {
      "id": "tieu_chi_1",
      "concept": "Khái niệm 1",
      "earned_weight": 40,
      "feedback": "Học viên giải thích chuẩn xác ý này."
    }
  ],
  "missing_points": [
    {
      "id": "tieu_chi_2",
      "concept": "Khái niệm 2",
      "criteria": "Tiêu chuẩn giải thích",
      "weight": 30,
      "reason": "Học viên chưa đề cập đến ý này."
    }
  ],
  "misconceptions_flagged": [
    "Khẳng định sai của học viên nếu có"
  ],
  "professor_feedback": "Lời nhận xét của Giáo sư AI (khen ngợi hoặc đưa gợi ý câu hỏi dẫn dắt)",
  "bot_guidance": "Gợi ý cho bạn học (Bot Ngu) cách đáp lại học viên"
}

QUY TẮC ĐÁNH GIÁ SƯ PHẠM:
1. `status` là "PASS" nếu `mastery_score` >= 80, ngược lại là "NEEDS_IMPROVEMENT".
2. Trong `professor_feedback`:
   - Nếu PASS: Khen ngợi tinh tế, chốt lại 1 ý cốt lõi từ slide bài học và vui vẻ bảo học viên sang câu tiếp theo.
   - Nếu NEEDS_IMPROVEMENT: Ghi nhận ý học viên làm tốt, chỉ ra chính xác điểm còn thiếu hoặc còn mơ hồ theo slide bài học và đưa ra câu hỏi gợi mở / gợi ý mà KHÔNG trực tiếp đưa ra đáp án thay người học.
3. Giữ giọng văn thân thiện, uyên bác, khích lệ và chuẩn xác về mặt chuyên môn AI.
4. Trả về DUY NHẤT một khối JSON hợp lệ, không kèm văn bản giải thích ngoài.
"""


class ProfessorEvaluatorAgent:
    def __init__(self, provider: Provider | None = None, model: str | None = None):
        if provider is None:
            provider_name = os.getenv("LLM_PROVIDER")
            if not provider_name:
                if os.getenv("OPENROUTER_API_KEY"):
                    provider_name = "openrouter"
                elif os.getenv("GEMINI_API_KEY"):
                    provider_name = "gemini"
                elif os.getenv("OPENAI_API_KEY"):
                    provider_name = "openai"
                else:
                    provider_name = "openrouter"
            provider = make_provider(provider_name)
        self.provider = provider
        self.model = model

    def evaluate_explanation(
        self,
        checkpoint_id: str,
        user_explanation: str,
        lesson_id: str = "lesson_01"
    ) -> dict[str, Any]:
        cp = get_checkpoint_by_id(checkpoint_id)
        if not cp:
            lesson_data = load_lessons_data(lesson_id)
            cps = lesson_data.get("checkpoints", [])
            cp = cps[0] if cps else None

        if not cp:
            return {
                "checkpoint_id": checkpoint_id,
                "mastery_score": 0,
                "status": "NEEDS_IMPROVEMENT",
                "covered_points": [],
                "missing_points": [],
                "professor_feedback": "Không tìm thấy thông tin checkpoint để chấm điểm.",
                "bot_guidance": "Vui lòng thử lại."
            }

        pdf_filename = "d2-slide-hackathon.pdf" if lesson_id in ["lesson_02", "lesson_03"] else "d1-slide-hackathon.pdf"
        slides = load_slides_from_pdf(pdf_filename)
        slides_text = "\n\n".join([f"Trang {s['slide']}: {s['content']}" for s in slides[:12]])

        user_prompt = f"""TÀI LIỆU SLIDE BÀI GIẢNG (Nguồn tri thức):
{slides_text}

THÔNG TIN CHECKPOINT ĐANG KIỂM TRA:
- ID: {cp.get('id')}
- Tiêu đề: {cp.get('title')}
- Tiêu chí chấm điểm (Rubrics): {json.dumps(cp.get('rubric_points', []), ensure_ascii=False)}
- Các hiểu lầm cần tránh: {json.dumps(cp.get('misconceptions', []), ensure_ascii=False)}

LỜI GIẢI THÍCH CỦA HỌC VIÊN (USER):
"{user_explanation}"

Hãy đánh giá câu trả lời trên và xuất ra JSON theo đúng định dạng được yêu cầu."""

        try:
            response = self.provider.complete(
                messages=[
                    {"role": "system", "content": PROFESSOR_EVALUATOR_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                tools=None,
            )

            raw_text = response.text.strip()
            if raw_text.startswith("```"):
                lines = raw_text.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                raw_text = "\n".join(lines).strip()

            result = json.loads(raw_text)
            result["checkpoint_id"] = checkpoint_id
            result["checkpoint_title"] = cp.get("title", "")
            result["source_citation"] = cp.get("source_citation", "")
            return result
        except Exception as err:
            print(f"⚠️ Lỗi đánh giá từ ProfessorEvaluatorAgent: {err}")
            return {
                "checkpoint_id": checkpoint_id,
                "checkpoint_title": cp.get("title", ""),
                "mastery_score": 50,
                "status": "NEEDS_IMPROVEMENT",
                "covered_points": [],
                "missing_points": [],
                "professor_feedback": f"Giáo sư AI đánh giá: Câu trả lời chưa đủ chi tiết. Lỗi: {str(err)}",
                "bot_guidance": "Hãy giải thích rõ ràng hơn các khái niệm cốt lõi từ slide bài giảng."
            }
