from __future__ import annotations

from typing import Any
from ._shared import get_checkpoint_by_id, load_lessons_data


def lookup_lesson_point(checkpoint_id: str) -> dict[str, Any]:
    """Tra cứu kiến thức chuẩn, danh sách rubric criteria và các hiểu lầm phổ biến của một Checkpoint."""
    cp = get_checkpoint_by_id(checkpoint_id)
    if not cp:
        all_cps = [c.get("id") for c in load_lessons_data().get("checkpoints", [])]
        return {
            "error": "checkpoint_not_found",
            "message": f"Không tìm thấy checkpoint '{checkpoint_id}'. Danh sách hợp lệ: {all_cps}"
        }

    return {
        "id": cp["id"],
        "title": cp["title"],
        "order": cp.get("order", 1),
        "misconceptions": cp.get("misconceptions", []),
        "rubric_points": cp.get("rubric_points", []),
        "source_citation": cp.get("source_citation", ""),
        "summary_for_passed": cp.get("summary_for_passed", "")
    }

