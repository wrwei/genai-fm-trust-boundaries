"""Render the bounded AMR case's two evidence paths as a manuscript figure."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
OUT = HERE / "amr_evidence_chain.png"
W, H = 1880, 850
im = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(im)
regular = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 31)
small = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 25)
bold = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 32)
lane = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 27)
ink = "#193244"
blue = "#dcecf2"
blue_edge = "#376880"
green = "#e2efe5"
green_edge = "#40825c"
amber = "#fff2d8"
amber_edge = "#9c7732"


def box(x0, y0, x1, y1, lines, fill=blue, edge=blue_edge):
    d.rounded_rectangle((x0, y0, x1, y1), radius=19, fill=fill, outline=edge, width=4)
    heights = [d.textbbox((0, 0), line, font=bold if i == 0 else small)[3] for i, line in enumerate(lines)]
    total = sum(heights) + 9 * (len(lines) - 1)
    y = (y0 + y1 - total) // 2
    for i, line in enumerate(lines):
        font = bold if i == 0 else small
        width = d.textbbox((0, 0), line, font=font)[2]
        d.text(((x0 + x1 - width) // 2, y), line, fill=ink, font=font)
        y += heights[i] + 9


def arrow(x0, y0, x1, y1, color=blue_edge):
    d.line((x0, y0, x1, y1), fill=color, width=5)
    if x1 >= x0:
        points = [(x1, y1), (x1 - 17, y1 - 10), (x1 - 17, y1 + 10)]
    else:
        points = [(x1, y1), (x1 - 10, y1 - 17), (x1 + 10, y1 - 17)]
    d.polygon(points, fill=color)


def tag(x, y, number, caption):
    d.rounded_rectangle((x, y, x + 50, y + 50), radius=15, fill=amber, outline=amber_edge, width=3)
    d.text((x + 15, y + 8), str(number), fill=ink, font=bold)
    d.text((x + 62, y + 9), caption, fill=ink, font=small)


d.text((52, 27), "Bounded mobile-robot evidence chain", fill=ink, font=bold)
d.text((52, 103), "DESIGN TIME", fill=blue_edge, font=lane)
d.text((52, 440), "RUN TIME", fill=green_edge, font=lane)
d.line((52, 417, 1820, 417), fill="#bbccd3", width=3)

box(60, 166, 340, 328, ["DeepSeek", "candidate source"])
box(435, 166, 745, 328, ["Contract", "1,824 inputs"])
box(840, 166, 1180, 328, ["Selected source", "P3-R1 bytes"], green, green_edge)
box(1280, 166, 1600, 328, ["Extractor", "restricted profile"])
box(1660, 166, 1830, 328, ["Model", "+ proof"])
for x0, x1 in [(340, 435), (745, 840), (1180, 1280), (1600, 1660)]:
    arrow(x0 + 7, 247, x1 - 10, 247)
tag(516, 345, 1, "requirement to source")
tag(1310, 345, 2, "source to model")

box(60, 500, 350, 660, ["DeepSeek", "advice: A or B"], amber, amber_edge)
box(440, 500, 725, 660, ["Adapter", "typed, bound reply"], green, green_edge)
box(810, 500, 1110, 660, ["Source", "final selection"], green, green_edge)
box(1190, 500, 1490, 660, ["Protocol", "Validate / Commit", "/ Apply"], green, green_edge)
box(1570, 500, 1830, 660, ["Plant", "reference route"], blue, blue_edge)
for x0, x1 in [(350, 440), (725, 810), (1110, 1190), (1490, 1570)]:
    arrow(x0 + 7, 580, x1 - 10, 580, green_edge)
arrow(1000, 340, 1000, 488, green_edge)
tag(395, 689, 3, "advice to authority")
tag(1060, 689, 4, "protocol to physical meaning")
tag(1412, 761, 5, "progress to completion")

im.save(OUT, dpi=(300, 300))
print(OUT)
