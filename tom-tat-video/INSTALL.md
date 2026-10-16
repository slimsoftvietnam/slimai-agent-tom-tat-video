# Cài đặt Agent tóm tắt video

## 1. Đặt skill

Chép thư mục `tom-tat-video` (giữ nguyên cấu trúc) vào:

| Công cụ | Theo dự án | Dùng chung mọi dự án |
|---|---|---|
| Claude Code | `<dự-án>/.claude/skills/tom-tat-video` | `~/.claude/skills/tom-tat-video` |
| Codex | `<dự-án>/.agents/skills/tom-tat-video` | `~/.codex/skills/tom-tat-video` |

## 2. Cài Python 3.9+, ffmpeg và yt-dlp

- macOS: Python có sẵn (`python3`). Cài thêm: `brew install ffmpeg yt-dlp`
- Windows: cài Python từ python.org; rồi `winget install Gyan.FFmpeg yt-dlp.yt-dlp`
- Ubuntu/Debian: `sudo apt-get install python3 python3-venv ffmpeg`, và yt-dlp bản mới từ https://github.com/yt-dlp/yt-dlp/releases

Kiểm tra: `ffmpeg -version` và `yt-dlp --version` chạy được. yt-dlp phải là bản mới (YouTube đổi liên tục); báo lỗi 403 hoặc "page needs to be reloaded" thì nâng cấp: `brew upgrade yt-dlp` / `winget upgrade yt-dlp.yt-dlp`.

## 3. Tạo môi trường chạy

Trong thư mục `tom-tat-video`:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 4. Bìa và sơ đồ: Google Chrome hoặc Microsoft Edge

Script dùng Chrome/Edge chạy ngầm để vẽ bìa và sơ đồ minh hoạ. Máy đã có một trong hai trình duyệt là đủ (Windows có sẵn Edge). Không có thì tài liệu vẫn dựng được nhưng bìa chỉ có chữ và không có sơ đồ.

## 5. (Tuỳ chọn) PDF và phiên âm

- PDF: macOS có Pages là đủ (script tự xuất PDF qua Pages). Máy khác: cài LibreOffice, hoặc mở file Word rồi Xuất PDF.
- Video không có phụ đề: cần `whisper-cli` (macOS: `brew install whisper-cpp`) và model đa ngôn ngữ `ggml-large-v3.bin` hoặc `ggml-medium.bin` (không dùng bản `.en`). Hầu hết video YouTube tiếng Việt đã có phụ đề tự động nên thường không cần.

## 6. Kiểm tra nhanh

```sh
.venv/bin/python scripts/lay_video.py "https://www.youtube.com/watch?v=<id>" --thu-muc output/thu
.venv/bin/python scripts/ve_minh_hoa.py thu output/so-do-mau
```

Thấy dòng `Lời thoại: … — nguồn: phụ đề YouTube` và 5 dòng `True` (5 sơ đồ mẫu trong `output/so-do-mau`) là đã sẵn sàng.
