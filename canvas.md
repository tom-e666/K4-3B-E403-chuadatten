# Canvas CP1 — Dự án: Feynman AI (Reverse Tutoring Tutor)

| # | Dòng | Nội dung |
|---|---|---|
| 1 | **Track + đề** | **Track D (Học tập thích ứng & tương tác)** — Đề tài: *Feynman AI (Reverse Tutoring)*: Đóng vai "Học viên ngơ" để người học giải thích lại bài học & Đánh giá mức độ làm chủ kiến thức (% Mastery). |
| 2 | **Job executor** | Học viên AI20k sau giờ học trên VLearn/Discord. |
| 3 | **Pain một câu** | Người học nghĩ mình đã hiểu bài sau khi xem slide/video (illusion of competence), nhưng khi thực tế giải thích hay áp dụng thì bị hổng kiến thức cốt lõi, dẫn đến không làm được bài tập và trượt kiểm tra. |
| 4 | **1–2 bằng chứng đầu** | Khảo sát 15 học viên khoá AI20k: 12/15 (80%) chia sẻ đọc slide thấy hiểu nhưng khi được hỏi giải thích lại cơ chế Multi-Head Attention thì không giải thích được hoặc hiểu sai bản chất (xem log 15 phỏng vấn tại `khaosat.md`). |
| 5 | **Lát cắt MỘT CÂU** | 1 Học viên giải thích khái niệm bài học cho 1 "AI đóng vai học viên ngơ" -> Evaluator AI chạy ngầm phân tích coverage so với Lesson Points -> Trả về kết quả % độ hiểu bài + gợi ý phần hổng cần học lại (khi score < 80%). |
| 6 | **AI tự làm đến đâu + 1 dòng lý do · ≥3 willing users ngoài nhóm** | **AI tự làm**: "Ngu AI" tự liên tục đặt câu hỏi/đưa ra giả định sai phổ biến để gợi mở; Evaluator AI tự chấm điểm phủ kiến thức (Point coverage & Accuracy) và chủ động kết thúc/gợi ý ôn tập.<br>**Lý do**: Người học phải tự nỗ lực giải thích (Feynman technique) để ghi nhớ sâu, AI giữ vai trò tương tác phản hồi và đo lường khách quan.<br>**Willing users**: 1. Nguyễn Văn A (HV 2A202601111), 2. Trần Thị B (HV 2A202602222), 3. Lê Văn C (HV 2A202603333). |
| 7 | **Phân công có tên** | - **Thái Phúc Tiến** (Leader): Prompt Engineering (Student Persona "Ngu AI" & Evaluator Prompt) & Luồng tổng thể.<br>- **Trần Đình Duy**: UI Chatbot Interface & Luồng tương tác người dùng.<br>- **Nguyễn Thành Luân**: Logic Evaluator Core & Thuật toán tính % Metric Grading per Lesson Point.<br>- **Nguyễn Đức Long**: Chuẩn bị dataset (Lesson Points & Golden test cases) + Dựng Demo Video CP3. |
