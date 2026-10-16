"""Vẽ bìa và sơ đồ / infographic minh hoạ (HTML → PNG bằng Chrome hoặc Edge chạy ngầm).

Dùng từ dung_tai_lieu.py. Có thể chạy riêng để xem thử một sơ đồ:
  python ve_minh_hoa.py thu <thư-mục-ra>

Phong cách "Ghi chú khoá học": bìa nền tối, nhấn cam; sơ đồ nền kem, chữ đậm, số thứ tự cam.
Loại sơ đồ (trường "loai" trong noi_dung.json → muc[].minh_hoa[]):
  quy_trinh  {"buoc": [{"ten", "mo_ta"}]}                  2–6 bước theo thứ tự
  so_sanh    {"trai": {"ten", "y": []}, "phai": {"ten", "y": []}}   trước/sau, sai/đúng, A/B
  chi_so     {"muc": [{"so", "nhan", "mo_ta"}]}             2–4 con số nổi bật
  khung      {"o": [{"ten", "mo_ta"}], "trung_tam"?}        2–6 thành phần ngang hàng
  chu_trinh  {"buoc": [{"ten", "mo_ta"}], "trung_tam"?}     3–6 bước lặp lại thành vòng
"""
from __future__ import annotations

import html
import json
import math
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ORANGE = "#E8692C"
ORANGE2 = "#F59A3C"
INK = "#1F1F1F"
MUTED = "#6F6A63"
CREAM = "#F7F1E6"
LINE = "#E6DCCB"
FONTS = ("<link rel='stylesheet' href='https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800"
         "&family=Lora:ital,wght@0,400;1,400&display=swap'>")
SANS = "'Be Vietnam Pro','Helvetica Neue',Arial,sans-serif"
SERIF = "Lora,Georgia,'Times New Roman',serif"


def e(s) -> str:
    return html.escape(str(s or ""))


def find_browser() -> str | None:
    cands = []
    if platform.system() == "Darwin":
        cands += ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                  "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
                  "/Applications/Chromium.app/Contents/MacOS/Chromium"]
    elif platform.system() == "Windows":
        for base in (os.environ.get("PROGRAMFILES", ""), os.environ.get("PROGRAMFILES(X86)", ""), os.environ.get("LOCALAPPDATA", "")):
            cands += [os.path.join(base, "Google", "Chrome", "Application", "chrome.exe"),
                      os.path.join(base, "Microsoft", "Edge", "Application", "msedge.exe")]
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge"):
        if shutil.which(name):
            cands.append(shutil.which(name))
    return next((c for c in cands if c and os.path.exists(c)), None)


def shoot(page: str, out: Path, width: int, height: int, bg: tuple[int, int, int] | None) -> bool:
    """Chụp trang HTML thành PNG (x2). bg: màu nền để cắt bớt khoảng trống phía dưới."""
    browser = find_browser()
    if not browser:
        return False
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "page.html"
        src.write_text(page, encoding="utf-8")
        subprocess.run([browser, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
                        "--force-device-scale-factor=2", f"--window-size={width},{height}",
                        "--virtual-time-budget=6000", f"--user-data-dir={Path(tmp) / 'profile'}",
                        f"--screenshot={out}", src.as_uri()], capture_output=True, timeout=120)
    if not out.exists():
        return False
    if bg:
        try:
            from PIL import Image
            im = Image.open(out).convert("RGB")
            w, h = im.size
            px = im.load()
            bottom = h - 1
            while bottom > 0 and all(sum(abs(a - b) for a, b in zip(px[x, bottom], bg)) < 12 for x in range(0, w, 7)):
                bottom -= 1
            im.crop((0, 0, w, min(h, bottom + 70))).save(out)
        except ImportError:
            pass
    return True


# ---------- Bìa ----------

def cover_html(nd: dict, info: dict, n_images: int, n_questions: int, cover_img: str | None) -> str:
    b = nd.get("bia") or {}
    year = (nd.get("nam") or "")
    title = nd.get("tieu_de", "")
    top = b.get("dong_tren") or title
    big = b.get("nhan_manh", "")
    after = b.get("dong_duoi", "")
    stats = b.get("chi_so", [])[:3]
    stats_html = "".join(
        f"<div class='st'><div class='sn'>{e(s.get('so'))}</div><div class='sl'>{e(s.get('nhan'))}</div>"
        f"<div class='sd'>{e(s.get('mo_ta'))}</div></div>" for s in stats)
    big_html = (f"<div class='bigrow'><span class='big'>{e(big)}</span><span class='after'>{e(after)}</span></div>"
                if big else "")
    img_html = f"<div class='shot'><img src='{cover_img}'></div>" if cover_img else ""
    quote = b.get("trich_dan", "")
    dur = info.get("thoi_luong_giay", 0)
    dur_s = f"{dur // 60}:{dur % 60:02d}" if dur < 3600 else f"{dur // 3600}:{dur % 3600 // 60:02d}:{dur % 60:02d}"
    kenh = info.get("kenh", "")
    return f"""<!doctype html><html lang='vi'><head><meta charset='utf-8'>{FONTS}<style>
*{{box-sizing:border-box;margin:0}}
html,body{{width:827px;height:1169px;overflow:hidden;background:#141312}}
body{{font-family:{SANS};color:#F3EEE6;position:relative;padding:0 52px;
 background:radial-gradient(520px 420px at 92% 88%,rgba(232,105,44,.38),transparent 70%),
 linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px) 0 0/44px 44px,
 linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px) 0 0/44px 44px,#141312}}
.bar{{position:absolute;left:0;right:0;top:0;height:6px;background:linear-gradient(90deg,{ORANGE},{ORANGE2},#F4C04E)}}
.hd{{display:flex;justify-content:space-between;padding:38px 0 14px;border-bottom:1px solid rgba(232,105,44,.45);
 font-size:11px;font-weight:700;letter-spacing:.22em;color:#E9A26F;text-transform:uppercase}}
.kick{{margin-top:44px;font-size:12px;font-weight:700;letter-spacing:.2em;color:{ORANGE2};text-transform:uppercase}}
.kick:before{{content:'';display:inline-block;width:34px;height:2px;background:{ORANGE};vertical-align:middle;margin-right:12px}}
h1{{margin-top:14px;font-size:{50 if len(top) < 44 else 40}px;line-height:1.08;font-weight:800;letter-spacing:-.02em;max-width:700px}}
.bigrow{{display:flex;align-items:center;gap:22px;margin-top:2px}}
.big{{font-size:{150 if len(big) <= 4 else 96}px;line-height:1;font-weight:800;letter-spacing:-.04em;
 background:linear-gradient(180deg,#F6A04A,{ORANGE} 60%,#C9541C);-webkit-background-clip:text;color:transparent}}
.after{{font-size:44px;line-height:1.05;font-weight:800;max-width:260px}}
.lead{{margin-top:22px;font-family:{SERIF};font-size:18px;line-height:1.55;color:#D9D2C7;max-width:640px}}
.stats{{display:grid;grid-template-columns:repeat({max(len(stats), 1)},1fr);margin-top:44px;border-top:1px solid rgba(255,255,255,.14);
 border-bottom:1px solid rgba(255,255,255,.14)}}
.st{{padding:20px 18px 22px 0}}.st+.st{{padding-left:18px;border-left:1px solid rgba(255,255,255,.14)}}
.sn{{font-size:46px;font-weight:700;color:transparent;-webkit-text-stroke:1.4px {ORANGE2};line-height:1}}
.sl{{margin-top:10px;font-size:15px;font-weight:700}}.sd{{margin-top:4px;font-size:12.5px;line-height:1.5;color:#A9A196}}
.quote{{margin-top:36px;font-family:{SERIF};font-style:italic;font-size:24px;line-height:1.35;max-width:{390 if cover_img else 700}px}}
.qs{{margin-top:10px;font-size:11px;letter-spacing:.18em;color:#A9A196;text-transform:uppercase}}
.shot{{position:absolute;right:46px;bottom:150px;width:340px;transform:rotate(-3deg);border-radius:12px;overflow:hidden;
 box-shadow:0 30px 60px -20px rgba(0,0,0,.8);border:6px solid #F3EEE6;background:#F3EEE6}}
.shot img{{display:block;width:100%}}
.ft{{position:absolute;left:52px;right:52px;bottom:40px;display:flex;justify-content:space-between;align-items:flex-end;
 padding-top:16px;border-top:1px solid rgba(255,255,255,.14);font-size:12px;line-height:1.55;color:#C9C1B5}}
.ft b{{color:#F3EEE6}}.fr{{text-align:right;font-weight:700;letter-spacing:.16em;color:#E9A26F;text-transform:uppercase;font-size:11px}}
</style></head><body><div class='bar'></div>
<div class='hd'><span>Ghi chú khoá học</span><span>Video summary · {e(year)}</span></div>
<div class='kick'>{e(b.get('kicker', 'Tài liệu học tập từ video'))}</div>
<h1>{e(top)}</h1>{big_html}
<p class='lead'>{e(b.get('mo_ta') or nd.get('phu_de', ''))}</p>
<div class='stats'>{stats_html}</div>
{f"<div class='quote'>{e(quote)}</div><div class='qs'>— Ý chính của video</div>" if quote else ""}
{img_html}
<div class='ft'><div><b>Tóm tắt từ video{(' của ' + e(kenh)) if kenh else ''}</b><br>“{e(info.get('tieu_de', ''))}” · {dur_s}</div>
<div class='fr'>{n_images} hình minh hoạ<br>{n_questions} câu hỏi tự ôn</div></div>
</body></html>"""


def render_cover(nd, info, n_images, n_questions, cover_img: Path | None, out: Path) -> bool:
    uri = cover_img.resolve().as_uri() if cover_img and cover_img.exists() else None
    return shoot(cover_html(nd, info, n_images, n_questions, uri), out, 827, 1169, None)


# ---------- Sơ đồ ----------

def _frame(title: str, inner: str, extra_css: str = "") -> str:
    return f"""<!doctype html><html lang='vi'><head><meta charset='utf-8'>{FONTS}<style>
*{{box-sizing:border-box;margin:0}}
html,body{{width:1200px;background:{CREAM}}}
body{{font-family:{SANS};color:{INK};padding:44px 52px 30px}}
.t{{font-size:15px;font-weight:800;letter-spacing:.16em;text-transform:uppercase;color:{ORANGE};margin-bottom:26px}}
.t:before{{content:'';display:inline-block;width:30px;height:3px;background:{ORANGE};vertical-align:middle;margin-right:12px}}
.card{{background:#fff;border:1.5px solid {LINE};border-radius:16px;padding:22px 22px 24px}}
.n{{width:46px;height:46px;border-radius:50%;background:{ORANGE};color:#fff;display:grid;place-items:center;font-weight:800;font-size:20px}}
.h{{font-size:22px;font-weight:800;line-height:1.25}}
.d{{font-size:17px;line-height:1.5;color:{MUTED};margin-top:8px}}
{extra_css}</style></head><body><div class='t'>{e(title)}</div>{inner}</body></html>"""


def d_quy_trinh(m: dict) -> str:
    steps = m.get("buoc", [])[:6]
    cols = min(len(steps), 3 if len(steps) in (5, 6) else 4) or 1
    cells = []
    for i, s in enumerate(steps, 1):
        arrow = "<div class='ar'>→</div>" if i % cols and i < len(steps) else ""
        cells.append(f"<div class='cell'><div class='card'><div class='n'>{i}</div><div class='h' style='margin-top:16px'>{e(s.get('ten'))}</div>"
                     f"<div class='d'>{e(s.get('mo_ta'))}</div></div>{arrow}</div>")
    css = (f".g{{display:grid;grid-template-columns:repeat({cols},1fr);gap:26px 38px}}.cell{{position:relative}}.card{{height:100%}}"
           f".ar{{position:absolute;right:-31px;top:50%;transform:translateY(-50%);font-size:28px;font-weight:800;color:{ORANGE}}}")
    return _frame(m.get("tieu_de", "Quy trình"), f"<div class='g'>{''.join(cells)}</div>", css)


def d_so_sanh(m: dict) -> str:
    def col(side, cls, mark):
        items = "".join(f"<li><span class='mk'>{mark}</span>{e(x)}</li>" for x in side.get("y", []))
        return f"<div class='col {cls}'><div class='ch'>{e(side.get('ten'))}</div><ul>{items}</ul></div>"
    css = (f".g{{display:grid;grid-template-columns:1fr 1fr;gap:26px}}.col{{border-radius:16px;overflow:hidden;border:1.5px solid {LINE};background:#fff}}"
           f".ch{{padding:18px 24px;font-size:22px;font-weight:800}}.l .ch{{background:#ECE6DB;color:{MUTED}}}.r .ch{{background:{ORANGE};color:#fff}}"
           f"ul{{list-style:none;padding:12px 24px 20px}}li{{display:flex;gap:12px;font-size:18px;line-height:1.5;padding:10px 0;border-bottom:1px solid #F0E9DD}}"
           f"li:last-child{{border:0}}.mk{{font-weight:800;flex:none}}.l .mk{{color:#A39B8E}}.r .mk{{color:{ORANGE}}}")
    inner = f"<div class='g'>{col(m.get('trai', {}), 'l', '✕')}{col(m.get('phai', {}), 'r', '✓')}</div>"
    return _frame(m.get("tieu_de", "So sánh"), inner, css)


def d_chi_so(m: dict) -> str:
    items = m.get("muc", [])[:4]
    cells = "".join(f"<div class='card'><div class='sn'>{e(s.get('so'))}</div><div class='h'>{e(s.get('nhan'))}</div>"
                    f"<div class='d'>{e(s.get('mo_ta'))}</div></div>" for s in items)
    css = (f".g{{display:grid;grid-template-columns:repeat({max(len(items), 1)},1fr);gap:22px}}"
           f".sn{{font-size:64px;font-weight:800;line-height:1.05;letter-spacing:-.03em;margin-bottom:10px;"
           f"background:linear-gradient(180deg,{ORANGE2},{ORANGE});-webkit-background-clip:text;color:transparent}}")
    return _frame(m.get("tieu_de", "Con số chính"), f"<div class='g'>{cells}</div>", css)


def d_khung(m: dict) -> str:
    items = m.get("o", [])[:6]
    cols = 3 if len(items) in (3, 5, 6) else 2
    center = m.get("trung_tam")
    cells = "".join(f"<div class='card k'><div class='h'>{e(s.get('ten'))}</div><div class='d'>{e(s.get('mo_ta'))}</div></div>" for s in items)
    head = f"<div class='ctr'>{e(center)}</div>" if center else ""
    css = (f".g{{display:grid;grid-template-columns:repeat({cols},1fr);gap:20px}}.k{{border-top:6px solid {ORANGE}}}"
           f".ctr{{background:{INK};color:#fff;border-radius:16px;padding:20px 26px;font-size:24px;font-weight:800;margin-bottom:20px;text-align:center}}")
    return _frame(m.get("tieu_de", "Các thành phần"), head + f"<div class='g'>{cells}</div>", css)


def d_chu_trinh(m: dict) -> str:
    steps = m.get("buoc", [])[:6]
    n = max(len(steps), 1)
    W, H, R = 1096, 640, 250
    cx, cy = W / 2, H / 2 + 10
    nodes = []
    for i, s in enumerate(steps):
        a = -math.pi / 2 + 2 * math.pi * i / n
        x, y = cx + R * 1.55 * math.cos(a), cy + R * math.sin(a)
        nodes.append(f"<div class='nd' style='left:{x - 150:.0f}px;top:{y - 58:.0f}px'><div class='n'>{i + 1}</div>"
                     f"<div><div class='h'>{e(s.get('ten'))}</div><div class='d'>{e(s.get('mo_ta'))}</div></div></div>")
    center = m.get("trung_tam", "")
    css = (f".wrap{{position:relative;width:{W}px;height:{H}px}}svg{{position:absolute;inset:0}}"
           f".nd{{position:absolute;width:300px;display:flex;gap:14px;align-items:flex-start;background:#fff;border:1.5px solid {LINE};border-radius:14px;padding:14px 16px}}"
           f".nd .h{{font-size:19px}}.nd .d{{font-size:14.5px;margin-top:4px}}.n{{flex:none;width:38px;height:38px;font-size:17px}}"
           f".c{{position:absolute;left:{cx - 120:.0f}px;top:{cy - 46:.0f}px;width:240px;height:92px;display:grid;place-items:center;text-align:center;"
           f"background:{INK};color:#fff;border-radius:46px;font-size:19px;font-weight:800;padding:0 18px}}")
    ring = (f"<svg width='{W}' height='{H}'><ellipse cx='{cx}' cy='{cy}' rx='{R * 1.55}' ry='{R}' fill='none' stroke='{ORANGE}' "
            f"stroke-width='3' stroke-dasharray='10 9'/></svg>")
    inner = f"<div class='wrap'>{ring}{''.join(nodes)}{f'<div class=c>{e(center)}</div>' if center else ''}</div>"
    return _frame(m.get("tieu_de", "Chu trình"), inner, css)


DIAGRAMS = {"quy_trinh": d_quy_trinh, "so_sanh": d_so_sanh, "chi_so": d_chi_so, "khung": d_khung, "chu_trinh": d_chu_trinh}


def render_diagram(m: dict, out: Path) -> bool:
    fn = DIAGRAMS.get(m.get("loai", ""))
    if not fn:
        return False
    return shoot(fn(m), out, 1200, 1400, (0xF7, 0xF1, 0xE6))


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "thu":
        out = Path(sys.argv[2])
        out.mkdir(parents=True, exist_ok=True)
        samples = [
            {"loai": "quy_trinh", "tieu_de": "Quy trình mẫu", "buoc": [{"ten": "Lấy lời thoại", "mo_ta": "Phụ đề có mốc"}, {"ten": "Nhìn video", "mo_ta": "Bảng ảnh nhỏ"}, {"ten": "Viết", "mo_ta": "Theo chương"}, {"ten": "Dựng", "mo_ta": "Word và PDF"}]},
            {"loai": "so_sanh", "tieu_de": "So sánh mẫu", "trai": {"ten": "Trước", "y": ["Ghi chép tay 3 giờ", "Hay bỏ dở"]}, "phai": {"ten": "Sau", "y": ["Có tài liệu trong 30 phút", "Có mốc thời gian"]}},
            {"loai": "chi_so", "tieu_de": "Chỉ số mẫu", "muc": [{"so": "80%", "nhan": "Việc lặp lại", "mo_ta": "giao cho AI"}, {"so": "3", "nhan": "Nguyên tắc", "mo_ta": "không thoả hiệp"}]},
            {"loai": "khung", "tieu_de": "Khung mẫu", "trung_tam": "Một nhân sự AI", "o": [{"ten": "Instruction", "mo_ta": "luôn đọc"}, {"ten": "Memory", "mo_ta": "khi liên quan"}, {"ten": "Skill", "mo_ta": "khi làm việc"}]},
            {"loai": "chu_trinh", "tieu_de": "Chu trình mẫu", "trung_tam": "Cải tiến liên tục", "buoc": [{"ten": "Làm", "mo_ta": "thử với AI"}, {"ten": "Xem", "mo_ta": "kết quả"}, {"ten": "Góp ý", "mo_ta": "cụ thể"}, {"ten": "Đóng gói", "mo_ta": "thành skill"}]},
        ]
        for i, m in enumerate(samples, 1):
            print(m["loai"], render_diagram(m, out / f"so-do-{i}.png"))
    else:
        print(__doc__)
