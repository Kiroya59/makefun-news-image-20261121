#!/usr/bin/env python3
"""Draw the rev-2 front page for news-image-20261121.

A one-day newspaper front page, 1024x1024 PNG, rendered with PIL in a
flat editorial style. One generated photograph (no text in it) illustrates
the lead story; every headline, standfirst, caption and figure on the
page is vector text drawn by PIL, so a reader can actually read it.

All copy lives in the SECTIONS table below: one line per headline, one
line per standfirst. Before anything is drawn, every string is measured
against the column it will sit in; a string that would not fit stops the
build instead of being clipped.

Run:  python3 compose.py   (writes image.png next to this file)
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageOps

BASE = os.path.dirname(os.path.abspath(__file__))
PHOTO = os.path.join(
    BASE, "work", "photos",
    "media-generation-cop31-antalya-hall-0-cf6ddb49-727e-4a0f-90fb-a5586e668f2a.webp")
TARGET = os.path.join(BASE, "image.png")

PAGE = 1024
BG = (248, 244, 236)
FG = (22, 22, 22)
SUB_FG = (60, 58, 52)
MUTED = (110, 108, 100)
NAVY = (20, 38, 74)
SCARLET = (176, 42, 30)
FAINT = (215, 210, 200)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def load(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


MASTHEAD = load("DejaVuSerif-Bold.ttf", 46)
DATELINE = load("DejaVuSans-Bold.ttf", 13)
KICKER = load("DejaVuSans-Bold.ttf", 13)
LEADLINE = load("DejaVuSerif-Bold.ttf", 28)
LEADSTAND = load("DejaVuSans.ttf", 14)
SECTHEAD = load("DejaVuSans-Bold.ttf", 14)
HEADLINE = load("DejaVuSerif-Bold.ttf", 15)
STAND = load("DejaVuSans.ttf", 12)
SMALL = load("DejaVuSans.ttf", 11)
BIGFIG = load("DejaVuSans-Bold.ttf", 12)

# (section title, [(headline, standfirst), ...]) — 31 stories + lead.
SECTIONS = [
    ("EUROPE", [
        ("GEN Z FLOODS EUROPE'S STREETS",
         "Youth strike in 25+ nations over costs."),
        ("POLAND SEEKS MORE NATO JETS",
         "Warsaw asks allies for air defence."),
        ("UKRAINE RETAKES 204 SQ KM",
         "14 settlements freed in Bear Trap push."),
        ("RUSSIA FIRES 148 DRONES",
         "Overnight strikes hit 19 sites in Ukraine."),
        ("GREECE-ISRAEL IN \u20ac1B TALKS",
         "Defence deals worth up to \u20ac1 billion."),
    ]),
    ("AMERICAS", [
        ("M6.8 QUAKE SHAKES PERU",
         "Junin tremor felt in Lima; no deaths yet."),
        ("TRUMP: BRING HUANG BACK",
         "President urges Nvidia board to reinstate ex-CEO."),
        ("BESSENT: NO NEW CHIP CURBS",
         "No further limits on older Nvidia sales."),
        ("MAMDANI: RIKERS SHUT BY 2032",
         "NYC mayor sets new date to close jail."),
    ]),
    ("ASIA-PACIFIC", [
        ("INDIA SETS INFLOW RECORD",
         "Record foreign inflow into Indian shares."),
        ("NEPAL PM HEADS TO DELHI",
         "Balen Shah's first foreign trip since March."),
        ("M6.8 QUAKE HITS TIMOR",
         "Tremor north-east of Lospalos; no tsunami."),
        ("AIR NIUGINI JET LANDS SAFELY",
         "Emergency landing ends without injury."),
    ]),
    ("MIDDLE EAST & AFRICA", [
        ("EISENKOT INVITES LIKUD",
         "Ex-general seeks unity government in Israel."),
        ("THREE KILLED IN GAZA STRIKE",
         "Vehicle carrying aid papers hit in Gaza City."),
        ("ISRAEL PUSHES INTO SYRIA",
         "Troops enter Daraa and Quneitra districts."),
        ("HORMUZ COULD REOPEN SOON",
         "Iran FM: strait reopens if US meets terms."),
        ("SOMALIA EXPELS UAE ENVOY",
         "Diplomatic row deepens in the Horn of Africa."),
    ]),
    ("TECH & SCIENCE", [
        ("MUSK WARNS OF AI CASH CRUNCH",
         "Compute bills arrive long before revenue."),
        ("SPACEX CHIP LOANS IN DOUBT",
         "$43B chip deal stalls over space launch plan."),
        ("CURSOR DROPS CHINESE AI",
         "Coding platform cites geopolitical risk."),
        ("MARKETS SLIDE ON AI FEARS",
         "Nasdaq sell-off on AI and rate worries."),
    ]),
    ("SPORT & CULTURE", [
        ("ENGLAND 37, ALL BLACKS 12",
         "Record win over New Zealand; five tries."),
        ("IRELAND 20, SOUTH AFRICA 17",
         "Springboks reach final despite defeat."),
        ("FRANCE 45, ARGENTINA 17",
         "France face South Africa in 29 Nov final."),
        ("AUSTRALIA EDGE WALES 29-26",
         "Scotland thrash Japan 67-5; Fiji beat Italy."),
        ("KL RAHUL COMPLETES SENA SET",
         "First Indian opener with tons in all SENA lands."),
        ("LEEDS STUN CHELSEA 4-1",
         "Shock defeat piles pressure on the Blues."),
        ("SATWIK-CHIRAG EXIT IN SEMIS",
         "Indian pair lose semi in straight games."),
        ("INDIA A WIN BY 306 RUNS",
         "Tilak Varma and Kushagra hit tons in Doha."),
    ]),
]

# Which sections go in each of the three columns, in order.
COLUMNS = [[0, 1], [2, 3, 4], [5]]

LEAD_KICKER = "CLIMATE  \u2022  ANTALYA, TURKEY"
LEAD_HEADLINE = "COP31 TALKS RUN INTO OVERTIME"
LEAD_STAND = "Draft drops fossil fuels; 100 groups warn the summit is set to fail."
LEAD_NOTE = "Talks ran two days past their Friday deadline."
PHOTO_CREDIT = "The plenary hall, Antalya. (Illustration)"

QUOTE_LINES = [
    '"COP31 is in a bleak overtime, with dwindling food',
    'and water, and no sign of any progress."',
]
QUOTE_CREDIT = "- Rachel Cleetus, Union of Concerned Scientists"

# (figure, label) pairs for the numbers box.
FIGURES = [
    ("6.8", "Peru quake magnitude, Junin region"),
    ("148", "Russian drones fired at Ukraine overnight"),
    ("204 km\u00b2", "Land Ukraine says it retook"),
    ("\u20b91.22 lakh crore", "Record inflow to Indian shares"),
    ("37-12", "England's record win over the All Blacks"),
    ("$43B", "SpaceX chip financing in dispute"),
    ("100", "Groups warning COP31 is set to fail"),
]

FOOT_SOURCES = ("Compiled from Reuters, AP, BBC, Al Jazeera, "
                "The Verge and TechCrunch")
FOOT_DATE = ("All stories as reported on Saturday 21 November 2026  "
             "\u2022  Sport: Saturday's results")


def must_fit(canvas, text, face, width, label):
    if canvas.textlength(text, font=face) > width:
        print("TOO WIDE (%s): %r is %.0fpx, limit %dpx"
              % (label, text, canvas.textlength(text, font=face), width),
              file=sys.stderr)
        sys.exit(1)


def paint_section(canvas, left, top, width, title, items, floor):
    """Paint one navy section header plus its stories. Returns the y
    just below the last story rule."""
    canvas.rectangle([left, top, left + width, top + 24], fill=NAVY)
    canvas.text((left + 8, top + 4), title, font=SECTHEAD, fill="white")
    y = top + 29
    for head, stand in items:
        if y > floor - 20:
            print("OVERFLOW in %s at %r" % (title, head), file=sys.stderr)
            sys.exit(1)
        must_fit(canvas, head, HEADLINE, width, title + " headline")
        must_fit(canvas, stand, STAND, width, title + " standfirst")
        canvas.text((left, y), head, font=HEADLINE, fill=FG)
        canvas.text((left, y + 18), stand, font=STAND, fill=SUB_FG)
        y += 37
        canvas.line([left, y, left + width, y], fill=FAINT, width=1)
        y += 6
    return y


def paint_box_head(canvas, left, top, width, title):
    canvas.rectangle([left, top, left + width, top + 22], fill=SCARLET)
    canvas.text((left + 8, top + 3), title, font=SECTHEAD, fill="white")
    return top + 22


def build():
    page = Image.new("RGB", (PAGE, PAGE), BG)
    canvas = ImageDraw.Draw(page)

    # Masthead.
    canvas.text((PAGE // 2, 12), "THE WORLD IN ONE DAY", font=MASTHEAD,
                fill=NAVY, anchor="ma")
    canvas.text((PAGE // 2, 66),
                "SATURDAY, 21 NOVEMBER 2026  \u2022  31 STORIES FROM EVERY REGION",
                font=DATELINE, fill=FG, anchor="ma")
    canvas.line([28, 88, PAGE - 28, 88], fill=NAVY, width=3)
    canvas.line([28, 92, PAGE - 28, 92], fill=NAVY, width=1)

    # Lead story, left; photo, right.
    lx, ly, lw = 28, 100, 660
    canvas.text((lx, ly), LEAD_KICKER, font=KICKER, fill=SCARLET)
    must_fit(canvas, LEAD_HEADLINE, LEADLINE, lw, "lead headline")
    must_fit(canvas, LEAD_STAND, LEADSTAND, lw, "lead standfirst")
    canvas.text((lx, ly + 24), LEAD_HEADLINE, font=LEADLINE, fill=FG)
    canvas.text((lx, ly + 62), LEAD_STAND, font=LEADSTAND, fill=SUB_FG)
    canvas.text((lx, ly + 86), LEAD_NOTE, font=SMALL, fill=MUTED)

    px, py, pw, ph = 712, 100, 284, 142
    shot = ImageOps.fit(Image.open(PHOTO).convert("RGB"), (pw, ph),
                        method=Image.LANCZOS)
    page.paste(shot, (px, py))
    canvas.rectangle([px, py, px + pw - 1, py + ph - 1], outline=NAVY, width=1)
    canvas.text((px, py + ph + 6), PHOTO_CREDIT, font=SMALL, fill=MUTED)

    canvas.line([28, 268, PAGE - 28, 268], fill=NAVY, width=2)

    # Three columns of sections.
    margin, gutter = 28, 14
    col_w = (PAGE - 2 * margin - 2 * gutter) // 3
    xs = [margin, margin + col_w + gutter, margin + 2 * (col_w + gutter)]
    top, floor = 278, 962

    y = top
    for idx in COLUMNS[0]:
        title, items = SECTIONS[idx]
        y = paint_section(canvas, xs[0], y, col_w, title, items, floor)
        y += 4

    # Quote of the day, foot of column one.
    y = paint_box_head(canvas, xs[0], y + 2, col_w, "QUOTE OF THE DAY")
    for line in QUOTE_LINES:
        must_fit(canvas, line, STAND, col_w, "quote")
        y += 4
        canvas.text((xs[0], y), line, font=STAND, fill=FG)
        y += 16
    must_fit(canvas, QUOTE_CREDIT, SMALL, col_w, "quote credit")
    canvas.text((xs[0], y + 2), QUOTE_CREDIT, font=SMALL, fill=MUTED)
    y += 18
    if y > floor:
        print("OVERFLOW: quote box ends at y=%d, floor=%d" % (y, floor),
              file=sys.stderr)
        sys.exit(1)

    y = top
    for idx in COLUMNS[1]:
        title, items = SECTIONS[idx]
        y = paint_section(canvas, xs[1], y, col_w, title, items, floor)
        y += 4

    y = top
    for idx in COLUMNS[2]:
        title, items = SECTIONS[idx]
        y = paint_section(canvas, xs[2], y, col_w, title, items, floor)
        y += 4

    # By the numbers, foot of column three.
    y = paint_box_head(canvas, xs[2], y + 2, col_w, "BY THE NUMBERS")
    for figure, label in FIGURES:
        fig_w = canvas.textlength(figure, font=BIGFIG)
        lab_w = canvas.textlength(label, font=STAND)
        if fig_w + 6 + lab_w > col_w:
            print("TOO WIDE (numbers row): %r" % (figure + "  " + label,),
                  file=sys.stderr)
            sys.exit(1)
        y += 4
        canvas.text((xs[2], y), figure, font=BIGFIG, fill=FG)
        canvas.text((xs[2] + fig_w + 6, y), label, font=STAND, fill=FG)
        y += 16
    if y > floor:
        print("OVERFLOW: numbers box ends at y=%d, floor=%d" % (y, floor),
              file=sys.stderr)
        sys.exit(1)

    # Footer.
    canvas.line([28, 968, PAGE - 28, 968], fill=NAVY, width=2)
    canvas.text((PAGE // 2, 976), FOOT_SOURCES, font=SMALL, fill=MUTED,
                anchor="ma")
    canvas.text((PAGE // 2, 994), FOOT_DATE, font=SMALL, fill=MUTED,
                anchor="ma")

    page.save(TARGET, format="PNG", optimize=True)
    print("wrote %s  %s  %d bytes"
          % (TARGET, page.size, os.path.getsize(TARGET)))


if __name__ == "__main__":
    build()
