"""
Agent 1 — sinh Lesson + Checkpoint từ file slide PDF (Feynman AI).

Đọc trực tiếp file PDF bằng khả năng hiểu PDF gốc của Gemini hoặc OpenAI (không cần
thư viện tách chữ riêng), yêu cầu model trả về đúng cấu trúc dữ liệu mà
backend/data/lessons.json đang dùng (slides + checkpoint kèm rubric_points/đáp án
chuẩn — số lượng checkpoint tùy nội dung thật của slide, không cố định), rồi ghi
thêm (hoặc thay thế theo id) vào file đó.

Cách dùng:
    python backend/lesson_ingest.py --pdf backend/data/vlearn-pack/slides/d1-slide-hackathon.pdf \
        --lesson-id lesson_04 --video-title "Buổi 4: ..." --video-duration "50 phút"

Mặc định tự chọn provider theo key có sẵn trong .env (ưu tiên GEMINI_API_KEY, sau đó
OPENAI_API_KEY) — thêm --provider gemini|openai để chỉ định rõ.

Thêm --dry-run để chỉ in JSON ra màn hình, không ghi vào lessons.json.

Không bắt buộc chạy tay bằng dòng lệnh: FE có sẵn mục "Nguồn slide PDF" trong sidebar, bấm
"⚡ Phân tích" là gọi POST /api/lessons/generate chạy đúng Agent 1 này rồi tự nạp checkpoint mới
lên giao diện (FE nạp bài học thật qua GET /api/lessons?full=1, không còn dùng dữ liệu mock cứng).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(BACKEND_DIR))

from backend.env_loader import load_lab_env  # noqa: E402
load_lab_env(PROJECT_ROOT)

DEFAULT_LESSONS_FILE = BACKEND_DIR / "data" / "lessons.json"   # kho cũ, chỉ đọc để tương thích
LESSONS_DIR = BACKEND_DIR / "data" / "lessons"                 # mỗi slide -> 1 file JSON checkpoint
DEFAULT_MODEL_GEMINI = "gemini-3.5-flash"
DEFAULT_MODEL_OPENAI = "gpt-5.6-luna"

PROMPT_TEMPLATE = """Bạn là chuyên gia thiết kế chương trình học (instructional designer) cho nền tảng VLearn AI20k.
Nhiệm vụ: đọc kỹ toàn bộ nội dung slide PDF đính kèm và tạo ra dữ liệu bài học JSON theo ĐÚNG cấu trúc dưới đây,
để dùng cho tính năng "Feynman Reverse Tutoring" — nơi học viên phải tự giải thích lại kiến thức cho một AI đóng
vai bạn học ngơ ngác, rồi một AI khác (Giáo sư AI) chấm điểm mức độ hiểu bài bằng cách đọc hiểu ngữ nghĩa.

YÊU CẦU BẮT BUỘC:
- Số lượng checkpoint KHÔNG cố định — tùy vào slide thực sự có bao nhiêu khái niệm cốt lõi, khó, dễ hiểu lầm
  (thường rơi vào khoảng 2-6). Đừng cố ép đủ một con số nào đó: slide mỏng thì ít checkpoint, slide sâu/nhiều ý
  thì nhiều checkpoint hơn. Mỗi checkpoint PHẢI thực sự có mặt và được giảng giải rõ trong chính file PDF đính
  kèm. TUYỆT ĐỐI không tự bịa ra khái niệm chỉ vì nó "nên có" trong chủ đề — mọi checkpoint phải truy được về
  đúng trang thật trong PDF, không suy diễn từ kiến thức nền của bạn ngoài nội dung slide.
- "pdf_page": SỐ TRANG THẬT (đếm từ trang 1 của chính file PDF đính kèm, không phải số thứ tự in trên slide) nơi
  khái niệm của checkpoint này được giảng giải kỹ nhất — dùng để phần mềm tự nhảy tới đúng trang khi học viên vào
  checkpoint đó. Phải là số trang có thật, đã tự kiểm tra lại nội dung trang đó đúng khớp trước khi điền.
- Mỗi checkpoint có 2-3 rubric_points mô tả RÕ RÀNG, CỤ THỂ ý nào phải có trong câu trả lời mới coi là đạt — vì
  phần chấm điểm sau này do một AI khác đọc "criteria" này rồi so sánh Ý NGHĨA với câu học viên trả lời, KHÔNG
  dùng từ khóa cố định — nên "criteria" phải viết đủ chi tiết để một người chưa học bài cũng chấm đúng được.
- "student_starter_message": câu hỏi mở đầu của một người bạn học đang hiểu sai hoặc thắc mắc ngây ngô về đúng
  checkpoint đó — văn phong tự nhiên, xưng "tớ - cậu", để một AI khác dùng nguyên văn làm lời mở đầu hội thoại.
- "correction": lời giải thích chuẩn, đầy đủ, dùng khi học viên bỏ cuộc hoặc thử 3 lần vẫn chưa đạt.
- "sample_correct" / "sample_wrong": ví dụ câu trả lời đạt / chưa đạt, giống văn phong học viên thật (không phải
  văn phong giáo trình) — dùng làm dữ liệu test nhanh.
- "source_citation": trích đúng số trang thật (khớp với "pdf_page") / mục trong slide đính kèm, KHÔNG bịa nguồn.
- Giữ tiếng Việt tự nhiên, không dịch các thuật ngữ kỹ thuật tiếng Anh đã quen dùng (Query, Key, Value, Attention...).

TRẢ VỀ DUY NHẤT một JSON object đúng schema sau (không thêm chữ nào khác ngoài JSON, không dùng markdown fence):
{{
  "id": "{lesson_id}",
  "topic": "...",
  "short_title": "...",
  "course": "{course}",
  "duration": "{video_duration}",
  "video_title": "{video_title}",
  "summary": "...",
  "slides": [
    {{"slide": 1, "kicker": "...", "title": "...", "bullets": ["...", "..."], "citation": "..."}}
  ],
  "checkpoints": [
    {{
      "id": "cp1_<slug_ngan_gon_tieng_anh>",
      "order": 1,
      "short": "CP1",
      "title": "...",
      "slide": 1,
      "pdf_page": 1,
      "student_starter_message": "...",
      "misconceptions": ["...", "...", "..."],
      "rubric_points": [
        {{"id": "<slug>", "concept": "...", "criteria": "...", "weight": 40}}
      ],
      "source_citation": "...",
      "correction": "...",
      "sample_correct": "...",
      "sample_wrong": "...",
      "deep_dive": "..."
    }}
    // Thêm bao nhiêu object checkpoint tùy số lượng khái niệm cốt lõi thật có trong slide, không cố định.
  ]
}}
"""


def _next_lesson_id(existing: list[dict[str, Any]]) -> str:
    nums = [int(m.group(1)) for lsn in existing if (m := re.match(r"lesson_(\d+)$", str(lsn.get("id", ""))))]
    return f"lesson_{(max(nums) + 1) if nums else 1:02d}"


def _load_store() -> dict[str, Any]:
    if DEFAULT_LESSONS_FILE.exists():
        with open(DEFAULT_LESSONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"lessons": []}


def _all_known_lessons() -> list[dict[str, Any]]:
    """Mọi bài học đang có: các file JSON theo slide + kho lessons.json cũ (để đánh số id không trùng)."""
    lessons = list(_load_store().get("lessons", []))
    if LESSONS_DIR.exists():
        for path in LESSONS_DIR.glob("*.json"):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    lessons.append(json.load(f))
            except (OSError, json.JSONDecodeError):
                continue
    return lessons


def _validate_lesson(lesson: dict[str, Any]) -> None:
    missing_top = [k for k in ("topic", "checkpoints") if not lesson.get(k)]
    if missing_top:
        raise ValueError(f"JSON model trả về thiếu field bắt buộc: {missing_top}")

    checkpoints = lesson.get("checkpoints", [])
    if not (1 <= len(checkpoints) <= 8):
        raise ValueError(
            f"Số checkpoint bất thường ({len(checkpoints)}) — kỳ vọng 1-8 checkpoint thực sự có trong slide. "
            f"Có thể model bịa thêm hoặc bỏ sót, thử chạy lại."
        )
    for cp in checkpoints:
        for cp_field in ("id", "title", "student_starter_message", "rubric_points", "correction"):
            if not cp.get(cp_field):
                raise ValueError(f"Checkpoint '{cp.get('id', '?')}' thiếu field bắt buộc: {cp_field}")


def _resolve_provider(explicit: str | None) -> str:
    if explicit:
        return explicit
    provider = os.getenv("LLM_PROVIDER")
    if provider in ("gemini", "openai"):
        return provider
    if os.getenv("GEMINI_API_KEY"):
        return "gemini"
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    raise RuntimeError(
        "Không tìm thấy GEMINI_API_KEY hay OPENAI_API_KEY trong .env — Agent 1 cần ít nhất 1 trong 2 để đọc PDF."
    )


def _call_gemini(pdf_path: Path, prompt: str, model: str | None) -> str:
    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:
        raise RuntimeError("Cần cài google-genai: pip install google-genai") from exc

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Thiếu GEMINI_API_KEY trong .env — nhánh Gemini của Agent 1 cần key này.")

    client = genai.Client(api_key=api_key)
    resp = client.models.generate_content(
        model=model or os.getenv("LLM_MODEL") or DEFAULT_MODEL_GEMINI,
        contents=[
            types.Part.from_bytes(data=pdf_path.read_bytes(), mime_type="application/pdf"),
            prompt,
        ],
        config=types.GenerateContentConfig(temperature=0.3, response_mime_type="application/json"),
    )
    return (resp.text or "").strip()


def _call_openai(pdf_path: Path, prompt: str, model: str | None) -> str:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("Cần cài openai: pip install openai") from exc

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Thiếu OPENAI_API_KEY trong .env — nhánh OpenAI của Agent 1 cần key này.")

    import base64
    pdf_b64 = base64.b64encode(pdf_path.read_bytes()).decode("utf-8")

    # BASE_URL cho phép trỏ tới endpoint tương thích OpenAI khác (proxy/reseller)
    # thay vì mặc định api.openai.com — dùng khi OPENAI_API_KEY không phải key OpenAI gốc.
    client = OpenAI(api_key=api_key, base_url=os.getenv("BASE_URL") or None)
    resp = client.responses.create(
        model=model or os.getenv("LLM_MODEL") or DEFAULT_MODEL_OPENAI,
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {
                        "type": "input_file",
                        "filename": pdf_path.name,
                        "file_data": f"data:application/pdf;base64,{pdf_b64}",
                    },
                ],
            }
        ],
        text={"format": {"type": "json_object"}},
        temperature=0.3,
    )
    return (resp.output_text or "").strip()


def generate_lesson_from_pdf(
    pdf_path: Path,
    *,
    lesson_id: str | None = None,
    course: str = "AI20k Khóa 4",
    video_title: str = "",
    video_duration: str = "45 phút",
    model: str | None = None,
    provider: str | None = None,
) -> dict[str, Any]:
    if not pdf_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file PDF: {pdf_path}")

    resolved_provider = _resolve_provider(provider)

    resolved_id = lesson_id or _next_lesson_id(_all_known_lessons())

    prompt = PROMPT_TEMPLATE.format(
        lesson_id=resolved_id,
        course=course,
        video_title=video_title or pdf_path.stem,
        video_duration=video_duration,
    )

    print(f"(Agent 1 dùng provider: {resolved_provider})")
    if resolved_provider == "gemini":
        raw_text = _call_gemini(pdf_path, prompt, model)
    elif resolved_provider == "openai":
        raw_text = _call_openai(pdf_path, prompt, model)
    else:
        raise ValueError(f"Provider không hỗ trợ: {resolved_provider} (chỉ nhận 'gemini' hoặc 'openai')")

    if not raw_text:
        raise RuntimeError(f"{resolved_provider} không trả về nội dung nào (rỗng) — thử lại hoặc kiểm tra file PDF.")

    lesson = json.loads(raw_text)
    _validate_lesson(lesson)
    lesson["id"] = resolved_id
    lesson.setdefault("slides_count", len(lesson.get("slides", [])))
    lesson.setdefault("source_transcript", "")
    return lesson


def lesson_json_path(lesson: dict[str, Any]) -> Path:
    """Đường dẫn file JSON checkpoint của một bài học: đặt tên theo chính file slide sinh ra nó."""
    stem = Path(lesson.get("pdf_file") or "").stem or str(lesson.get("id") or "lesson")
    safe = re.sub(r"[^0-9A-Za-z._-]+", "-", stem).strip("-") or "lesson"
    return LESSONS_DIR / f"{safe}.json"


def save_lesson(lesson: dict[str, Any], *, out_file: Path | None = None) -> Path:
    """Ghi checkpoint của bài học ra ĐÚNG MỘT file JSON riêng (mỗi slide PDF một file).

    Trả về đường dẫn file vừa ghi. Backend nạp checkpoint lên UI từ chính các file này.
    """
    target = out_file or lesson_json_path(lesson)
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        json.dump(lesson, f, ensure_ascii=False, indent=2)

    # Dọn bản trùng id còn sót trong lessons.json cũ để UI không hiện 2 bài giống nhau.
    if DEFAULT_LESSONS_FILE.exists():
        try:
            store = _load_store()
            lessons = store.get("lessons", [])
            kept = [l for l in lessons if l.get("id") != lesson.get("id")]
            if len(kept) != len(lessons):
                store["lessons"] = kept
                with open(DEFAULT_LESSONS_FILE, "w", encoding="utf-8") as f:
                    json.dump(store, f, ensure_ascii=False, indent=2)
        except (OSError, json.JSONDecodeError):
            pass

    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="Agent 1 — sinh checkpoint bài học từ slide PDF.")
    parser.add_argument("--pdf", required=True, help="Đường dẫn file PDF slide.")
    parser.add_argument("--lesson-id", default=None, help="vd lesson_04 — bỏ trống để tự tăng số.")
    parser.add_argument("--course", default="AI20k Khóa 4")
    parser.add_argument("--video-title", default="")
    parser.add_argument("--video-duration", default="45 phút")
    parser.add_argument("--provider", choices=["gemini", "openai"], default=None, help="Bỏ trống để tự chọn theo key có trong .env.")
    parser.add_argument("--model", default=None, help="Tên model — mặc định theo provider.")
    parser.add_argument("--dry-run", action="store_true", help="Chỉ in JSON, không ghi lessons.json.")
    args = parser.parse_args()

    print(f"Đang đọc & phân tích slide: {args.pdf} ...")
    lesson = generate_lesson_from_pdf(
        Path(args.pdf),
        lesson_id=args.lesson_id,
        course=args.course,
        video_title=args.video_title,
        video_duration=args.video_duration,
        model=args.model,
        provider=args.provider,
    )

    print(json.dumps(lesson, ensure_ascii=False, indent=2))

    if args.dry_run:
        print("\n(dry-run) Chưa ghi vào lessons.json.")
        return

    out_path = save_lesson(lesson)
    print(f"\nĐã ghi lesson '{lesson['id']}' ({len(lesson['checkpoints'])} checkpoint) vào {out_path}")
    print("Lưu ý: FE/mock-cp2/index.html tự chứa MOCK_LESSONS riêng, không gọi /api/lessons —")
    print("muốn hiện lesson này trên UI mock thì phải copy tay checkpoint sang đó.")


if __name__ == "__main__":
    main()
