from __future__ import annotations

from typing import Any
from ._shared import load_lessons_data


def generate_session_report(session_results: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Tổng kết toàn bộ phiên học Reverse Tutoring:
    - Điểm Mastery trung bình
    - Danh sách Checkpoint đã vượt qua (PASS) vs Cần ôn lại (<80%)
    - Đề xuất tài liệu / Slide tương ứng cho từng điểm hổng
    """
    lessons_data = load_lessons_data()
    all_checkpoints = lessons_data.get("checkpoints", [])
    
    total_score = 0
    passed_checkpoints = []
    review_checkpoints = []

    results_map = {r.get("checkpoint_id"): r for r in session_results}

    for cp in all_checkpoints:
        cp_id = cp["id"]
        res = results_map.get(cp_id)
        if res:
            score = res.get("mastery_score", 0)
            total_score += score
            item = {
                "checkpoint_id": cp_id,
                "title": cp["title"],
                "score": score,
                "status": "PASSED" if score >= 80 else "NEED_REVIEW",
                "trials_used": res.get("trials", 1),
                "source_citation": cp.get("source_citation", ""),
                "recommendation": "Đã làm chủ kiến thức vững vàng." if score >= 80 else f"Cần xem lại {cp.get('source_citation')} để nắm vững các khái niệm hổng."
            }
            if score >= 80:
                passed_checkpoints.append(item)
            else:
                review_checkpoints.append(item)
        else:
            review_checkpoints.append({
                "checkpoint_id": cp_id,
                "title": cp["title"],
                "score": 0,
                "status": "SKIPPED",
                "trials_used": 0,
                "source_citation": cp.get("source_citation", ""),
                "recommendation": f"Chưa thực hành phần này. Xem slide {cp.get('source_citation')}."
            })

    evaluated_count = len(session_results)
    avg_score = int(round(total_score / evaluated_count)) if evaluated_count > 0 else 0
    overall_status = "EXCELLENT" if avg_score >= 85 else ("PASSED" if avg_score >= 80 else "NEEDS_REVISION")

    return {
        "topic": lessons_data.get("topic"),
        "overall_score": avg_score,
        "overall_status": overall_status,
        "total_checkpoints": len(all_checkpoints),
        "passed_count": len(passed_checkpoints),
        "review_count": len(review_checkpoints),
        "passed_checkpoints": passed_checkpoints,
        "review_checkpoints": review_checkpoints,
        "advice": (
            "Chúc mừng bạn đã hoàn thành xuất sắc các thử thách giải thích kiến thức!"
            if overall_status in ["EXCELLENT", "PASSED"]
            else "Bạn có nền tảng tốt nhưng còn vài điểm mấu chốt chưa giải thích rõ ràng. Hãy xem lại các slide gợi ý nhé!"
        )
    }

