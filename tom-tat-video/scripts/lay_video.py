"""Bước 1: tải video và lấy lời thoại có mốc thời gian.

Cách dùng:
  python lay_video.py <link-YouTube | đường-dẫn-file-video> [--thu-muc output/<tên>]

Tạo trong thư mục kết quả:
  video.mp4          video 720p (để chụp hình)
  loi_thoai.txt      lời thoại, mỗi dòng "[MM:SS] ..." khoảng 20 giây
  thong_tin.json     tiêu đề, kênh, thời lượng, link, mục lục tác giả (nếu có)
Ưu tiên phụ đề có sẵn của YouTube; chỉ tự phiên âm khi không có phụ đề.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path



def stamp(seconds: float) -> str:
    s = int(seconds)
    h, r = divmod(s, 3600)
    m, s = divmod(r, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def slug(text: str) -> str:
    import unicodedata
    text = unicodedata.normalize("NFD", text.replace("đ", "d").replace("Đ", "D"))
    text = "".join(c for c in text if unicodedata.category(c) != "Mn").lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")[:60] or "video"


def ytdlp_cmd() -> list[str]:
    """Chọn bản yt-dlp mới nhất trên máy (bản cũ hay bị YouTube trả 403 / 'page needs to be reloaded')."""
    candidates = []
    for exe in {shutil.which("yt-dlp"), "/opt/homebrew/bin/yt-dlp", "/usr/local/bin/yt-dlp",
                os.path.expanduser("~/.local/bin/yt-dlp"), str(Path(__file__).resolve().parent.parent / "bin" / "yt-dlp")}:
        if exe and os.path.isfile(exe) and os.access(exe, os.X_OK):
            candidates.append([exe])
    try:
        import yt_dlp  # noqa: F401
        candidates.append([sys.executable, "-m", "yt_dlp"])
    except ImportError:
        pass
    best, best_ver = None, ""
    for cmd in candidates:
        r = subprocess.run(cmd + ["--version"], capture_output=True, text=True)
        ver = r.stdout.strip()
        if r.returncode == 0 and ver > best_ver:
            best, best_ver = cmd, ver
    if not best:
        sys.exit("Thiếu yt-dlp. Cài theo INSTALL.md (macOS: brew install yt-dlp; Windows: winget install yt-dlp).")
    return best


def group_json3(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    lines, cur, start = [], [], None
    for ev in data.get("events", []):
        text = "".join(seg.get("utf8", "") for seg in ev.get("segs") or []).replace("\n", " ").strip()
        if not text:
            continue
        if start is None:
            start = ev.get("tStartMs", 0)
        cur.append(text)
        if ev.get("tStartMs", 0) - start >= 20000:
            lines.append(f"[{stamp(start / 1000)}] {' '.join(cur)}")
            cur, start = [], None
    if cur:
        lines.append(f"[{stamp(start / 1000)}] {' '.join(cur)}")
    return lines


def group_vtt(path: Path) -> list[str]:
    lines, cur, start = [], [], None
    t = None
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"\s*(?:(\d+):)?(\d{2}):(\d{2})[.,]\d+\s+-->", raw)
        if m:
            t = int(m.group(1) or 0) * 3600 + int(m.group(2)) * 60 + int(m.group(3))
            continue
        text = re.sub(r"<[^>]+>", "", raw).strip()
        if not text or text.isdigit() or text.upper().startswith("WEBVTT") or t is None:
            continue
        if cur and text == cur[-1]:
            continue
        if start is None:
            start = t
        cur.append(text)
        if t - start >= 20:
            lines.append(f"[{stamp(start)}] {' '.join(cur)}")
            cur, start = [], None
    if cur:
        lines.append(f"[{stamp(start)}] {' '.join(cur)}")
    return lines


def pick_subtitle(info: dict) -> tuple[str | None, str]:
    """Phụ đề người làm (vi) > tự động theo ngôn ngữ gốc (vi-orig) > vi tự động > ngôn ngữ gốc khác > en."""
    manual = info.get("subtitles") or {}
    auto = info.get("automatic_captions") or {}
    if "vi" in manual:
        return "vi", "manual"
    for lang in ("vi-orig", "vi"):
        if lang in auto:
            return lang, "auto"
    orig = [k for k in auto if k.endswith("-orig")]
    if orig:
        return orig[0], "auto"
    for lang in ("en",):
        if lang in manual:
            return lang, "manual"
        if lang in auto:
            return lang, "auto"
    return None, ""


def find_whisper_model() -> str | None:
    for pattern in ("~/.cache/**/ggml-large-v3*.bin", "~/.cache/**/ggml-medium*.bin", "~/**/ggml-large-v3*.bin"):
        hits = glob.glob(os.path.expanduser(pattern), recursive=True)
        hits = [h for h in hits if not os.path.basename(h).endswith(".en.bin")]
        if hits:
            return hits[0]
    return None


def transcribe_local(video: Path, out: Path) -> list[str]:
    exe = shutil.which("whisper-cli")
    model = find_whisper_model()
    if not exe or not model or not shutil.which("ffmpeg"):
        sys.exit("KHONG_CO_PHU_DE: video không có phụ đề và máy chưa có công cụ phiên âm "
                 "(whisper-cli + model đa ngôn ngữ). Hãy hỏi người dùng trước khi cài thêm.")
    print("Video không có phụ đề — đang tự phiên âm tiếng Việt trên máy (video 1 giờ có thể mất 30 phút).", flush=True)
    wav = out / "am_thanh.wav"
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(video), "-vn", "-ac", "1",
                    "-ar", "16000", "-c:a", "pcm_s16le", str(wav)], check=True)
    subprocess.run([exe, "-m", model, "-f", str(wav), "-l", "vi", "-ovtt", "-of", str(out / "phien_am")],
                   check=True, stdout=subprocess.DEVNULL)
    wav.unlink(missing_ok=True)
    return group_vtt(out / "phien_am.vtt")


def chapters_from(info: dict) -> list[dict]:
    if info.get("chapters"):
        return [{"timestamp": stamp(c["start_time"]), "title": c["title"]} for c in info["chapters"]]
    found = []
    for line in (info.get("description") or "").splitlines():
        m = re.match(r"\s*((?:\d{1,2}:)?\d{1,2}:\d{2})\s*[-–—:)]?\s*(.+)", line)
        if m:
            parts = [int(x) for x in m.group(1).split(":")]
            secs = parts[0] * 3600 + parts[1] * 60 + parts[2] if len(parts) == 3 else parts[0] * 60 + parts[1]
            found.append({"timestamp": stamp(secs), "title": m.group(2).strip()})
    return found if len(found) >= 3 else []


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("nguon")
    ap.add_argument("--thu-muc")
    a = ap.parse_args()
    is_url = re.match(r"https?://", a.nguon) is not None

    if is_url:
        meta = subprocess.run(ytdlp_cmd() + ["--no-playlist", "--skip-download", "--dump-single-json", a.nguon],
                              capture_output=True, text=True)
        if meta.returncode:
            sys.exit("Không đọc được link video: " + (meta.stderr.strip().splitlines() or ["?"])[-1])
        info = json.loads(meta.stdout)
        title = info.get("title") or "video"
    else:
        src = Path(a.nguon).expanduser().resolve()
        if not src.is_file():
            sys.exit(f"Không tìm thấy file: {src}")
        info, title = {"title": src.stem}, src.stem

    out = Path(a.thu_muc or f"output/{slug(title)}").resolve()
    out.mkdir(parents=True, exist_ok=True)
    video = out / "video.mp4"
    lines: list[str] = []
    source = ""

    if is_url:
        cmd = ytdlp_cmd() + ["--no-playlist", "-f", "bv*[height<=720]+ba/b[height<=720]/b", "--merge-output-format", "mp4",
                             "-o", str(out / "video.%(ext)s"), a.nguon]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode or not video.exists():
            last = (r.stderr.strip().splitlines() or ["?"])[-1]
            hint = " (yt-dlp đã cũ — macOS: brew upgrade yt-dlp; Windows: winget upgrade yt-dlp)" if ("403" in last or "reload" in last) else ""
            sys.exit(f"Tải video thất bại: {last}{hint}")
        # Chỉ tải MỘT bản phụ đề: xin nhiều ngôn ngữ cùng lúc (kể cả bản dịch máy) dễ bị YouTube chặn 429.
        lang, kind = pick_subtitle(info)
        if lang:
            flag = "--write-subs" if kind == "manual" else "--write-auto-subs"
            for attempt in range(3):
                subprocess.run(ytdlp_cmd() + ["--no-playlist", "--skip-download", flag, "--sub-langs", lang,
                                              "--sub-format", "json3", "-o", str(out / "video.%(ext)s"), a.nguon],
                               capture_output=True, text=True)
                sub = out / f"video.{lang}.json3"
                if sub.exists():
                    lines, source = group_json3(sub), f"phụ đề YouTube ({lang}{', tự động' if kind == 'auto' else ''})"
                    break
                time.sleep(10 * (attempt + 1))
    else:
        if src.suffix.lower() == ".mp4":
            shutil.copy2(src, video)
        else:
            subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(src), "-c:v", "libx264",
                            "-c:a", "aac", str(video)], check=True)
        for ext in (".vtt", ".srt"):
            side = src.with_suffix(ext)
            if side.exists():
                lines, source = group_vtt(side), f"phụ đề đi kèm ({side.name})"
                break

    if not lines:
        lines, source = transcribe_local(video, out), "tự phiên âm (whisper)"

    (out / "loi_thoai.txt").write_text("\n".join(lines), encoding="utf-8")
    summary = {
        "tieu_de": title,
        "kenh": info.get("channel") or info.get("uploader") or "",
        "thoi_luong_giay": int(info.get("duration") or 0),
        "link": info.get("webpage_url") or (a.nguon if is_url else ""),
        "nguon_loi_thoai": source,
        "muc_luc_tac_gia": chapters_from(info),
    }
    if not summary["thoi_luong_giay"] and shutil.which("ffprobe"):
        p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
                           capture_output=True, text=True)
        summary["thoi_luong_giay"] = int(float(p.stdout.strip() or 0))
    (out / "thong_tin.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    for leftover in out.glob("video.*.json3"):
        leftover.unlink()

    print(f"THU_MUC: {out}")
    print(f"Tiêu đề: {title} | {stamp(summary['thoi_luong_giay'])} | {summary['kenh']}")
    print(f"Lời thoại: {len(lines)} dòng, {sum(map(len, lines))} ký tự — nguồn: {source}")
    if summary["muc_luc_tac_gia"]:
        print(f"Mục lục của tác giả: {len(summary['muc_luc_tac_gia'])} mục (trong thong_tin.json) — dùng làm khung chương")


if __name__ == "__main__":
    main()
