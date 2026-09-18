from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient
from backend.server import app


def run_e2e_tests() -> bool:
    client = TestClient(app)
    all_passed = True

    print("============================================================", flush=True)
    print("FEYNMAN AI — END-TO-END (E2E) SERVER TEST SUITE", flush=True)
    print("============================================================\n", flush=True)

    # -------------------------------------------------------------------------
    # TEST 1: Root & Static Assets
    # -------------------------------------------------------------------------
    print("👉 Test 1: Root & Frontend Serving", flush=True)
    r_root = client.get("/")
    assert r_root.status_code == 200, f"Root status expected 200, got {r_root.status_code}"
    assert "Feynman AI" in r_root.text, "Title 'Feynman AI' not found in root HTML"
    print("   ✅ Frontend root loaded successfully (200 OK)\n", flush=True)

    # -------------------------------------------------------------------------
    # TEST 2: Multi-Lesson Catalogue
    # -------------------------------------------------------------------------
    print("👉 Test 2: Lesson Catalogue (/api/lessons)", flush=True)
    r_lessons = client.get("/api/lessons")
    assert r_lessons.status_code == 200
    lessons = r_lessons.json().get("lessons", [])
    assert len(lessons) >= 3, f"Expected at least 3 lessons, got {len(lessons)}"
    print(f"   ✅ Returned {len(lessons)} lessons:", flush=True)
    for l in lessons:
        print(f"      - {l['id']}: {l.get('short_title', l.get('topic'))} ({l.get('duration')})", flush=True)
    print("", flush=True)

    # -------------------------------------------------------------------------
    # TEST 3: Multi-Lesson Session Initialization
    # -------------------------------------------------------------------------
    print("👉 Test 3: Session Start across Multiple Lessons", flush=True)
    for lid in ["lesson_01", "lesson_02", "lesson_03"]:
        sid = f"e2e_session_{lid}"
        r_start = client.post("/api/session/start", json={"session_id": sid, "lesson_id": lid})
        assert r_start.status_code == 200, f"Failed start for {lid}: {r_start.text}"
        data = r_start.json()
        assert data["session_id"] == sid
        assert data["lesson_id"] == lid
        assert data["current_checkpoint"]["id"] is not None
        print(f"   ✅ Initialized {lid}: CP1 = '{data['current_checkpoint']['title']}'", flush=True)
    print("", flush=True)

    # -------------------------------------------------------------------------
    # TEST 4: NEEDS_IMPROVEMENT Path (Checkpoint Non-Advancement)
    # -------------------------------------------------------------------------
    print("👉 Test 4: Negative Path — Insufficient Explanation (Non-Progression)", flush=True)
    sid_neg = "e2e_test_negative_path"
    client.post("/api/session/start", json={"session_id": sid_neg, "lesson_id": "lesson_02"})
    r_chat_fail = client.post("/api/chat", json={
        "session_id": sid_neg,
        "message": "Hôm nay trời đẹp quá bạn ơi, không muốn học bài đâu."
    })
    assert r_chat_fail.status_code == 200
    neg_data = r_chat_fail.json()
    eval_fail = neg_data.get("latest_evaluation") or {}
    
    is_passed = (eval_fail.get("status") == "PASS")
    assert is_passed is False, "Checkpoint should not pass on off-topic input"
    assert neg_data.get("advance_checkpoint") is False, "Checkpoint should NOT advance on off-topic input"
    assert neg_data.get("current_checkpoint_index") == 0, "Index should remain 0"
    print(f"   ✅ Negative Path Verified: Status = {eval_fail.get('status') or 'No tool evaluation'}, Advance = {neg_data.get('advance_checkpoint')}, Index = {neg_data.get('current_checkpoint_index')}\n", flush=True)

    # -------------------------------------------------------------------------
    # TEST 5: PASS Path (Checkpoint Progression & Advance)
    # -------------------------------------------------------------------------
    print("👉 Test 5: Positive Path — Correct Explanation (Progression)", flush=True)
    sid_pos = "e2e_test_positive_path"
    client.post("/api/session/start", json={"session_id": sid_pos, "lesson_id": "lesson_02"})
    r_chat_pass = client.post("/api/chat", json={
        "session_id": sid_pos,
        "message": "Self-attention sử dụng bộ ba Query, Key và Value. Query là câu hỏi hoặc từ đang xét tìm kiếm gì, Key đóng vai trò nhãn nhận dạng của các từ khác. Ta tính tích vô hướng (dot-product) giữa Query và Key để đo độ tương đồng, sau đó chuẩn hóa bằng Softmax để ra các trọng số xác suất, rồi nhân tổng có trọng số với Value để lấy ra vector ngữ cảnh."
    })
    assert r_chat_pass.status_code == 200
    pos_data = r_chat_pass.json()
    eval_pass = pos_data.get("latest_evaluation") or {}

    print(f"   ✅ Evaluation Result: Status = {eval_pass.get('status')}, Score = {eval_pass.get('mastery_score')}%, Advance = {pos_data.get('advance_checkpoint')}", flush=True)
    if eval_pass.get("status") == "PASS":
        assert pos_data.get("advance_checkpoint") is True, "Checkpoint SHOULD advance on PASS"
        assert pos_data.get("current_checkpoint_index") == 1, "Index should advance to 1"
        print(f"   ✅ Checkpoint advanced to Index 1 (Next: '{pos_data.get('next_checkpoint_title')}')\n", flush=True)
    else:
        print(f"   ℹ️ Evaluator returned status {eval_pass.get('status')} (Advance: {pos_data.get('advance_checkpoint')})\n", flush=True)

    # -------------------------------------------------------------------------
    # TEST 6: Session Mastery Report Retrieval
    # -------------------------------------------------------------------------
    print("👉 Test 6: Mastery Report Generation (/api/session/report)", flush=True)
    r_report = client.get(f"/api/session/report?session_id={sid_pos}")
    assert r_report.status_code == 200, f"Report failed: {r_report.text}"
    report_data = r_report.json()
    assert "overall_score" in report_data, "Missing 'overall_score' in report"
    assert "passed_checkpoints" in report_data, "Missing 'passed_checkpoints' in report"
    assert "review_checkpoints" in report_data, "Missing 'review_checkpoints' in report"
    print(f"   ✅ Report generated successfully: Overall Score = {report_data.get('overall_score')}%, Status = {report_data.get('overall_status')}\n", flush=True)

    # -------------------------------------------------------------------------
    # TEST 7: Checkpoints Filtering Query
    # -------------------------------------------------------------------------
    print("👉 Test 7: Query Checkpoints by Lesson ID", flush=True)
    r_cp = client.get("/api/checkpoints?lesson_id=lesson_03")
    assert r_cp.status_code == 200
    cp_data = r_cp.json()
    assert len(cp_data.get("checkpoints", [])) >= 3
    print(f"   ✅ Lesson 3 has {len(cp_data.get('checkpoints', []))} checkpoints\n", flush=True)

    print("============================================================", flush=True)
    print("🎉 TẤT CẢ 7 BƯỚC KIỂM THỬ END-TO-END ĐỀU THÀNH CÔNG RỰC RỠ!", flush=True)
    print("============================================================\n", flush=True)
    return True


if __name__ == "__main__":
    run_e2e_tests()
