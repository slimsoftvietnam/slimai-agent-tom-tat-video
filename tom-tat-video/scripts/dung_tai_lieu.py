"""Bước 4: dựng tài liệu Word (+ PDF nếu máy có Pages hoặc LibreOffice) từ noi_dung.json, rồi tự chấm.

Cách dùng:
  python dung_tai_lieu.py <thư-mục-kết-quả> [--nguoi-soan "Tên bạn"] [--khong-pdf]

Đọc: noi_dung.json (agent viết), loi_thoai.txt, thong_tin.json, video.mp4
Tạo: <tên>.docx, <tên>.pdf (nếu được), hinh/*.jpg, tu_cham.txt
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

NAVY = RGBColor(0x0B, 0x2A, 0x5B)
ACCENT = RGBColor(0x12, 0x7F, 0xB5)
MUTED = RGBColor(0x5B, 0x64, 0x75)
FONT = "Arial"


def secs(ts: str) -> int | None:
    if not isinstance(ts, str) or not re.fullmatch(r"(\d{1,2}:)?\d{1,2}:\d{2}", ts.strip()):
        return None
    p = [int(x) for x in ts.strip().split(":")]
    return p[0] * 3600 + p[1] * 60 + p[2] if len(p) == 3 else p[0] * 60 + p[1]


def stamp(s: int) -> str:
    h, r = divmod(int(s), 3600)
    m, s = divmod(r, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def slug(text: str) -> str:
    import unicodedata
    text = unicodedata.normalize("NFD", text.replace("đ", "d").replace("Đ", "D"))
    text = "".join(c for c in text if unicodedata.category(c) != "Mn").lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")[:60] or "tai-lieu"


def run(par, text, size=None, bold=False, italic=False, color=None):
    r = par.add_run(text)
    r.font.name = FONT
    r._element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    if size:
        r.font.size = Pt(size)
    r.bold, r.italic = bold, italic
    if color is not None:
        r.font.color.rgb = color
    return r


def link(par, url, text, size=9):
    rid = par.part.relate_to(url, RT.HYPERLINK, is_external=True)
    h = OxmlElement("w:hyperlink")
    h.set(qn("r:id"), rid)
    r = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    for tag, val in (("w:rFonts", None), ("w:color", "127FB5"), ("w:sz", str(size * 2)), ("w:u", "single")):
        el = OxmlElement(tag)
        if tag == "w:rFonts":
            el.set(qn("w:ascii"), FONT)
            el.set(qn("w:hAnsi"), FONT)
        else:
            el.set(qn("w:val"), val)
        rpr.append(el)
    r.append(rpr)
    t = OxmlElement("w:t")
    t.text = text
    r.append(t)
    h.append(r)
    par._p.append(h)


def shade(par, fill="EEF5FB"):
    ppr = par._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    ppr.append(shd)


def rule(par, color="127FB5", size="12"):
    ppr = par._p.get_or_add_pPr()
    bdr = OxmlElement("w:pBdr")
    b = OxmlElement("w:bottom")
    for k, v in (("val", "single"), ("sz", size), ("space", "4"), ("color", color)):
        b.set(qn(f"w:{k}"), v)
    bdr.append(b)
    ppr.append(bdr)


def field(par, code):
    f = OxmlElement("w:fldSimple")
    f.set(qn("w:instr"), code)
    r = OxmlElement("w:r")
    t = OxmlElement("w:t")
    t.text = "1"
    r.append(t)
    f.append(r)
    par._p.append(f)


def heading(doc, text, level):
    p = doc.add_heading(level=level)
    run(p, text, size={1: 18, 2: 13.5, 3: 12}[level], bold=True, color=NAVY)
    p.paragraph_format.space_before = Pt(16 if level == 1 else 12)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    if level == 1:
        rule(p)
    return p


def body(doc, text, italic=False, color=None):
    p = doc.add_paragraph()
    run(p, text, size=11, italic=italic, color=color)
    p.paragraph_format.space_after = Pt(7)
    p.paragraph_format.line_spacing = 1.3
    return p


def bullets(doc, items, style="List Bullet"):
    for it in items:
        p = doc.add_paragraph(style=style)
        run(p, it, size=11)
        p.paragraph_format.space_after = Pt(3)


def video_link(base: str, s: int) -> str | None:
    if not base:
        return None
    return f"{base}{'&' if '?' in base else '?'}t={s}s"


def grab(video: Path, s: int, dest: Path) -> bool:
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", str(s), "-i", str(video),
                    "-frames:v", "1", "-vf", "scale=1280:-2", "-q:v", "3", str(dest)], check=False)
    return dest.exists() and dest.stat().st_size > 0


def to_pdf(docx: Path) -> Path | None:
    pdf = docx.with_suffix(".pdf")
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if soffice:
        subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", str(docx.parent), str(docx)],
                       capture_output=True, timeout=300)
    elif platform.system() == "Darwin" and Path("/Applications/Pages.app").exists():
        script = (f'tell application "Pages"\nset d to open POSIX file "{docx}"\ndelay 2\n'
                  f'export d to POSIX file "{pdf}" as PDF\nclose d saving no\nend tell')
        subprocess.run(["osascript", "-e", script], capture_output=True, timeout=300)
    return pdf if pdf.exists() else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("thu_muc")
    ap.add_argument("--nguoi-soan", default="")
    ap.add_argument("--khong-pdf", action="store_true")
    a = ap.parse_args()
    out = Path(a.thu_muc).resolve()
    nd = json.loads((out / "noi_dung.json").read_text(encoding="utf-8"))
    info = json.loads((out / "thong_tin.json").read_text(encoding="utf-8"))
    transcript = (out / "loi_thoai.txt").read_text(encoding="utf-8")
    valid = {secs(t) for t in re.findall(r"^\[((?:\d{2}:)?\d{2}:\d{2})\]", transcript, re.M)}
    duration = info.get("thoi_luong_giay") or max(valid or {0})
    base = info.get("link", "")
    warnings: list[str] = []

    doc = Document()
    sec = doc.sections[0]
    sec.left_margin = sec.right_margin = Inches(1)
    sec.top_margin = sec.bottom_margin = Inches(0.9)
    title = nd.get("tieu_de") or info.get("tieu_de", "Tài liệu từ video")

    # Bìa
    for _ in range(5):
        doc.add_paragraph()
    p = doc.add_paragraph()
    run(p, "TÀI LIỆU HỌC TẬP TỪ VIDEO", size=10, bold=True, color=ACCENT)
    p = doc.add_paragraph()
    run(p, title, size=28, bold=True, color=NAVY)
    p.paragraph_format.space_after = Pt(10)
    if nd.get("phu_de"):
        p = doc.add_paragraph()
        run(p, nd["phu_de"], size=13, color=MUTED)
    rule(doc.add_paragraph(), size="18")
    meta = [f"Nguồn: {info.get('tieu_de', '')}" + (f" — {info['kenh']}" if info.get("kenh") else ""),
            f"Thời lượng video: {stamp(duration)}"]
    meta.append(f"Biên soạn bằng AI Agent{' · ' + a.nguoi_soan if a.nguoi_soan else ''} · {dt.date.today():%d/%m/%Y}")
    for line in meta:
        p = doc.add_paragraph()
        run(p, line, size=10.5, color=MUTED)
    if base:
        p = doc.add_paragraph()
        link(p, base, base, size=10)
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    # Đầu trang, chân trang
    hp = sec.header.paragraphs[0]
    run(hp, title, size=8.5, color=MUTED)
    fp = sec.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run(fp, "Trang ", size=8.5, color=MUTED)
    field(fp, "PAGE")

    chapters = nd.get("chuong", [])
    heading(doc, "Mục lục", 1)
    for i, ch in enumerate(chapters, 1):
        p = doc.add_paragraph()
        run(p, f"Chương {i} · {ch.get('tieu_de', '')}", size=11, bold=True, color=NAVY)
        if ch.get("moc"):
            run(p, f"   {ch['moc']}", size=9.5, color=MUTED)
        for j, m in enumerate(ch.get("muc", []), 1):
            q = doc.add_paragraph()
            q.paragraph_format.left_indent = Inches(0.3)
            q.paragraph_format.space_after = Pt(1)
            run(q, f"{i}.{j}  {m.get('tieu_de', '')}", size=10)
    for name in ("Thuật ngữ", "Điểm cần ghi nhớ", "Câu hỏi ôn tập"):
        p = doc.add_paragraph()
        run(p, name, size=11, bold=True, color=NAVY)
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    heading(doc, "Tổng quan", 1)
    for para in re.split(r"\n\s*\n", nd.get("tong_quan", "").strip()):
        if para.strip():
            body(doc, para.strip())
    if nd.get("y_chinh"):
        heading(doc, "Ý chính", 2)
        bullets(doc, nd["y_chinh"])

    words = 0
    images = 0
    last_moc = 0
    sections_without_moc = 0
    (out / "hinh").mkdir(exist_ok=True)
    for old in (out / "hinh").glob("*.jpg"):
        old.unlink()
    video = out / "video.mp4"
    for i, ch in enumerate(chapters, 1):
        p = heading(doc, f"Chương {i} · {ch.get('tieu_de', '')}", 1)
        p.paragraph_format.page_break_before = True
        if ch.get("mo_dau"):
            body(doc, ch["mo_dau"], italic=True, color=MUTED)
        for j, m in enumerate(ch.get("muc", []), 1):
            heading(doc, f"{i}.{j}  {m.get('tieu_de', '')}", 2)
            s = secs(m.get("moc", ""))
            if s is None:
                sections_without_moc += 1
                warnings.append(f"Mục {i}.{j} thiếu mốc thời gian hợp lệ")
            else:
                last_moc = max(last_moc, s)
                p = doc.add_paragraph()
                run(p, "▶ Xem trong video: ", size=9, color=MUTED)
                url = video_link(base, s)
                if url:
                    link(p, url, stamp(s))
                else:
                    run(p, stamp(s), size=9, color=MUTED)
            pending = []
            for h in m.get("hinh", []):
                hs = secs(h.get("moc", ""))
                if hs is None or (valid and hs not in valid) or hs >= max(duration, 1):
                    warnings.append(f"Bỏ hình mục {i}.{j}: mốc '{h.get('moc')}' không có trong lời thoại")
                    continue
                pending.append((hs, h))
            pending.sort(key=lambda x: x[0])
            doans = m.get("doan", [])
            for k, d in enumerate(doans):
                text = d.get("noi_dung", "") if isinstance(d, dict) else str(d)
                body(doc, text)
                words += len(text.split())
                if isinstance(d, dict) and secs(d.get("moc", "")) is not None:
                    last_moc = max(last_moc, secs(d["moc"]))
                nxt = secs(doans[k + 1].get("moc", "")) if k + 1 < len(doans) and isinstance(doans[k + 1], dict) else None
                while pending and (nxt is None or pending[0][0] < nxt):
                    hs, h = pending.pop(0)
                    images += 1
                    img = out / "hinh" / f"hinh-{images:02d}-{stamp(hs).replace(':', '')}.jpg"
                    if not grab(video, hs, img):
                        warnings.append(f"Không chụp được hình tại {stamp(hs)}")
                        images -= 1
                        continue
                    doc.add_picture(str(img), width=Inches(6.2))
                    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
                    cap = doc.add_paragraph()
                    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    run(cap, f"Hình {images}. {h.get('tieu_de', '')}", size=9, bold=True, color=MUTED)
                    if h.get("chu_thich"):
                        run(cap, f" — {h['chu_thich']}", size=9, color=MUTED)
                    run(cap, f" ({stamp(hs)})", size=9, color=MUTED)
        if ch.get("tom_tat"):
            p = doc.add_paragraph()
            run(p, "TÓM TẮT CHƯƠNG", size=9.5, bold=True, color=ACCENT)
            shade(p)
            for t in ch["tom_tat"]:
                q = doc.add_paragraph()
                run(q, "•  " + t, size=10.5)
                shade(q)
                q.paragraph_format.space_after = Pt(0)

    terms = nd.get("thuat_ngu", [])
    if terms:
        heading(doc, "Thuật ngữ", 1).paragraph_format.page_break_before = True
        table = doc.add_table(rows=1, cols=2)
        table.style = "Light Grid Accent 1"
        for cell, txt in zip(table.rows[0].cells, ("Thuật ngữ", "Giải thích")):
            cell.paragraphs[0].text = ""
            run(cell.paragraphs[0], txt, size=10, bold=True)
        for t in terms:
            row = table.add_row().cells
            run(row[0].paragraphs[0], t.get("tu", ""), size=10, bold=True)
            run(row[1].paragraphs[0], t.get("giai_thich", ""), size=10)
    if nd.get("ghi_nho"):
        heading(doc, "Điểm cần ghi nhớ", 1)
        bullets(doc, nd["ghi_nho"])
    questions = nd.get("cau_hoi", [])
    if questions:
        heading(doc, "Câu hỏi ôn tập", 1)
        bullets(doc, questions, style="List Number")

    name = slug(title)
    docx_path = out / f"{name}.docx"
    doc.save(docx_path)
    pdf_path = None if a.khong_pdf else to_pdf(docx_path)

    minutes = max(duration / 60, 1)
    sections = sum(len(c.get("muc", [])) for c in chapters)
    checks = [
        ("Đủ nội dung (≥ 70 chữ / phút video)", words / minutes >= 70, f"{words} chữ, {words / minutes:.0f} chữ/phút"),
        ("Phủ hết video (mục cuối ≥ 85% thời lượng)", last_moc >= 0.85 * duration - 60, f"mốc cuối {stamp(last_moc)} / {stamp(duration)}"),
        ("Mỗi mục có mốc thời gian", sections_without_moc == 0, f"{sections - sections_without_moc}/{sections} mục"),
        ("Có hình minh hoạ (≥ 1 hình / 5 phút)", images >= max(1, int(minutes // 5)), f"{images} hình"),
        ("Có thuật ngữ (≥ 5)", len(terms) >= 5, f"{len(terms)} thuật ngữ"),
        ("Có câu hỏi ôn tập (≥ 5)", len(questions) >= 5, f"{len(questions)} câu"),
    ]
    report = ["BẢNG TỰ CHẤM", *(f"[{'ĐẠT' if ok else 'CHƯA ĐẠT'}] {name_}: {detail}" for name_, ok, detail in checks)]
    if warnings:
        report += ["", "Cảnh báo:", *("- " + w for w in warnings)]
    (out / "tu_cham.txt").write_text("\n".join(report), encoding="utf-8")
    print("\n".join(report))
    print(f"\nWORD: {docx_path}")
    print(f"PDF: {pdf_path or 'không tạo được (máy không có Pages/LibreOffice) — mở file Word rồi Xuất PDF'}")
    print(f"HÌNH: {out / 'hinh'} ({images} hình)")
    print(f"{len(chapters)} chương, {sections} mục")
    if not all(ok for _, ok, _ in checks):
        sys.exit(2)


if __name__ == "__main__":
    main()
