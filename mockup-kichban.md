# Danh Sách Mock Skills / Tools của AI Agent (Feynman Tutor)

Dưới đây là danh sách các **Mock Tools / Skills** phục vụ luồng ReAct Agent cho hệ thống Feynman AI Reverse Tutoring:

---

## 🛠️ 1. กลุ่ม Skills Trích Xuất Kiến Thức (Knowledge Extraction Skills)

### 1. `get_video_transcript(video_id, start_time?, end_time?)`
- **Mục đích**: Trích xuất nội dung transcript bài giảng kèm mốc thời gian (timestamps) từ video Youtube/VLearn.
- **Input**: `video_id: string`, `start_time: int`, `end_time: int`
- **Output**: Khung văn bản transcript dùng làm ngữ cảnh gốc (Ground Truth) để AI chấm điểm.

### 2. `get_video_knowledge_checkpoints(video_id, watched_percentage)`
- **Mục đích**: Tự động phân tích video/slide và trả về danh sách các **Lesson Checkpoints (Ý cốt lõi)** thuộc phạm vi người dùng đã học.
- **Input**: `video_id: string`, `watched_percentage: float` (ví dụ: 100% video)
- **Output**: Danh sách JSON gồm các Checkpoint:
  ```json
  [
    {"cp_id": "CP1", "title": "Self-Attention Query-Key-Value", "key_facts": ["Query đại diện câu hỏi", "Key đại diện chỉ mục", "Value đại diện nội dung"]},
    {"cp_id": "CP2", "title": "Multi-Head Attention", "key_facts": ["Tách d_model thành h subspace", "Học nhiều mối quan hệ song song", "Concatenate các head"]}
  ]
  ```

---

## 🛠️ 2. Nhóm Skills Tương Tác & Đóng Vai (Persona Interaction Skills)

### 3. `generate_misconception_question(checkpoint_id, trial_count)`
- **Mục đích**: Đóng vai "Bot Ngu" (Student Persona) tạo ra câu hỏi ngơ ngẩn hoặc đưa ra một hiểu sai phổ biến dựa trên Checkpoint đang xét.
- **Input**: `checkpoint_id: string`, `trial_count: int` (lần thử 1, 2 hay 3)
- **Output**: Câu thoại đóng vai sinh viên ngơ ngác đặt câu hỏi gợi mở cho người học giải thích.

---

## 🛠️ 3. Nhóm Skills Đánh Giá & Theo Dõi Tiến Độ (Evaluation & Tracking Skills)

### 4. `get_user_knowledge_progress(user_id, lesson_id)`
- **Mục đích**: Trích xuất lịch sử học tập của người dùng (các khái niệm đã vững, các lỗ hổng kiến thức thường gặp từ các bài trước).
- **Input**: `user_id: string`, `lesson_id: string`
- **Output**: Bảng tiến độ và mức độ mastery hiện tại của người dùng.

### 5. `evaluate_explanation_score(user_explanation, checkpoint_id)`
- **Mục đích**: "Giáo sư AI" ngầm đánh giá độ khớp kiến thức (% Mastery Score) giữa câu trả lời người dùng và `key_facts` của Checkpoint.
- **Input**: `user_explanation: string`, `checkpoint_id: string`
- **Output**: 
  - `score: number` (0 - 100%)
  - `passed: boolean` (True nếu score ≥ 80%)
  - `missing_concepts: array` (các ý cốt lõi người dùng bỏ sót)
  - `feedback: string` (tóm tắt khen ngợi hoặc gợi ý thử lại)

### 6. `generate_summary_recommendation(user_id, session_evaluations)`
- **Mục đích**: Đóng loop tương tác $\rightarrow$ Tạo Báo cáo Tổng quan % Mastery bài học và đề xuất chính xác timestamp/slide cần xem lại.
- **Input**: `user_id: string`, `session_evaluations: array`
- **Output**: Báo cáo tổng kết dạng Markdown kèm biểu đồ % mastery và link học lại bài.
