from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.tools.evaluator import grade_explanation

DATASET_FILE = Path(__file__).resolve().parent / "golden_dataset.json"
RESULTS_DIR = Path(__file__).resolve().parent / "results"
OUTPUT_REPORT_FILE = Path(__file__).resolve().parent / "eval_report.json"
V2_RESULTS_JSON = RESULTS_DIR / "v2_results.json"
V2_RESULTS_MD = RESULTS_DIR / "v2_results.md"


def validate_dataset(dataset: list[dict]) -> tuple[bool, list[str]]:
    errors = []
    seen_ids = set()
    for idx, case in enumerate(dataset, 1):
        cid = case.get("id")
        if not cid:
            errors.append(f"Case #{idx} is missing an 'id'.")
        elif cid in seen_ids:
            errors.append(f"Duplicate case id '{cid}' at case #{idx}.")
        else:
            seen_ids.add(cid)

        if not case.get("checkpoint_id"):
            errors.append(f"Case '{cid}' is missing 'checkpoint_id'.")
        if "user_input" not in case:
            errors.append(f"Case '{cid}' is missing 'user_input'.")

        expected_verdict = case.get("expected_status") or case.get("expected", {}).get("verdict")
        if not expected_verdict:
            errors.append(f"Case '{cid}' is missing expected status/verdict.")

    return len(errors) == 0, errors


def run_evaluation() -> dict:
    if not DATASET_FILE.exists():
        print(f"❌ Không tìm thấy file dữ liệu kiểm thử: {DATASET_FILE}", flush=True)
        sys.exit(1)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    with open(DATASET_FILE, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    is_valid, validation_errors = validate_dataset(dataset)
    if not is_valid:
        print(f"❌ Lỗi cấu trúc Golden Set:", flush=True)
        for err in validation_errors:
            print(f"   - {err}", flush=True)
        sys.exit(1)

    total_cases = len(dataset)
    passed_tests = 0
    failed_tests = 0
    detailed_results = []
    category_stats: dict[str, dict[str, int]] = {}
    failed_cases_summary = []

    print("============================================================", flush=True)
    print("FEYNMAN AI — GOLDEN SET EVALUATION RUNNER", flush=True)
    print("============================================================", flush=True)
    print(f"Version Under Test: v2", flush=True)
    print(f"Dataset:            {DATASET_FILE.name} ({total_cases} cases)", flush=True)
    print(f"Timestamp:          {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
    print("------------------------------------------------------------\n", flush=True)

    start_time = time.time()

    for idx, case in enumerate(dataset, 1):
        case_id = case["id"]
        cp_id = case["checkpoint_id"]
        user_input = case["user_input"]
        category = case.get("category", "general")
        expected_verdict = case.get("expected_status") or case.get("expected", {}).get("verdict")
        expected_advance = case.get("expected", {}).get("checkpoint_advance")

        t_case_start = time.time()
        eval_result = grade_explanation(cp_id, user_input)
        duration_s = round(time.time() - t_case_start, 3)

        actual_verdict = eval_result.get("status")
        mastery_score = eval_result.get("mastery_score")

        # Test assertion: does actual product verdict match expected verdict?
        verdict_matches = (actual_verdict == expected_verdict)
        advance_matches = True
        if expected_advance is not None:
            actual_advance = (actual_verdict == "PASS")
            advance_matches = (actual_advance == expected_advance)

        test_passed = verdict_matches and advance_matches

        if test_passed:
            passed_tests += 1
        else:
            failed_tests += 1
            reason = []
            if not verdict_matches:
                reason.append(f"Verdict mismatch (Expected: {expected_verdict}, Actual: {actual_verdict})")
            if not advance_matches:
                reason.append(f"Advance mismatch (Expected advance: {expected_advance})")
            failed_cases_summary.append({
                "id": case_id,
                "expected": expected_verdict,
                "actual": actual_verdict,
                "reason": "; ".join(reason)
            })

        if category not in category_stats:
            category_stats[category] = {"total": 0, "passed": 0}
        category_stats[category]["total"] += 1
        if test_passed:
            category_stats[category]["passed"] += 1

        icon = "✅" if test_passed else "❌"
        print(f"{icon} Case {idx:02d} [{case_id}] ({category})", flush=True)
        print(f"   - Product Verdict: {actual_verdict} (Score: {mastery_score}%) | Expected: {expected_verdict}", flush=True)
        if not test_passed:
            print(f"   - Input: \"{user_input[:80]}...\"", flush=True)
            print(f"   - Failure Reason: Expected {expected_verdict}, but got {actual_verdict}", flush=True)

        detailed_results.append({
            "case_id": case_id,
            "category": category,
            "checkpoint_id": cp_id,
            "lesson_id": case.get("lesson_id"),
            "expected_verdict": expected_verdict,
            "actual_verdict": actual_verdict,
            "mastery_score": mastery_score,
            "test_result": "PASS" if test_passed else "FAIL",
            "duration_seconds": duration_s,
            "covered_points": eval_result.get("covered_points", []),
            "missing_points": eval_result.get("missing_points", []),
            "misconceptions_flagged": eval_result.get("misconceptions_flagged", [])
        })

    total_duration = round(time.time() - start_time, 2)
    pass_rate = (passed_tests / total_cases) * 100.0 if total_cases > 0 else 0.0

    print("\n============================================================", flush=True)
    print("FEYNMAN AI — GOLDEN SET EVALUATION SUMMARY", flush=True)
    print("============================================================", flush=True)
    print(f"Version:           v2", flush=True)
    print(f"Total cases:       {total_cases}", flush=True)
    print(f"Passed:            {passed_tests}", flush=True)
    print(f"Failed:            {failed_tests}", flush=True)
    print(f"Pass rate:         {pass_rate:.2f}%", flush=True)
    print(f"Total duration:    {total_duration}s", flush=True)
    print("\nBY CATEGORY", flush=True)
    for cat, stats in category_stats.items():
        cat_pass_pct = (stats["passed"] / stats["total"]) * 100.0
        print(f"  {cat.ljust(24)} {stats['passed']}/{stats['total']} ({cat_pass_pct:.1f}%)", flush=True)

    if failed_cases_summary:
        print("\nFAILED CASES", flush=True)
        for fc in failed_cases_summary:
            print(f"  {fc['id']}", flush=True)
            print(f"    Expected: {fc['expected']}", flush=True)
            print(f"    Actual:   {fc['actual']}", flush=True)
            print(f"    Reason:   {fc['reason']}", flush=True)
    else:
        print("\nFAILED CASES: None", flush=True)
    print("============================================================\n", flush=True)

    report = {
        "evaluation_version": "v2",
        "timestamp": datetime.now().isoformat(),
        "total_cases": total_cases,
        "passed_cases": passed_tests,
        "failed_cases": failed_tests,
        "pass_rate_percentage": round(pass_rate, 2),
        "total_duration_seconds": total_duration,
        "category_metrics": {
            cat: {
                "total": stats["total"],
                "passed": stats["passed"],
                "failed": stats["total"] - stats["passed"],
                "pass_rate": round((stats["passed"] / stats["total"]) * 100.0, 2)
            }
            for cat, stats in category_stats.items()
        },
        "failed_cases": failed_cases_summary,
        "detailed_results": detailed_results
    }

    # Save v2_results.json
    with open(V2_RESULTS_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # Save eval_report.json (for backward compatibility)
    with open(OUTPUT_REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": report["timestamp"],
            "total_cases": total_cases,
            "correct_predictions": passed_tests,
            "accuracy_percentage": round(pass_rate, 2),
            "category_breakdown": {
                cat: {
                    "total": stats["total"],
                    "correct": stats["passed"],
                    "accuracy": round((stats["passed"] / stats["total"]) * 100.0, 1)
                }
                for cat, stats in category_stats.items()
            },
            "results": detailed_results
        }, f, ensure_ascii=False, indent=2)

    # Generate v2_results.md
    md_lines = [
        "# Feynman AI — Evaluation Report (v2)",
        "",
        f"- **Timestamp**: `{report['timestamp']}`",
        f"- **Version**: `v2`",
        f"- **Total Cases**: `{total_cases}`",
        f"- **Test Passed**: `{passed_tests}`",
        f"- **Test Failed**: `{failed_tests}`",
        f"- **Pass Rate (Accuracy)**: **`{pass_rate:.2f}%`**",
        f"- **Duration**: `{total_duration}s`",
        "",
        "## Metrics by Category",
        "",
        "| Category | Total | Passed | Failed | Pass Rate |",
        "|---|---|---|---|---|"
    ]
    for cat, stats in report["category_metrics"].items():
        md_lines.append(f"| `{cat}` | {stats['total']} | {stats['passed']} | {stats['failed']} | {stats['pass_rate']}% |")

    md_lines.extend([
        "",
        "## Failed Cases",
        ""
    ])
    if failed_cases_summary:
        for fc in failed_cases_summary:
            md_lines.append(f"- **`{fc['id']}`**:")
            md_lines.append(f"  - Expected: `{fc['expected']}`")
            md_lines.append(f"  - Actual: `{fc['actual']}`")
            md_lines.append(f"  - Reason: {fc['reason']}")
    else:
        md_lines.append("No failures recorded. All test cases passed.")

    md_lines.extend([
        "",
        "## Detailed Test Log",
        "",
        "| Case ID | Category | Checkpoint | Expected | Actual | Score | Test Result |",
        "|---|---|---|---|---|---|---|"
    ])
    for r in detailed_results:
        md_lines.append(f"| `{r['case_id']}` | `{r['category']}` | `{r['checkpoint_id']}` | `{r['expected_verdict']}` | `{r['actual_verdict']}` | {r['mastery_score']}% | **{r['test_result']}** |")

    with open(V2_RESULTS_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print(f"Results saved to:")
    print(f"  - {V2_RESULTS_JSON}")
    print(f"  - {V2_RESULTS_MD}")
    print(f"  - {OUTPUT_REPORT_FILE}\n", flush=True)

    return report


if __name__ == "__main__":
    run_evaluation()
