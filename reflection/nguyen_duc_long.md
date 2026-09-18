# Reflection Cá Nhân — Nguyễn Đức Long

> **Thông tin thành viên**:
> - **Họ và tên**: Nguyễn Đức Long
> - **Vai trò chính**: Phát triển Agent ngơ và Agent Giáo sư, xây dựng feature đánh giá tiến độ người học, xây dựng UI mô phỏng VLearn.

---

## 1. Vai trò & Phần việc đã thực hiện
- **Đóng góp chính**: 
  - Xây dựng Agent 1 (`backend/lesson_ingest.py`) chuyên tự động đọc file slide PDF bài giảng để tự trích xuất Checkpoints & Rubric points chuẩn theo số trang thực tế.
  - Tích hợp thêm các provider AI khác nhau (OpenAI, Gemini, DeepSeek) vào hệ thống provider [`backend/providers/`](file:///C:/AI/vinai20k/K4-3B-E403-chuadatten/backend/providers/).
  - Xây dựng tính năng theo dõi tiến độ học tập (% Mastery) và đề xuất vị trí slide cần ôn lại trong `reporter.py`.
- **Commit chính trên Git**: `6c27136` (them provider), `11ddd53` (fix loi agent ngu o bai hoc 1), `2768d07` (checkpoint theo slide), `cba0406` (Merge branch 'dlong').

---

## 2. Ứng dụng AI trong quá trình làm việc
- Sử dụng các API Multimodal / Text Extraction của Gemini và OpenAI để tự động đọc trích xuất văn bản từ slide PDF bài giảng.
- Dùng AI để hỗ trợ kiểm thử và tinh chỉnh Persona "Minh AI" (Bot ngơ) để giữ văn phong xưng hô "tớ - cậu" tự nhiên của bạn học.

---

## 3. Bài học kinh nghiệm từ Case Fail của nhóm
- **Case Fail thực tế**: Khi đổi sang dùng các LLM Provider khác nhau (như DeepSeek hoặc OpenAI Proxy), Agent 1 bị vỡ do SDK khác nhau không hỗ trợ gửi thẳng file PDF đính kèm.
- **Bài học rút ra**: *"Luôn luôn phải xây dựng giải pháp dự phòng (Fallback mechanism) - ví dụ như tự rút text từng trang bằng pypdf khi API không nhận file trực tiếp, để đảm bảo hệ thống luôn chạy ổn định trên mọi môi trường."*
