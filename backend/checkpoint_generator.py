from __future__ import annotations

import argparse
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
from backend.tools._shared import load_slides_from_pdf, VLEARN_SLIDES_DIR

GENERATE_CHECKPOINTS_SYSTEM_PROMPT = """Bạn là Chuyên gia Đóng gói Giáo trình & Đánh giá Năng lực AI (Feynman Curriculum Agent).

Nhiệm vụ của bạn:
Phân tích toàn bộ nội dung tài liệu Slide bài giảng PDF được cung cấp, trích xuất các chủ đề/kiến thức cốt lõi nhất và xây dựng danh sách các Checkpoints (Điểm kiểm tra kỹ năng) phục vụ cho phương pháp Feynman Reverse Tutoring (người học giảng lại cho bạn học).

MỖI CHECKPOINT CẦN CÓ CẤU TRÚC JSON CHUẨN SAU:
{
  "id": "cp1_ten_chu_de",
  "order": 1,
  "title": "Tên Checkpoint ngắn gọn",
  "student_starter_message": "Câu thắc mắc ngây ngô của bạn học (Bot Ngu) mở đầu phiên Feynman. Xưng hô tớ-cậu hoặc mình-bạn. Nêu một nhận định hoặc thắc mắc ngây ngô cần người dùng giải thích lại.",
  "misconceptions": [
    "Danh sách các hiểu lầm phổ biến mà học viên hay gặp phải ở chủ đề này"
  ],
  "rubric_points": [
    {
      "id": "tieu_chi_1",
      "concept": "Khái niệm cốt lõi cần giải thích",
      "criteria": "Tiêu chuẩn giải thích đúng và đầy đủ",
      "weight": 35
    },
    {
      "id": "tieu_chi_2",
      "concept": "Khái niệm thứ hai",
      "criteria": "Tiêu chuẩn chi tiết",
      "weight": 35
    },
    {
      "id": "tieu_chi_3",
      "concept": "Khái niệm thứ ba",
      "criteria": "Tiêu chuẩn chi tiết",
      "weight": 30
    }
  ],
  "source_citation": "Trích dẫn trang slide (ví dụ: Slide [Tr.5-8])",
  "summary_for_passed": "Lời động viên khen ngợi khi người học giải thích xuất sắc và vượt qua checkpoint"
}

YÊU CẦU ĐẦU RA:
- Trả về ĐÚNG MỘT JSON ARRAY có số lượng checkpoints phù hợp với nội dung bài học.
- (Tùy vào độ khó bài học mà có số lượng checkpoint khác nhau, có thể nhiều hơn 4 nhưng phải phù hợp với nội dung slide)
- Tuỳ vào nội dung giữa các check point mà đưa ra số lượng tiêu chí khác nhau (không nhất thiết phải luôn luôn là 3 tiêu chí)
- Tổng trọng số (weight) của các rubric_points trong mỗi Checkpoint phải bằng 100.
- Không kèm bất kỳ văn bản giải thích thừa nào ngoài khối JSON.
"""


class CheckpointGeneratorAgent:
    def __init__(self, provider: Provider | None = None, model: str | None = None):
        if provider is None:
            provider_name = os.getenv("LLM_PROVIDER")
            if not provider_name:
                if os.getenv("GEMINI_API_KEY"):
                    provider_name = "gemini"
                elif os.getenv("OPENROUTER_API_KEY"):
                    provider_name = "openrouter"
                elif os.getenv("OPENAI_API_KEY"):
                    provider_name = "openai"
                else:
                    provider_name = "gemini"
            provider = make_provider(provider_name)
        self.provider = provider
        self.model = model

    def generate_checkpoints_from_pdf(self, pdf_filename: str) -> list[dict[str, Any]]:
        slides = load_slides_from_pdf(pdf_filename)
        if not slides:
            raise FileNotFoundError(f"Không tìm thấy hoặc không đọc được slide PDF: {pdf_filename}")

        slides_text_content = "\n\n".join([
            f"--- SLIDE TRANG {s['slide']} ---\n{s['content']}"
            for s in slides
        ])

        user_prompt = f"""Dưới đây là nội dung toàn bộ 29 trang Slide bài giảng từ file '{pdf_filename}':

{slides_text_content}

Hãy phân tích kỹ nội dung bài giảng trên và sinh danh sách 3-4 Checkpoints theo chuẩn phương pháp Feynman (kèm student_starter_message, misconceptions, và rubric_points). Trả về duy nhất JSON array."""

        response = self.provider.complete(
            messages=[
                {"role": "system", "content": GENERATE_CHECKPOINTS_SYSTEM_PROMPT},
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

        try:
            checkpoints = json.loads(raw_text)
            return checkpoints
        except json.JSONDecodeError as err:
            print(f"⚠️ Lỗi decode JSON từ phản hồi LLM: {err}\nNội dung raw:\n{raw_text}")
            return []


def main():
    parser = argparse.ArgumentParser(description="Feynman Checkpoint Generator Agent")
    parser.add_argument("--pdf", type=str, default="d1-slide-hackathon.pdf", help="Tên file PDF slide trong vlearn-pack/slides")
    parser.add_argument("--out", type=str, default=None, help="Đường dẫn file JSON để lưu kết quả")
    args = parser.parse_args()

    print(f"[+] Dang khoi chay Checkpoint Generator Agent cho file: {args.pdf}...")
    agent = CheckpointGeneratorAgent()
    checkpoints = agent.generate_checkpoints_from_pdf(args.pdf)

    print(f"\n[+] Da sinh thanh cong {len(checkpoints)} Checkpoints.")

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(checkpoints, f, ensure_ascii=False, indent=2)
        print(f"[+] Da luu danh sach Checkpoints vao: {args.out}")


if __name__ == "__main__":
    main()
