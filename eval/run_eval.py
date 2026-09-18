from __future__ import annotations

import json
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.tools.evaluator import grade_explanation

DATASET_FILE = Path(__file__).resolve().parent / "golden_dataset.json"
OUTPUT_REPORT_FILE = Path(__file__).resolve().parent / "eval_report.json"


def run_evaluation() -> dict:
    if not DATASET_FILE.exists():
        print(f"❌ Không tìm thấy file dữ liệu kiểm thử: {DATASET_FILE}")
        sys.exit(1)

    with open(DATASET_FILE, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    total_cases = len(dataset)
    correct_predictions = 0
    detailed_results = []
    category_stats: dict[str, dict[str, int]] = {}

    print(f"\n=======================================================")
    print(f"🚀 BẮT ĐẦU CHẠY EVALUATION BỘ GOLDEN SET ({total_cases} CASES)")
    print(f"=======================================================\n")

    for idx, case in enumerate(dataset, 1):
        case_id = case.get("id")
        cp_id = case.get("checkpoint_id")
        user_input = case.get("user_input")
        expected_status = case.get("expected_status")
        category = case.get("category", "general")

        eval_result = grade_explanation(cp_id, user_input)
        actual_status = eval_result.get("status")
        mastery_score = eval_result.get("mastery_score")

        is_match = (actual_status == expected_status)
        if is_match:
            correct_predictions += 1

        if category not in category_stats:
            category_stats[category] = {"total": 0, "correct": 0}
        category_stats[category]["total"] += 1
        if is_match:
            category_stats[category]["correct"] += 1

        icon = "✅" if is_match else "❌"
        print(f"{icon} Case {idx:02d} [{case_id}] ({category})")
        print(f"   - Expected: {expected_status} | Actual: {actual_status} (Score: {mastery_score}%)")
        if not is_match:
            print(f"   - Input: \"{user_input[:80]}...\"")

        detailed_results.append({
            "case_id": case_id,
            "category": category,
            "checkpoint_id": cp_id,
            "expected_status": expected_status,
            "actual_status": actual_status,
            "mastery_score": mastery_score,
            "is_correct": is_match,
            "missing_points": eval_result.get("missing_points", []),
            "misconceptions_flagged": eval_result.get("misconceptions_flagged", [])
        })

    accuracy = (correct_predictions / total_cases) * 100.0 if total_cases > 0 else 0.0

    report = {
        "timestamp": datetime.now().isoformat(),
        "total_cases": total_cases,
        "correct_predictions": correct_predictions,
        "accuracy_percentage": round(accuracy, 2),
        "category_breakdown": {
            cat: {
                "total": stats["total"],
                "correct": stats["correct"],
                "accuracy": round((stats["correct"] / stats["total"]) * 100.0, 1)
            }
            for cat, stats in category_stats.items()
        },
        "results": detailed_results
    }

    with open(OUTPUT_REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n=======================================================")
    print(f"📊 KẾT QUẢ ĐÁNH GIÁ TỔNG QUAN:")
    print(f"   - Tổng số test cases: {total_cases}")
    print(f"   - Số case dự đoán đúng: {correct_predictions}/{total_cases}")
    print(f"   - TỶ LỆ CHÍNH XÁC (ACCURACY): {accuracy:.1f}%")
    print(f"   - Báo cáo chi tiết đã lưu tại: {OUTPUT_REPORT_FILE}")
    print(f"=======================================================\n")

    return report


if __name__ == "__main__":
    run_evaluation()

