# Báo cáo Đánh giá Phiên bản v1 (First Functional Prototype)

- **Mốc phiên bản**: `v1` (Prototype chức năng đầu tiên kết nối AI thật)
- **Commit định danh**: `c90b4da` (`tired`)
- **Trạng thái kiểm thử tự động**: **`HISTORICAL_RESULT_UNAVAILABLE` (Kết quả lịch sử chưa được lưu trữ tự động)**

---

## 1. Bản chất & Phạm vi của v1

Phiên bản v1 đánh dấu bước nhảy vọt quan trọng từ kịch bản tĩnh sang một **ứng dụng hoạt động thực tế (Working Prototype)**:
- Xây dựng Backend bằng **FastAPI** (`backend/server.py`).
- Tích hợp Agent với **LLM Provider thật** (Google Gemini API / OpenAI API) thực hiện kỹ thuật Prompting và Tool Calling.
- Đưa vào thử nghiệm cơ chế **Dual Evaluation**: Bạn học ngây ngô đặt câu hỏi $\rightarrow$ Người học giải thích $\rightarrow$ Evaluator phân tích mức độ bao phủ Rubric Points và phát hiện ngộ nhận.
- Áp dụng trên 1 bài học duy nhất: *Transformer Architecture & Multi-Head Attention*.

---

## 2. Phương pháp Đánh giá tại mốc v1

Tại thời điểm v1:
- Nhóm tiến hành kiểm thử tương tác ad-hoc (thử nghiệm trực tiếp qua giao diện chat và qua lệnh gọi API cURL/Postman).
- **Trạng thái Benchmark tự động**: Kiểm tra lịch sử Git tại commit `c90b4da` cho thấy thư mục `eval/` và file `golden_dataset.json` chưa được commit vào repository ở mốc này (thư mục `eval/` chỉ chính thức xuất hiện từ commit `c8d6102`).
- **Nguyên tắc phương pháp luận**: Tuân thủ tiêu chuẩn đánh giá AI chuyên nghiệp — tuyệt đối **không bịa đặt kết quả số liệu trong quá khứ** khi không có log chạy hoặc artifact có thể tái lập 100%. Vì vậy, chỉ số kiểm thử tự động của v1 được ghi nhận chính xác là **`NOT REPRODUCED / HISTORICAL RESULT UNAVAILABLE`**.

---

## 3. Bảng Chỉ số Đo lường v1

| Tiêu chí | Giá trị tại mốc v1 | Ghi chú |
|---|:---:|---|
| **Bộ Golden Set tự động** | `Historical Result Unavailable` | Chưa có artifact lưu trong git tại commit `c90b4da` |
| **Kết nối AI thực tế** | **ĐẠT (Yes)** | Đã gọi thành công Gemini/OpenAI API |
| **Hỗ trợ Đa bài học** | Chưa hỗ trợ | Chỉ chạy cứng 1 bài học Transformer |
| **Cơ chế tự phục hồi (Fallback)** | Chưa có | Hệ thống có thể sập hoặc văng lỗi 500 nếu API bị 429 |
| **Trải nghiệm giao diện (UI/UX)** | Hạn chế | Toàn bộ trang web bị cuộn dọc (page scroll) khi hội thoại dài |

---

## 4. Các điểm nghẽn kỹ thuật thúc đẩy nâng cấp lên v2

1. **Lỗi tràn layout (Full-page scroll)**: Khi người học thảo luận dài, toàn bộ trang web bị cuộn, đẩy khung xem video/slide bài giảng trôi mất.
2. **Nguy cơ lỗi 500 khi hết hạn mức**: Việc phụ thuộc hoàn toàn vào API bên ngoài khiến phiên demo có nguy cơ bị gián đoạn nếu gặp sự cố mạng hoặc chạm trần rate limit.
3. **Thiếu tính đa dạng bài học**: Chưa khai thác được kho dữ liệu thực chiến phong phú của khóa học.
4. **Thiếu tầng đánh giá chuẩn mực**: Thúc đẩy nhóm xây dựng thư mục `eval/` với bộ Golden Set và test suite E2E chính thức trong phiên bản v2.

