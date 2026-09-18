# Báo Cáo Khảo Sát Nỗi Đau Học Viên (Bằng Chứng R1 — CP1)

> **Mục tiêu khảo sát**: Xác minh hiện tượng "Illusion of Competence" — người học có cảm giác đã hiểu Multi-Head Attention sau khi đọc slide/nghe giảng, nhưng vẫn gặp khó khăn khi phải tự giải thích lại cơ chế, luồng dữ liệu và ý nghĩa của từng thành phần.

---

## 1. Tổng Quan Khảo Sát

- **Đối tượng**: 11 học viên tham gia khảo sát về nội dung Multi-Head Attention.
- **Phương pháp**: Google Forms kết hợp câu hỏi định lượng và câu hỏi tự luận.
- **Nội dung kiểm tra**:
  - Mức độ đã học/đọc Multi-Head Attention.
  - Mức độ tự đánh giá hiểu bài.
  - Khả năng tự giải thích lại kiến thức.
  - Hiểu biết về lý do sử dụng nhiều Attention Head.
  - Hiểu biết về Q, K, V và cách kết hợp output các head.
  - Những phần kiến thức học viên cảm thấy khó hiểu.
  - Nguyên nhân khiến slide hiện tại chưa giúp hiểu sâu.
  - Nhu cầu đối với công cụ trực quan/học tập tương tác.

> **Lưu ý về cỡ mẫu**: Các câu hỏi định lượng chính có 11 câu trả lời. Câu hỏi tự luận "Tại sao Transformer sử dụng nhiều Attention Head?" có 8 câu trả lời và câu hỏi mô tả luồng dữ liệu có 6 câu trả lời.

---

## 2. Thống Kê Con Số (Quantitative Evidence)

### 2.1. Mức độ tiếp xúc với kiến thức

Với câu hỏi **"Bạn đã học/đọc phần Multi-Head Attention trong slide chưa?"**:

- **45,5% (5/11)**: Đã đọc/học kỹ.
- **27,3% (3/11)**: Đã đọc nhưng chưa kỹ.
- **27,3% (3/11)**: Chưa học phần này.

=> Chỉ **5/11 học viên (45,5%)** cho rằng mình đã học/đọc kỹ nội dung Multi-Head Attention.

---

### 2.2. Mức độ tự đánh giá hiểu bài

Với thang điểm từ **1 đến 5**:

| Mức độ | Số người | Tỷ lệ |
|---|---:|---:|
| 1 | 3 | 27,3% |
| 2 | 1 | 9,1% |
| 3 | 2 | 18,2% |
| 4 | 3 | 27,3% |
| 5 | 2 | 18,2% |

- Điểm trung bình: **3,0/5**.
- **5/11 (45,5%)** tự đánh giá ở mức khá/cao (4–5).
- **4/11 (36,4%)** tự đánh giá ở mức thấp (1–2).

=> Mức độ hiểu bài tự đánh giá phân tán mạnh; ngay sau khi tiếp xúc với slide vẫn có hơn 1/3 học viên đánh giá mình ở mức hiểu thấp.

---

### 2.3. Khả năng tự giải thích Multi-Head Attention cho người khác

Với câu hỏi:

**"Nếu chỉ dựa vào slide hiện tại, bạn có tự tin rằng mình có thể giải thích Multi-Head Attention cho một người khác không?"**

- **27,3% (3/11)**: Có.
- **45,5% (5/11)**: Khá tự tin.
- **27,3% (3/11)**: Không chắc.
- **0%**: Không.

=> **8/11 (72,7%)** cho rằng mình "Có" hoặc "Khá tự tin" có thể giải thích lại.
Tuy nhiên, các câu hỏi kiểm tra kiến thức phía sau cho thấy sự tự tin này **không phải lúc nào cũng đi kèm với khả năng mô tả đầy đủ cơ chế**.

Đây là tín hiệu đáng chú ý liên quan đến giả thuyết **Illusion of Competence**.

---

### 2.4. Kiểm tra hiểu biết: Q, K, V của từng Attention Head

Câu hỏi:

**"Trong Multi-Head Attention, mỗi head có Q, K, V riêng hay tất cả các head sử dụng chính xác cùng một Q, K, V?"**

Kết quả:

- **63,6% (7/11)** chọn đúng: mỗi head có các phép chiếu Q, K, V riêng.
- **9,1% (1/11)** cho rằng tất cả các head dùng chung hoàn toàn Q, K, V.
- **27,3% (3/11)**: Không chắc.

=> **4/11 (36,4%)** trả lời sai hoặc chưa chắc về một thành phần cốt lõi của Multi-Head Attention.

---

### 2.5. Kiểm tra hiểu biết: Cách kết hợp output của các Attention Head

Câu hỏi:

**"Output của các Attention Head được kết hợp như thế nào?"**

- **45,5% (5/11)** chọn đúng:
  **Concatenate các head rồi qua một phép chiếu tuyến tính.**
- **36,4% (4/11)** chọn "Cộng trực tiếp tất cả output".
- **18,2% (2/11)**: Không chắc.

=> **6/11 (54,5%)** chưa xác định đúng cách output của các Attention Head được kết hợp.

Đây là một khoảng trống kiến thức đáng chú ý vì bước **Concatenate + Linear Projection** là thành phần cơ bản trong luồng Multi-Head Attention.

---

## 3. Phân Tích Câu Trả Lời Tự Luận (Qualitative Evidence)

### 3.1. Tại sao Transformer sử dụng nhiều Attention Head?

Câu hỏi nhận được **8 câu trả lời**.

Một số câu cho thấy học viên đã nắm được ý tưởng cơ bản:

> "Vì nhiều multi head sẽ phân tích được nhiều khía cạnh của 1 câu."

> "Để có nhiều góc nhìn khác nhau."

> "Mỗi attention head có thể mang đến 1 thông tin ngữ cảnh khác nhau cho từ..."

> "Để mô hình có thể đồng thời tập trung vào nhiều khía cạnh, góc nhìn và mối quan hệ khác nhau của dữ liệu đầu vào."

Tuy nhiên, cũng xuất hiện các câu:

> "Mình không nhớ rõ."

> "Ko biết."

> "Để giữ lại context nhiều hơn."

=> Có sự phân hóa rõ ràng: một nhóm hiểu được trực giác "nhiều head = nhiều góc nhìn/quan hệ", trong khi một số học viên vẫn chưa thể diễn đạt được mục đích của Multi-Head Attention.

---

### 3.2. Khả năng mô tả luồng dữ liệu qua Multi-Head Attention

Câu hỏi:

**"Hãy mô tả ngắn gọn dữ liệu đi qua Multi-Head Attention như thế nào."**

Có **6 câu trả lời**.

Một số câu trả lời thể hiện hiểu biết tương đối tốt:

> "Đi qua từng head và sau đó tổng hợp lại."

> "Các từ sẽ nhìn attention các từ khác rồi lấy điểm đó nhân với ma trận value."
> "Mỗi token có nhiều head, mỗi head có K, Q, V riêng..."

> "Chia nhỏ không gian embedding thành nhiều phần song song để mô hình học tập ở nhiều góc nhìn khác nhau cùng một lúc."

Trong khi đó vẫn có câu:

> "Mình không nhớ rõ."

> "Chịu."

=> Trong số người thực sự trả lời câu hỏi tự luận, vẫn tồn tại trường hợp **không thể tự tái hiện luồng xử lý bằng lời**, dù nội dung đã được trình bày trong slide.

---

## 4. Các Điểm Gây Khó Hiểu Nhất

Khi được hỏi **"Phần nào của Multi-Head Attention khiến bạn khó hiểu nhất?"**, kết quả nổi bật:

- **6/11 (54,5%)**: Cách chia dimension cho các head.
- **5/11 (45,5%)**: Q, K, V là gì.
- **4/11 (36,4%)**: Scaled Dot-Product Attention.
- **4/11 (36,4%)**: Tại sao cần nhiều head.
- **4/11 (36,4%)**: Ma trận projection.
- **3/11 (27,3%)**: Mỗi head học cái gì khác nhau.
- **3/11 (27,3%)**: Concatenate các head.
- **2/11 (18,2%)**: Luồng dữ liệu từ input đến output.

=> Hai pain point nổi bật nhất là:

**(1) Cách chia dimension cho các head — 54,5%.**

**(2) Ý nghĩa của Q, K, V — 45,5%.**

---

## 5. Tại Sao Slide Hiện Tại Chưa Giúp Học Viên Hiểu Sâu?

Kết quả khảo sát cho thấy:

- **8/11 (72,7%)**: Nhiều công thức nhưng ít giải thích/trực quan.
- **6/11 (54,5%)**: Không hiểu ý nghĩa của Q, K, V.
- **5/11 (45,5%)**: Đọc thì hiểu nhưng khó tự giải thích lại.
- **4/11 (36,4%)**: Thiếu hình ảnh hoặc animation.
- **4/11 (36,4%)**: Thiếu ví dụ cụ thể.
- **3/11 (27,3%)**: Hiểu từng bước nhưng chưa kết nối được toàn bộ luồng.
- **1/11 (9,1%)**: Slide hiện tại đã đủ dễ hiểu.
- **1/11 (9,1%)**: Khác.

=> Pain point lớn nhất không đơn thuần là "thiếu kiến thức", mà là **cách biểu diễn kiến thức chưa giúp người học hình thành mental model rõ ràng**.

Người học có thể nhìn công thức và cảm thấy quen thuộc, nhưng vẫn khó:
- hiểu ý nghĩa Q, K, V;
- hình dung dữ liệu chạy qua từng head;
- hiểu cách các head hoạt động song song;
- hiểu cách output được concatenate;
- tự giải thích lại toàn bộ quá trình.

---

## 6. Nhu Cầu Đối Với Giải Pháp Trực Quan / Tương Tác

Với câu hỏi:

**"Nếu có một công cụ trực quan cho phép bạn nhìn từng bước dữ liệu chạy qua Multi-Head Attention, bạn có muốn sử dụng không?"**

- **36,4% (4/11)**: Rất muốn.
- **27,3% (3/11)**: Có.
- **36,4% (4/11)**: Có thể.
- **0%**: Không cần.

=> **7/11 (63,6%)** thể hiện nhu cầu trực tiếp ("Rất muốn" hoặc "Có").

=> **11/11 (100%)** ít nhất sẵn sàng cân nhắc sử dụng công cụ; không có người trả lời "Không cần".

---
## 7. Những Tính Năng Học Viên Mong Muốn

Các tính năng được lựa chọn nhiều nhất:

- **6/11 (54,5%)**: Xem từng Attention Head đang tập trung vào đâu.
- **6/11 (54,5%)**: Step-by-step calculation.
- **6/11 (54,5%)**: So sánh Single-Head và Multi-Head Attention.
- **6/11 (54,5%)**: Quiz tương tác sau mỗi bước.
- **5/11 (45,5%)**: Visualize Attention Matrix.
- **5/11 (45,5%)**: Chatbot giải thích khi không hiểu.
- **3/11 (27,3%)**: Animation Q → K → V.
- **1/11 (9,1%)**: Khác.

=> Không có một tính năng duy nhất áp đảo. Dữ liệu cho thấy người học ưu tiên sự kết hợp giữa:

**Visual Explanation + Step-by-Step + Active Recall/Quiz.**

Điều này hỗ trợ hướng giải pháp không chỉ "làm slide đẹp hơn", mà tạo ra một **interactive learning tool** giúp người học quan sát, thao tác và tự kiểm tra mức độ hiểu.

---

## 8. Evidence về "Illusion of Competence"

Dữ liệu cho thấy một khoảng cách đáng chú ý giữa **perceived understanding** và **demonstrated understanding**:

- **72,7% (8/11)** cho rằng mình "Có" hoặc "Khá tự tin" có thể giải thích Multi-Head Attention cho người khác.
- Nhưng chỉ **45,5% (5/11)** trả lời đúng cách output của các Attention Head được kết hợp.
- **36,4% (4/11)** trả lời sai hoặc không chắc về việc mỗi head có các phép chiếu Q, K, V riêng.
- **45,5% (5/11)** trực tiếp chọn pain point:
  **"Đọc thì hiểu nhưng khó tự giải thích lại."**
- Các câu tự luận cũng xuất hiện phản hồi:
  **"Mình không nhớ rõ"**, **"Ko biết"**, **"Chịu"**.

=> Dữ liệu **ủng hộ giả thuyết ban đầu** rằng một bộ phận học viên có khoảng cách giữa cảm giác hiểu bài và khả năng tự tái hiện/giải thích kiến thức.

> Tuy nhiên, với cỡ mẫu hiện tại là 11 người và một số câu tự luận có ít người trả lời hơn, kết quả nên được xem là **evidence ban đầu cho CP1**, chưa nên khái quát thành kết luận cho toàn bộ học viên AI20k.

---

## 9. Kết Luận Pain Validation

### Pain được xác nhận

Khảo sát cho thấy vấn đề không chỉ là học viên "chưa học Multi-Head Attention", mà còn tồn tại khoảng cách giữa:

**Đọc/nhìn thấy kiến thức → Cảm thấy hiểu → Tự giải thích → Áp dụng chính xác.**

Evidence nổi bật:

- 72,7% tự nhận có/khá tự tin giải thích.
- Nhưng 54,5% chưa trả lời đúng bước kết hợp output các head.
- 36,4% chưa xác định đúng hoặc chưa chắc về Q, K, V riêng của từng head.
- 72,7% cho rằng slide có nhiều công thức nhưng ít giải thích/trực quan.
- 45,5% cho biết "đọc thì hiểu nhưng khó tự giải thích lại".
- 100% ít nhất sẵn sàng cân nhắc một công cụ trực quan hóa từng bước.

### Problem Statement được đề xuất

> **Học viên khi học các khái niệm AI phức tạp như Multi-Head Attention có thể cảm thấy đã hiểu sau khi đọc slide/nghe giảng, nhưng vẫn gặp khó khăn khi phải tự giải thích lại luồng xử lý và ý nghĩa của các thành phần cốt lõi. Slide tĩnh và công thức chưa cung cấp đủ trực quan, tương tác và cơ chế kiểm tra active recall để người học phát hiện khoảng trống kiến thức của chính mình.**

---

## 10. Ứng Dụng Đưa Vào Canvas CP1 & Spec

### Dòng Evidence ngắn cho Canvas CP1

> **Khảo sát 11 học viên về Multi-Head Attention cho thấy 8/11 (72,7%) tự nhận có hoặc khá tự tin có thể giải thích lại kiến thức, nhưng chỉ 5/11 (45,5%) xác định đúng cách output các Attention Head được concatenate rồi linear projection; 5/11 (45,5%) trực tiếp cho biết "đọc thì hiểu nhưng khó tự giải thích lại". Đồng thời, 8/11 (72,7%) cho rằng slide có nhiều công thức nhưng ít giải thích/trực quan.**

### Evidence về nhu cầu giải pháp

> **11/11 người khảo sát không chọn "Không cần" khi được hỏi về công cụ trực quan hóa từng bước Multi-Head Attention; 7/11 (63,6%) trả lời "Rất muốn" hoặc "Có". Các tính năng được mong muốn nhất gồm xem từng Attention Head, step-by-step calculation, so sánh Single/Multi-Head và quiz tương tác (đều 6/11 — 54,5%).**

### Giả thuyết giải pháp

> **Một công cụ học tập tương tác sử dụng visualization + step-by-step explanation + active recall/reverse tutoring có thể giúp học viên chuyển từ "cảm giác đã hiểu" sang khả năng thực sự giải thích và vận dụng kiến thức.**