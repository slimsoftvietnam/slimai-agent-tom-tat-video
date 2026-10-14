"""Bước 2: chụp ảnh nhỏ ở các mốc lời thoại và ghép thành bảng để agent xem, chọn hình đúng slide.

Cách dùng:
  python anh_nho.py <thư-mục-kết-quả>

Tạo <thư-mục>/anh_nho/bang_01.jpg, bang_02.jpg... (mỗi bảng 6 cột x 5 hàng = 30 ô, đọc từ trái sang phải,
trên xuống dưới) và anh_nho/danh_sach.txt ghi mốc thời gian của từng ô.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

COLS, ROWS = 6, 5
MAX_SHOTS = 360  # video rất dài: giãn mốc để không quá 12 bảng


def secs(ts: str) -> int:
    p = [int(x) for x in ts.split(":")]
    return p[0] * 3600 + p[1] * 60 + p[2] if len(p) == 3 else p[0] * 60 + p[1]


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    out = Path(sys.argv[1]).resolve()
    if not shutil.which("ffmpeg"):
        sys.exit("Thiếu ffmpeg (xem INSTALL.md).")
    stamps = re.findall(r"^\[((?:\d{2}:)?\d{2}:\d{2})\]", (out / "loi_thoai.txt").read_text(encoding="utf-8"), re.M)
    step = max(1, -(-len(stamps) // MAX_SHOTS))
    stamps = stamps[::step]
    shots = out / "anh_nho" / "_tung_anh"
    shots.mkdir(parents=True, exist_ok=True)
    video = out / "video.mp4"
    for i, ts in enumerate(stamps):
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", str(secs(ts)), "-i", str(video),
                        "-frames:v", "1", "-vf", "scale=320:-2", str(shots / f"{i:04d}.jpg")], check=False)
    files = sorted(shots.glob("*.jpg"))
    per = COLS * ROWS
    lines = []
    for b in range(0, len(files), per):
        n = b // per + 1
        group = files[b:b + per]
        listing = shots / f"list_{n}.txt"
        listing.write_text("".join(f"file '{f}'\n" for f in group))
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i",
                        str(listing), "-vf", f"tile={COLS}x{ROWS}:padding=4", "-frames:v", "1",
                        str(out / "anh_nho" / f"bang_{n:02d}.jpg")], check=True)
        cells = ", ".join(f"ô {k + 1}={stamps[b + k]}" for k in range(len(group)))
        lines.append(f"bang_{n:02d}.jpg: {cells}")
    (out / "anh_nho" / "danh_sach.txt").write_text("\n".join(lines), encoding="utf-8")
    shutil.rmtree(shots)
    print(f"Đã tạo {len(lines)} bảng ảnh nhỏ trong {out / 'anh_nho'} ({len(files)} mốc). Mở từng bảng để xem; "
          f"ô đếm từ trái sang phải, trên xuống dưới, {COLS} ô mỗi hàng; mốc của từng ô trong danh_sach.txt.")


if __name__ == "__main__":
    main()
