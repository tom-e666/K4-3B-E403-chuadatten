# Báo Cáo Validation Người Dùng (Validation Log — Bonus R6)

> **Phương pháp**: Phỏng vấn & cho dùng thử prototype 1-1 (10 phút/người) theo chuẩn User Testing Stanford CS177 / PAIR 5.1 với 3 Willing Users đã khai báo tại `spec.md` §8.

---

## 📋 Bảng Nhật Ký Validation Chi Tiết (User Feedback Log)

| Người thử | Task giao | Quan sát hành vi (Observe) | Quote nguyên văn | Mức nghiêm trọng |
|---|---|---|---|---|
| **Nguyễn Công Duẩn**<br>*(HV 2A202602716 — Willing User 1)* | Thử nghiệm giải thích bài học và đề xuất khi bị bí từ diễn đạt. | - **Quan sát**: Trải nghiệm giải thích bài, khi bị AI hỏi lại yêu cầu bổ sung ý thì gặp khó khăn trong việc tìm từ ngữ diễn đạt.<br>- **Hành vi**: Đề xuất cần có gợi ý mẫu để giúp người học khỏi bị bí. | *"Chắc là có thể thêm 1 cái một nút 'Cho tôi xem ví dụ mẫu' thay vì chỉ bảo 'bạn hãy bổ sung' để gợi ý cách diễn đạt nếu bị bí"* | **Trung bình (Feature Request)** |
| **Phùng Quốc Việt**<br>*(HV 2A202602456 — Willing User 2)* | Dùng thử tương tác đa lượt và thử nghiệm case trả lời lảng sang chủ đề khác. | - **Quan sát**: Nhận xét thời gian AI phản hồi hơi chậm.<br>- **Hành vi**: Thử hỏi lảng sang chủ đề B khi AI đang hỏi chủ đề A để xem AI có gợi ý lại hay lặp lại mãi. | *"tôi thấy cũng ok r nma thấy rep hơi chậm. với khbiet là ví dụ mình cứ trả lời lảng đi cái khác nó có gợi ý đi gợi ý lại k ví dụ như hỏi A mà mình cứ trl B nó có trả lời mãi là chưa đúng r gợi ý ./....."* | **Trung bình (UX & Edge Case)** |
| **Phan Hoàng Vũ**<br>*(HV 2A202602450 — Willing User 3)* | Thử thách "nói dối/giải thích sai bản chất" xem AI có phát hiện ra không. | - **Lượt 1**: Cố tình nhập *"Multi-Head Attention giúp giảm bớt tham số mô hình"*. <br>- **Lượt 2**: Ngu AI đưa ra câu hỏi phản ví dụ (counter-example) nghi vấn.<br>- **Lượt 3**: Thử gõ liên tiếp 2 câu ngắn rồi tìm nút gửi. | *"Tớ định troll thử xem bot có gật gù khen bừa không, ai ngờ nó vặn lại ngay bảo tổng tham số có giảm đâu. Cơ mà cái ô gõ chat hơi nhỏ khi tớ muốn viết đoạn dài."* | **Trung bình (Giao diện)** |

---

## 📊 Tổng Hợp 4 Dòng Bài Học Sau Validation

1. **Chủ đề lặp lại nhiều nhất**: Học viên gặp khó khăn khi bị bí từ diễn đạt (cần gợi ý ví dụ mẫu) và phản hồi của bot còn hơi chậm; học viên quan tâm tới kịch bản hỏi lảng sang chủ đề khác (Edge case).
2. **1-2 Thay đổi đã thực hiện trước Demo (Cập nhật vào `spec.md` §9)**:
   - Bổ sung nút gợi ý **"Cho tôi xem ví dụ mẫu"** để giúp người học khi bị bí từ diễn đạt (theo góp ý của Nguyễn Công Duẩn).
   - Xử lý kịch bản lảng sang chủ đề khác (Out-of-scope / Repetitive evasion): Ngu AI kéo về chủ đề cũ tối đa 2 lần trước khi ngắt phiên hoặc đưa gợi ý định hướng (theo góp ý của Phùng Quốc Việt).
3. **Giữ nguyên có lý do**: Giữ nguyên cơ chế tương tác đa lượt (Multi-turn) để buộc người học phải tư duy active recall, không cung cấp đáp án thẳng ngay từ đầu.
4. **Đưa vào Backlog (Slide 6)**: Tối ưu latency phản hồi của Backend Server (streaming response) để giảm cảm giác rep chậm.

---

## 💡 Đánh Giá Theo Thang Đo Disappointment (Sean Ellis Test)

- **Câu hỏi**: *"Nếu từ mai không được sử dụng Feynman AI nữa, bạn cảm thấy thế nào?"*
- **Kết quả**:
  - **2/3 (66.7%)**: Rất tiếc (*"Vì giúp tớ phát hiện đúng chỗ ngơ trước khi vào làm bài tập thật"*).
  - **1/3 (33.3%)**: Hơi tiếc (*"Nếu có thêm phần gợi ý slide cần đọc lại ngay trong chat thì tuyệt hơn"*).
