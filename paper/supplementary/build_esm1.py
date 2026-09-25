"""Build the submission-facing evidence matrix PDF from the Markdown source."""

from __future__ import annotations

import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "ESM_1_evidence_matrix.md"
OUTPUT = ROOT / "ESM_1_evidence_matrix.pdf"
TEXT = SOURCE.read_text(encoding="utf-8")

pdfmetrics.registerFont(TTFont("Arial", r"C:\Windows\Fonts\arial.ttf"))
pdfmetrics.registerFont(TTFont("ArialBold", r"C:\Windows\Fonts\arialbd.ttf"))


def markup(value: str) -> str:
    """Convert the small Markdown subset used here to ReportLab markup."""
    links: list[tuple[str, str]] = []

    def hold_link(match: re.Match[str]) -> str:
        links.append((match.group(1), match.group(2)))
        return f"ZZLINK{len(links) - 1}ZZ"

    value = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", hold_link, value)
    value = html.escape(value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", value)
    value = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", value)
    value = re.sub(r"`([^`]+)`", r"<font face='Courier'>\1</font>", value)
    for n, (label, url) in enumerate(links):
        safe_label = html.escape(label)
        safe_url = html.escape(url, quote=True)
        value = value.replace(f"ZZLINK{n}ZZ", f"<link href='{safe_url}' color='#145c7a'>{safe_label}</link>")
    return value


body = ParagraphStyle(
    "body", fontName="Arial", fontSize=9.1, leading=12.4, textColor=colors.HexColor("#243344"), spaceAfter=7
)
small = ParagraphStyle(
    "small", parent=body, fontSize=8.0, leading=10.4, spaceAfter=0
)
title = ParagraphStyle(
    "title", parent=body, fontName="ArialBold", fontSize=16, leading=19, spaceAfter=10
)
heading = ParagraphStyle(
    "heading", parent=body, fontName="ArialBold", fontSize=11, leading=14, spaceBefore=14, spaceAfter=6
)
cell = ParagraphStyle("cell", parent=small, fontSize=7.8, leading=10.1)
cell_center = ParagraphStyle("center", parent=cell, alignment=TA_CENTER, fontName="ArialBold")

lines = TEXT.splitlines()
table_start = next(i for i, line in enumerate(lines) if line.startswith("| Study (role)"))
table_end = next(i for i in range(table_start + 2, len(lines)) if not lines[i].startswith("|"))
rows = []
for line in [lines[table_start], *lines[table_start + 2 : table_end]]:
    values = [part.strip() for part in line.strip().strip("|").split("|")]
    if len(values) != 7:
        raise ValueError(f"Expected seven matrix columns: {values}")
    rows.append([Paragraph(markup(v), cell_center if j >= 3 else cell) for j, v in enumerate(values)])
if len(rows) != 21:
    raise ValueError(f"Expected 20 studies, found {len(rows) - 1}")

story = []
for line in lines[:table_start]:
    if not line.strip():
        continue
    if line.startswith("# "):
        story.append(Paragraph(markup(line[2:]), title))
    elif line.startswith("## "):
        story.append(Paragraph(markup(line[3:]), heading))
    else:
        story.append(Paragraph(markup(line), body))

matrix = Table(rows, colWidths=[191, 239, 515, 34, 34, 34, 34], repeatRows=1, hAlign="LEFT")
matrix.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dce9ed")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f8f9")]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LINEBELOW", (0, 0), (-1, 0), 0.7, colors.HexColor("#557783")),
            ("LINEBELOW", (0, -1), (-1, -1), 0.5, colors.HexColor("#557783")),
        ]
    )
)
story.extend([Spacer(1, 8), matrix, PageBreak()])
for line in lines[table_end:]:
    if not line.strip():
        continue
    if line.startswith("## "):
        story.append(Paragraph(markup(line[3:]), heading))
    else:
        story.append(Paragraph(markup(line), body))


def footer(canvas, document):
    canvas.saveState()
    canvas.setFont("Arial", 8)
    canvas.setFillColor(colors.HexColor("#667785"))
    canvas.drawString(36, 22, "Online Resource 1 · Evidence matrix · 23 September 2026")
    canvas.drawRightString(1154, 22, f"Page {document.page}")
    canvas.restoreState()


doc = SimpleDocTemplate(
    str(OUTPUT), pagesize=landscape(A3), leftMargin=36, rightMargin=36, topMargin=34, bottomMargin=40,
    title="Online Resource 1: Primary-study evidence matrix", author="AIR manuscript author team",
)
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(f"Created {OUTPUT} with {len(rows) - 1} studies")
