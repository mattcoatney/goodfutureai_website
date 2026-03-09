from PIL import Image, ImageDraw, ImageFont

OUT = "c:/Projects/thirdpeakstudio/goodfutureai_website/images"
F   = "C:/Windows/Fonts/"

DEEP  = (15,  46,  61,  255)
GOLD  = (242, 169, 59,  255)
TEAL  = (59,  165, 165, 255)
CORAL = (232, 93,  74,  255)
LIGHT = (251, 246, 239, 255)

def gfont(s):  return ImageFont.truetype(F+"georgiab.ttf", s)
def gfonti(s): return ImageFont.truetype(F+"georgiai.ttf", s)
def sfont(s):  return ImageFont.truetype(F+"calibrib.ttf",  s)
def sfontr(s): return ImageFont.truetype(F+"calibri.ttf",   s)

def arc_pts(x0, y0, x1, y1, peak_y, steps=120):
    mx = (x0+x1)/2
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
    """
    Draw an antialiased arc onto base_img using supersampling.
    Renders at supersample× resolution on a transparent layer, downscales,
    then alpha-composites — avoids dark fringe from overlapping semi-transparent strokes.
    """
    # Bounding box of arc with padding
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

    # Draw at supersample× on transparent layer
    S = supersample
    hi = Image.new("RGBA", (bw * S, bh * S), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hi)
    pts = arc_pts((x0 - bx0) * S, (y0 - by0) * S,
                  (x1 - bx0) * S, (y1 - by0) * S,
                  (peak_y - by0) * S)
    for i in range(len(pts) - 1):
        hd.line([pts[i], pts[i+1]], fill=(*color_rgb, 255), width=stroke_w * S)

    # Downscale with LANCZOS for antialiasing
    lo = hi.resize((bw, bh), Image.LANCZOS)

    # Composite onto base
    base_img.paste(lo, (bx0, by0), lo)


# ── TEST WORDMARK ─────────────────────────────────────────────────────────
def make_test_wordmark():
    fnt_size = 60
    fnt      = gfont(fnt_size)
    parts    = ["GoodFut", "ur", "e", ".ai"]
    colors   = [DEEP[:3], DEEP[:3], DEEP[:3], TEAL[:3]]
    pos, total_w = measure(fnt, parts)

    lc_top_off  = pos["ur"][1]      # 26 — top of lowercase glyphs
    bottom_off  = pos["GoodFut"][3] # 57 — bottom of text

    pad_x    = 20
    arc_gap  = 3    # px gap between arc base and top of "ur"
    arc_rise = 29   # how high the arc peaks
    pad_top  = arc_gap + arc_rise + 4  # headroom above text for full arc

    draw_y   = pad_top
    arc_y    = draw_y + lc_top_off - arc_gap
    arc_peak = arc_y - arc_rise

    canvas_w = total_w + pad_x * 2
    canvas_h = draw_y + bottom_off + 12

    img  = Image.new("RGBA", (canvas_w, canvas_h), LIGHT)
    draw = ImageDraw.Draw(img)

    # Draw text — track ur position using live textbbox at actual coordinates
    tx = pad_x
    ur_x0 = ur_x1 = 0
    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    for p, col in zip(parts, colors):
        pb = probe.textbbox((tx, draw_y), p, font=fnt)
        if p == "ur":
            ur_x0, ur_x1 = pb[0], pb[2]
        draw.text((tx, draw_y), p, fill=col, font=fnt)
        tx += pos[p][2] - pos[p][0]

    # Crisp supersampled arc — no dark border, proper antialiasing
    draw_crisp_arc(img, ur_x0 - 2, arc_y, ur_x1 + 2, arc_y, arc_peak,
                   GOLD[:3], stroke_w=2, supersample=4)

    img.save(f"{OUT}/test-wordmark.png")
    print(f"test-wordmark.png  {canvas_w}x{canvas_h}")
    print(f"  draw_y={draw_y}  arc_y={arc_y}  arc_peak={arc_peak}  rise={arc_rise}px  ur={ur_x0}..{ur_x1}")


make_test_wordmark()


# ── TEST PODCAST COVER (1400x1400) ────────────────────────────────────────
def make_test_podcast(S=1400):
    img  = Image.new("RGB", (S, S), DEEP[:3])
    adraw = ImageDraw.Draw(img, "RGBA")

    # Background sunrise arcs
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

    # ── GF logomark ─────────────────────────────────────────────────────
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

    lm_bottom = lm_cy + lm_r   # pixel bottom of circle

    # ── THE and PODCAST: same font, same size ────────────────────────────
    label_fnt  = sfont(int(S * 0.040))   # bold sans, equal for both
    bb_the     = draw.textbbox((0, 0), "THE",     font=label_fnt)
    bb_pod     = draw.textbbox((0, 0), "PODCAST", font=label_fnt)
    label_h    = bb_the[3] - bb_the[1]  # both same height (same font/size)

    # ── GoodFuture.ai title ───────────────────────────────────────────────
    title_fnt = gfont(int(S * 0.095))
    parts     = ["GoodFuture", ".ai"]
    tcolors   = [LIGHT[:3], TEAL[:3]]
    tpos, total_tw = measure(title_fnt, parts)
    cap_top_off  = tpos["GoodFuture"][1]   # ~21
    bottom_off   = tpos["GoodFuture"][3]   # ~125
    title_vis_h  = bottom_off - cap_top_off  # visible pixel height of title

    # ── Compute equal spacing ─────────────────────────────────────────────
    # Stack: lm_bottom → [gap_A] → THE → [gap_B] → GoodFuture.ai → [gap_B] → PODCAST
    # gap_A = bigger (more space between mark and THE)
    # gap_B = equal gap between the three label/title lines
    gap_A = int(S * 0.050)   # circle → THE
    gap_B = int(S * 0.022)   # THE → title
    gap_C = int(S * 0.055)   # title → PODCAST (more space)

    the_top_y    = lm_bottom + gap_A
    the_bottom_y = the_top_y + label_h

    # title draw_y adjusted so visible cap top aligns to the_bottom_y + gap_B
    title_draw_y  = the_bottom_y + gap_B - cap_top_off
    title_vis_top = title_draw_y + cap_top_off
    title_bottom  = title_draw_y + bottom_off

    pod_top_y    = title_bottom + gap_C
    pod_bottom_y = pod_top_y + label_h

    # ── Draw THE ─────────────────────────────────────────────────────────
    draw.text(((S - (bb_the[2]-bb_the[0]))//2 - bb_the[0],
               the_top_y - bb_the[1]),
              "THE", fill=GOLD[:3], font=label_fnt)

    # ── Draw GoodFuture.ai (no arc) ────────────────────────────────────
    tx = (S - total_tw) // 2
    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    for p, col in zip(parts, tcolors):
        draw.text((tx, title_draw_y), p, fill=col, font=title_fnt)
        tx += tpos[p][2] - tpos[p][0]

    # ── Draw PODCAST ─────────────────────────────────────────────────────
    draw.text(((S - (bb_pod[2]-bb_pod[0]))//2 - bb_pod[0],
               pod_top_y - bb_pod[1]),
              "PODCAST", fill=GOLD[:3], font=label_fnt)

    # ── Rule ─────────────────────────────────────────────────────────────
    rule_y = pod_bottom_y + int(S * 0.042)
    draw.line([(int(S*0.30), rule_y), (int(S*0.70), rule_y)],
              fill=(*GOLD[:3],), width=max(1, S//600))

    # ── "with" + "Matt Coatney" ───────────────────────────────────────────
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

    # ── Tagline ───────────────────────────────────────────────────────────
    tag_fnt = sfontr(int(S * 0.022))
    tag_txt = "Honest conversations for the AI era  -  goodfuture.ai"
    bb = draw.textbbox((0, 0), tag_txt, font=tag_fnt)
    draw.text(((S-(bb[2]-bb[0]))//2 - bb[0], int(S*0.935) - bb[1]),
              tag_txt, fill=(*TEAL[:3],), font=tag_fnt)

    img.save(f"{OUT}/test-podcast-cover.png", "PNG")
    print(f"test-podcast-cover.png  {S}x{S}")
    print(f"  lm_bottom={lm_bottom}  the_top={the_top_y}  the_bottom={the_bottom_y}")
    print(f"  title_vis_top={title_vis_top}  title_bottom={title_bottom}")
    print(f"  pod_top={pod_top_y}  gap_B={gap_B}px")
    print(f"  THE->title gap={title_vis_top - the_bottom_y}px  title->PODCAST gap={pod_top_y - title_bottom}px")


make_test_podcast(1400)
