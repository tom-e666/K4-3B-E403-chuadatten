# AI SPEC — Feynman AI (Reverse Tutoring Tutor) · Nhóm K4-3B-E403 · Zone E403

> **Bản nháp điền sẵn từ dữ liệu đã có trong repo.** Chỗ nào ghi `[NHÓM XÁC NHẬN]` là suy ra từ tài liệu nhóm,
> cần một người đọc lại và chốt trước khi nộp. Nguồn: `khaosat.md`, `canvas7dong.md`, `mockplan.md`,
> `eval/golden_dataset.json`, `eval/eval_report.json`, code trong `backend/` và `FE/mock-cp2/`.

Hướng: **[x] A — VLearn**  [ ] B — Trợ lý Học viên  [ ] C — Làn mở
Loại: [ ] Tối ưu tính năng có sẵn  **[x] Tính năng mới**

---

## §1. User & Job

**Job executor + workflow**

Học viên AI20k khóa 4 (lớp 3A/3B), sau giờ học trên VLearn/Discord, tự ôn lại bài bằng cách đọc slide và xem
lại video. Workflow hiện tại: xem slide → thấy "hiểu rồi" → đóng slide → tới khi làm bài tập hoặc bị hỏi mới
phát hiện không diễn đạt được → quay lại đọc slide từ đầu, không biết mình hổng chỗ nào.

**Core JTBD**

> Khi vừa học xong một bài dài, tôi muốn biết chắc mình thực sự nắm phần nào và hổng phần nào, để tôi tập
> trung ôn đúng chỗ yếu thay vì đọc lại cả bài.

**Problem statement** *(không dùng chữ AI)*

> Người học tưởng đã hiểu bài sau khi đọc slide (illusion of competence), nhưng khi phải diễn đạt lại bằng lời
> thì hổng ngay ở khái niệm cốt lõi. Hiện không có cách nào kiểm chứng được điều đó ngay sau buổi học, nên lỗ
> hổng chỉ lộ ra lúc làm bài tập hoặc kiểm tra — khi đã muộn.

**Evidence (chuẩn A — phỏng vấn trực tiếp, log đầy đủ tại `khaosat.md`)**

- **n = 15** học viên AI20k (S001–S015), phỏng vấn 1-1 tại lớp và qua Discord, theo nguyên tắc Mom Test:
  giao *hành động* ("giải thích giúp mình cơ chế Multi-Head Attention") thay vì hỏi cảm nhận.
- **15/15 (100%)** khẳng định đã xem slide/nghe giảng bài Transformer.
- **12/15 (80%)** không giải thích được đúng bản chất: 5/15 dùng buzzword nhưng sai luồng dữ liệu,
  4/15 ấp úng không nói thành lời, 3/15 hiểu sai hoàn toàn (nhầm Multi-Head với Multi-Layer / CNN).
- **3/15 (20%)** giải thích đúng và mạch lạc.

**≥5 quote nguyên văn**

1. **S005**: *"Đọc slide thấy công thức Softmax(QK^T / sqrt(d_k))V hiểu lắm, mà bảo tớ nói lại bằng lời thì tớ chịu chết."*
2. **S011**: *"Lúc giảng nghe thầy nói hay lắm, giờ bảo giảng lại cho cậu tớ mới thấy tớ chả nhớ câu trước kết nối câu sau thế nào."*
3. **S014**: *"Bình thường tớ toàn học vẹt để qua quiz, chứ bảo giải thích lại như thầy giáo thì tớ tắc tịt."*
4. **S002**: *"Slide giảng 8 head... nhưng mà 8 head đó chạy song song hay nối tiếp nhỉ? Tự nhiên tớ quên mất luồng."*
5. **S010**: *"Tớ đọc xong slide thấy trôi lắm, mà làm bài tập tool calling / prompt với Transformer toàn bị lẫn."*
6. **S004**: *"Nó giúp chú ý đến các từ quan trọng trong câu."* → hỏi sâu vì sao cần **Multi**: *"Ờ... thì chắc để chú ý được nhiều từ hơn?"*

---

## §2. Impact & quyết định chọn

| # | Ứng viên | Bao nhiêu người | Tần suất | Tốn gì mỗi lần | Khả thi trong hackathon |
|---|---|---|---|---|---|
| 1 | **Luyện giải thích lại bài cho một bạn học (Feynman) + đo % nắm bài** | 12/15 học viên khảo sát gặp đúng nỗi đau này (80%) | Sau mỗi buổi học — 2–3 lần/tuần `[NHÓM XÁC NHẬN]` | 30–45 phút đọc lại cả bài mà vẫn không biết hổng chỗ nào `[NHÓM XÁC NHẬN]` | Cao — chỉ cần slide PDF sẵn có + 2 prompt persona |
| 2 | Chatbot hỏi đáp tài liệu (RAG trên slide) | Gần như cả lớp | Bất kỳ lúc nào | Vài phút/câu hỏi | Cao, nhưng tốn hạ tầng vector DB |
| 3 | Tự sinh quiz trắc nghiệm từ slide | Cả lớp | 1 lần/bài | 5–10 phút | Cao |
| 4 | Nhắc lịch ôn tập giãn cách (spaced repetition) | Cả lớp | Hằng ngày | ~0, chi phí là thói quen | Trung bình — cần dùng nhiều tuần mới thấy tác dụng |

**Ứng viên đã loại + vì sao**

- **(2) Chatbot hỏi đáp**: trả lời hộ người học, làm nỗi đau *nặng thêm* — đọc câu trả lời trôi chảy càng củng
  cố cảm giác "mình hiểu rồi". Không chạm vào nguyên nhân gốc là *người học chưa bao giờ phải tự nói ra*.
- **(3) Quiz trắc nghiệm**: đo nhận biết (recognition), không đo diễn đạt (production). Chính 15/15 học viên đều
  qua được quiz trên VLearn nhưng 12/15 vẫn không giải thích nổi — bằng chứng cho thấy quiz không phát hiện được
  lỗ hổng này. S014 nói thẳng: *"toàn học vẹt để qua quiz"*.
- **(4) Spaced repetition**: đúng hướng nhưng hiệu quả chỉ đo được sau nhiều tuần, không kiểm chứng nổi trong
  khuôn khổ hackathon, và vẫn không nói được người học *hổng cái gì*.

**Ứng viên CHỌN + vì sao (bằng số)**

Chọn **(1)**. Bắt người học tự diễn đạt là phép thử duy nhất trong 4 phương án phân biệt được 12/15 người
"tưởng hiểu" với 3/15 người thực sự hiểu — đúng phép thử đã dùng trong khảo sát và cho ra tín hiệu rõ rệt
(80% vs 20%). Ba phương án còn lại đều để cả 15/15 cùng "qua".

---

## §3. Giải pháp tương tự đã nghiên cứu

| Sản phẩm | Flow | Đáng học | Đáng né | Mình khác gì |
|---|---|---|---|---|
| **Khanmigo** (Khan Academy) | Gia sư AI hỏi theo lối Socratic, không đưa thẳng đáp án mà dẫn dắt để học viên tự nói ra | Nguyên tắc "không giải hộ" — chúng tôi giữ nguyên trong prompt của Giáo sư AI | Vẫn là AI hỏi / học viên trả lời, tức vai trò người học vẫn là *người bị kiểm tra* | Đảo vai hẳn: AI đóng **bạn học ngơ**, người học là *thầy*. Và checkpoint sinh từ đúng slide của buổi học, không phải kho bài chung |
| **Duolingo** | Chia bài thành đơn vị nhỏ, phản hồi tức thì, thanh tiến độ, streak | Vòng lặp ngắn + nhìn thấy tiến độ ngay (chúng tôi làm timeline checkpoint) | Đo bằng câu hỏi đóng, chọn đáp án → đúng dạng "qua bài mà không hiểu" | Đo bằng câu người học tự viết, chấm bằng so khớp ngữ nghĩa với rubric chứ không so khớp đáp án |
| **Quizlet / Anki (flashcard)** | Lật thẻ, tự đánh giá nhớ/không nhớ | Gắn mỗi đơn vị kiến thức về đúng nguồn bài học | Người học tự chấm mình — đúng cái đang hỏng ở đây (S014, S005 đều tự tin sai) | Chấm bởi rubric do LLM đọc từ slide sinh ra, có trích dẫn số trang để người học kiểm chứng lại |

---

## §4. Thiết kế

**Lát cắt MỘT CÂU**

> Một học viên lớp 3B gõ lời giải thích bài học của mình vào khung chat → Evaluator AI đối chiếu ngữ nghĩa với
> rubric của checkpoint đang luyện → trả về % mức nắm bài kèm đúng phần còn hổng và số trang slide cần xem lại.

**Non-goals (KHÔNG build)**

1. Không chấm điểm chính thức thay giảng viên — kết quả chỉ để người học tự biết mình đang ở đâu.
2. Không dạy kiến thức nằm ngoài slide: mọi checkpoint và đáp án phải truy được về đúng trang PDF của buổi học.
3. Không làm chatbot hỏi đáp tự do — AI không giải thích hộ, trừ khi người học chủ động bỏ cuộc.
4. Không sinh video/bài giảng mới, không chấm bài tập code.
5. Không lưu hồ sơ học viên dài hạn — phiên học nằm trong RAM, tắt server là hết.

**Mức prototype: [x] Working** (mock phần nào, thật phần nào)

- **Thật**: upload slide PDF → LLM đọc sinh file JSON checkpoint (`backend/lesson_ingest.py`); chấm ngữ nghĩa
  2 tầng (Evaluator AI → persona bạn học) trong `backend/agent.py`; khung slide PDF.js tự lướt tới trang của
  checkpoint; bộ eval 20 case chạy được bằng `run_eval.bat`.
- **Mock**: giao diện VLearn (dựng lại theo ảnh, không phải VLearn thật); video bài giảng chỉ là nút bấm;
  mục "Bài tập thực hành" ở sidebar là tĩnh; chưa có đăng nhập, mọi người dùng chung một phiên.

**Automation: [x] augment** (không phải automate)

Cost-of-error ở đây là *chấm sai làm người học hiểu sai về chính mình*: chấm rộng tay → người học yên tâm sai
và bỏ qua lỗ hổng; chấm chặt tay → nản, bỏ cuộc. Cả hai đều không tự phục hồi được, nên hệ thống chỉ **đưa ra
nhận định kèm lý do và trang slide để người học tự kiểm chứng**, không khoá bài, không ghi điểm vào học bạ,
không chặn ai học tiếp. Người học luôn có quyền thử lại (3 lượt) hoặc xin đáp án.

**§4b. Nguyên tắc đã áp dụng (HAX)**

| Nguyên tắc | Áp cụ thể vào đâu trong prototype |
|---|---|
| **G1 — Làm rõ hệ thống làm được gì** | Ngay đầu hội thoại, khung chat liệt kê đủ các checkpoint AI vừa sinh từ slide kèm số trang, để người học biết trước sẽ bị hỏi những gì |
| **G2 — Làm rõ hệ thống làm tốt tới đâu** | Trả về % mastery theo từng checkpoint thay vì một chữ "Đạt/Không đạt"; báo cáo cuối phiên tách rõ phần đạt và phần cần xem lại |
| **G11 — Làm rõ vì sao hệ thống phán như vậy** | Khi chưa đạt, hiển thị đúng `missing_points` (ý nào thiếu + vì sao chưa đạt) và `source_citation` trỏ về trang slide, không chỉ nói "sai rồi" |
| **G9 — Hỗ trợ sửa sai hiệu quả** | Cho tối đa 3 lượt giải thích lại, mỗi lượt bạn học AI chỉ hỏi vặn đúng **một** ý còn thiếu; slide tự lướt tới trang liên quan để người học đọc lại ngay |
| **G16 — Cho biết hậu quả của hành động** | Người học chủ động nói "chịu/không biết" → hệ thống báo trước là sẽ đưa đáp án và checkpoint bị đánh dấu "cần học lại", chứ không lặng lẽ cho qua |

---

## §5. Kiểu lỗi — 4 lớp chỗ khó + kịch bản

| # | Lớp chỗ khó | Kịch bản lỗi | Xử lý hiện tại |
|---|---|---|---|
| 1 | **Đầu vào (slide PDF)** | Slide là bản scan ảnh, không có lớp text → LLM không đọc được nội dung | Trạng thái `error` kèm lý do ở panel nguồn slide, có nút thử lại `[CHƯA CÓ: OCR]` |
| 2 | Đầu vào | Slide quá mỏng/toàn ảnh bìa → không đủ khái niệm để sinh checkpoint | `_validate_lesson` chặn khi số checkpoint ngoài khoảng 1–8 và báo chạy lại |
| 3 | **Sinh checkpoint** | LLM bịa ra khái niệm "nên có" của chủ đề nhưng không có trong slide (vd Q/K/V với slide không hề nhắc) | Prompt cấm tuyệt đối suy diễn ngoài slide, bắt mọi checkpoint truy được về trang thật; `source_citation` để người kiểm tra đối chiếu |
| 4 | Sinh checkpoint | `pdf_page` trỏ tới trang không tồn tại (vd trang 50 của file 29 trang) → bấm vào nhảy hụt | Server đối chiếu với số trang thật bằng `pypdf`: thiếu → trang 1, vượt → trang cuối, ghi rõ trong `warnings` |
| 5 | **Chấm ngữ nghĩa** | Người học diễn đạt đúng bản chất nhưng dùng từ khác hoàn toàn với rubric → bị chấm trượt oan | Evaluator được lệnh so khớp **ý nghĩa**, cấm so khớp từ khóa; rubric viết dạng tiêu chí mô tả chứ không phải đáp án mẫu |
| 6 | Chấm ngữ nghĩa | Người học chép nguyên văn slide dán vào → được điểm cao mà không thực sự hiểu | `[CHƯA XỬ LÝ]` — cần thêm dấu hiệu phát hiện sao chép nguyên văn |
| 7 | Chấm ngữ nghĩa | Người học viết lan man, tiếng Việt lẫn tiếng Anh, sai chính tả | Có trong golden set (`low_effort`, `edge_case`); prompt yêu cầu bỏ qua hình thức, chỉ xét nội dung |
| 8 | Chấm ngữ nghĩa | Người học hỏi ngược sang chuyện ngoài bài (`out_of_scope`) hoặc nói lời xúc phạm (`toxic`) | Có case trong golden set; persona kéo về đúng checkpoint, không đôi co |
| 9 | Chấm ngữ nghĩa | Người học bỏ cuộc ("chịu", "cho đáp án") nhưng hệ thống vẫn cố hỏi vặn | Evaluator có trạng thái riêng `GAVE_UP` → đưa `reveal_answer` đầy đủ bằng giọng bạn học |
| 10 | **Vận hành / hệ thống** | LLM trả về JSON kèm ```json fence hoặc lời dẫn thừa → parse hỏng | `_parse_json_object` bóc JSON đầu tiên, có verdict dự phòng khi vẫn hỏng |
| 11 | Vận hành | Server sập giữa phiên → phiên chat trong RAM mất, `/api/chat` tạo lại session với lesson mặc định và **chấm nhầm sang bài khác** | `[LỖI ĐÃ BIẾT — CHƯA SỬA]` — cần gửi kèm `lesson_id` trong mỗi lượt chat |
| 12 | Vận hành | Nhà cung cấp LLM sập / hết quota giữa buổi demo | Checkpoint đã sinh nằm trên đĩa nên vẫn học được; FE có bộ chấm offline đơn giản để demo không đứng hình |

---

## §6. Bốn đường đi của trải nghiệm

- **Happy path**: người học giải thích đủ ý → Evaluator trả `PASS` (≥80%) → bạn học AI gật gù chốt lại một ý
  cốt lõi → timeline tick xanh, slide tự lướt sang trang của checkpoint kế tiếp.
- **Low-confidence (②)**: `NEEDS_IMPROVEMENT` → bạn học AI chỉ thắc mắc đúng **một** ý còn thiếu (không liệt kê
  hết, không giảng hộ), kèm gợi ý lấy từ rubric; còn tối đa 3 lượt.
- **Failure / không căn cứ (①)**: hết 3 lượt vẫn chưa đạt → hệ thống đưa `correction` chuẩn kèm trích dẫn trang
  slide, đánh dấu checkpoint "cần học lại" rồi chuyển tiếp, không để người học kẹt lại.
- **Correction (user sửa)**: người học viết lại, bổ sung ý thiếu → chấm lại từ đầu với đủ rubric, không cộng dồn
  điểm của lượt trước; người học cũng có thể bấm thẳng vào checkpoint bất kỳ trên timeline để quay lại.
- **Bị đòi ngoài phạm vi (③)**: hỏi chuyện ngoài bài (vd "làm hộ bài tập", "GPT-5 khác gì") → bạn học AI kéo về
  đúng checkpoint đang luyện, nói rõ mình chỉ đang nhờ giảng lại phần này.
- **Case đặc thù domain (④)**: thuật ngữ tiếng Anh giữ nguyên không dịch (Query, Key, Value, Attention) — người
  học viết "truy vấn" hay "Query" đều phải được tính là đúng; ngược lại, nói đúng *tên* mà sai *cơ chế*
  (buzzword như S001) phải bị tính là chưa đạt.

---

## §7. Kiểm thử

**Chiều chất lượng + định nghĩa kiểm chứng được**

Hệ thống phán đúng *trạng thái* của một lời giải thích: `PASS` khi và chỉ khi lời giải thích phủ ≥80% trọng số
rubric của checkpoint đó; `NEEDS_IMPROVEMENT` khi thiếu/sai ý; `GAVE_UP` khi người học xin hàng. Đo bằng cách
so trạng thái hệ thống trả về với trạng thái do nhóm gán tay trong golden set.

**Golden set: 20 case** (`eval/golden_dataset.json`), cơ cấu thật hiện tại:

| Nhóm case | Số lượng |
|---|---|
| happy_path | 7 |
| missing_concept | 3 |
| misconception | 3 |
| low_effort | 2 |
| adversarial | 2 |
| out_of_scope | 1 |
| edge_case | 1 |
| toxic | 1 |

Trải trên 3 checkpoint (`cp1_self_attention` 8 case, `cp2_multi_head_attention` 6, `cp3_positional_encoding` 6);
kỳ vọng 8 `PASS` / 12 `NEEDS_IMPROVEMENT`.

**Quality bar** (chốt từ thời điểm nộp, giữ nguyên sau đó):

> Đạt khi **≥ 85%** case trong golden set cho ra đúng trạng thái kỳ vọng, **và** không có case `misconception`
> hay `adversarial` nào bị chấm nhầm thành `PASS` (chấm rộng tay cho một lời giải thích sai bản chất là lỗi
> nặng nhất của sản phẩm này). `[NHÓM XÁC NHẬN con số 85%]`

**Kết quả các lượt chạy**

| Lượt | Thời điểm | Kết quả | Ghi chú |
|---|---|---|---|
| 1 | 2026-09-18 14:45 | **20/20 = 100%** | `eval/eval_report.json` |

> ⚠ **Rủi ro cần nói thẳng khi trình bày**: golden set đang gắn với bộ checkpoint viết tay của bài Transformer
> (`cp1_self_attention`…), trong khi sản phẩm hiện đã chuyển sang checkpoint do LLM tự sinh từ slide thật
> (`d1-slide-hackathon.json`, `d2-slide-hackathon.json`). Con số 100% vì vậy chưa phủ luồng mới, và 100% với 20
> case cũng là dấu hiệu bộ test còn dễ. Việc cần làm: bổ sung case cho checkpoint sinh tự động.

---

## §8. Phân công & kế hoạch

| Người | Vai trò |
|---|---|
| **Thái Phúc Tiến** | PM & Prompt cho persona "Ngu AI" — spec, luồng tổng thể |
| **Trần Đình Duy** | Data Retriever & Golden Set — bằng chứng, bộ case kiểm thử |
| **Nguyễn Thành Luân** | Analysis & Metric Scoring Logic — logic chấm, % mastery |
| **Nguyễn Đức Long** | CTO & App System Architecture — backend, FE, demo |

> ⚠ `canvas.md` và `canvas7dong.md` đang ghi **hai bảng phân công khác nhau** (canvas.md: Tiến = Prompt,
> Duy = UI, Luân = Evaluator, Long = dataset+video). Bảng trên lấy theo `canvas7dong.md`. **Phải thống nhất
> một bản trước khi nộp.**

**Willing users (≥2)**

1. Nguyễn Công Duẩn — 2A202602716
2. Phùng Quốc Việt — 2A202602456
3. Phan Hoàng Vũ — 2A202602450

Kế hoạch vòng validation: cho cả 3 dùng thử trên đúng slide buổi học gần nhất, đo 2 thứ — (a) hệ thống có chỉ ra
đúng chỗ họ hổng không (đối chiếu với nhận định của chính họ sau buổi thử), (b) họ có quay lại dùng lần 2 không.
`[NHÓM XÁC NHẬN đã chạy hay chưa]`

**Multi-prototype**: `[NHÓM ĐIỀN nếu có làm]`

---

## §9. Changelog

| Thời điểm | Đổi gì | Vì sao |
|---|---|---|
| 18/9 sáng | Checkpoint chuyển từ viết tay sang **LLM tự đọc slide PDF sinh ra** (`lesson_ingest.py`) | Viết tay không nhân rộng được sang bài giảng khác; mỗi buổi học một bộ checkpoint riêng |
| 18/9 trưa | Mỗi checkpoint gắn `pdf_page`, khung slide tự lướt + loé sáng đúng trang | Phản hồi "chưa đạt" chỉ hữu ích khi người học tới thẳng được chỗ cần đọc lại (HAX G11) |
| 18/9 chiều | Server tự phân tích slide ở luồng nền; thêm upload PDF; checkpoint lưu thành **một file JSON cho mỗi slide** (`backend/data/lessons/`) | Bỏ thao tác thủ công; kết quả đắt tiền nhất (đã gọi LLM) được ghi xuống đĩa nên sập/restart không phải chạy lại |
| 18/9 chiều | Chốt lại `pdf_page` theo số trang thật bằng `pypdf` | Gặp thật: LLM trả về trang không tồn tại → bấm vào nhảy hụt |
