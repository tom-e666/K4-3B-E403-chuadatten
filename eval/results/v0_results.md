# Báo cáo Đánh giá Phiên bản v0 (Static Scripted Proof-of-Concept)

- **Mốc phiên bản**: `v0` (Khởi tạo ý tưởng & Kịch bản cứng)
- **Commit định danh**: `839edde` (`kichban mockup`)
- **Tài liệu nguồn**: [`co_kich_ban.html`](file:///d:/vin20k/minihack/K4-3B-E403-chuadatten/co_kich_ban.html)
- **Trạng thái kiểm thử tự động**: **`N/A` (Không áp dụng)**

---

## 1. Bản chất & Phạm vi của v0

Phiên bản v0 được xây dựng trong giai đoạn đầu của cuộc thi (CP1 / CP2) với mục đích:
- Chứng minh tính khả thi của ý tưởng **Reverse Tutoring** (Kỹ thuật Feynman): Người học đóng vai trò người dạy để giải thích lại bài học cho bạn học AI ngây ngô.
- Thử nghiệm giao diện tương tác dạng chatbox 2 vai (Minh AI & Trợ giảng AI).
- Toàn bộ nội dung hội thoại, câu hỏi và phản hồi đều được viết cứng (**hardcoded**) bằng JavaScript trong file `co_kich_ban.html`.

---

## 2. Phương pháp Đánh giá tại mốc v0

Tại thời điểm v0:
- **Chưa có backend server**: Không có FastAPI hay server lắng nghe request.
- **Chưa có tích hợp AI/LLM thật**: Không có kết nối tới Gemini, OpenAI hay OpenRouter.
- **Chưa có bộ kiểm thử tự động**: Không có thư mục `eval/` hay dataset `golden_dataset.json`.

Hình thức kiểm thử duy nhất được thực hiện là **Thao tác thủ công theo kịch bản (Manual Scripted Walkthrough)**: Thành viên nhóm mở file `co_kich_ban.html` trên trình duyệt và bấm các nút chọn câu trả lời mẫu để xác nhận tính hợp lý của luồng sư phạm.

---

## 3. Bảng Chỉ số Đo lường v0

| Chỉ số kiểm thử | Giá trị ghi nhận | Ghi chú phương pháp luận |
|---|:---:|---|
| **Bộ Golden Set tự động** | `N/A` | Chưa xây dựng tại mốc v0 |
| **Số test case tự động** | `0` | Không có runner kiểm thử |
| **Pass Rate tự động** | `N/A` | Không bịa đặt số liệu giả |
| **Xác minh kịch bản thủ công** | ĐẠT (5/5 luồng mẫu) | Đã thử nghiệm luồng đối thoại trên HTML |
| **Tích hợp LLM thực tế** | `0` | Hoàn toàn chạy bằng script tĩnh |

---

## 4. Kết luận & Điểm hạn chế chính của v0

* **Ưu điểm**: Giúp cả nhóm hình dung rõ ràng luồng tương tác và kịch bản sư phạm.
* **Hạn chế**: Không có khả năng xử lý câu trả lời tự do của học viên, không thể đánh giá độ hiểu bài động, chưa đáp ứng quy định tối thiểu $\ge 1$ lời gọi AI thật của hackathon.

