import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient
from backend.server import app

def run_tests():
    client = TestClient(app)

    # Test 1: Root frontend
    r_root = client.get("/")
    assert r_root.status_code == 200, f"Root status: {r_root.status_code}"
    assert "Feynman AI" in r_root.text
    print("✅ Test 1: Frontend Root loaded successfully (200 OK)")

    # Test 2: Lessons endpoint
    r_lessons = client.get("/api/lessons")
    assert r_lessons.status_code == 200
    lessons = r_lessons.json().get("lessons", [])
    assert len(lessons) == 3, f"Expected 3 lessons, got {len(lessons)}"
    print(f"✅ Test 2: /api/lessons returned {len(lessons)} lessons:")
    for l in lessons:
        print(f"   - {l['id']}: {l['short_title']} ({l['duration']})")

    # Test 3: Session start on all 3 lessons
    for lid in ["lesson_01", "lesson_02", "lesson_03"]:
        r_start = client.post("/api/session/start", json={"session_id": f"test_{lid}", "lesson_id": lid})
        assert r_start.status_code == 200, f"Failed start for {lid}: {r_start.text}"
        data = r_start.json()
        print(f"✅ Test 3 ({lid}): Checkpoint = {data['current_checkpoint']['title']}")

    # Test 4: Chat evaluation on Lesson 1
    r_chat = client.post("/api/chat", json={
        "session_id": "test_lesson_01",
        "message": "LLM là cỗ máy dự đoán token tiếp theo theo xác suất thống kê. Nó bị ảo giác hallucination vì chỉ nối từ cho thuận tai chứ không có ý thức kiểm chứng sự thật."
    })
    assert r_chat.status_code == 200, f"Chat failed: {r_chat.text}"
    cdata = r_chat.json()
    eval_info = cdata.get("latest_evaluation") or {}
    print(f"✅ Test 4 (Chat Step): Eval Status = {eval_info.get('status')}, Score = {eval_info.get('mastery_score')}%, Advance = {cdata.get('advance_checkpoint')}")

    # Test 5: Checkpoints query by lesson
    r_cp3 = client.get("/api/checkpoints?lesson_id=lesson_03")
    assert r_cp3.status_code == 200
    cp3_data = r_cp3.json()
    print(f"✅ Test 5 (Checkpoints query): Lesson 3 has {len(cp3_data.get('checkpoints', []))} checkpoints")

    print("\n🎉 TẤT CẢ 5 BƯỚC KIỂM THỬ END-TO-END ĐỀU THÀNH CÔNG RỰC RỠ!")

if __name__ == "__main__":
    run_tests()
