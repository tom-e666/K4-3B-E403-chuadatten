# Trạng thái hiện tại của dự án Feynman AI

Cập nhật ngày 18/09/2026 trên nhánh `feature/luannt`, tại commit `75dfc21`.

Nội dung dưới đây được viết sau khi đối chiếu mã nguồn backend, giao diện người học, trang giảng viên, bộ kiểm thử và phần thay đổi giữa `origin/feature/luannt` với phiên bản hiện tại. Đây là trạng thái thực tế của prototype, không phải danh sách ý tưởng ban đầu.

## Tổng quan

Feynman AI đã có một luồng học hoàn chỉnh ở mức prototype. Người học có thể tải slide PDF lên, chờ AI chia bài thành các checkpoint, giải thích lại kiến thức bằng lời của mình và nhận câu hỏi tiếp theo dựa trên phần còn thiếu. Slide tự chuyển đến trang liên quan, kết quả được chấm theo rubric và cuối buổi có phần tổng kết để học lại checkpoint yếu.

Phần backend đang dùng FastAPI, lưu phiên học trong bộ nhớ và gọi một trong các provider Gemini, OpenAI hoặc OpenRouter. Frontend vẫn là một trang HTML lớn trong `FE/mock-cp2`, chưa được tách thành ứng dụng có hệ thống component hoặc build pipeline riêng.

Phiên bản hiện tại phù hợp để demo trên một máy hoặc cho một người dùng thử. Dự án chưa sẵn sàng để mở cho cả lớp dùng đồng thời vì chưa có tài khoản, phân quyền, lưu phiên bền vững và cơ chế cô lập dữ liệu giữa nhiều người học.

## Những feature mới đã được bổ sung

So với commit `28ed6e0` trên `origin/feature/luannt`, thay đổi mới nhất bổ sung cơ chế chống chép slide. Hệ thống lấy chữ ở đúng trang PDF của checkpoint, so các cụm sáu từ và cảnh báo khi mức trùng đạt ngưỡng. Câu trả lời bị nhận diện là chép sẽ chưa được tính điểm trong hai lần đầu; từ lần thứ ba hệ thống vẫn cho chấm để tránh làm người học mắc kẹt.

Cuối phiên học đã có thẻ tổng kết chi tiết thay cho phần báo điểm đơn giản trước đây. Thẻ hiển thị điểm tổng, trạng thái từng checkpoint, trang slide liên quan, các ý còn thiếu và gợi ý checkpoint nên học lại trước.

Người học có thể bấm “Học lại” ngay tại từng checkpoint. Backend có API đặt lại đúng checkpoint được chọn, frontend đưa người học trở về câu hỏi mở đầu và tự cuộn slide đến đúng trang thay vì bắt đầu lại toàn bộ bài.

Dự án đã có trang báo cáo dành cho giảng viên tại `/teacher`. Mỗi khi một checkpoint kết thúc, backend ghi một dòng JSONL vào `backend/data/progress`. Trang báo cáo tổng hợp số lượt làm, số phiên học, tỉ lệ đạt, điểm trung bình, số lần bỏ cuộc và các ý người học thường thiếu để chỉ ra phần nên giảng lại.

Timeline checkpoint đã được sửa để cuộn ngang khi bài có nhiều checkpoint. Mốc đang học được tự đưa vào vùng nhìn, tránh tình trạng tên checkpoint bị ép nhỏ hoặc nằm ngoài màn hình.

Frontend hiện gửi kèm `lesson_id` ở mỗi lượt chat. Sau khi server khởi động lại và mất phiên trong RAM, backend ít nhất có thể mở lại đúng bài học thay vì rơi về bài mặc định và chấm nhầm checkpoint của bài khác. Việc này chỉ sửa lỗi chọn sai bài, chưa khôi phục tiến độ đang học dở.

Bộ đánh giá mới đã được thêm cho dữ liệu checkpoint sinh tự động. `eval/build_auto_dataset.py` tạo các nhóm tình huống đúng, sai kiến thức, trả lời một phần, bỏ cuộc, né tránh và chép slide. `eval/run_eval_auto.py` chạy các tình huống đó qua đúng Evaluator đang dùng trong sản phẩm, thay vì chỉ dựa vào bộ từ khóa cứng của bài Transformer cũ.

Các nền tảng đã có từ phiên bản trước vẫn được giữ lại, gồm đọc slide PDF để sinh checkpoint, tạo ngân hàng 10 đến 15 câu hỏi theo ba mức độ, cộng dồn các ý đã trả lời đúng, hỏi tiếp đúng phần còn thiếu, giới hạn số câu cho mỗi checkpoint, hai cấp gợi ý trước khi đưa đáp án và tách vai giữa bạn học Feynman AI với Giáo sư AI.

Luồng hội thoại có hỗ trợ SSE. Kết quả đánh giá được gửi về trước, sau đó lời của bạn học mới hiển thị dần. OpenAI có luồng stream thật; các provider không hỗ trợ sẽ trả nội dung một lần nhưng vẫn giữ được chức năng chính.

## Những vấn đề còn tồn đọng

Vấn đề lớn nhất là hệ thống chưa nhận diện được từng người học. Frontend đang tạo `session_id` theo mẫu `vlearn_<lesson_id>`, vì vậy hai người học cùng một bài trên cùng server sẽ dùng chung phiên và có thể ghi đè tiến độ của nhau. Chỉ số “người học” trên trang giảng viên hiện thực chất là số `session_id`, chưa phải danh tính thật.

Toàn bộ trạng thái đang học được giữ trong biến `sessions` của tiến trình FastAPI. Khi server restart, checkpoint hiện tại, các ý đã phủ, số câu đã hỏi, lịch sử hội thoại và báo cáo tổng kết của phiên đều mất. Nhật ký JSONL chỉ ghi checkpoint đã kết thúc nên không thể dùng để tiếp tục một phiên đang dở.

Trang `/teacher` và các API báo cáo chưa có đăng nhập hoặc phân quyền. Bất kỳ ai truy cập được server đều có thể xem dữ liệu tổng hợp. API tải slide, tạo lại lesson và đọc báo cáo cũng chưa có lớp xác thực, nên chỉ nên chạy trong môi trường demo tin cậy.

Frontend đưa nhiều dữ liệu động vào `innerHTML`, trong khi hàm `formatMarkdown` không escape HTML trước khi render. Nội dung do LLM sinh, tên bài học, tiêu đề checkpoint hoặc dữ liệu được tạo từ slide có thể chứa HTML và trở thành điểm XSS. Hàm `escapeHtml` đã tồn tại nhưng chưa được áp dụng nhất quán.

Kết quả chất lượng của bộ eval mới chưa được chạy và chốt bằng số. File `golden_auto.json` đã có dữ liệu, nhưng chưa có `eval_report_auto.json` được lưu trong dự án. Vì vậy chưa thể khẳng định luồng checkpoint tự sinh đạt quality bar nào.

Bộ eval mới cũng có nguy cơ tự xác nhận chính mình. Nhiều case đúng và sai được lấy từ `sample_correct`, `sample_wrong` và rubric do cùng quá trình sinh lesson tạo ra. Kết quả cao trên bộ này chưa chứng minh hệ thống chấm tốt câu trả lời thật của học viên. Cần thêm một tập dữ liệu được con người gán nhãn độc lập, có câu diễn đạt tự nhiên và lỗi hiểu sai không xuất phát từ chính lesson JSON.

Bộ `eval/run_eval.py` cũ đạt 20/20 nhưng chỉ phủ ba checkpoint Transformer viết tay và dùng logic từ khóa. Con số này không đại diện cho chất lượng hiện tại. File `eval/test_server_e2e.py` cũng đang giả định cố định có ba lesson và gọi chat mà không luôn truyền `lesson_id`, nên cần cập nhật trước khi xem đây là kiểm thử hồi quy đáng tin cậy.

Dữ liệu lesson sinh ra trong `backend/data/lessons` đang bị `.gitignore` bỏ qua theo quy định bảo mật dữ liệu hackathon. Đây là lựa chọn đúng đối với slide thật, nhưng làm cho một bản clone mới không có sẵn checkpoint và phải gọi LLM để tạo lại. Cách xử lý phù hợp là cung cấp một bộ fixture đã ẩn danh hoặc dữ liệu tổng hợp dùng cho demo và test, không phải đưa dữ liệu thật trở lại Git.

Việc ghi file lesson chưa có cơ chế atomic write. `save_lesson` ghi thẳng vào file đích; nếu tiến trình dừng giữa lúc ghi, file JSON có thể bị thiếu. Nhật ký tiến độ cũng được append trực tiếp mà không có khóa theo file, vì vậy nhiều request đồng thời có thể làm dữ liệu báo cáo không ổn định.

Độ chính xác nội dung vẫn phụ thuộc mạnh vào lesson do LLM sinh. Hệ thống chỉ kiểm tra `pdf_page` có nằm trong số trang thật, chưa xác minh trang đó có thực sự giảng đúng khái niệm. Nếu rubric sai, thiếu hoặc mơ hồ thì Evaluator vẫn chấm theo rubric sai đó.

Slide scan hoặc slide chỉ chứa ảnh chưa có OCR nên không tạo được lesson đáng tin cậy. Đường fallback bằng `pypdf` chỉ đọc được lớp text có sẵn trong PDF.

Cơ chế chống chép hiện chỉ so với đúng trang được gắn cho checkpoint, bỏ qua câu dưới 25 từ và chủ yếu bắt sao chép gần nguyên văn. Chép từ trang khác, lấy từ nguồn ngoài hoặc dùng AI để diễn đạt lại vẫn có thể vượt qua. Sau hai cảnh báo, hệ thống chủ động cho chấm bình thường, nên đây là biện pháp hỗ trợ hành vi học chứ không phải cơ chế chống gian lận hoàn chỉnh.

Phần tải file nhận PDF dưới dạng base64 trong JSON và chỉ kiểm giới hạn sau khi đã decode toàn bộ dữ liệu vào bộ nhớ. Một request rất lớn vẫn có thể làm tăng mạnh lượng RAM trước khi bị từ chối. Luồng upload cũng chưa có giới hạn tốc độ hoặc quota theo người dùng.

Streaming hiện không đồng nhất giữa các provider. Phần giao diện vẫn hoạt động khi không stream, nhưng trải nghiệm và thời gian phản hồi thực tế sẽ khác nhau tùy provider. Dự án còn phụ thuộc vào `pypdf`, phiên bản trình duyệt đủ mới cho PDF.js và API bên ngoài; thiếu một trong các thành phần này sẽ làm giảm đáng kể chức năng.

Tài liệu test tay có chỗ chưa đồng bộ với code. Case D7 vẫn ghi rằng chép nguyên slide sẽ được tính đạt, trong khi nhóm case P1 đến P3 và code hiện tại đã có bộ chặn chép. Các mô tả lỗi restart server cũng còn lẫn giữa hành vi cũ và hành vi mới.

Giao diện hiện còn nút video mô phỏng chỉ mở hộp thoại, mục bài tập thực hành chưa có luồng thật và chưa tích hợp với VLearn. Đây vẫn là prototype dựng theo giao diện tham chiếu, không phải một module đã cắm vào hệ thống của trường.

## Những feature chưa có nhưng nên làm tiếp

Cần thêm tài khoản hoặc ít nhất một mã người học riêng cho mỗi phiên, sau đó tạo `session_id` không trùng và gắn mọi bản ghi tiến độ với danh tính đó. Đây là điều kiện đầu tiên để cho nhiều người dùng cùng lúc và để báo cáo lớp có ý nghĩa.

Cần lưu session xuống cơ sở dữ liệu hoặc kho bền vững. Dữ liệu nên bao gồm checkpoint hiện tại, rubric đã phủ, số câu đã dùng, số lần gợi ý, kết quả từng checkpoint và lịch sử cần thiết để tiếp tục sau khi server restart.

Cần có đăng nhập và phân quyền cho giảng viên, đồng thời giới hạn API upload, tạo lại lesson và báo cáo. Khi triển khai thật, dữ liệu tiến độ nên có chính sách lưu giữ, ẩn danh và xóa rõ ràng.

Cần bổ sung spaced repetition. Những checkpoint có điểm thấp hoặc phải xem đáp án nên được lên lịch hỏi lại sau một khoảng thời gian, thay vì chỉ xuất hiện trong thẻ tổng kết cuối phiên.

Cần khai thác transcript video để tạo checkpoint từ cả slide lẫn lời giảng, đồng thời gắn checkpoint với mốc thời gian trong video. Hiện dữ liệu lesson cũ có trường transcript nhưng luồng ingest mới chủ yếu dựa vào PDF.

Cần thêm trả lời bằng giọng nói nếu muốn bám sát phương pháp Feynman. Người học nên có thể nói, xem lại bản chép lời và sửa transcript trước khi gửi chấm.

Cần thêm OCR cho slide dạng ảnh, sau đó hiển thị cảnh báo độ tin cậy thấp để người dùng biết nội dung nào cần kiểm tra thủ công.

Cần có chức năng xuất báo cáo CSV, Excel hoặc PDF cho giảng viên. Báo cáo nên hỗ trợ lọc theo bài học, người học, thời gian và checkpoint thay vì chỉ hiển thị bảng tổng hợp hiện tại.

Cần tách frontend thành các module nhỏ hơn, bổ sung lớp sanitize HTML và kiểm thử trình duyệt. File `index.html` hiện chứa cả dữ liệu mock, style, state và logic API nên việc sửa một phần có nguy cơ gây hồi quy ở phần khác.

## Thứ tự ưu tiên đề xuất

Ưu tiên đầu tiên là tách phiên theo người học, lưu trạng thái bền vững và thêm phân quyền cho trang giảng viên. Ba việc này giải quyết rủi ro lớn nhất khi chuyển từ demo một máy sang dùng thật.

Ưu tiên tiếp theo là sửa toàn bộ điểm render HTML không an toàn, chuyển ghi JSON sang atomic write và bảo vệ luồng append progress khi có nhiều request đồng thời.

Sau đó cần xây một golden set được gán nhãn thủ công, chạy `run_eval_auto.py`, ghi lại kết quả theo từng nhóm case và phân tích lỗi thay vì chỉ báo một con số tổng.

Cuối cùng mới nên mở rộng trải nghiệm bằng spaced repetition, transcript video, giọng nói, OCR và xuất báo cáo. Các feature này có giá trị, nhưng không nên đi trước nền tảng đa người dùng, độ bền dữ liệu và đo chất lượng.

## Trạng thái kiểm tra trong lần cập nhật này

Mã nguồn đã được đối chiếu bằng lịch sử Git, diff của commit mới nhất và đọc trực tiếp các luồng chính trong backend, frontend và eval.

Các lệnh kiểm tra Python chưa chạy được trên máy hiện tại vì Windows Python Launcher tồn tại nhưng không tìm thấy bản Python đã cài. Do đó chưa có kết quả mới cho `compileall`, `eval/check_lessons.py`, `eval/test_server_e2e.py` hoặc `eval/run_eval_auto.py`. Phần status này không coi các test đó là đã đạt.
