"""Chạy golden set của checkpoint do AI sinh, chấm bằng đúng Evaluator thật (Giáo sư AI).

Khác với eval/run_eval.py (chấm bằng bộ từ khoá cứng cho bài Transformer viết tay), script này
đi qua đúng đường mà sản phẩm dùng: bộ chặn chép slide + Evaluator LLM.

Chạy:  python eval/build_auto_dataset.py   (dựng bộ case)
       python eval/run_eval_auto.py        (chấm, mặc định tối đa 24 case cho đỡ tốn)
       python eval/run_eval_auto.py --all --dry-run
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.env_loader import load_lab_env  # noqa: E402
load_lab_env(PROJECT_ROOT)

from backend.tools._shared import get_checkpoint_by_id  # noqa: E402
from backend.tools.copy_check import looks_copied  # noqa: E402

DATASET = Path(__file__).resolve().parent / "golden_auto.json"
REPORT = Path(__file__).resolve().parent / "eval_report_auto.json"


def make_agent():
    import os
    from backend.providers import make_provider
    from backend.agent import FeynmanAgent

    provider_name = os.getenv("LLM_PROVIDER") or ("gemini" if os.getenv("GEMINI_API_KEY") else "openai")
    return FeynmanAgent(provider=make_provider(provider_name), model=os.getenv("LLM_MODEL") or None)


def judge(agent, case: dict) -> str:
    """Trạng thái mà hệ thống thực sự trả về cho một case."""
    checkpoint = get_checkpoint_by_id(case["checkpoint_id"])
    if not checkpoint:
        return "CHECKPOINT_NOT_FOUND"

    copied, _ratio = looks_copied(case["user_input"], case.get("pdf_file"), case.get("pdf_page"))
    if copied:
        return "COPIED"   # chặn trước, không tốn lượt gọi LLM — đúng như trong sản phẩm

    verdict = agent._run_evaluator(checkpoint, case["user_input"], trials_used=1)
    return verdict.get("status", "?")


def main() -> None:
    ap = argparse.ArgumentParser(description="Chấm golden set của checkpoint sinh tự động.")
    ap.add_argument("--all", action="store_true", help="Chạy hết, không giới hạn số case.")
    ap.add_argument("--limit", type=int, default=24, help="Số case tối đa (mặc định 24).")
    ap.add_argument("--dry-run", action="store_true", help="Chỉ in danh sách case, không gọi LLM.")
    args = ap.parse_args()

    if not DATASET.exists():
        print(f"Chưa có {DATASET.name}. Chạy trước: python eval/build_auto_dataset.py")
        raise SystemExit(1)

    cases = json.loads(DATASET.read_text(encoding="utf-8"))
    if not args.all:
        cases = cases[:args.limit]

    print(f"\n=== CHẤM {len(cases)} CASE (checkpoint do AI sinh từ slide) ===\n")
    if args.dry_run:
        for c in cases:
            print(f"  [{c['category']:<13}] {c['id']:<45} -> kỳ vọng {c['expected']}")
        print("\n(dry-run) Chưa gọi LLM.")
        return

    agent = make_agent()
    results, stats = [], Counter()
    correct = 0

    for i, case in enumerate(cases, 1):
        actual = judge(agent, case)
        ok = actual == case["expected"]
        correct += ok
        stats[(case["category"], ok)] += 1
        results.append({**case, "actual": actual, "match": ok})
        print(f"{'✅' if ok else '❌'} {i:02d}/{len(cases)} [{case['category']:<13}] {case['id']}")
        if not ok:
            print(f"     kỳ vọng {case['expected']} · nhận {actual}")
            print(f"     input: \"{case['user_input'][:90]}...\"")

    by_cat = {}
    for (cat, ok), n in stats.items():
        row = by_cat.setdefault(cat, {"total": 0, "correct": 0})
        row["total"] += n
        if ok:
            row["correct"] += n

    accuracy = round(correct / len(cases) * 100, 1) if cases else 0.0
    print(f"\n=== KẾT QUẢ: {correct}/{len(cases)} = {accuracy}% ===")
    for cat, row in sorted(by_cat.items()):
        print(f"  {cat:<14} {row['correct']}/{row['total']}")

    REPORT.write_text(json.dumps({
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "total_cases": len(cases),
        "correct_predictions": correct,
        "accuracy_percentage": accuracy,
        "category_breakdown": by_cat,
        "results": results,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nĐã ghi báo cáo: {REPORT.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
