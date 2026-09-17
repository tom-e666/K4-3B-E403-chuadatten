# Kế Hoạch Prototype & Mockup Luồng Hoạt Động (CP2 — Feynman AI VLearn)

## 1. Ý Tưởng Giao Diện & Tích Hợp (UI & Integration Concept)
- **Giao diện**: Mô phỏng giao diện học tập **VLearn** (VLearn LMS Clone) với layout 2 cột:
  - Cột trái: Khung phát Video bài giảng (Youtube Embed) / Slide bài học + Tiến trình xem.
  - Cột phải: Khung chat **Feynman AI** (thay thế trợ lý chatbot VLearn mặc định).

---

## 2. Kịch Bản & Luồng Tương Tác Chi Tiết (Interaction Flow Loop)

### 🚀 Bước 1: Kích Hoạt (Trigger Event)
- Khi người dùng hoàn thành video/slide hoặc ấn nút **"Bắt đầu luyện tập Feynman"**.
- Hệ thống trích xuất danh sách **Checkpoints / Lesson Points** tương ứng với phần bài học người dùng đã xem (ví dụ bài *Transformer Architecture* có 3 Checkpoints: 1. Self-Attention, 2. Multi-Head Attention, 3. Positional Encoding).

### 🔄 Bước 2: Vòng Lặp Kiểm Tra Khái Niệm (Lesson Checkpoints Loop)
Với mỗi **Lesson Checkpoint**:
1. **"Bot Ngu" (Student Persona)**:
   - Chủ động nhắn tin đặt câu hỏi ngơ ngẩn hoặc đưa ra một hiểu sai phổ biến (misconception) về Checkpoint đó.
2. **Người học (User)**:
   - Nhập tin nhắn đóng vai người thầy giải thích lại khái niệm cho Bot Ngu.
3. **"Giáo sư AI" (Evaluator AI ngầm)**:
   - Phân tích câu trả lời của người học đối chiếu với Lesson Point chuẩn:
     - **Nếu ĐÚNG (Score ≥ 80%)**: Bot Ngu gật đầu cảm ơn + Giáo sư tóm tắt lại ý đúng ngắn gọn $\rightarrow$ Chuyển sang Checkpoint tiếp theo.
     - **Nếu SAI / HỔNG (Score < 80%)**: 
       - Giáo sư đưa ra gợi ý/định hướng để người dùng giải thích lại (cho phép **tối đa 3 lần thử / Max Trial = 3**).
       - Sau 3 lần vẫn chưa đạt $\rightarrow$ Giáo sư đính chính kiến thức chuẩn, đánh dấu "Cần học lại" và chuyển tiếp.

### 📊 Bước 3: Tổng Kết & Đánh Giá (Final Summary & Mastery Report)
- Sau khi đi hết các Checkpoints:
  - Hiển thị Báo cáo Tổng quan (% Mastery Score tổng thể).
  - Bảng danh sách Lesson Points: Đạt (Passed) vs Chưa đạt (Need Review).
  - Đề xuất link bài học/slide cụ thể cần học lại cho các điểm < 80%.

---

## 3. Kiến Trúc Kỹ Thuật (Technical Specs & Stack)
- **Frontend**: Next.js / React + Vanilla CSS (Mô phỏng VLearn Theme: Dark mode, Glassmorphism, Responsive).
- **AI Model Core**: API DeepSeek / OpenAI (Tối ưu Prompting cho 2 Persona: Student Persona "Bot Ngu" & Evaluator Persona "Giáo sư AI").
- **Dữ Liệu Mẫu (Sample Lesson Dataset)**:
  - **Bài học**: *Transformer Architecture & Multi-Head Attention*.
  - **Media**: 1 Video Youtube giảng Transformer + Slide tóm tắt.
  - **Lesson Checkpoints Matrix**:
    - `CP1`: Khái niệm Self-Attention & Ý nghĩa của Query, Key, Value.
    - `CP2`: Tại sao cần Multi-Head Attention thay vì Single-Head.
    - `CP3`: Vai trò của Positional Encoding trong dữ liệu chuỗi.
