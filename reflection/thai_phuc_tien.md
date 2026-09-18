# Reflection Cá Nhân — Thái Phúc Tiến (Leader)

> **Thông tin thành viên**:
> - **Họ và tên**: Thái Phúc Tiến (Leader)
> - **Vai trò chính**: Quyết định giao diện, feature, backend architecture, deliverables & pitching (`spec.md`, `slide_presentation.html`, `cp4.md`).

---

## 1. Vai trò & Phần việc đã thực hiện
- **Đóng góp chính**: 
  - Đăng ký và quản lý repo nhóm, phân công nhiệm vụ và giữ nhịp tiến độ cho cả 4 mốc Checkpoint (CP1 $\rightarrow$ CP4).
  - Soạn thảo và hoàn thiện toàn bộ file kiến trúc tài liệu [`spec.md`](file:///C:/AI/vinai20k/K4-3B-E403-chuadatten/spec.md) phủ đủ 8 phần tiêu chuẩn (User JTBD, Impact Candidate Matrix, HAX/PAIR principles, 4 lớp chỗ khó, 4 đường đi trải nghiệm và Quality Bar).
  - Thiết kế kịch bản thuyết trình 6 trang ([`slide6pagekichban.md`](file:///C:/AI/vinai20k/K4-3B-E403-chuadatten/slide6pagekichban.md)) và làm file giao diện slide HTML cao cấp ([`slide_presentation.html`](file:///C:/AI/vinai20k/K4-3B-E403-chuadatten/slide_presentation.html)) theo chuẩn VLearn Theme.
- **Commit chính trên Git**: `3e03345` (update spec & checklist), `8fd8c46` (update spec & log), `9a4a977` (CP4 deliverables), `e1ac777` (add presentations).

---

## 2. Ứng dụng AI trong quá trình làm việc
- Sử dụng AI Coding Assistant (Antigravity AI Agent) để hỗ trợ tra cứu chuẩn Rubric 8 phần, trích xuất dữ liệu khảo sát từ `khaosat.md` và tự động hóa sinh các kịch bản lỗi (Error Scenarios) theo nguyên tắc PAIR/HAX.
- Dùng AI để hỗ trợ kiểm tra tính nhất quán giữa file `spec.md`, file khảo sát thực tế và mã nguồn backend (`backend/agent.py`).

---

## 3. Bài học kinh nghiệm từ Case Fail của nhóm
- **Case Fail thực tế**: Khi nhóm chạy đánh giá tự động (Golden Set 22 cases), tỷ lệ đạt ban đầu bị rớt xuống **68.18%** (vỡ 7 cases) do API Gemini Quota bị quá tải (`429 RESOURCE_EXHAUSTED`), làm hệ thống fallback nhầm các câu trả lời đúng thành `NEEDS_IMPROVEMENT`.
- **Bài học rút ra**: *"Giao diện đẹp không thay thế được tư duy kiểm thử tự động (Evals); việc đo lường trung thực bằng code giúp nhóm phát hiện đúng ranh giới chịu tải và thiết kế cơ chế ứng phó rủi ro (Fallback Graceful Failure) thực tế cho hệ thống AI."*
