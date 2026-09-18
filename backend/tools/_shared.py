from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
LESSONS_MULTI_FILE = DATA_DIR / "lessons.json"
LESSONS_SINGLE_FILE = DATA_DIR / "transformer_lessons.json"
# Mỗi file slide PDF được Agent 1 phân tích sẽ sinh ra ĐÚNG MỘT file JSON checkpoint trong thư mục này
# (vd: d1-slide-hackathon.json). Checkpoint hiển thị trên UI được nạp từ chính các file đó.
LESSONS_DIR = DATA_DIR / "lessons"

VLEARN_SLIDES_DIR = DATA_DIR / "vlearn-pack" / "slides"

_CACHED_STORE: dict[str, Any] | None = None
_PDF_SLIDES_CACHE: dict[str, list[dict[str, Any]]] = {}


def load_slides_from_pdf(pdf_filename: str) -> list[dict[str, Any]]:
    """Trích xuất danh sách các trang slide trực tiếp từ file PDF trong vlearn-pack/slides."""
    if pdf_filename in _PDF_SLIDES_CACHE:
        return _PDF_SLIDES_CACHE[pdf_filename]

    pdf_path = VLEARN_SLIDES_DIR / pdf_filename
    if not pdf_path.exists():
        return []

    slides = []
    try:
        import pypdf
        reader = pypdf.PdfReader(pdf_path)
        for idx, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            slides.append({
                "slide": idx,
                "title": f"Trang slide {idx} ({pdf_filename})",
                "pdf_url": f"/slides/{pdf_filename}",
                "content": text.strip(),
                "bullets": [line.strip() for line in text.split("\n") if line.strip()][:5]
            })
    except Exception as err:
        print(f"⚠️ Lỗi đọc file PDF slide {pdf_filename}: {err}")

    _PDF_SLIDES_CACHE[pdf_filename] = slides
    return slides


def _load_raw_store() -> dict[str, Any]:
    """Gộp bài học từ 2 nguồn: các file JSON sinh theo từng slide (ưu tiên) và file lessons.json cũ."""
    global _CACHED_STORE
    if _CACHED_STORE is not None:
        return _CACHED_STORE

    lessons: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    # 1) Nguồn chính: mỗi slide một file JSON trong data/lessons/
    if LESSONS_DIR.exists():
        for path in sorted(LESSONS_DIR.glob("*.json")):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    lesson = json.load(f)
            except (OSError, json.JSONDecodeError) as exc:
                print(f"⚠ Bỏ qua file checkpoint hỏng {path.name}: {exc}")
                continue
            lesson["_source_file"] = path.name
            if lesson.get("id"):
                seen_ids.add(lesson["id"])
            lessons.append(lesson)

    # 2) Nguồn cũ (tương thích ngược): lessons.json gộp nhiều bài trong 1 file
    if LESSONS_MULTI_FILE.exists():
        try:
            with open(LESSONS_MULTI_FILE, "r", encoding="utf-8") as f:
                for lesson in json.load(f).get("lessons", []):
                    if lesson.get("id") not in seen_ids:
                        lessons.append(lesson)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"⚠ Không đọc được lessons.json: {exc}")

    if not lessons and LESSONS_SINGLE_FILE.exists():
        with open(LESSONS_SINGLE_FILE, "r", encoding="utf-8") as f:
            lessons = [json.load(f)]

    _CACHED_STORE = {"lessons": lessons}
    return _CACHED_STORE


def invalidate_cache() -> None:
    """Xoá cache lessons đang giữ trong RAM — gọi ngay sau khi Agent 1 ghi thêm/ghi đè
    bài học mới vào lessons.json, để các request sau đọc được dữ liệu vừa sinh."""
    global _CACHED_STORE
    _CACHED_STORE = None


def get_full_lessons() -> list[dict[str, Any]]:
    """Trả về nguyên vẹn danh sách bài học (đủ slides + checkpoints), dùng cho FE nạp 1 lần."""
    return _load_raw_store().get("lessons", [])


CHECKPOINTS_D1_FILE = DATA_DIR / "checkpoints_d1.json"
CHECKPOINTS_D2_FILE = DATA_DIR / "checkpoints_d2.json"


def load_generated_checkpoints(lesson_id: str) -> list[dict[str, Any]]:
    """Tải danh sách checkpoints sinh ra từ Agent AI tương ứng với từng bài học."""
    cp_file = CHECKPOINTS_D2_FILE if lesson_id in ["lesson_02", "lesson_03"] else CHECKPOINTS_D1_FILE
    if cp_file.exists():
        try:
            with open(cp_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as err:
            print(f"⚠️ Lỗi đọc file checkpoint {cp_file}: {err}")
    return []


def get_all_lessons() -> list[dict[str, Any]]:
    """Trả về danh sách tất cả các bài học (slides & checkpoints sinh từ PDF)."""
    store = _load_raw_store()
    lessons = store.get("lessons", [])
    result = []
    for lsn in lessons:
        lesson_id = lsn.get("id", "lesson_default")
        pdf_file = "d2-slide-hackathon.pdf" if lesson_id in ["lesson_02", "lesson_03"] else "d1-slide-hackathon.pdf"
        pdf_slides = load_slides_from_pdf(pdf_file)
        gen_cps = load_generated_checkpoints(lesson_id)
        result.append({
            "id": lesson_id,
            "topic": lsn.get("topic", "Chủ đề bài học"),
            "short_title": lsn.get("short_title", lsn.get("topic", "")),
            "course": lsn.get("course", "VLearn AI20k"),
            "duration": lsn.get("duration", "45 phút"),
            "source_transcript": lsn.get("source_transcript", ""),
            "pdf_url": f"/slides/{pdf_file}",
            "slides_count": len(pdf_slides) if pdf_slides else len(lsn.get("slides", [])),
            "summary": lsn.get("summary", ""),
            "checkpoints_count": len(gen_cps) if gen_cps else len(lsn.get("checkpoints", []))
        })
    return result


def get_lesson_by_id(lesson_id: str) -> dict[str, Any] | None:
    """Lấy toàn bộ chi tiết của một bài học (với slides và checkpoints sinh từ PDF)."""
    store = _load_raw_store()
    for lsn in store.get("lessons", []):
        if lsn.get("id") == lesson_id:
            lesson_copy = dict(lsn)
            pdf_file = "d2-slide-hackathon.pdf" if lesson_id in ["lesson_02", "lesson_03"] else "d1-slide-hackathon.pdf"
            pdf_slides = load_slides_from_pdf(pdf_file)
            gen_cps = load_generated_checkpoints(lesson_id)
            lesson_copy["pdf_url"] = f"/slides/{pdf_file}"
            if pdf_slides:
                lesson_copy["slides"] = pdf_slides
            if gen_cps:
                lesson_copy["checkpoints"] = gen_cps
            return lesson_copy
    return None


def load_lessons_data(lesson_id: str | None = None) -> dict[str, Any]:
    """
    Tương thích ngược với code cũ:
    - Nếu lesson_id có giá trị: lấy bài học tương ứng.
    - Nếu lesson_id là None: ưu tiên lấy bài học lesson_02 (Transformer) hoặc bài học đầu tiên.
    """
    store = _load_raw_store()
    lessons = store.get("lessons", [])
    if not lessons:
        return {}

    if lesson_id:
        target = get_lesson_by_id(lesson_id)
        if target:
            return target

    for lsn in lessons:
        if lsn.get("id") == "lesson_02":
            return get_lesson_by_id("lesson_02") or lsn
    return get_lesson_by_id(lessons[0].get("id")) or lessons[0]


def get_checkpoint_by_id(checkpoint_id: str) -> dict[str, Any] | None:
    """Tra cứu checkpoint theo id trên toàn bộ các bài học trong kho dữ liệu."""
    for lid in ["lesson_01", "lesson_02", "lesson_03"]:
        cps = load_generated_checkpoints(lid)
        for cp in cps:
            if cp.get("id") == checkpoint_id:
                return cp

    store = _load_raw_store()
    for lsn in store.get("lessons", []):
        for cp in lsn.get("checkpoints", []):
            if cp.get("id") == checkpoint_id:
                return cp
    return None
