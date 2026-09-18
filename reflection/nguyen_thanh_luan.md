# Reflection Cá Nhân — Nguyễn Thành Luân

> **Thông tin thành viên**:
> - **Họ và tên**: Nguyễn Thành Luân
> - **Vai trò chính**: Đề xuất và xây dựng hệ thống metric point, xây dựng UI mô phỏng VLearn, xây dựng agent tương tác người học.

---

## 1. Vai trò & Phần việc đã thực hiện
- **Đóng góp chính**: 
  - Đề xuất và phát triển tính năng Ngân hàng câu hỏi (Question Bank), câu hỏi dẫn dắt từng bước và cơ chế Streaming response trên nhánh `feature/luannt`.
  - Thiết kế và hoàn thiện cấu trúc UI mô phỏng VLearn trong [`FE/mock-cp2/index.html`](file:///C:/AI/vinai20k/K4-3B-E403-chuadatten/FE/mock-cp2/index.html) với phong cách sáng/tối hiện đại, giúp trải nghiệm người học mượt mà.
  - Phụ trách logic chấm điểm phân tách từng ý cốt lõi (Metric Grading per Lesson Point).
- **Commit chính trên Git**: `28ed6e0` (Ngân hàng câu hỏi, hỏi dẫn dắt, streaming & tách vai Giáo sư AI), `dcbdbad` (update FE & agent logic).

---

## 2. Ứng dụng AI trong quá trình làm việc
- Dùng AI để thiết kế các Prompt sinh câu hỏi tự động dựa trên mức độ nhận biết, thông hiểu và vận dụng trong `lesson_ingest.py`.
- Tận dụng AI để tối ưu hóa code JavaScript trên Frontend, xử lý mượt mà việc render markdown và hiển thị kết quả chấm điểm từng Checkpoint realtime.

---

## 3. Bài học kinh nghiệm từ Case Fail của nhóm
- **Case Fail thực tế**: Khi người dùng cố tình trả lời lảng sang chủ đề khác (Evaded), Bot Ngu bị lặp lại câu hỏi cũ quá nhiều lần gây cảm giác khó chịu (theo phản hồi của học viên Phùng Quốc Việt khi User Testing).
- **Bài học rút ra**: *"Tương tác AI cần có giới hạn chịu đựng (Evasion threshold). Khi học viên trả lời lảng quá 2 lần, hệ thống phải tự động đổi chiến lược hỏi hoặc gợi ý đáp án thay vì lặp lại cứng nhắc."*
