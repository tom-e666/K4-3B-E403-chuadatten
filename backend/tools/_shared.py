from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
LESSONS_MULTI_FILE = DATA_DIR / "lessons.json"
LESSONS_SINGLE_FILE = DATA_DIR / "transformer_lessons.json"

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
        except ImportError:
            import fitz
            doc = fitz.open(pdf_path)
            for idx, page in enumerate(doc, start=1):
                text = page.get_text() or ""
                slides.append({
                    "slide": idx,
                    "title": f"Trang slide {idx} ({pdf_filename})",
                    "pdf_url": f"/slides/{pdf_filename}",
                    "content": text.strip(),
                    "bullets": [line.strip() for line in text.split("\n") if line.strip()][:5]
                })
    except Exception as err:
        print(f"Error reading PDF slide {pdf_filename}: {str(err).encode('ascii', 'ignore').decode('ascii')}")

    _PDF_SLIDES_CACHE[pdf_filename] = slides
    return slides


def _load_raw_store() -> dict[str, Any]:
    global _CACHED_STORE
    if _CACHED_STORE is not None:
        return _CACHED_STORE

    if LESSONS_MULTI_FILE.exists():
        with open(LESSONS_MULTI_FILE, "r", encoding="utf-8") as f:
            _CACHED_STORE = json.load(f)
            return _CACHED_STORE

    if LESSONS_SINGLE_FILE.exists():
        with open(LESSONS_SINGLE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            _CACHED_STORE = {"lessons": [data]}
            return _CACHED_STORE

    raise FileNotFoundError(f"Missing lessons file at: {LESSONS_MULTI_FILE} or {LESSONS_SINGLE_FILE}")


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
