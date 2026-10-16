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
| [`tom-tat-video/THE_NHIEM_VU.md`](tom-tat-video/THE_NHIEM_VU.md) | Thẻ nhiệm vụ chi tiết cho agent: tiêu chí đạt, không được làm gì, nghiệm thu |
| `tom-tat-video/scripts/` | `lay_video.py` (video + lời thoại có mốc), `anh_nho.py` (bảng ảnh nhỏ để chọn hình), `ve_minh_hoa.py` (bìa + sơ đồ/infographic), `dung_tai_lieu.py` (dựng Word/PDF + tự chấm) |

## Skill tạo ra những gì

Mỗi video có một thư mục `output/<tên-video>/`:

| Tệp | Là gì |
|---|---|
| `<tên-video>.docx` | File Docs tổng hợp: bìa ghi nguồn, mục lục, tổng quan, các chương mục có mốc thời gian, hình chụp đúng slide, thuật ngữ, câu hỏi ôn tập |
| `<tên-video>.pdf` | Bản PDF (macOS có Pages hoặc máy có LibreOffice; không có thì xuất từ Word) |
| `tu_cham.txt` | Bảng tự chấm 6 tiêu chí |
| `hinh/` | Các hình minh hoạ |
| `loi_thoai.txt`, `noi_dung.json`, `anh_nho/` | File làm việc để sửa và dựng lại |

## Thẻ nhiệm vụ

**Bài về nhà · Tóm tắt video khoá học — Agent xem video và viết lại thành tài liệu học tập**

### Tình huống thực tế

Mỗi tuần bạn xem vài buổi đào tạo, webinar, livestream. Xem xong là quên; muốn ghi chép lại một video một tiếng thì mất cả buổi chiều, và thường bỏ dở giữa chừng.

Agent lấy phụ đề có mốc thời gian, "nhìn" video qua bảng ảnh nhỏ để chọn đúng slide, viết lại theo chương mục, rồi dựng Word và PDF và tự chấm theo 6 tiêu chí. **Tài liệu chỉ dùng để học; video của người khác phải ghi nguồn.**

### Mô hình PEAS

| | | |
|---|---|---|
| **P** | Kết quả cần có | Một **file Docs tổng hợp nội dung khoá học**. |
| **E** | Môi trường làm việc | Một **thư mục làm việc trên máy tính**, link YouTube hoặc file video trên máy. |
| **A** | Hành động | Tải video và phụ đề, chụp ảnh nhỏ, viết nội dung, dựng Word và PDF, tự chấm và sửa.<br>**Không được:** bịa nội dung, tự phiên âm khi video đã có phụ đề, cài phần mềm hệ thống khi chưa hỏi, dùng hình có mã QR hay quảng cáo của bên khác, xoá file hoặc gửi tài liệu đi đâu. |
| **S** | Đầu vào | **Video khoá học**: file trên máy, link YouTube hoặc link video khác. |

> **Lưu ý:** Phụ đề tự động có thể nghe nhầm tên riêng. Agent chỉ sửa khi chắc chắn; khi đọc tài liệu, đối chiếu lại những chỗ quan trọng với video.

Hướng dẫn từng bước có hình minh hoạ: [ai.slim.vn/huong-dan-ai-agent-tom-tat-video-khoa-hoc](https://ai.slim.vn/huong-dan-ai-agent-tom-tat-video-khoa-hoc)

## Lưu ý khác

- Không cần API key: phần viết nội dung do chính Claude Code / Codex làm. Video có phụ đề YouTube chạy nhanh nhất; video không có phụ đề cần công cụ phiên âm trên máy (xem INSTALL.md).
- Tài liệu tạo từ video của người khác chỉ dùng để học. Skill tự ghi nguồn trên bìa; không phát hành khi chưa xin phép tác giả.
- yt-dlp phải là bản mới (YouTube thay đổi liên tục). Lỗi 403 hoặc "page needs to be reloaded" thì nâng cấp yt-dlp.
