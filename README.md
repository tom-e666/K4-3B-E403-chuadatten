Mini Hackathon AI — Batch 04 · Lớp 3B
SPEC → Prototype → Demo. Đây không phải cuộc thi code — đây là cuộc thi tư duy sản phẩm AI.

👥 Thành viên nhóm & Phân công vai trò
Lớp: 3B · Phòng: E403 · Cụm: Zone 05 · Track: 04

Họ và Tên	Mã Học Viên	Vai trò chính	Phần việc đảm nhiệm trong dự án

Thái Phúc Tiến	2A202602873 x x

Trần Đình Duy 2A202602631 x x

Nguyễn Thành Luân 2A202602769 x x

Nguyễn Đức Long 2A202602917 x x

* x: chưa điền thông tin

Nhóm copy nguyên file README này về repo của mình, rồi điền bảng trên. Cột Phần việc đảm nhiệm ghi càng cụ thể càng tốt.

Thời lượng: 39 giờ từ phát đề đến thuyết trình (ca 3B) — LAB 5 (phát đề + build) · LEC 6 (tiếp tục build theo ca) · LAB 6 (vòng thi)
Nhóm: 3-4 người · thi theo phòng (E403 / E402), chia cụm rồi chung kết phòng — xem Thể thức thi
Chia cụm theo bàn, không cần chung đề tài. Chủ đề tự chọn trong khuôn khổ đề bài
Nhóm nhỏ thì chọn lát cắt nhỏ, và phải có khảo sát nỗi đau thật — đây là chỗ ăn điểm nặng nhất
Bắt đầu từ đâu?
Đọc 01-challenge-brief.md để hiểu khung chung và 5 tiêu chí, rồi tracks/README.md để chọn track và đề.
Mở 02-guide.md — hướng dẫn từng giai đoạn, đứng ở đâu đọc mục đó.
Viết spec theo 03-ai-spec-template.md — deliverable trung tâm của cả sự kiện.
Đọc 04-rubric.md ngay từ đầu — biết trước bài được chấm theo tiêu chí nào.
File / thư mục	Nội dung
01-challenge-brief.md	Đề bài: bảng 5 track · lát cắt · ràng buộc chung · 5 tiêu chí nghiệm thu
02-guide.md	Hướng dẫn 5 giai đoạn: khám phá → spec → build → đo & validate → demo
03-ai-spec-template.md	Template AI Spec (nộp tại hạn chốt spec — xem Lịch)
04-rubric.md	Rubric 100 điểm (25 nộp checkpoint + 67 chấm bài + 8 điểm R6) + checklist xác minh 6 mốc
examples/	Ví dụ bài nộp của khoá trước (đã ẩn tên): canvas-cp1.md — mẫu trống Canvas 7 dòng + 3 ví dụ đạt (track A, A/D, B)
tracks/	5 track, mỗi đề cùng một khung mục: A VLearn Tutor · B Trợ lý Discord · C Lesson Studio · D Học tập thích ứng & tương tác · E Làn mở (trong phạm vi AI20k) — bắt đầu từ tracks/README.md
data/	Dữ liệu thật đã ẩn danh: vlearn-pack/ (chatlog VLearn tutor + 6 transcript bài giảng + 2 bộ slide bản hackathon) và discord-pack/ (tin nhắn Discord khoá 4 + bản tin bot) — dùng để tìm bằng chứng và xây golden set. Đọc data/README.md trước
further-reading/	Tài liệu tham khảo có tóm lược tiếng Việt: Mom Test (phỏng vấn), PAIR Guidebook (Google, 6 chương), HAX Toolkit (Microsoft, 18 nguyên tắc), JTBD Playbook + worksheet — bắt đầu từ further-reading/README.md
Lịch — 6 checkpoint (ca 3B · 39 giờ)
Mốc	Cần hoàn thành	Hạn (ca 3B)
—	Khai mạc 17:30 · phát đề 18:00	17/9
CP1	Canvas 7 dòng (02-guide.md §1.5) + đội trưởng + link repo GitHub công khai	19:30 · 17/9
CP2	Cho thấy luồng hoạt động — bấm thử được, hoặc sơ đồ luồng	21:00 · 17/9
CP3	Video thao tác 30 giây + số đo (thử bao nhiêu, đúng bao nhiêu)	16:00 · 18/9
CP4	Chốt spec.md — khoá chuẩn "đạt" · tự khai phần chưa xong	21:00 · 18/9
CP5	Slide PDF + video demo dự phòng cho buổi pitch — nộp cuối	22:30 · 18/9
CP6	Thuyết trình · không nộp thêm	09:00 · 19/9
CP1 đến CP5 mỗi mốc 5 điểm. Nộp đúng hạn được đủ, nộp muộn là 0 điểm mốc đó — không bù được bằng mốc khác.

Làm bài lúc nào
Thời gian tự làm	Ngoài giờ học, và trong buổi LEC ngày 18/9
Coach hỗ trợ	Trên lớp và trên Discord
Buổi LAB 19/9 · 09:00–13:00	Đây là vòng thi, không phải giờ làm bài
Hai phòng cùng ca dùng chung lịch mốc. Năm link form phát đủ từ đầu — xong mốc nào nộp mốc đó, không phải chờ.

Giải thích từng mốc
CP1 · Chốt Canvas + repo
Để làm gì: chốt rõ làm cho ai và giải vấn đề gì trước khi bắt tay vào code. Bỏ qua bước này thì hay gặp cảnh làm xong mới nhận ra không ai cần đến.

Nộp:

Canvas điền đủ 7 dòng theo scaffold trong 02-guide.md §1.5 (track + đề · job executor · pain · bằng chứng đầu · lát cắt 1 câu · automation + willing users · phân công) — mẫu trống + ví dụ: examples/canvas-cp1.md
Họ tên và mã học viên của đội trưởng
Link repo GitHub đã để công khai
Khai báo willing user — người sẵn sàng cho nhóm thử sản phẩm ở CP5. Cần ít nhất 2 người, khai từ đây
Khai willing user ngay từ CP1, đừng để đến CP5. Khối R6 ở CP5 yêu cầu có ít nhất 2 willing user đã khai ở mốc này. Đến lúc cần mới đi tìm người thì không kịp.

CP2 · Cho thấy luồng hoạt động
Để làm gì: nhìn được cả luồng từ đầu đến cuối — người dùng bấm gì trước, thấy gì sau, kết thúc ở đâu. Vẽ ra giấy thì phát hiện chỗ hổng trong mười phút; code xong mới thấy thì mất cả buổi sửa.

Nộp một trong ba thứ, thứ nào cũng được:

Bản mock bấm được — Figma, trang tĩnh, Canva, bất cứ thứ gì click qua lại được
Sơ đồ luồng vẽ tay hay vẽ máy, miễn thấy rõ các bước
Video quay màn hình đi hết một lượt
Chưa cần AI chạy thật — cái đó để CP3. Mốc này để nhẹ, chỉ cần cho thấy nhóm đang đi hướng nào.

CP3 · Video thao tác + số đo
Để làm gì: biết sản phẩm của mình đang đúng đến đâu. Có con số thì mới biết nên sửa chỗ nào tiếp, và lúc pitch cũng có cái để nói thay vì nói suông.

Nộp hai thứ:

1 · Video thao tác — 30 giây, quay màn hình. Bấm thật trên sản phẩm, thấy AI trả kết quả thật. Không cần dựng, không cần lồng tiếng.

2 · Số đo — thử bao nhiêu lần, đúng được bao nhiêu.

Đây là con số cho biết sản phẩm tốt đến đâu. Cách làm:

1. Chuẩn bị một bộ câu thử  — ví dụ 20 câu hỏi người dùng hay hỏi
2. Cho sản phẩm chạy hết 20 câu đó
3. Đếm bao nhiêu câu ra kết quả đạt chuẩn nhóm tự đặt
Chưa đạt	Đạt
"Sản phẩm chạy tốt"	"Thử 21 câu, 13 câu trả đúng có dẫn nguồn, 8 câu sai hoặc bịa"
"Độ chính xác cao"	"Thử 30 file, 24 file tóm tắt đúng ý chính, 6 file bỏ sót"
Số xấu vẫn được đủ điểm — miễn là số thật. 13 trên 21 mà phân tích được vì sao 8 câu kia sai thì ăn điểm cao hơn "chạy tốt" không có gì chứng minh.

CP4 · Chốt spec.md
Để làm gì: chốt "thế nào là đạt" trước khi biết kết quả. Đặt chuẩn sau khi đã thấy kết quả thì con số không nói lên điều gì — và người nghe cũng biết vậy.

Nộp:

Link spec.md đã chốt — trong đó nhóm tự chốt "thế nào là đạt" cho sản phẩm mình
Tự khai phần nào chưa làm xong
Sau 21:00 hôm đó không sửa chuẩn "đạt" được nữa.

Khai thiếu không bị trừ điểm. Giấu mới bị.

CP5 · Slide + video dự phòng
Để làm gì: đảm bảo buổi pitch chạy được dù mạng hỏng hay máy chết. Đây cũng là hạn nộp cuối — sau mốc này không nộp thêm gì.

Nộp:

Slide 6 trang, xuất ra PDF theo 02-guide.md §5.1. Nộp PDF chứ không nộp link — link hay hỏng quyền đúng lúc cần
Video demo dự phòng — quay sẵn phần demo. Nếu hôm pitch mạng chết thì BTC chiếu video này và không trừ điểm
CP3 và CP5 là hai video khác nhau: CP3 chứng minh sản phẩm chạy — quay ngắn, quay thô cũng được. CP5 là bản sao lưu để buổi pitch không chết vì mạng — quay đúng phần định demo trên sân khấu.

CP6 · Thuyết trình
Không nộp gì. Ngày này chỉ để trình bày.

Giám khảo có thể hỏi bất kỳ thành viên nào về phần có tên người đó trong bảng phân công.

Link nộp
Mốc	Form nộp
CP1	(cập nhật lúc khai mạc)
CP2	(cập nhật lúc khai mạc)
CP3	(cập nhật lúc khai mạc)
CP4	(cập nhật lúc khai mạc)
CP5	(cập nhật lúc khai mạc)
Đội trưởng nộp form thay cả nhóm — một phiếu cho cả nhóm ở mỗi mốc, không phải mỗi thành viên tự nộp. 25 điểm nộp là điểm chung của nhóm: mọi thành viên cùng được hoặc cùng mất.

⚠️ Cả 5 mốc phải nộp bằng cùng một mã học viên của đội trưởng. BTC ghép 5 phiếu của nhóm lại với nhau dựa trên mã học viên người nộp. Mốc này người A nộp, mốc kia người B nộp thì hệ thống hiểu là hai nhóm khác nhau, và nhóm mất điểm ở những mốc lệch.

Chọn đội trưởng là người chắc chắn có mặt và theo được cả năm mốc. Nếu bất khả kháng phải đổi người nộp, báo coach ngay trong buổi.

Link được công bố tại khai mạc, ghim trên Discord và đăng trên VLearn — hai nơi, cùng một bộ link.

Thể thức thi
2 ca × 2 phòng = 4 cuộc thi độc lập, chấm và trao giải riêng từng phòng; mỗi phòng một tổ giám khảo. Không thi liên phòng, liên khoá.
E403 (~230 người): 6 cụm thi, mỗi nhóm 6 phút ở vòng cụm → 6 đội vào chung kết phòng → Top 3.
E402 (~120 người): 5 cụm thi, mỗi nhóm 7 phút ở vòng cụm → 5 đội vào chung kết phòng → Top 2.
Giám khảo có thể hỏi bất kỳ thành viên — ai cũng phải hiểu bài (vibe-coding rule).
Số nhóm mỗi cụm là ước tính; thể lệ chi tiết vòng cụm và chung kết công bố lúc khai mạc.
Vòng cụm — game đầu tư
Mỗi đội có 100 điểm vốn, đội trưởng đại diện xem và đầu tư. Đội nhận nhiều vốn nhất cụm đi tiếp vào chung kết phòng.

Hai luật: không được đầu tư vào đội mình · tổng phải đúng 100, thừa hoặc thiếu là phiếu không được tính.

Chia cho mấy đội là tuỳ — dồn hết vào một đội cũng được. Mẹo: trong lúc xem thì ghi số dự định ra giấy nháp, xem xong cả cụm mới cân đối lại rồi điền form.

Chung kết phòng
Sau khi chốt danh sách, các đội có 10–15 phút chuẩn bị. Thứ tự trình bày quay ngẫu nhiên tại chỗ.

Mỗi đội 10 phút: 7 phút trình bày + 3 phút hỏi đáp.

Cả phòng bình chọn — mỗi người đánh giá từng đội một cách độc lập, không giới hạn số đội được bầu.

Giải thưởng
Giải theo phòng — mỗi lớp 5 đội, hai lớp 10 đội:

Lớp	E403	E402	Tổng
3A	Top 3	Top 2	5 đội
3B	Top 3	Top 2	5 đội
Điểm thưởng cộng vào bài lab ngày 5 và ngày 6, cho mỗi thành viên:

Ai được	Cộng
Giải Nhất của phòng	+10
Giải Nhì của phòng	+5
Giải Ba — chỉ E403	+3
Vào chung kết nhưng không có giải	+2
Đội đầu tư nhiều điểm nhất và sớm nhất vào đội giải Nhất	+2
Mỗi phòng E403 có 7 đội được cộng điểm, E402 có 6 đội — không chỉ riêng đội vô địch.

Dòng cuối chỉ có một đội mỗi phòng: xét điểm đầu tư cao nhất trước, bằng nhau thì lấy đội nộp phiếu sớm hơn theo dấu thời gian của form.

Giải theo track — 4 giải, chấm chung cả hai lớp:

Track A · VLearn Tutor và Track D · Học tập thích ứng & tương tác: 2 giải, do team VLearn chọn.
Track C · Lesson Studio: 2 giải, do team Studio chọn.
Hai team chấm ngay tại buổi trình bày. Một đội có thể vừa vào Top phòng vừa nhận giải track. Phần thưởng cụ thể sẽ được công bố sau.

Mỗi mốc cần show gì và được xác minh thế nào: xem bảng trong 04-rubric.md.

Nộp bài
Tạo repo mới — không fork repo đề bài
Nhóm tạo một repo hoàn toàn mới và trống. Không fork, không clone repo này rồi push lên.

Lý do: fork mang theo cả thư mục data/, mà repo nộp bài bắt buộc phải công khai — nghĩa là dữ liệu thật của khoá học sẽ lên mạng. Vi phạm thẳng điều 2 và điều 3 của quy định bảo mật bên dưới.

Nhóm chỉ cần lấy đúng một file từ repo này: 03-ai-spec-template.md, copy vào repo mình và đặt tên spec.md. Mọi thứ còn lại là tài liệu đọc, mở tại đây là đủ.

Cách đặt tên repo
K4-<mã lớp>-<phòng>-<tên nhóm>
Ví dụ	Của nhóm nào
K4-3B-E403-ChamCongAI	Lớp 3B · phòng E403 · nhóm ChamCongAI
K4-3B-E402-DiscordBuddy	Lớp 3B · phòng E402 · nhóm DiscordBuddy
Ba phần đầu bắt buộc đúng. Phòng là phòng nhóm đang ngồi thi.

Tên nhóm ở cuối đặt gì cũng được — viết liền, không dấu, không khoảng trắng.

Repo phải để công khai. Thử mở bằng cửa sổ ẩn danh — mở được thì mới đúng. Để riêng tư là giám khảo không chấm được bài.

Cấu trúc repo
Spec chốt tại hạn chốt spec (xem Lịch); bản hoàn chỉnh trước CP6.

repo/
├── README.md          ← copy file này, điền bảng thành viên ở đầu
├── spec.md            ← AI Spec theo 03-ai-spec-template.md
├── demo-slides.pdf    ← slide 6 trang theo 02-guide.md §5.1
├── codebase/          ← prototype (ghi rõ phần nào mock)
├── eval/              ← golden set + bảng kết quả các lượt chạy
├── validation/        ← nhật ký cho người ngoài dùng thử (R6 — không làm thì trần điểm 92)
└── reflection/        ← mỗi người 1 file
README.md của nhóm
Copy nguyên file README này về repo của mình, rồi điền bảng thành viên ở đầu file. Không cần viết thêm gì khác.

Mã học viên phải đúng — đây là căn cứ đối chiếu điểm.

Chấm điểm
Tổng 100 điểm = 25 điểm nộp checkpoint + 67 điểm chấm bài nộp + 8 điểm R6 (cho người ngoài dùng thử). Chi tiết từng ý điểm: 04-rubric.md.

25 điểm nộp — mỗi checkpoint 5 điểm (CP1-CP5): nộp đúng hạn → 5 điểm · nộp muộn → 0 điểm cho mốc đó. Đội trưởng nộp thay cả nhóm — đây là điểm chung của nhóm, không phải điểm cá nhân.

67 điểm chấm + 8 điểm R6 — trên file trong repo, mỗi con điểm trỏ về một chỗ:

Khối	Điểm	Chấm trên file nào
R1 · Bằng chứng & impact	15	spec.md §1-§2 + log khảo sát
R2 · Lát cắt & thiết kế	15	spec.md §4
R3 · Chỗ khó & kịch bản rủi ro	11	spec.md §5-§6
R4 · Kiểm thử	15	spec.md §7 + eval/
R5 · Prototype chạy được	8	codebase/ + demo
R6 · Cho người ngoài dùng thử	8	validation/
R7 · Quy trình & repo	3	cấu trúc repo
Ba khối nặng nhất — R1, R2, R4 — đều nằm trong spec.md. Viết spec tử tế là ăn 45 trên 67 điểm.

R6 · Cho người ngoài dùng thử — 8 điểm
Không làm thì trần điểm là 92. Vì 25 + 67 = 92, cộng R6 mới đủ 100.

Làm ở CP5, lưu trong thư mục validation/.

Người dùng chê cũng được tính đủ điểm. Mục đích là xem giải pháp có ăn thua không — ra kết quả nào cũng ghi nhận, miễn là bằng chứng thật. Phát hiện sản phẩm chưa ổn rồi sửa còn dễ ăn điểm hơn, vì có chỗ cụ thể để nói.

Hai ví dụ thật từ kỳ trước:

Nhóm MeaterBeat phát hiện học viên non-IT lúng túng không biết bấm nút nào, AI trả lời chậm — tức là giải pháp chưa ổn. Họ thêm tooltip hướng dẫn, thêm loading spinner, và giải trình phần độ trễ không sửa được vì phụ thuộc API. Đủ điểm.

Nhóm VLearn Recall phát hiện đúng như giả định: người ta nhớ chủ đề nhưng không nhớ nằm ở slide hay bài giảng — tức là giải pháp đi đúng hướng. Họ giữ nguyên thiết kế source-first và bổ sung thêm câu thử. Cũng đủ điểm.

Phải có đủ bốn thứ:

5 người ngoài nhóm dùng thử	trong đó 2 người đã khai từ CP1
Quote nguyên văn	chép đúng lời họ nói, kể cả viết sai chính tả
Bảng nhật ký	ai thử · giao task gì · kẹt ở đâu · quote · quyết định
Ít nhất 1 thay đổi	ghi vào §9 Changelog trong spec.md. Giữ nguyên thì nói rõ vì sao
Cuối bảng viết 4 dòng: chủ đề lặp nhiều nhất · sẽ sửa gì trước demo · giữ nguyên gì và vì sao · gì để dành sau.

Quote thế nào mới ăn điểm:

Chưa đạt	Đạt
"Demo này ok rồi đấy"	"Mình muốn tìm thông tin về code cho ReAct"
Bên trái là lời khen xã giao. Bên phải là lời người dùng nói lúc đang cố làm việc — nhìn vào biết ngay họ vướng ở đâu.

Muốn có quote như vậy: giao task rồi ngồi im xem họ làm, đừng hỏi "sản phẩm này hay không".

Ba điều nên biết trước khi làm:

Điểm dựa trên chuỗi quyết định và bằng chứng, không dựa trên mức độ hoành tráng của sản phẩm.
Kết quả đo ghi nhận trung thực — kể cả khi không đạt mục tiêu nhóm tự đặt — vẫn được tính đủ điểm. Số liệu bị chỉnh sửa hoặc che giấu sẽ không được tính.
Reflection cá nhân chấm riêng theo rubric của khoá. Điểm vòng demo, chấm chéo trong cụm và thưởng thêm (nếu có) theo thể lệ công bố lúc khai mạc.
Luật chung
Prototype có 3 mức Sketch / Mock / Working — mức nào cũng bắt buộc ≥1 lời gọi AI chạy thật. Đây là thứ phải thấy được trong video thao tác ở CP3.
Vibe-coding rule: dùng AI để build thoải mái, nhưng không giải thích được phần có tên mình thì phần đó 0 điểm (giám khảo hỏi bất kỳ thành viên khi thuyết trình).
Quality bar chốt tại hạn chốt spec (21:00 18/9, tại CP4) và giữ nguyên sau đó.
Chỉ dùng dữ liệu trong data/ hoặc dữ liệu giả tự sinh — không dùng dữ liệu thật của người thật. Không commit API key.
Tuân thủ quy định bảo mật dữ liệu bên dưới — đây là điều kiện để được cấp data.
Bảo mật dữ liệu được cung cấp
Dữ liệu trong data/ là dữ liệu thật của khoá học (đã ẩn danh), cấp riêng cho hackathon này. Khi nhận data, nhóm cam kết:

Chỉ dùng trong phạm vi hackathon — cho việc tìm bằng chứng, xây golden set và build prototype. Không dùng cho mục đích khác.
Không chia sẻ ra ngoài khoá học — không đăng lên mạng xã hội, không gửi cho người ngoài, không đưa vào bất kỳ dataset hay repo công khai nào.
Không commit data pack vào repo nộp bài — repo nhóm chỉ chứa trích dẫn ngắn để minh hoạ (vài dòng); golden set trích từ data ghi rõ mã đoạn/mã hội thoại thay vì dán nguyên văn dài.
Cẩn trọng khi đưa data vào công cụ ngoài — chỉ đưa phần tối thiểu cần cho việc đang làm; lưu ý API/công cụ free tier có thể dùng dữ liệu để huấn luyện (xem 02-guide.md §3.4).
Không cố suy ngược danh tính từ dữ liệu đã ẩn danh (S####, T#####, D####, [HV], [học viên]). Riêng discord-pack/: người trong đó là bạn cùng khoá — tuyệt đối không đoán/hỏi "tin này của ai"; trích dẫn tối đa 2 câu mỗi ví dụ (xem data/discord-pack/README.md).
Sau sự kiện, xoá các bản sao data pack khỏi máy cá nhân và các công cụ đã upload nếu ban tổ chức yêu cầu.
Vi phạm được xử lý theo quy định của khoá và có thể ảnh hưởng trực tiếp đến điểm của nhóm.

---

## Luồng "Tải slide PDF lên → AI sinh file JSON checkpoint → UI nạp từ file đó"

**Mỗi file slide PDF = một bài giảng = một file JSON checkpoint riêng.**

1. Chạy `run_server.bat`, mở **http://localhost:8000** (mở thẳng `index.html` sẽ không gọi được API).
2. Sidebar trái, mục **Nguồn slide PDF** → bấm **⬆ Tải slide PDF lên** hoặc kéo thả file PDF vào ô đó.
   File được gửi lên `POST /api/slides/upload` (base64 trong JSON, không cần `python-multipart`), lưu vào
   `backend/data/vlearn-pack/slides/`; trùng tên thì tự thêm hậu tố `-2`, `-3`… chứ không đè.
3. Server lập tức cho Agent 1 (`backend/lesson_ingest.py`) đọc file PDF đó bằng LLM ở luồng nền và **ghi ra
   `backend/data/lessons/<tên-slide>.json`** — chứa toàn bộ checkpoint: `rubric_points` để chấm, câu hỏi mở đầu
   của bạn học, `correction`, và `pdf_page` (trang slide giảng kỹ nhất khái niệm đó). Mất khoảng 30–90 giây.
4. Giao diện hiện tiến trình ("🤖 AI đang đọc slide...") và tự hỏi lại server mỗi 4 giây. Xong là **checkpoint
   được nạp lên từ chính file JSON vừa sinh**: khung chat liệt kê các checkpoint kèm số trang, bạn học AI hỏi
   câu đầu tiên, khung slide tự cuộn tới đúng trang và loé sáng.
5. Nút **↻** cạnh mỗi bài chỉ dùng khi muốn AI **đọc lại** slide (ghi đè đúng file JSON đó).

Dữ liệu nằm ở đâu:

```
backend/data/
├── vlearn-pack/slides/<file>.pdf     ← slide gốc (upload vào đây)
├── lessons/<file>.json               ← checkpoint do LLM sinh, UI nạp từ đây
└── lessons.json                      ← kho cũ, chỉ còn các bài viết tay không gắn slide
```

Server cũng tự quét thư mục slides lúc khởi động: file PDF nào chưa có JSON checkpoint thì phân tích luôn,
nên copy tay file PDF vào thư mục đó cũng có tác dụng tương tự upload.

### Ngân hàng câu hỏi & cách hỏi dẫn dắt

Sau khi đọc slide sinh checkpoint, mỗi checkpoint được gọi LLM **thêm một lượt** (chỉ text, không gửi lại PDF)
để sinh **10–15 câu hỏi** chia 3 mức độ, lưu trong cùng file JSON ở trường `question_bank`:

| Mức | Hỏi gì |
|---|---|
| `nhan_biet` | Khái niệm, định nghĩa, thành phần — chỉ cần nhớ và nói ra |
| `thong_hieu` | Vì sao, cơ chế, so sánh, bỏ đi thì sao |
| `van_dung` | Đặt tình huống cụ thể, bắt áp dụng khái niệm để giải thích |

Mỗi câu gắn `targets` = các `rubric_points` mà nó nhắm tới. Nhờ vậy vòng hội thoại chạy như sau:

1. Mở checkpoint bằng câu **dễ nhất** trong ngân hàng.
2. Mỗi câu trả lời được chấm trên **toàn bộ rubric**, ý nào đạt thì **cộng dồn** vào phiên
   (trả lời đúng nhưng chưa đủ thì phần đã đúng được giữ lại, không phải nói lại từ đầu).
3. Còn thiếu ý nào → chọn câu hỏi **nhắm đúng ý đó**, độ khó tăng dần mỗi khi học viên vừa tiến bộ.
   Bạn học AI ghi nhận ngắn phần vừa đúng rồi hỏi tiếp — đó là phần "dẫn dắt".
4. Qua checkpoint khi **phủ hết rubric**, hoặc khi đã hỏi hết **tối đa 5 câu** (`MAX_QUESTIONS_PER_CP`
   trong `backend/agent.py`) thì chốt điểm: ≥80% coi là đạt, dưới ngưỡng thì đưa đáp án chuẩn và đánh dấu
   "cần học lại".

Giao diện hiện dải trạng thái ngay dưới timeline: checkpoint nào, câu thứ mấy trên tối đa, mức độ, và đã nắm
bao nhiêu ý trên tổng số.

Bài học sinh từ bản cũ (chưa có `question_bank`) sẽ được server **tự bổ sung câu hỏi** ở lần khởi động kế tiếp,
không cần đọc lại file PDF. Checkpoint nào không sinh được câu hỏi thì tự rơi về lối hỏi cũ (một câu mở đầu,
tối đa 3 lượt thử).

### Chữ chảy dần & gợi ý trước khi giải thích

**Streaming**: FE gọi `POST /api/chat/stream` (SSE). Server đẩy `evaluation` ngay khi Giáo sư AI chấm xong —
dải tiến trình và dòng gợi ý hiện lập tức — rồi stream lời thoại của bạn học theo từng đoạn (`delta`), khép lại
bằng `done`. Provider nào không có hàm `stream` (hiện chỉ OpenAI có) thì tự rơi về trả nguyên cục; `/api/chat`
thường vẫn giữ nguyên làm đường dự phòng khi SSE lỗi.

**Né tránh / không biết**: Giáo sư AI phân biệt ba kiểu — trả lời sai (`NEEDS_IMPROVEMENT`), **né câu hỏi**
(`EVADED`: lảng sang chuyện khác, hỏi ngược, nói vài chữ vô nghĩa) và **bỏ cuộc** (`GAVE_UP`: "chịu", "không
biết", "cho đáp án"). Với hai kiểu sau, hệ thống **không đưa đáp án ngay** mà gợi ý tăng dần tối đa
`MAX_HINTS_BEFORE_REVEAL = 2` lần:

1. Lần 1 — hướng vào khái niệm còn thiếu kèm số trang slide để đọc lại.
2. Lần 2 — thu hẹp phạm vi: dùng `hint` của câu hỏi trong ngân hàng, hoặc liệt kê **tên** các ý còn thiếu.
   Tuyệt đối không đọc `criteria` của rubric ra — criteria viết theo kiểu "câu trả lời phải có X, Y, Z"
   nên nói ra là lộ nguyên đáp án.
3. Lần 3 — mới giải thích kiến thức chuẩn (`correction`), đánh dấu "cần học lại" và chuyển checkpoint.

**Ai được nói gì** — hai nhân vật tách bạch:

| Nhân vật | Vai | Được nói gì |
|---|---|---|
| **Feynman AI** (bạn học) | Người học giả vờ chưa hiểu, nhờ giảng lại | Chỉ hỏi, phản ứng, bàn giao cho trợ giảng khi bí. **Không bao giờ giảng kiến thức**, kể cả khi bị nài nỉ |
| **Giáo sư AI** | Trợ giảng đứng sau | Gợi ý và giải thích kiến thức chuẩn. Hiện thành bong bóng riêng (viền tím, nhãn "Giáo sư AI") |

Lượt nào do Giáo sư AI nói thì backend **không gọi LLM cho bạn học** — vừa đúng vai, vừa bớt một lượt gọi ở
đúng những lượt hay chậm nhất.

### API liên quan

| Endpoint | Việc |
|---|---|
| `POST /api/slides/upload` | `{filename, data_base64}` — nhận file PDF, lưu vào thư mục slides và xếp hàng cho AI đọc. Trả về ngay, không chờ LLM |
| `GET /api/slides` | Liệt kê slide + trạng thái `pending` / `running` / `ready` / `error`, tên file JSON checkpoint, và cờ `analyzing` |
| `POST /api/lessons/generate` | `{pdf_file, force: true}` — bắt AI đọc lại một slide đã có checkpoint |
| `GET /api/lessons?full=1` | Toàn bộ bài học (gộp các file JSON trong `data/lessons/` và kho cũ) |
| `POST /api/session/start` | `{session_id, lesson_id}` — FE gọi mỗi khi đổi bài để chấm đúng bộ checkpoint |

`pdf_page` do LLM trả về luôn được kiểm lại theo số trang thật của file PDF (dùng `pypdf`): thiếu → về trang 1,
vượt quá → ép về trang cuối, và báo rõ trong `warnings` để không bao giờ nhảy tới trang không tồn tại.
