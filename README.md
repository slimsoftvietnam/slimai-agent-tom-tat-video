# Agent tóm tắt video khoá học · SlimAI

Xem xong một buổi đào tạo, webinar hay livestream là quên; ghi chép lại một video một tiếng mất cả buổi chiều. Skill này biến **video khoá học** (file trên máy, link YouTube hoặc link video khác) thành **một file Docs tổng hợp nội dung khoá học**, kèm bản PDF.

Tài liệu thực hành (bài về nhà Buổi 1), [Khoá học AI Agent cho người đi làm](https://ai.slim.vn) của SlimAI.

## Bắt đầu bằng một prompt

Mở Claude Code hoặc Codex tại một thư mục trống rồi dán prompt trong [PROMPT_CAI_VA_CHAY_THU.md](PROMPT_CAI_VA_CHAY_THU.md). AI tự tải repo, cài skill và báo khi sẵn sàng. Sau đó chỉ cần:

```text
Dùng skill tom-tat-video để tóm tắt video này thành file Word và PDF: [link video]
```

## Trong repo có gì

| Thư mục / tệp | Nội dung |
|---|---|
| [`tom-tat-video/SKILL.md`](tom-tat-video/SKILL.md) | Skill cho Claude Code / Codex: các bước agent làm, mẫu nội dung, cách viết cho đầy đủ |
| [`tom-tat-video/INSTALL.md`](tom-tat-video/INSTALL.md) | Cài đặt: nơi đặt skill, ffmpeg, yt-dlp, môi trường Python |
| [`tom-tat-video/THE_NHIEM_VU.md`](tom-tat-video/THE_NHIEM_VU.md) | Thẻ nhiệm vụ: tình huống, kết quả cần đạt, PEAS, không được làm gì, nghiệm thu |
| `tom-tat-video/scripts/` | `lay_video.py` (video + lời thoại có mốc), `anh_nho.py` (bảng ảnh nhỏ để chọn hình), `dung_tai_lieu.py` (dựng Word/PDF + tự chấm) |

## Skill tạo ra những gì

Mỗi video có một thư mục `output/<tên-video>/`:

| Tệp | Là gì |
|---|---|
| `<tên-video>.docx` | File Docs tổng hợp: bìa ghi nguồn, mục lục, tổng quan, các chương mục có mốc thời gian, hình chụp đúng slide, thuật ngữ, câu hỏi ôn tập |
| `<tên-video>.pdf` | Bản PDF (macOS có Pages hoặc máy có LibreOffice; không có thì xuất từ Word) |
| `tu_cham.txt` | Bảng tự chấm 6 tiêu chí |
| `hinh/` | Các hình minh hoạ |
| `loi_thoai.txt`, `noi_dung.json`, `anh_nho/` | File làm việc để sửa và dựng lại |

## PEAS trong một bảng

| Chữ | Dịch | Nhớ nhanh | Agent này |
|---|---|---|---|
| **P** · Performance measure | Thước đo hiệu quả | KPI | Một file Docs tổng hợp nội dung khoá học, bảng tự chấm đạt đủ |
| **E** · Environment | Môi trường | Bàn làm việc | Một thư mục làm việc trên máy tính |
| **A** · Actuators | Cơ cấu chấp hành | Đôi tay | Tải video và phụ đề, chụp ảnh, viết nội dung, dựng Word/PDF. **Không** bịa nội dung, không xoá file, không gửi tài liệu đi đâu |
| **S** · Sensors | Cảm biến | Đôi mắt | Video khoá học: file trên máy, link YouTube hoặc link video khác |

## Lưu ý

- Không cần API key: phần viết nội dung do chính Claude Code / Codex làm. Video có phụ đề YouTube chạy nhanh nhất; video không có phụ đề cần công cụ phiên âm trên máy (xem INSTALL.md).
- Tài liệu tạo từ video của người khác chỉ dùng để học. Skill tự ghi nguồn trên bìa; không phát hành khi chưa xin phép tác giả.
- yt-dlp phải là bản mới (YouTube thay đổi liên tục). Lỗi 403 hoặc "page needs to be reloaded" thì nâng cấp yt-dlp.
