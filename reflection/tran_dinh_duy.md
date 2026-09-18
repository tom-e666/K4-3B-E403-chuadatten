# Reflection Cá Nhân — Trần Đình Duy

> **Thông tin thành viên**:
> - **Họ và tên**: Trần Đình Duy
> - **Vai trò chính**: Xây dựng hệ thống backend `agent.py`, phát triển hệ thống metric, eval & thực hiện khảo sát thực tế.

---

## 1. Vai trò & Phần việc đã thực hiện
- **Đóng góp chính**: 
  - Trực tiếp phát triển mô hình Multi-Agent backend trong [`backend/agent.py`](file:///C:/AI/vinai20k/K4-3B-E403-chuadatten/backend/agent.py), phân tách rõ vai trò giữa Agent 2 ("Minh AI" - Bạn học ngơ) và Agent 3 ("Giáo sư AI" - Chấm điểm RAG & Rubric ngầm).
  - Thiết kế và đo đạc các bộ kết quả kiểm thử v0, v1, v2 trong thư mục [`eval/results/`](file:///C:/AI/vinai20k/K4-3B-E403-chuadatten/eval/results/), tạo báo cáo so sánh chi tiết [`eval/results/comparison.md`](file:///C:/AI/vinai20k/K4-3B-E403-chuadatten/eval/results/comparison.md).
  - Thu thập và mã hóa dữ liệu khảo sát thực tế $n=11$ học viên AI20K tại [`khaosat.md`](file:///C:/AI/vinai20k/K4-3B-E403-chuadatten/khaosat.md).
- **Commit chính trên Git**: `d1289f0` (evaluation v0-v2 comparison), `96ec1ec` (run_eval.bat modification), `c8d6102` (reverse tutoring prototype).

---

## 2. Ứng dụng AI trong quá trình làm việc
- Dùng AI để hỗ trợ viết nhanh các hàm trích xuất JSON Schema trong `agent.py` và tối ưu hóa hệ thống Prompt cho Giáo sư AI để chấm điểm bám sát `rubric_points`.
- Sử dụng LLM APIs để xây dựng bộ đánh giá song song (Dual Engine Evaluation) giữa điểm phủ % (Point Coverage) và nhận diện hiểu lầm (Misconceptions).

---

## 3. Bài học kinh nghiệm từ Case Fail của nhóm
- **Case Fail thực tế**: Lần đầu chạy `run_eval.py` với 22 cases, backend bị vỡ luồng do các lỗi ngoại lệ (Exceptions) từ LLM Provider làm nghẽn tiến trình `uvicorn`.
- **Bài học rút ra**: *"Khi xây dựng hệ thống ReAct / Multi-Agent, việc bao bọc ngoại lệ (Error Handling) và xây dựng bộ kiểm thử End-to-End (`test_server_e2e.py`) là cực kỳ sống còn để đảm bảo hệ thống không sập khi gặp các input tiêu cực hoặc lỗi gián đoạn kết nối API."*
