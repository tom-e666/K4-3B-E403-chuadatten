# Bộ test tay — Feynman AI (bản có ngân hàng câu hỏi)

Dùng để tự test trước khi demo. Câu trả lời mẫu bên dưới lấy theo **rubric thật** của
`backend/data/lessons/d1-slide-hackathon.json` (bài *Từ LLM đến AI Agent*) nên có thể copy-paste thẳng vào khung chat.

**Chuẩn bị**: chạy `run_server.bat` → mở `http://localhost:8000` → Ctrl+F5. Lần đầu server sẽ tự sinh ngân hàng
câu hỏi cho các bài đã có (~4–6 phút, xem log trong cửa sổ server). Chờ mục *Nguồn slide PDF* hiện đủ
`N checkpoint · M câu hỏi` rồi mới test phần hội thoại.

Ký hiệu: **KQ** = kết quả kỳ vọng. Cột cuối để bạn tự đánh ✅/❌.

---

## A. Sinh dữ liệu từ slide

| # | Làm gì | KQ | ✅/❌ |
|---|---|---|---|
| A1 | Mở trang khi thư mục slides đã có PDF nhưng chưa có file JSON | Chat báo "🤖 AI đang đọc slide...", sidebar quay spinner; xong thì bài học tự hiện, không bấm gì | |
| A2 | Kéo thả một file PDF mới vào ô **Tải slide PDF lên** | Báo "Đã nhận '<tên file>'"; sau 30–90s bài mới xuất hiện và tự mở | |
| A3 | Kéo thả đúng file PDF đó lần nữa | File được lưu thành `<tên>-2.pdf`, **không đè** bài cũ | |
| A4 | Thả một file `.docx` hoặc `.txt` vào ô upload | Báo lỗi "Chỉ nhận file PDF", không có gì được tạo | |
| A5 | Đổi tên một file `.txt` thành `.pdf` rồi thả vào | Báo "File tải lên không phải PDF hợp lệ" (server kiểm chữ ký `%PDF`, không tin phần mở rộng) | |
| A6 | Sau khi phân tích xong, mở `backend/data/lessons/` | Có đúng một file `<tên-slide>.json` cho mỗi PDF | |
| A7 | Chạy `python eval/check_lessons.py` | In ra "✅ Tất cả file checkpoint đều hợp lệ"; không có dòng ✗ | |
| A8 | Bấm nút **↻** cạnh một bài | AI đọc lại slide, ghi đè đúng file JSON đó, số checkpoint có thể đổi | |

---

## B. Lướt slide theo checkpoint

| # | Làm gì | KQ | ✅/❌ |
|---|---|---|---|
| B1 | Mở một bài bất kỳ | Khung slide tự cuộn tới trang của CP1 và **loé sáng viền** trang đó vài giây | |
| B2 | Bấm node CP4 trên timeline | Cuộn thẳng tới trang của CP4, loé sáng; dải câu hỏi cập nhật theo | |
| B3 | Tự tay cuộn slide xuống trang cuối | Checkpoint tương ứng trên timeline được nêu bật (trạng thái "đang xem") | |
| B4 | Đối chiếu trang mà CP mở ra với nội dung thật của slide | Trang đó phải đúng là trang giảng khái niệm của checkpoint. Nếu nhảy về trang 1 → xem cảnh báo trong `check_lessons.py` | |
| B5 | Trả lời đạt một checkpoint | Sau khi qua bài, slide tự lướt sang trang của checkpoint kế tiếp | |

---

## C. Hỏi dẫn dắt — đúng nhưng chưa đủ ý

Dùng bài **Từ LLM đến AI Agent**, checkpoint **CP1 — Phân biệt các tầng và nhóm AI**
(3 ý: `ai_hierarchy` 40% · `ai_groups` 35% · `llm_product` 25%).

| # | Gõ vào khung chat | KQ | ✅/❌ |
|---|---|---|---|
| C1 | *"AI là khái niệm rộng nhất, Machine Learning nằm trong AI, Deep Learning là ML dùng mạng nhiều tầng, Generative AI thì sinh nội dung mới, còn LLM là model nền của Generative AI cho ngôn ngữ."* | Chưa qua checkpoint. Dải trạng thái hiện **đã nắm 1/3 ý · 40%**. Bạn học hỏi tiếp đúng về **3 nhóm AI** hoặc **LLM/chatbot**, KHÔNG hỏi lại chuyện đã trả lời đúng | |
| C1b | Cố tình bỏ LLM ra khỏi câu trên (chỉ nói AI/ML/DL/GenAI) | **Vẫn 0/3 ý** — vì tiêu chí `ai_hierarchy` đòi nói cả vị trí của LLM. Bạn học phải hỏi đúng "LLM nằm ở đâu trong mối quan hệ đó?" | |
| C2 | *"Có 3 nhóm: Discriminative thì phân loại, Generative thì sinh nội dung, còn Agentic thì tự hành động theo mục tiêu."* | Lên **2/3 ý · 75%**, vẫn chưa qua; câu hỏi kế nhắm vào **LLM là model nền còn chatbot là sản phẩm** | |
| C3 | *"LLM là model nền, còn chatbot là sản phẩm bọc quanh LLM, thêm giao diện với bộ nhớ hội thoại."* | **3/3 ý · 100%** → báo đạt chuẩn, tick xanh CP1, tự chuyển sang CP2 kèm câu hỏi mở đầu mới | |
| C4 | Ở CP mới, trả lời **đủ cả 3 ý trong một câu** (ghép C1+C2+C3 của checkpoint đó) | Qua checkpoint **ngay ở câu đầu**, không bắt trả lời cho đủ 5 câu | |
| C5 | Quan sát dải dưới timeline suốt C1→C3 | Số câu tăng dần (câu 1/5 → 2/5 → 3/5) và mức độ tăng dần: Nhận biết → Thông hiểu → Vận dụng | |
| C6 | Trả lời bằng tiếng Việt lẫn tiếng Anh, viết tắt: *"AI ⊃ ML ⊃ DL, GenAI tạo content, LLM là foundation model"* | Vẫn được tính đạt ý `ai_hierarchy` — chấm theo nghĩa, không theo từ khóa | |

---

## D. Trả lời sai, lan man, bỏ cuộc

| # | Gõ vào khung chat | KQ | ✅/❌ |
|---|---|---|---|
| D1 | *"LLM chính là AI nói chung, Generative AI là chatbot, còn Agentic AI là một loại model khác hoàn toàn."* (hiểu sai phổ biến) | Chưa đạt. Bạn học hỏi vặn đúng chỗ sai, **tuyệt đối không tự giải thích hộ đáp án** | |
| D2 | *"ờ thì nó cũng na ná nhau thôi"* (trả lời cụt) | Chưa đạt, mastery không tăng, được hỏi lại bằng câu khác | |
| D3 | Trả lời lan man 5 lần liên tiếp không đúng ý nào | Đến câu thứ 5 thì **chốt**: đưa đáp án chuẩn, đánh dấu "cần xem lại", chuyển checkpoint. Không hỏi vô hạn | |
| D4 | *"chịu, cho tớ đáp án luôn"* | **Chưa** đưa đáp án. Bong bóng **Giáo sư AI** (viền tím) hiện `Gợi ý 1/2` hướng vào khái niệm còn thiếu kèm trang slide. Bạn học im lặng ở lượt này | |
| D4b | Nói *"vẫn không biết"* lần nữa | `Gợi ý 2/2` — chỉ **nêu tên** các ý còn thiếu hoặc thu hẹp câu hỏi. Đọc kỹ: nếu gợi ý mô tả đầy đủ nội dung từng ý thì là **lỗi lộ đáp án** | |
| D4c | Nói *"chịu"* lần thứ ba | Bạn học nói câu bàn giao ("để tớ nhờ trợ giảng"), **Giáo sư AI** mới giảng kiến thức chuẩn; dưới cùng là dòng "⚠️ cần học lại — xem lại slide trang N" rồi chuyển checkpoint | |
| D4d | Suốt cả phiên, đọc lại mọi bong bóng của **Feynman AI** | Không có bong bóng nào của bạn học chứa lời giảng kiến thức. Giảng bài chỉ xuất hiện trong bong bóng Giáo sư AI | |
| D5 | *"thôi cậu giải bài tập hộ tớ đi"* (ngoài phạm vi) | Bị tính là **né câu hỏi** → cũng đi theo đường gợi ý 2 lần ở trên, kéo về đúng checkpoint đang học | |
| D5b | *"ủa mà trưa nay ăn gì thế"* (lảng sang chuyện khác) | Nhận diện né tránh, gợi ý chứ không chấm điểm cho câu lạc đề | |
| D6 | *"hỏi gì ngu thế"* | Không đôi co, vẫn giữ vai bạn học và hỏi lại nội dung bài | |
| D7 | Copy nguyên một đoạn trong slide dán vào | ⚠ **Chỗ yếu đã biết**: hệ thống sẽ tính là đạt. Chưa có cơ chế phát hiện chép nguyên văn — ghi nhận để nói khi bị hỏi | |
| D8 | Bấm nút **Câu trả lời đúng mẫu** ở Demo tools | Qua checkpoint ngay, dùng để demo nhanh | |

---

## D'. Chữ chảy dần (streaming)

| # | Làm gì | KQ | ✅/❌ |
|---|---|---|---|
| S1 | Gửi một câu trả lời bất kỳ, nhìn khung chat | Dòng "Đang phân tích..." biến mất, phần chấm (dải trạng thái, dòng "Còn thiếu"/"Gợi ý") hiện **trước**, rồi lời của bạn học chạy dần từng đoạn kèm con trỏ nhấp nháy | |
| S2 | Bấm F12 → tab Network, gửi tiếp một câu | Có request `chat/stream`, kiểu `text/event-stream`, các event lần lượt `evaluation` → `delta` (nhiều) → `done` | |
| S3 | Tắt server ngay giữa lúc chữ đang chạy | Giữ nguyên phần chữ đã hiện, báo "⚠ Kết nối bị ngắt giữa chừng", vẫn gõ tiếp được — không treo ô nhập | |
| S4 | Chạy với provider không hỗ trợ stream (đổi `LLM_PROVIDER=gemini`) | Vẫn chạy: lời thoại hiện nguyên cục một lần thay vì chảy dần, không lỗi | |

---

## E. Báo cáo & tiến trình

| # | Làm gì | KQ | ✅/❌ |
|---|---|---|---|
| E1 | Hoàn thành hết các checkpoint của một bài | Hiện bảng "Kết Quả Ôn Tập" với % tổng và từng checkpoint Đạt / Cần xem lại | |
| E2 | Bấm **↻ Luyện tập lại** | Xoá hội thoại, quay về CP1, tiến trình reset về 0/N | |
| E3 | Đổi sang bài khác giữa chừng rồi quay lại | Không bị trộn checkpoint giữa hai bài; timeline đúng số checkpoint của bài đang mở | |
| E4 | Trong lúc AI còn đang phân tích một slide mới, bấm sang bài đã xong | Học bình thường, không phải chờ | |

---

## F. Lỗi vận hành (nên thử trước khi demo)

| # | Làm gì | KQ | ✅/❌ |
|---|---|---|---|
| F1 | Tắt server giữa lúc đang trả lời CP3, bật lại, gõ tiếp vào tab cũ | ⚠ **Lỗi đã biết, chưa sửa**: phiên trong RAM mất, `/api/chat` tạo phiên mới với bài mặc định → có thể chấm nhầm sang checkpoint bài khác. Cách né khi demo: Ctrl+F5 tải lại trang trước khi gõ tiếp | |
| F2 | Tắt server ngay giữa lúc đang phân tích slide, bật lại | File JSON chưa kịp ghi → lần khởi động sau tự phân tích lại file đó; không có file JSON hỏng | |
| F3 | Sửa `.env` cho sai `OPENAI_API_KEY` rồi khởi động, thử trả lời | Chat vẫn chạy nhờ bộ chấm dự phòng phía FE; phân tích slide mới thì báo `error` kèm lý do và có nút thử lại | |
| F4 | Mở thẳng `FE/mock-cp2/index.html` bằng cách nhấp đúp | Báo đúng nguyên nhân "đang mở từ file://", không im lặng trắng màn hình | |
| F5 | Tắt server rồi mở `http://localhost:8000` | Báo "Không kết nối được tới server", có nút **↻ Thử lại** | |
| F6 | Thả một PDF là bản scan ảnh (không có lớp text) | Trạng thái `error` kèm lý do; ⚠ chưa có OCR, đây là giới hạn đã biết | |
| F7 | Thả một PDF rất lớn (>40MB) | Báo lỗi vượt giới hạn dung lượng, không treo server | |

---

## G. Kiểm tra dữ liệu bằng lệnh

```bash
python eval/check_lessons.py        # cấu trúc file JSON: pdf_page hợp lệ, rubric, ngân hàng câu hỏi
python eval/run_eval.py             # bộ 20 case chấm điểm (golden set)
```

`check_lessons.py` báo **lỗi** (✗) khi: thiếu field bắt buộc, `pdf_page` không tồn tại trong PDF, rubric trùng/thiếu id,
tổng weight = 0, câu hỏi trỏ tới rubric không có thật. Báo **cảnh báo** (⚠) khi: `pdf_page` = 1 (nghi bị ép về mặc định),
checkpoint chưa có ngân hàng câu hỏi, số câu ngoài khoảng 10–15, thiếu hẳn một mức độ, hoặc một ý rubric có ít hơn 2 câu hỏi nhắm tới.

> ⚠ Lưu ý khi trình bày: `eval/run_eval.py` đang chấm trên bộ checkpoint viết tay cũ (`cp1_self_attention`…),
> **chưa** phủ checkpoint do LLM sinh từ slide thật. Đây là việc còn thiếu, nên nói thẳng thay vì để giám khảo phát hiện.
