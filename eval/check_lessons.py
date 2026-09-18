"""Kiểm tra cấu trúc các file JSON checkpoint do Agent 1 sinh ra.

Chạy:  python eval/check_lessons.py
Không gọi LLM, không cần server — chỉ đọc backend/data/lessons/*.json và file PDF tương ứng.
Dùng để kiểm nhanh sau mỗi lần phân tích slide xem dữ liệu có hợp lệ không.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LESSONS_DIR = ROOT / "backend" / "data" / "lessons"
SLIDES_DIR = ROOT / "backend" / "data" / "vlearn-pack" / "slides"
LEVELS = ("nhan_biet", "thong_hieu", "van_dung")


def pdf_pages(name: str) -> int | None:
    try:
        from pypdf import PdfReader
        return len(PdfReader(str(SLIDES_DIR / name)).pages)
    except Exception:
        return None


def check_lesson(path: Path) -> list[str]:
    errors: list[str] = []
    warns: list[str] = []
    lesson = json.loads(path.read_text(encoding="utf-8"))
    name = path.name

    for field in ("id", "topic", "short_title", "pdf_file", "checkpoints"):
        if not lesson.get(field):
            errors.append(f"[{name}] thiếu field bắt buộc: {field}")
    if errors:
        return errors

    total_pages = pdf_pages(lesson["pdf_file"])
    if total_pages is None:
        warns.append(f"[{name}] không đọc được file PDF '{lesson['pdf_file']}' (thiếu pypdf hoặc thiếu file)")

    checkpoints = lesson.get("checkpoints", [])
    if not 1 <= len(checkpoints) <= 8:
        errors.append(f"[{name}] số checkpoint bất thường: {len(checkpoints)}")

    for cp in checkpoints:
        cid = cp.get("id", "?")
        for field in ("title", "correction", "rubric_points"):
            if not cp.get(field):
                errors.append(f"[{name}/{cid}] thiếu {field}")

        page = cp.get("pdf_page")
        if not isinstance(page, int) or page < 1:
            errors.append(f"[{name}/{cid}] pdf_page không hợp lệ: {page!r}")
        elif total_pages and page > total_pages:
            errors.append(f"[{name}/{cid}] pdf_page={page} vượt quá {total_pages} trang")
        elif page == 1:
            warns.append(f"[{name}/{cid}] pdf_page=1 — kiểm tra lại xem có phải bị ép về mặc định không")

        rubric = cp.get("rubric_points") or []
        rubric_ids = [str(rp.get("id")) for rp in rubric if rp.get("id")]
        if len(rubric_ids) != len(rubric):
            errors.append(f"[{name}/{cid}] có rubric_point thiếu id")
        if len(set(rubric_ids)) != len(rubric_ids):
            errors.append(f"[{name}/{cid}] rubric_point trùng id")
        total_weight = sum(float(rp.get("weight", 0) or 0) for rp in rubric)
        if total_weight <= 0:
            errors.append(f"[{name}/{cid}] tổng weight rubric = 0, không tính được % mastery")
        elif abs(total_weight - 100) > 1:
            warns.append(f"[{name}/{cid}] tổng weight = {total_weight:g} (không phải 100)")

        bank = cp.get("question_bank") or []
        if not bank:
            warns.append(f"[{name}/{cid}] chưa có ngân hàng câu hỏi — sẽ chạy lối hỏi cũ (1 câu, 3 lượt)")
            continue
        if not 10 <= len(bank) <= 15:
            warns.append(f"[{name}/{cid}] có {len(bank)} câu hỏi (kỳ vọng 10-15)")

        q_ids = [q.get("id") for q in bank]
        if len(set(q_ids)) != len(q_ids):
            errors.append(f"[{name}/{cid}] câu hỏi trùng id")

        by_level = {lv: 0 for lv in LEVELS}
        hits = {rid: 0 for rid in rubric_ids}
        for q in bank:
            if not (q.get("question") or "").strip():
                errors.append(f"[{name}/{cid}/{q.get('id')}] câu hỏi rỗng")
            if q.get("level") not in LEVELS:
                errors.append(f"[{name}/{cid}/{q.get('id')}] level lạ: {q.get('level')!r}")
            else:
                by_level[q["level"]] += 1
            for t in q.get("targets") or []:
                if str(t) not in hits:
                    errors.append(f"[{name}/{cid}/{q.get('id')}] target '{t}' không có trong rubric")
                else:
                    hits[str(t)] += 1

        for lv, n in by_level.items():
            if n == 0:
                warns.append(f"[{name}/{cid}] không có câu nào ở mức '{lv}'")
        for rid, n in hits.items():
            if n < 2:
                warns.append(f"[{name}/{cid}] rubric '{rid}' chỉ được {n} câu hỏi nhắm tới (kỳ vọng ≥2)")

    for w in warns:
        print("  ⚠", w)
    return errors


def main() -> int:
    files = sorted(LESSONS_DIR.glob("*.json"))
    if not files:
        print(f"Không tìm thấy file checkpoint nào trong {LESSONS_DIR}")
        return 1

    all_errors: list[str] = []
    for path in files:
        lesson = json.loads(path.read_text(encoding="utf-8"))
        cps = lesson.get("checkpoints", [])
        total_q = sum(len(cp.get("question_bank") or []) for cp in cps)
        print(f"\n== {path.name} — {lesson.get('short_title')} "
              f"({len(cps)} checkpoint, {total_q} câu hỏi)")
        all_errors += check_lesson(path)

    print("\n" + "=" * 70)
    if all_errors:
        print(f"❌ {len(all_errors)} LỖI:")
        for e in all_errors:
            print("  ✗", e)
        return 1
    print("✅ Tất cả file checkpoint đều hợp lệ (cảnh báo ⚠ ở trên chỉ để xem lại, không phải lỗi).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
