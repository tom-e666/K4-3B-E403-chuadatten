from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
LESSONS_MULTI_FILE = DATA_DIR / "lessons.json"
LESSONS_SINGLE_FILE = DATA_DIR / "transformer_lessons.json"

_CACHED_STORE: dict[str, Any] | None = None


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


def get_all_lessons() -> list[dict[str, Any]]:
    """Trả về danh sách tất cả các bài học (kèm tóm tắt metadata)."""
    store = _load_raw_store()
    lessons = store.get("lessons", [])
    result = []
    for lsn in lessons:
        result.append({
            "id": lsn.get("id", "lesson_default"),
            "topic": lsn.get("topic", "Chủ đề bài học"),
            "short_title": lsn.get("short_title", lsn.get("topic", "")),
            "course": lsn.get("course", "VLearn AI20k"),
            "duration": lsn.get("duration", "45 phút"),
            "source_transcript": lsn.get("source_transcript", ""),
            "slides_count": len(lsn.get("slides", [])),
            "summary": lsn.get("summary", ""),
            "checkpoints_count": len(lsn.get("checkpoints", []))
        })
    return result


def get_lesson_by_id(lesson_id: str) -> dict[str, Any] | None:
    """Lấy toàn bộ chi tiết của một bài học (slides, transcript_excerpts, checkpoints)."""
    store = _load_raw_store()
    for lsn in store.get("lessons", []):
        if lsn.get("id") == lesson_id:
            return lsn
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

    # Mặc định lấy bài Transformer (lesson_02) hoặc bài đầu tiên để giữ tương thích tests cũ
    for lsn in lessons:
        if lsn.get("id") == "lesson_02":
            return lsn
    return lessons[0]


def get_checkpoint_by_id(checkpoint_id: str) -> dict[str, Any] | None:
    """Tra cứu checkpoint theo id trên toàn bộ các bài học trong kho dữ liệu."""
    store = _load_raw_store()
    for lsn in store.get("lessons", []):
        for cp in lsn.get("checkpoints", []):
            if cp.get("id") == checkpoint_id:
                return cp
    return None
