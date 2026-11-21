#!/usr/bin/env python3
"""Build-time composer for the news-image-20261121 front page.

Draws a 1024x1024 newspaper front page with PIL: a navy masthead, five
stories (four generated editorial photographs plus one drawn COP31
emblem), crisp vector headlines, and a footer strip of three briefs.
Deterministic: no network, no clock, no randomness. Writes image.png
next to this script.
"""

import glob
import hashlib
import os
import sys

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = os.path.dirname(os.path.abspath(__file__))
PHOTO_DIR = os.path.join(ROOT, "work", "photos")
OUT_PATH = os.path.join(ROOT, "image.png")

PAGE_W, PAGE_H = 1024, 1024
MARGIN = 16
CONTENT_W = PAGE_W - 2 * MARGIN

NAVY = (15, 42, 74)
NAVY_DARK = (10, 30, 54)
RED = (178, 34, 34)
TEAL = (14, 95, 92)
TEAL_DARK = (9, 66, 64)
GOLD = (201, 162, 39)
INK = (20, 20, 20)
GREY = (90, 90, 90)
PAPER = (250, 248, 243)
WHITE = (255, 255, 255)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SERIF_BOLD = lambda s: font("DejaVuSerif-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)
SANS_BOLD = lambda s: font("DejaVuSans-Bold.ttf", s)
SANS_ITALIC = lambda s: font("DejaVuSans-Oblique.ttf", s)


def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns a list of lines that fit in width."""
    lines, current = [], ""
    for word in text.split(" "):
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def fit_photo(name, width, height):
    """Load a photo by substring match and crop it to fill width x height."""
    matches = sorted(glob.glob(os.path.join(PHOTO_DIR, "*%s*.webp" % name)))
    if not matches:
        raise FileNotFoundError("no photo matching %r in %s" % (name, PHOTO_DIR))
    img = Image.open(matches[0]).convert("RGB")
    return ImageOps.fit(img, (width, height), method=Image.LANCZOS)


def draw_kicker(draw, x, y, text):
    fnt = SANS_BOLD(17)
    draw.text((x, y), text, font=fnt, fill=RED)


def draw_headline(draw, x, y, text, size, width, leading=None):
    fnt = SANS_BOLD(size)
    lead = leading or int(size * 1.12)
    lines = wrap(draw, text, fnt, width)
    for i, line in enumerate(lines):
        draw.text((x, y + i * lead), line, font=fnt, fill=INK)
    return y + len(lines) * lead


def draw_sub(draw, x, y, text, size, width, leading=None):
    fnt = SANS(size)
    lead = leading or int(size * 1.28)
    lines = wrap(draw, text, fnt, width)
    for i, line in enumerate(lines):
        draw.text((x, y + i * lead), line, font=fnt, fill=INK)
    return y + len(lines) * lead


def draw_rule(draw, y, weight=2):
    draw.rectangle([MARGIN, y, PAGE_W - MARGIN, y + weight - 1], fill=NAVY)


def draw_cop31_emblem(draw, box):
    """Drawn emblem for the COP31 story: teal panel, globe, COP31, Antalya."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=TEAL)
    draw.rectangle([x0, y0, x1, y0 + 4], fill=GOLD)
    cx, cy, r = x0 + 42, y0 + 52, 30
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 255), width=3)
    draw.ellipse([cx - 12, cy - r, cx + 12, cy + r], outline=(255, 255, 255), width=2)
    draw.line([cx - r, cy, cx + r, cy], fill=(255, 255, 255), width=2)
    draw.line([cx, cy - r, cx, cy + r], fill=(255, 255, 255), width=2)
    f_big = SANS_BOLD(40)
    label = "COP31"
    tw = draw.textlength(label, font=f_big)
    draw.text((x0 + (x1 - x0 - tw) / 2, y0 + 88), label, font=f_big, fill=WHITE)
    f_small = SANS_BOLD(16)
    sub = "ANTALYA"
    tw2 = draw.textlength(sub, font=f_small)
    draw.text((x0 + (x1 - x0 - tw2) / 2, y0 + 128), sub, font=f_small, fill=(210, 230, 228))


def build_page():
    page = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    draw = ImageDraw.Draw(page)

    # ---- Masthead ----
    draw.rectangle([0, 0, PAGE_W, 84], fill=NAVY)
    title = "THE WORLD IN ONE DAY"
    f_title = SERIF_BOLD(52)
    tw = draw.textlength(title, font=f_title)
    draw.text(((PAGE_W - tw) / 2, 14), title, font=f_title, fill=WHITE)
    draw.rectangle([0, 84, PAGE_W, 88], fill=GOLD)

    # ---- Dateline strip ----
    date_line = "SATURDAY  •  21 NOVEMBER 2026"
    f_date = SANS_BOLD(24)
    tw = draw.textlength(date_line, font=f_date)
    draw.text(((PAGE_W - tw) / 2, 92), date_line, font=f_date, fill=NAVY)
    draw_rule(draw, 122, weight=2)

    # ---- Lead story: Peru quake ----
    lead_y = 134
    photo = fit_photo("quake", 500, 292)
    page.paste(photo, (MARGIN, lead_y))
    tx = 532
    tw_col = PAGE_W - MARGIN - tx
    draw_kicker(draw, tx, lead_y, "PERU  •  EARTHQUAKE")
    y = draw_headline(draw, tx, lead_y + 28, "M6.8 QUAKE SHAKES PERU", 42, tw_col)
    draw_sub(draw, tx, y + 10,
             "Lima empties into the streets as the tremor rocks the Andes; "
             "rockfalls bury a coastal road. No casualties reported yet.",
             20, tw_col)

    draw_rule(draw, 440)

    # ---- Mid row: two photo stories ----
    mid_y = 452
    col_w = 488
    for x, name, kicker, headline, sub in [
        (MARGIN, "protests", "EUROPE  •  YOUTH PROTEST",
         "GEN Z FLOODS EUROPE'S STREETS",
         "Youth strike in 25 nations over living costs, schools and "
         "rearmament; rallies run into the weekend."),
        (MARGIN + col_w + 16, "chips", "TECH  •  NVIDIA",
         "TRUMP TO NVIDIA: BRING HUANG BACK",
         "\u201cGive him a second chance,\u201d the president says; board "
         "says no. US approved 900,000 AI chips for China."),
    ]:
        photo = fit_photo(name, col_w, 158)
        page.paste(photo, (x, mid_y))
        draw_kicker(draw, x, mid_y + 166, kicker)
        y = draw_headline(draw, x, mid_y + 188, headline, 27, col_w)
        draw_sub(draw, x, y + 6, sub, 17, col_w)

    draw_rule(draw, 748)

    # ---- Bottom row: Poland + COP31, thumb left, text right ----
    bot_y = 760
    thumb_w, thumb_h = 180, 150
    for x, name, kicker, headline, sub, emblem in [
        (MARGIN, "poland", "POLAND  •  WAR IN UKRAINE",
         "RUSSIAN MISSILE LANDS IN POLAND",
         "Tusk calls the crash a likely provocation as NATO jets scramble; "
         "8 killed in overnight strikes on Ukraine.", False),
        (MARGIN + col_w + 16, None, "CLIMATE  •  COP31",
         "COP31 DEAL STALLS",
         "Draft drops all mention of fossil fuels; talks in Antalya head "
         "into overtime.", True),
    ]:
        if emblem:
            draw_cop31_emblem(draw, (x, bot_y, x + thumb_w, bot_y + thumb_h))
        else:
            photo = fit_photo(name, thumb_w, thumb_h)
            page.paste(photo, (x, bot_y))
        tx2 = x + thumb_w + 12
        tw2 = x + col_w - tx2
        draw_kicker(draw, tx2, bot_y + 2, kicker)
        y = draw_headline(draw, tx2, bot_y + 24, headline, 24, tw2)
        draw_sub(draw, tx2, y + 6, sub, 16, tw2)

    # ---- Footer strip: three briefs ----
    draw.rectangle([0, 930, PAGE_W, PAGE_H], fill=NAVY_DARK)
    briefs = [
        ("CRICKET", "Rahul completes the SENA set, the first Indian opener "
         "with Test hundreds in all four SENA lands."),
        ("MARKETS", "A record \u20b91.22 lakh crore flows into Indian shares, "
         "the biggest monthly foreign inflow ever."),
        ("ISRAEL", "Eisenkot is tapped to form the next government, "
         "bypassing Netanyahu."),
    ]
    fy = 940
    for label, text in briefs:
        f_lab = SANS_BOLD(17)
        f_txt = SANS(17)
        draw.text((MARGIN, fy), label + "  \u2014  ", font=f_lab, fill=GOLD)
        lx = MARGIN + draw.textlength(label + "  \u2014  ", font=f_lab)
        draw.text((lx, fy), text, font=f_txt, fill=WHITE)
        fy += 26

    return page


def main():
    page = build_page()
    page.save(OUT_PATH, format="PNG", optimize=True)
    data = open(OUT_PATH, "rb").read()
    print("wrote %s  %d bytes  sha256 %s"
          % (OUT_PATH, len(data), hashlib.sha256(data).hexdigest()))
    if len(data) > 1048576:
        print("WARNING: over the 1 MiB limit", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
