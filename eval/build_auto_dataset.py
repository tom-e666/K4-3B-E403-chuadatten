"""Dựng golden set cho checkpoint do LLM tự sinh từ slide.

Bộ `golden_dataset.json` cũ gắn chặt với checkpoint viết tay của bài Transformer, không phủ được
dữ liệu mà sản phẩm đang thực sự dùng. Script này đọc thẳng các file trong backend/data/lessons/
và dựng case từ chính nội dung checkpoint:

  happy_path     sample_correct                        -> PASS
  misconception  sample_wrong                          -> NEEDS_IMPROVEMENT
  partial        chỉ nói 1 rubric point                -> NEEDS_IMPROVEMENT
  gave_up        "chịu, tớ không biết"                 -> GAVE_UP
  evaded         lảng sang chuyện khác                 -> EVADED
  copied         dán nguyên văn text trang slide       -> COPIED (chặn trước khi gọi LLM)

Chạy:  python eval/build_auto_dataset.py            (mặc định 2 checkpoint đầu của mỗi bài)
       python eval/build_auto_dataset.py --all      (toàn bộ checkpoint)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.tools.copy_check import get_page_text  # noqa: E402

LESSONS_DIR = PROJECT_ROOT / "backend" / "data" / "lessons"
OUT_FILE = Path(__file__).resolve().parent / "golden_auto.json"

EVADE_LINES = [
    "ủa mà trưa nay ăn gì thế cậu",
    "thôi cậu làm hộ tớ bài tập đi, tớ lười lắm",
    "cậu là AI mà, cậu tự biết rồi còn hỏi tớ làm gì",
]
GIVE_UP_LINES = [
    "chịu, tớ không biết",
    "thôi cho tớ đáp án luôn đi",
    "tớ quên sạch rồi, bó tay",
]


def build_cases(per_lesson_limit: int | None) -> list[dict]:
    cases: list[dict] = []
    for path in sorted(LESSONS_DIR.glob("*.json")):
        lesson = json.loads(path.read_text(encoding="utf-8"))
        checkpoints = lesson.get("checkpoints", [])
        if per_lesson_limit:
            checkpoints = checkpoints[:per_lesson_limit]

        for i, cp in enumerate(checkpoints):
            cid = cp.get("id")
            base = {"lesson_id": lesson.get("id"), "pdf_file": lesson.get("pdf_file"),
                    "checkpoint_id": cid, "pdf_page": cp.get("pdf_page")}

            if cp.get("sample_correct"):
                cases.append({**base, "id": f"{cid}__happy", "category": "happy_path",
                              "user_input": cp["sample_correct"], "expected": "PASS"})
            if cp.get("sample_wrong"):
                cases.append({**base, "id": f"{cid}__wrong", "category": "misconception",
                              "user_input": cp["sample_wrong"], "expected": "NEEDS_IMPROVEMENT"})

            rubric = cp.get("rubric_points") or []
            if len(rubric) >= 2:
                only = rubric[0]
                cases.append({**base, "id": f"{cid}__partial", "category": "partial",
                              "user_input": f"Tớ nhớ phần này nói về {only.get('concept')}. "
                                            f"{(only.get('criteria') or '')[:160]}",
                              "expected": "NEEDS_IMPROVEMENT",
                              "note": f"chỉ phủ rubric '{only.get('id')}', còn thiếu {len(rubric) - 1} ý"})

            cases.append({**base, "id": f"{cid}__gaveup", "category": "gave_up",
                          "user_input": GIVE_UP_LINES[i % len(GIVE_UP_LINES)], "expected": "GAVE_UP"})
            cases.append({**base, "id": f"{cid}__evaded", "category": "evaded",
                          "user_input": EVADE_LINES[i % len(EVADE_LINES)], "expected": "EVADED"})

            page_text = get_page_text(lesson.get("pdf_file", ""), cp.get("pdf_page") or 0)
            words = page_text.split()
            if len(words) >= 40:
                cases.append({**base, "id": f"{cid}__copied", "category": "copied",
                              "user_input": " ".join(words[:70]), "expected": "COPIED",
                              "note": "dán nguyên văn slide, phải bị chặn trước khi gọi LLM"})
    return cases


def main() -> None:
    ap = argparse.ArgumentParser(description="Dựng golden set từ checkpoint do AI sinh.")
    ap.add_argument("--all", action="store_true", help="Lấy toàn bộ checkpoint (mặc định 2 đầu mỗi bài).")
    ap.add_argument("--per-lesson", type=int, default=2, help="Số checkpoint lấy mỗi bài.")
    args = ap.parse_args()

    cases = build_cases(None if args.all else args.per_lesson)
    if not cases:
        print(f"Không tìm thấy checkpoint nào trong {LESSONS_DIR}")
        raise SystemExit(1)

    OUT_FILE.write_text(json.dumps(cases, ensure_ascii=False, indent=2), encoding="utf-8")

    by_cat: dict[str, int] = {}
    for c in cases:
        by_cat[c["category"]] = by_cat.get(c["category"], 0) + 1
    print(f"Đã ghi {len(cases)} case vào {OUT_FILE.relative_to(PROJECT_ROOT)}")
    for cat, n in sorted(by_cat.items(), key=lambda kv: -kv[1]):
        print(f"  {cat:<14} {n}")


if __name__ == "__main__":
    main()
