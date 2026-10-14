# Thẻ nhiệm vụ · Agent tóm tắt video khoá học

## Tình huống

Mỗi tuần xem vài buổi đào tạo, webinar, livestream; xem xong là quên, ghi chép lại một video 1 tiếng mất cả buổi chiều.

## Mục tiêu

Từ một link video, có tài liệu học tập đầy đủ trong **dưới 30 phút** (trước đây: 2–4 giờ ghi chép tay cho video 1 tiếng).

## Kết quả cần đạt (agent tạo ra)

| # | Kết quả | Đạt khi |
|---|---|---|
| 1 | File Word `.docx` | Mở được; có bìa, mục lục, tổng quan, các chương mục, thuật ngữ, câu hỏi ôn tập |
| 2 | File PDF | Cùng nội dung (máy có Pages hoặc LibreOffice); không có thì xuất từ Word |
| 3 | Nội dung đầy đủ | ≥ 70 chữ cho mỗi phút video; đọc một chương hiểu được mà không cần xem video |
| 4 | Mốc thời gian | Mục nào cũng có; bấm mở đúng đoạn trên YouTube; phủ đến cuối video |
| 5 | Hình minh hoạ | Khoảng 1 hình mỗi 3–5 phút, đúng slide/demo, có chú thích; lưu riêng trong `hinh/` |
| 6 | Bảng tự chấm | `tu_cham.txt`, mọi dòng ĐẠT |
| 7 | File làm việc | `loi_thoai.txt` (lời thoại có mốc), `noi_dung.json` (nội dung để sửa và dựng lại), `anh_nho/` (bảng ảnh nhỏ) |

## PEAS

| Chữ | Dịch | Nhớ nhanh | Agent này |
|---|---|---|---|
| **P** · Performance measure | Thước đo hiệu quả | KPI | 6 dòng tự chấm đều ĐẠT; 0 mốc thời gian sai; 0 nội dung bịa |
| **E** · Environment | Môi trường | Bàn làm việc | YouTube hoặc file video trên máy, thư mục làm việc, phụ đề có thể sai chính tả |
| **A** · Actuators | Cơ cấu chấp hành | Đôi tay | Tải video và phụ đề, chụp ảnh, viết nội dung, dựng Word/PDF. **Không** xoá file người dùng, không đăng hay gửi tài liệu đi đâu |
| **S** · Sensors | Cảm biến | Đôi mắt | Lời thoại có mốc giờ, mục lục của tác giả, bảng ảnh nhỏ để "nhìn" slide |

## Không được làm gì

- Không bịa nội dung, con số hay mốc thời gian không có trong video.
- Không tự phiên âm khi video đã có phụ đề; không tự cài phần mềm hệ thống khi chưa hỏi.
- Không dùng hình có mã QR, quảng cáo hoặc thông tin cá nhân của bên khác.
- Không phát hành tài liệu làm từ video của người khác; tài liệu chỉ để học.

## Nghiệm thu (người dùng tự làm, 5 phút)

1. Mở PDF/Word, đọc lướt mục lục và một chương bất kỳ.
2. Bấm thử 2 mốc thời gian, xem có khớp video.
3. Xem các hình có đúng slide không.
4. Dòng nào chưa đạt: nói lỗi trong một câu → "Sửa noi_dung.json và dựng lại".
