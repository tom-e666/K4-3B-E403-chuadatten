agent 1: tạo ra checkpoint, tóm tắt kiến thức
agent 2: AI Ngu (phản hồi, có thể hỏi các câu hỏi mở rộng)
agent 3: AI professional (So sánh độ khớp của câu trả lời với đáp án, trả lời luôn nếu phát hiện người dùng nhập vào là "ko biết", "chịu thua", ...)




xây dựng bộ test case

xây dựng version v0 - v3, phân tích vấn đề, edit prompt để cải thiện version

-> demo video: 

Video sẽ có 1 đoạn ngắn khoảng 30s (tùy đoạn nào)

Video chứa 



CP3:

Link video thao tác — 30 giây
vd: youtube, drive mở quyền public
*

Đã thử bao nhiêu lần?

Trong đó bao nhiêu lần đạt?
*

Chuẩn "đạt" của nhóm là gì?
*


Những lần chưa đạt sai ở đâu?
*



luồng :

C:\AI\vinai20k\K4-3B-E403-chuadatten\data\d1-slide-hackathon.pdf

file gốc

agent đọc pdf, xuất thành các lession point.
có system prompt riêng.
Xây các test case bằng cách random một số trang


agent ngu: đặt câu hỏi:
có system prompt riêng, xây testcase bằng handmade question

agent gs: phản hồi, xây testcase bằng handmade question.



Tổng 100 điểm Mini Hackathon được phân bổ như sau:

25đ (Tiến độ): Nộp đúng hạn, chia làm 5 mốc (5đ/mốc).

67đ (Chấm trên file repo):

45đ cốt lõi nằm ở file spec.md: R1 (Bằng chứng & Impact - 15đ), R2 (Lát cắt & thiết kế - 15đ), R4 (Kiểm thử - 15đ).

22đ còn lại: R3 (Phân tích chỗ khó & rủi ro - 11đ), R5 (Prototype chạy được - 8đ), R7 (Cấu trúc repo - 3đ).

8đ (Thực tế - R6): Bằng chứng cho người ngoài dùng thử (thư mục validation/).

Điểm yếu chí mạng và kịch bản tồi tệ nhất:

Chỉ cắm đầu làm code mà viết spec.md hời hợt: Bốc hơi ngay lập tức 45 điểm. Dự án tự động thất bại.

Bỏ qua bước cho người ngoài dùng thử: Trần điểm bị khóa cứng ở 92, mất đi lợi thế cạnh tranh.

Trễ mốc thời gian: Mất trắng 5đ cho mỗi mốc, lãng phí hoàn toàn quỹ điểm "cho không" dễ lấy nhất.


