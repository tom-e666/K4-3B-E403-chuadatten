# Báo Cáo Khảo Sát Nỗi Đau Học Viên (Bằng Chứng R1 — CP1)

> **Mục tiêu khảo sát**: Xác minh hiện tượng "Illusion of Competence" (tưởng mình đã hiểu bài sau khi đọc slide/xem video, nhưng thực tế hổng kiến thức cốt lõi khi phải giải thích lại).

---

## 1. Tổng Quan Khảo Sát

- **Đối tượng**: 15 học viên thuộc khóa AI20k (gồm các lớp 3A, 3B - đã ẩn danh mã S001 đến S015).
- **Phương pháp**: Phỏng vấn trực tiếp 1-1 tại lớp & qua tin nhắn Discord (Theo nguyên tắc Mom Test: yêu cầu thực hiện hành động giải thích thực tế thay vì hỏi cảm nhận chung chung).
- **Câu hỏi / Thử thách giao**: *"Bạn vừa học xong slide Transformer. Hãy giải thích giúp mình: Cơ chế Multi-Head Attention hoạt động ra sao và tại sao phải chia làm nhiều Head thay vì 1 Head đơn?"*

---

## 2. Thống Kê Con Số (Quantitative Evidence)

- **100% (15/15)** khẳng định đã xem slide hoặc nghe giảng bài Transformer.
- **80% (12/15)** không giải thích được đúng bản chất, gặp các sự cố:
  - 5/15 dùng từ khóa hoa mỹ (buzzwords) nhưng giải thích sai luồng dữ liệu.
  - 4/15 ấp úng, thừa nhận "nhớ mang mát chứ không tự nói ra được".
  - 3/15 hiểu sai hoàn toàn (nhầm Multi-Head Attention với Multi-layer Perceptron hoặc Convolution).
- **20% (3/15)** giải thích đúng và mạch lạc.

=> **Kết luận**: Nỗi đau "Illusion of Competence" là có thật và phổ biến (80%). Người học cần một phương pháp tương tác phản hồi (Reverse Tutoring / Feynman Technique) để tự kiểm tra kiến thức.

---

## 3. Bảng Nhật Ký Phỏng Vấn Chi Tiết (Raw Interview Logs)

| STT | Mã HV | Tự tin ban đầu | Kết quả thử thách giải thích | Quote nguyên văn (Mom Test) | Lỗi vướng chính |
|---|---|---|---|---|---|
| 1 | `S001` | Rất tự tin | Sai bản chất | *"Thì Multi-Head là nó nhân nhiều ma trận Query với Key lại với nhau để model thông minh hơn thôi..."* | Không hiểu cơ chế subspace (chiếu vector vào các không gian khác nhau). |
| 2 | `S002` | Khá tự tin | Ấp úng, dừng lại | *"Slide giảng 8 head... nhưng mà 8 head đó chạy song song hay nối tiếp nhỉ? Tự nhiên tớ quên mất luồng."* | Quên luồng xử lý song song & concat đầu ra. |
| 3 | `S003` | Bình thường | Nhầm lẫn khái niệm | *"Multi-Head Attention là nhiều lớp Transformer xếp chồng lên nhau đúng không b?"* | Nhầm giữa Multi-Head và Multi-Layer. |
| 4 | `S004` | Tự tin | Trả lời chung chung | *"Nó giúp chú ý đến các từ quan trọng trong câu."* -> Hỏi sâu vì sao cần *Multi*: *"Ờ... thì chắc để chú ý được nhiều từ hơn?"* | Không nắm được mối quan hệ từ vựng đa chiều (ngữ pháp, ngữ nghĩa, đại từ). |
| 5 | `S005` | Không tự tin | Thừa nhận ngơ | *"Đọc slide thấy công thức Softmax(QK^T / sqrt(d_k))V hiểu lắm, mà bảo tớ nói lại bằng lời thì tớ chịu chết."* | Học vẹt công thức toán, không chuyển hóa thành hiểu ngữ nghĩa. |
| 6 | `S006` | Tự tin | Giải thích đúng | *"Chia Q, K, V thành h phần để mỗi head học một khía cạnh quan hệ khác nhau như đại từ thay thế, quan hệ động từ..."* | Đạt (Có kiến thức vững). |
| 7 | `S007` | Bình thường | Ấp úng | *"À... thì đại loại là tách ma trận ra thành nhiều phần nhỏ... xong làm gì nữa nhỉ?"* | Hổng bước Concatenate & Linear projection cuối. |
| 8 | `S008` | Khá tự tin | Nhầm lẫn | *"Multi-head là cơ chế dùng trong CNN đúng ko?"* | Tải kiến thức sai lệch từ kiến thức cũ. |
| 9 | `S009` | Rất tự tin | Giải thích đúng | *"Giống như nhiều chuyên gia cùng soi 1 bức tranh, mỗi người nhìn 1 góc độ góc nhìn rồi tổng hợp lại."* | Đạt (Dùng analogy chuẩn). |
| 10 | `S010` | Bình thường | Thừa nhận ngơ | *"Tớ đọc xong slide thấy trôi lắm, mà làm bài tập tool calling / prompt với Transformer toàn bị lẫn."* | Không áp dụng được vào thực hành. |
| 11 | `S011` | Khá tự tin | Bị vỡ luồng | *"Lúc giảng nghe thầy nói hay lắm, giờ bảo giảng lại cho cậu tớ mới thấy tớ chả nhớ câu trước kết nối câu sau thế nào."* | Thiếu liên kết tư duy logic. |
| 12 | `S012` | Bình thường | Sai bản chất | *"Multi-head là để giảm bớt số lượng tham số cho mô hình nhẹ đi."* | Hiểu sai mục đích của Multi-Head. |
| 13 | `S013` | Tự tin | Giải thích đúng | *"Nó chia nhỏ d_model thành d_k = d_model / h để tính attention song song trên từng subspace..."* | Đạt. |
| 14 | `S014` | Không tự tin | Ấp úng | *"Bình thường tớ toàn học vẹt để qua quiz, chứ bảo giải thích lại như thầy giáo thì tớ tắc tịt."* | Thiếu công cụ tự luyện giảng (Feynman). |
| 15 | `S015` | Bình thường | Nhầm lẫn | *"Head 1 tính self-attention, head 2 tính cross-attention đúng không?"* | Nhầm lẫn chức năng các module trong Encoder/Decoder. |

---

## 4. Trích Dẫn Nổi Bật (Key Quotes)

> 💬 **HV S005**: *"Đọc slide thấy công thức Softmax(QK^T / sqrt(d_k))V hiểu lắm, mà bảo tớ nói lại bằng lời thì tớ chịu chết."*
> 
> 💬 **HV S011**: *"Lúc giảng nghe thầy nói hay lắm, giờ bảo giảng lại cho cậu tớ mới thấy tớ chả nhớ câu trước kết nối câu sau thế nào."*
> 
> 💬 **HV S014**: *"Bình thường tớ toàn học vẹt để qua quiz, chứ bảo giải thích lại như thầy giáo thì tớ tắc tịt."*

---

## 5. Ứng Dụng Đưa Vào Canvas CP1 & Spec

- **Dòng 4 Canvas CP1**: *Khảo sát 15 học viên khoá AI20k: 12/15 (80%) đọc slide thấy hiểu nhưng khi được hỏi giải thích lại cơ chế Multi-Head Attention thì không giải thích được hoặc hiểu sai bản chất (xem chi tiết log phỏng vấn S001-S015 tại `khaosat.md`).*
