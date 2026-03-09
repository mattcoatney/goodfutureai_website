#!/usr/bin/env python3
"""
gen_images.py
─────────────
Generates all logo and podcast-cover image assets for GoodFuture.ai.

Outputs to images/ directory (relative to repo root):
  Logomark (circle + GF):
    logomark-on-light.png           teal circle on warm-light bg
    logomark-on-dark.png            teal circle on deep-horizon bg
    logomark-transparent-dark.png   teal circle, transparent (for dark backgrounds)
    logomark-transparent-light.png  teal circle, transparent (for light backgrounds)
    logomark-gold.png               gold circle, transparent

  Wordmark (GoodFuture.ai text + arc):
    wordmark-on-light.png
    wordmark-on-dark.png
    wordmark-transparent-dark-text.png   light text, transparent
    wordmark-transparent-light-text.png  dark text, transparent
    wordmark-monochrome-light.png        all light text, transparent
    wordmark-monochrome-dark.png         all dark text, transparent

  Full logo (circle + wordmark side by side):
    logo-full-on-light.png
    logo-full-on-dark.png
    logo-full-transparent-light.png
    logo-full-transparent-dark.png

  Podcast covers:
    podcast-cover-3000.png
    podcast-cover-1400.png

Usage:
    python scripts/gen_images.py
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT  = ROOT / "images"
F    = "C:/Windows/Fonts/"

# ── Brand colours ──────────────────────────────────────────────────────────
DEEP  = (15,  46,  61,  255)
GOLD  = (242, 169, 59,  255)
TEAL  = (59,  165, 165, 255)
CORAL = (232, 93,  74,  255)
LIGHT = (251, 246, 239, 255)
TRANS = (0,   0,   0,   0)

def gfont(s):  return ImageFont.truetype(F + "georgiab.ttf", s)
def sfont(s):  return ImageFont.truetype(F + "calibrib.ttf",  s)
def sfontr(s): return ImageFont.truetype(F + "calibri.ttf",   s)


# ── Geometry helpers ────────────────────────────────────────────────────────
def arc_pts(x0, y0, x1, y1, peak_y, steps=120):
    mx = (x0 + x1) / 2
    return [((1-t)**2*x0 + 2*(1-t)*t*mx + t**2*x1,
              (1-t)**2*y0 + 2*(1-t)*t*peak_y + t**2*y1)
            for t in (i/steps for i in range(steps+1))]


def measure(fnt, parts):
    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    x, pos = 0, {}
    for p in parts:
        b = probe.textbbox((x, 0), p, font=fnt)
        pos[p] = b
        x += b[2] - b[0]
    return pos, x


def draw_crisp_arc(base_img, x0, y0, x1, y1, peak_y, color_rgb, stroke_w, supersample=4):
    all_x = [p[0] for p in arc_pts(x0, y0, x1, y1, peak_y)]
    all_y = [p[1] for p in arc_pts(x0, y0, x1, y1, peak_y)]
    pad = stroke_w * supersample + 4
    bx0 = max(0, int(min(all_x)) - pad)
    by0 = max(0, int(min(all_y)) - pad)
    bx1 = min(base_img.width,  int(max(all_x)) + pad)
    by1 = min(base_img.height, int(max(all_y)) + pad)
    bw, bh = bx1 - bx0, by1 - by0
    if bw <= 0 or bh <= 0:
        return
    S = supersample
    hi = Image.new("RGBA", (bw * S, bh * S), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hi)
    pts = arc_pts((x0 - bx0) * S, (y0 - by0) * S,
                  (x1 - bx0) * S, (y1 - by0) * S,
                  (peak_y - by0) * S)
    for i in range(len(pts) - 1):
        hd.line([pts[i], pts[i+1]], fill=(*color_rgb, 255), width=stroke_w * S)
    lo = hi.resize((bw, bh), Image.LANCZOS)
    base_img.paste(lo, (bx0, by0), lo)


# ── Wordmark builder ────────────────────────────────────────────────────────
def make_wordmark(bg_rgba, text_rgb, ai_rgb, arc_rgb, fnt_size=60, pad_x=20):
    """
    Returns an RGBA Image of the wordmark.
    bg_rgba  — background colour (use (0,0,0,0) for transparent)
    text_rgb — colour for 'GoodFuture' text
    ai_rgb   — colour for '.ai'
    arc_rgb  — colour for the arc
    """
    fnt    = gfont(fnt_size)
    parts  = ["GoodFut", "ur", "e", ".ai"]
    pos, total_w = measure(fnt, parts)

    lc_top_off  = pos["ur"][1]       # top of lowercase glyphs
    bottom_off  = pos["GoodFut"][3]  # bottom of text

    arc_gap  = 3
    arc_rise = 29
    pad_top  = arc_gap + arc_rise + 4

    draw_y   = pad_top
    arc_y    = draw_y + lc_top_off - arc_gap
    arc_peak = arc_y - arc_rise

    canvas_w = total_w + pad_x * 2
    canvas_h = draw_y + bottom_off + 12

    img  = Image.new("RGBA", (canvas_w, canvas_h), bg_rgba)
    draw = ImageDraw.Draw(img)

    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    tx = pad_x
    ur_x0 = ur_x1 = 0
    for p in parts:
        col = ai_rgb if p == ".ai" else text_rgb
        pb  = probe.textbbox((tx, draw_y), p, font=fnt)
        if p == "ur":
            ur_x0, ur_x1 = pb[0], pb[2]
        draw.text((tx, draw_y), p, fill=col, font=fnt)
        tx += pos[p][2] - pos[p][0]

    draw_crisp_arc(img, ur_x0 - 2, arc_y, ur_x1 + 2, arc_y, arc_peak,
                   arc_rgb, stroke_w=2, supersample=4)
    return img


# ── Logomark builder ────────────────────────────────────────────────────────
def make_logomark(size, bg_rgba, circle_rgb, text_rgb, circle_alpha=255):
    """
    Returns a square RGBA Image with the GF circle mark.
    size        — canvas size (square)
    bg_rgba     — background (use TRANS for transparent)
    circle_rgb  — circle fill colour
    text_rgb    — GF text colour
    """
    r   = int(size * 0.40)
    cx  = cy = size // 2
    fnt = gfont(int(r * 0.72))

    img  = Image.new("RGBA", (size, size), bg_rgba)
    draw = ImageDraw.Draw(img)

    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(*circle_rgb[:3], circle_alpha))

    bb = draw.textbbox((0, 0), "GF", font=fnt)
    draw.text((cx - (bb[2]-bb[0])//2 - bb[0],
               cy - (bb[3]-bb[1])//2 - bb[1]),
              "GF", fill=(*text_rgb[:3], 255), font=fnt)
    return img


# ── Full logo (logomark left + wordmark right) ──────────────────────────────
def make_full_logo(bg_rgba, lm_bg, lm_circle, lm_text,
                   wm_text, wm_ai, wm_arc, gap=24, fnt_size=60, lm_size=None):
    """Combine logomark and wordmark side-by-side."""
    wm = make_wordmark(TRANS, wm_text, wm_ai, wm_arc, fnt_size=fnt_size)
    if lm_size is None:
        lm_size = wm.height
    lm = make_logomark(lm_size, TRANS, lm_circle, lm_text)

    total_w = lm.width + gap + wm.width
    total_h = max(lm.height, wm.height)

    img = Image.new("RGBA", (total_w, total_h), bg_rgba)
    # Center logomark vertically
    lm_y = (total_h - lm.height) // 2
    img.paste(lm, (0, lm_y), lm)
    # Center wordmark vertically
    wm_y = (total_h - wm.height) // 2
    img.paste(wm, (lm.width + gap, wm_y), wm)
    return img


# ── Podcast cover builder ───────────────────────────────────────────────────
def make_podcast_cover(S=1400):
    img   = Image.new("RGB", (S, S), DEEP[:3])
    adraw = ImageDraw.Draw(img, "RGBA")

    arc_cx, arc_cy = S // 2, int(S * 0.80)
    for r_frac, col, a, w_frac in [
        (1.60, GOLD,  10, 0.004), (1.35, GOLD,  18, 0.005),
        (1.10, GOLD,  26, 0.006), (0.88, TEAL,  22, 0.005),
        (0.68, TEAL,  30, 0.006), (0.50, GOLD,  35, 0.007),
        (0.35, CORAL, 25, 0.006), (0.22, TEAL,  20, 0.005),
        (1.85, TEAL,   8, 0.003),
    ]:
        r = int(S * r_frac)
        w = max(2, int(S * w_frac))
        adraw.arc([arc_cx-r, arc_cy-r, arc_cx+r, arc_cy+r],
                  start=195, end=345, fill=(*col[:3], a), width=w)

    draw = ImageDraw.Draw(img)

    # GF logomark
    lm_r   = int(S * 0.085)
    lm_cx  = S // 2
    lm_cy  = int(S * 0.175)
    lm_fnt = gfont(int(lm_r * 0.72))
    draw.ellipse([lm_cx-lm_r-8, lm_cy-lm_r-8, lm_cx+lm_r+8, lm_cy+lm_r+8],
                 fill=(*GOLD[:3], 40))
    draw.ellipse([lm_cx-lm_r, lm_cy-lm_r, lm_cx+lm_r, lm_cy+lm_r],
                 fill=(*TEAL[:3],))
    bb = draw.textbbox((0, 0), "GF", font=lm_fnt)
    draw.text((lm_cx - (bb[2]-bb[0])//2 - bb[0],
               lm_cy - (bb[3]-bb[1])//2 - bb[1]),
              "GF", fill=LIGHT[:3], font=lm_fnt)

    lm_bottom = lm_cy + lm_r

    # THE and PODCAST — same font/size
    label_fnt = sfont(int(S * 0.040))
    bb_the    = draw.textbbox((0, 0), "THE",     font=label_fnt)
    bb_pod    = draw.textbbox((0, 0), "PODCAST", font=label_fnt)
    label_h   = bb_the[3] - bb_the[1]

    # GoodFuture.ai title
    title_fnt = gfont(int(S * 0.095))
    parts     = ["GoodFuture", ".ai"]
    tcolors   = [LIGHT[:3], TEAL[:3]]
    tpos, total_tw = measure(title_fnt, parts)
    cap_top_off  = tpos["GoodFuture"][1]
    bottom_off   = tpos["GoodFuture"][3]

    gap_A = int(S * 0.050)   # circle → THE
    gap_B = int(S * 0.022)   # THE → title
    gap_C = int(S * 0.055)   # title → PODCAST

    the_top_y    = lm_bottom + gap_A
    the_bottom_y = the_top_y + label_h
    title_draw_y  = the_bottom_y + gap_B - cap_top_off
    title_bottom  = title_draw_y + bottom_off
    pod_top_y    = title_bottom + gap_C

    # Draw THE
    draw.text(((S - (bb_the[2]-bb_the[0]))//2 - bb_the[0],
               the_top_y - bb_the[1]),
              "THE", fill=GOLD[:3], font=label_fnt)

    # Draw GoodFuture.ai
    tx = (S - total_tw) // 2
    for p, col in zip(parts, tcolors):
        draw.text((tx, title_draw_y), p, fill=col, font=title_fnt)
        tx += tpos[p][2] - tpos[p][0]

    # Draw PODCAST
    draw.text(((S - (bb_pod[2]-bb_pod[0]))//2 - bb_pod[0],
               pod_top_y - bb_pod[1]),
              "PODCAST", fill=GOLD[:3], font=label_fnt)

    # Rule
    rule_y = pod_top_y + label_h + int(S * 0.042)
    draw.line([(int(S*0.30), rule_y), (int(S*0.70), rule_y)],
              fill=(*GOLD[:3],), width=max(1, S//600))

    # "with" + "Matt Coatney"
    with_fnt = sfontr(int(S * 0.030))
    name_fnt = sfont(int(S  * 0.042))
    with_y   = rule_y + int(S * 0.032)
    bb = draw.textbbox((0, 0), "with", font=with_fnt)
    draw.text(((S-(bb[2]-bb[0]))//2 - bb[0], with_y - bb[1]),
              "with", fill=LIGHT[:3], font=with_fnt)
    name_y = with_y + (bb[3]-bb[1]) + int(S * 0.012)
    bb = draw.textbbox((0, 0), "Matt Coatney", font=name_fnt)
    draw.text(((S-(bb[2]-bb[0]))//2 - bb[0], name_y - bb[1]),
              "Matt Coatney", fill=LIGHT[:3], font=name_fnt)

    # Tagline
    tag_fnt = sfontr(int(S * 0.022))
    tag_txt = "Honest conversations for the AI era  -  goodfuture.ai"
    bb = draw.textbbox((0, 0), tag_txt, font=tag_fnt)
    draw.text(((S-(bb[2]-bb[0]))//2 - bb[0], int(S*0.935) - bb[1]),
              tag_txt, fill=(*TEAL[:3],), font=tag_fnt)

    return img


# ── Generate all assets ─────────────────────────────────────────────────────
def save(img, name):
    path = OUT / name
    img.save(str(path), "PNG")
    print(f"  {name}  {img.width}x{img.height}")


def main():
    OUT.mkdir(exist_ok=True)
    print("Generating logomarks...")

    save(make_logomark(256, LIGHT,        TEAL[:3],  LIGHT[:3]),  "logomark-on-light.png")
    save(make_logomark(256, DEEP,         TEAL[:3],  LIGHT[:3]),  "logomark-on-dark.png")
    save(make_logomark(256, TRANS,        TEAL[:3],  LIGHT[:3]),  "logomark-transparent-dark.png")
    save(make_logomark(256, (*LIGHT[:3], 0), TEAL[:3], DEEP[:3]), "logomark-transparent-light.png")
    save(make_logomark(256, TRANS,        GOLD[:3],  LIGHT[:3]),  "logomark-gold.png")

    print("Generating wordmarks...")
    save(make_wordmark(LIGHT,          DEEP[:3],  TEAL[:3], GOLD[:3]), "wordmark-on-light.png")
    save(make_wordmark(DEEP,           LIGHT[:3], TEAL[:3], GOLD[:3]), "wordmark-on-dark.png")
    save(make_wordmark(TRANS,          LIGHT[:3], TEAL[:3], GOLD[:3]), "wordmark-transparent-dark-text.png")
    save(make_wordmark((*LIGHT[:3],0), DEEP[:3],  TEAL[:3], GOLD[:3]), "wordmark-transparent-light-text.png")
    save(make_wordmark(TRANS,          LIGHT[:3], LIGHT[:3],GOLD[:3]), "wordmark-monochrome-light.png")
    save(make_wordmark((*LIGHT[:3],0), DEEP[:3],  DEEP[:3], DEEP[:3]), "wordmark-monochrome-dark.png")

    print("Generating full logos...")
    save(make_full_logo(LIGHT,          LIGHT,       TEAL[:3], LIGHT[:3], DEEP[:3],  TEAL[:3], GOLD[:3]),
         "logo-full-on-light.png")
    save(make_full_logo(DEEP,           DEEP,        TEAL[:3], LIGHT[:3], LIGHT[:3], TEAL[:3], GOLD[:3]),
         "logo-full-on-dark.png")
    save(make_full_logo((*LIGHT[:3],0), (*LIGHT[:3],0), TEAL[:3], DEEP[:3],  DEEP[:3],  TEAL[:3], GOLD[:3]),
         "logo-full-transparent-light.png")
    save(make_full_logo(TRANS,          TRANS,       TEAL[:3], LIGHT[:3], LIGHT[:3], TEAL[:3], GOLD[:3]),
         "logo-full-transparent-dark.png")

    print("Generating podcast covers...")
    save(make_podcast_cover(1400), "podcast-cover-1400.png")
    save(make_podcast_cover(3000), "podcast-cover-3000.png")

    print("Done.")


if __name__ == "__main__":
    main()
