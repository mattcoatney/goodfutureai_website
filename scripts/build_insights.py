#!/usr/bin/env python3
"""
build_insights.py
─────────────────
Reads every .md file in content/insights/ (skipping _template.md and any
file starting with _), converts the body to HTML, and:

  1. Regenerates data/insights.js  (for the interactive filter on insights/)
  2. Writes/updates insights/{slug}/index.html  (standalone article pages)
  3. Updates the static content sections in insights/index.html
  4. Updates the insights preview section in index.html (home page)

Sections in HTML pages are delimited by comment markers:
    <!-- GF:MARKER:START --> ... <!-- GF:MARKER:END -->

Usage:
    python scripts/build_insights.py

Run this whenever you add or update a file in content/insights/.
"""

import sys
import re
import yaml
import markdown
from pathlib import Path
from datetime import date

# Allow importing sibling module html_parts
sys.path.insert(0, str(Path(__file__).parent))
from html_parts import nav_html, footer_html, replace_section

# ── Paths ──────────────────────────────────────────────────────────────────
ROOT        = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content" / "insights"
OUTPUT_FILE = ROOT / "data" / "insights.js"
PAGES_DIR   = ROOT / "insights"
HOME_FILE   = ROOT / "index.html"
SITE_URL    = "https://goodfuture.ai"

FONTS_URL = (
    "https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@"
    "0,9..144,300;0,9..144,400;0,9..144,500;0,9..144,600;0,9..144,700;"
    "0,9..144,800;0,9..144,900;1,9..144,400;1,9..144,500;1,9..144,600"
    "&family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;"
    "1,400;1,500&display=swap"
)

# ── Markdown converter ─────────────────────────────────────────────────────
MD = markdown.Markdown(extensions=["extra", "nl2br"])

MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

# SVG constants (no curly braces so safe in f-strings)
ARROW_SVG = (
    '<svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">'
    '<path d="M2 7h10M8 3l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>'
    '</svg>'
)
DOC_SVG_LG = (
    '<svg width="48" height="48" viewBox="0 0 48 48" fill="none" aria-hidden="true">'
    '<path d="M8 16h32M8 24h24M8 32h28M8 40h16" stroke="white" stroke-width="2" stroke-linecap="round"/>'
    '</svg>'
)
DOC_SVG_SM = (
    '<svg width="48" height="48" viewBox="0 0 48 48" fill="none" aria-hidden="true">'
    '<path d="M8 14h32M8 22h24M8 30h28M8 38h16" stroke="white" stroke-width="2" stroke-linecap="round"/>'
    '</svg>'
)
VIDEO_BADGE = (
    '<div class="has-video">'
    '<svg width="10" height="10" viewBox="0 0 10 10" fill="white"><path d="M2 1l7 4-7 4V1z"/></svg>'
    ' Video</div>'
)


# ── Parsing helpers ────────────────────────────────────────────────────────

def parse_md_file(path: Path) -> tuple:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"{path.name}: missing YAML frontmatter (must start with ---)")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"{path.name}: malformed frontmatter (need opening and closing ---)")
    try:
        fm = yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        raise ValueError(f"{path.name}: YAML parse error — {e}")
    if not isinstance(fm, dict):
        raise ValueError(f"{path.name}: frontmatter is not a YAML mapping")
    return fm, parts[2].strip()


def md_to_html(text: str) -> str:
    MD.reset()
    return MD.convert(text)


def estimate_reading_time(html: str) -> str:
    words = len(re.sub(r"<[^>]+>", "", html).split())
    minutes = max(1, round(words / 200))
    return f"{minutes} min read"


def html_esc(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")


def format_date(date_val) -> str:
    d = date_val if hasattr(date_val, "month") else date.fromisoformat(str(date_val))
    return f"{MONTHS[d.month - 1]} {d.year}"


# ── JS rendering (data/insights.js) ───────────────────────────────────────

def js_string(value) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list):
        items = ", ".join(f'"{v}"' for v in value)
        return f"[{items}]"
    if isinstance(value, (int, float)):
        return str(value)
    s = (str(value)
         .replace("\\", "\\\\")
         .replace('"', '\\"')
         .replace("\r", "")
         .replace("\n", "\\n")
         .replace("`", "\\`")
         .replace("${", "\\${"))
    return f'"{s}"'


def js_body(html: str) -> str:
    escaped = html.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
    return f"`{escaped}`"


def render_js_entry(entry: dict) -> str:
    lines = [
        "  {",
        f"    slug:        {js_string(entry['slug'])},",
        f"    title:       {js_string(entry['title'])},",
        f"    date:        {js_string(str(entry['date']))},",
        f"    tags:        {js_string(entry.get('tags', []))},",
        f"    excerpt:     {js_string(entry.get('excerpt', ''))},",
        f"    body:        {js_body(entry['body'])},",
        f"    coverImage:  {js_string(entry.get('coverImage'))},",
        f"    youtubeId:   {js_string(entry.get('youtubeId'))},",
        f"    readingTime: {js_string(entry.get('readingTime', ''))},",
        f"    featured:    {js_string(entry.get('featured', False))},",
        "  }",
    ]
    return "\n".join(lines)


# ── Static HTML rendering for list pages ──────────────────────────────────

def render_filter_buttons(entries: list) -> str:
    """Render the filter bar buttons for insights/index.html."""
    tags = sorted(set(t for e in entries for t in e.get("tags", [])))
    all_btn = '<button class="filter-btn active" data-tag="all" onclick="filterBy(\'all\')">All</button>'
    tag_btns = "\n      ".join(
        f'<button class="filter-btn" data-tag="{html_esc(t)}" onclick="filterBy(\'{html_esc(t)}\')">{html_esc(t)}</button>'
        for t in tags
    )
    return f'      <span class="filters-label">Filter:</span>\n      {all_btn}\n      {tag_btns}'


def render_insight_card(entry: dict, is_featured: bool, delay: int) -> str:
    """Render a single article card for the insights list page."""
    title   = html_esc(entry["title"])
    excerpt = html_esc(entry["excerpt"])
    slug    = entry["slug"]
    date_d  = format_date(entry["date"])
    rt      = entry.get("readingTime", "")
    cover   = entry.get("coverImage") or ""
    youtube = entry.get("youtubeId") or ""
    tags    = entry.get("tags", [])

    featured_cls = " featured" if is_featured else ""
    tags_html    = "".join(f'<span class="a-tag">{html_esc(t)}</span>' for t in tags)

    if cover:
        img_html = f'<img src="{html_esc(cover)}" alt="{title}">'
    else:
        img_html = f'<div class="ic-img-overlay"></div>{DOC_SVG_LG}'

    video_html = VIDEO_BADGE if youtube else ""

    return (
        f'    <a class="insight-card{featured_cls} fade-up delay-{delay}" id="card-{slug}" href="{slug}/">\n'
        f'      <div class="ic-img">{img_html}{video_html}</div>\n'
        f'      <div class="ic-body">\n'
        f'        <div class="ic-tags">{tags_html}</div>\n'
        f'        <h3>{title}</h3>\n'
        f'        <p>{excerpt}</p>\n'
        f'        <div class="ic-meta">'
        f'<span>{date_d}</span><span class="ic-dot"></span><span>{rt}</span>'
        f'</div>\n'
        f'        <span class="ic-link">Read {ARROW_SVG}</span>\n'
        f'      </div>\n'
        f'    </a>'
    )


def render_insights_grid(entries: list) -> str:
    """Render all article cards for the GF:INSIGHTS_GRID section."""
    if not entries:
        return (
            '    <div class="no-results">\n'
            '      <h3>No articles yet</h3>\n'
            '      <p>Check back soon.</p>\n'
            '    </div>'
        )
    cards = []
    for i, entry in enumerate(entries):
        is_featured = (i == 0 and entry.get("featured"))
        delay       = (i % 3) + 1
        cards.append(render_insight_card(entry, is_featured, delay))
    return "\n".join(cards)


def render_home_insight_card(entry: dict, is_featured: bool, delay_cls: str) -> str:
    """Render an article card for the home page preview (uses .article CSS classes)."""
    title   = html_esc(entry["title"])
    excerpt = html_esc(entry["excerpt"])
    slug    = entry["slug"]
    date_d  = format_date(entry["date"])
    rt      = entry.get("readingTime", "")
    cover   = entry.get("coverImage") or ""
    tags    = entry.get("tags", [])

    # Cover image paths are relative to insights/ — adjust to root
    if cover.startswith("../"):
        cover_from_root = cover[3:]  # strip leading ../
    else:
        cover_from_root = cover

    featured_cls = " featured" if is_featured else ""
    first_tag    = html_esc(tags[0]) if tags else ""

    if cover_from_root:
        img_html = f'<img src="{html_esc(cover_from_root)}" alt="{title}">'
    else:
        img_html = f'<div class="a-img-overlay"></div>{DOC_SVG_SM}'

    tag_html = f'<span class="a-tag">{first_tag}</span>' if first_tag else ""

    return (
        f'    <a class="article{featured_cls} fade-up{delay_cls}" href="insights/{slug}/">\n'
        f'      <div class="a-img">{img_html}</div>\n'
        f'      <div class="a-body">\n'
        f'        {tag_html}\n'
        f'        <h3>{title}</h3>\n'
        f'        <p>{excerpt}</p>\n'
        f'        <div class="a-meta">'
        f'<span>{date_d}</span><span class="a-dot"></span><span>{rt}</span>'
        f'</div>\n'
        f'        <span class="a-link">Read {ARROW_SVG}</span>\n'
        f'      </div>\n'
        f'    </a>'
    )


def render_home_insights(entries: list) -> str:
    """Render featured + 2 cards for GF:HOME_INSIGHTS section on index.html."""
    if not entries:
        return ""
    featured = next((e for e in entries if e.get("featured")), entries[0])
    others   = [e for e in entries if e is not featured][:2]
    to_show  = [featured] + others

    cards = []
    for i, entry in enumerate(to_show):
        is_feat   = (i == 0 and entry.get("featured"))
        delay_cls = f" delay-{i}" if i > 0 else ""
        cards.append(render_home_insight_card(entry, is_feat, delay_cls))
    return "\n".join(cards)


# ── Standalone article page ────────────────────────────────────────────────

def render_article_page(entry: dict) -> str:
    """Return full HTML for a standalone article page at insights/{slug}/index.html."""
    title    = entry["title"]
    slug     = entry["slug"]
    excerpt  = entry.get("excerpt", "")
    body     = entry.get("body", "")
    tags     = entry.get("tags", [])
    rt       = entry.get("readingTime", "")
    cover    = entry.get("coverImage") or ""
    youtube  = entry.get("youtubeId") or ""
    date_display = format_date(entry["date"])

    tags_html = "".join(f'<span class="a-tag a-tag-inv">{t}</span>' for t in tags)

    meta_parts = [date_display]
    if rt:
        meta_parts.append(rt)
    meta_html = '<span class="art-meta-dot"></span>'.join(f"<span>{p}</span>" for p in meta_parts)

    og_image_tag = ""
    cover_html   = ""
    if youtube:
        cover_html = (
            '<div class="article-cover">'
            '<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;">'
            f'<iframe src="https://www.youtube.com/embed/{youtube}"'
            f' title="{html_esc(title)}" allowfullscreen loading="lazy"'
            ' style="position:absolute;top:0;left:0;width:100%;height:100%;border:none;"></iframe>'
            "</div></div>"
        )
        og_image_tag = f'<meta property="og:image" content="https://img.youtube.com/vi/{youtube}/maxresdefault.jpg">'
    elif cover:
        if cover.startswith("../"):
            page_src = "../../" + cover[3:]
            abs_src  = SITE_URL + "/" + cover[3:]
        else:
            page_src = cover
            abs_src  = ""
        cover_html   = f'<div class="article-cover"><img src="{page_src}" alt="{html_esc(title)}"></div>'
        og_image_tag = f'<meta property="og:image" content="{html_esc(abs_src)}">' if abs_src else ""

    canonical = f"{SITE_URL}/insights/{slug}/"
    nav       = nav_html("../../", active="insights")
    foot      = footer_html("../../")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html_esc(title)} — GoodFuture.ai</title>
<meta name="description" content="{html_esc(excerpt)}">
<link rel="canonical" href="{canonical}">

<!-- Open Graph / LinkedIn / Twitter -->
<meta property="og:type" content="article">
<meta property="og:title" content="{html_esc(title)}">
<meta property="og:description" content="{html_esc(excerpt)}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="GoodFuture.ai">
{og_image_tag}
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html_esc(title)}">
<meta name="twitter:description" content="{html_esc(excerpt)}">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{FONTS_URL}" rel="stylesheet">
<link rel="stylesheet" href="../../assets/css/main.css">
<link rel="icon" type="image/png" href="../../favicon.png">

<style>
.article-hero {{
  background: var(--deep-horizon);
  padding: 100px 0 56px;
  position: relative; overflow: hidden;
}}
.article-hero::after {{
  content: '';
  position: absolute; inset: 0;
  background: radial-gradient(ellipse at 80% 20%, rgba(59,165,165,.15) 0%, transparent 60%);
  pointer-events: none;
}}
.article-hero-inner {{ position: relative; z-index: 1; }}
.back-link {{
  display: inline-flex; align-items: center; gap: 6px;
  color: rgba(251,246,239,.5); font-size: 13px; font-weight: 600;
  text-decoration: none; margin-bottom: 28px;
  transition: color .2s;
}}
.back-link:hover {{ color: var(--warm-light); }}
.art-tags {{ display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 20px; }}
.a-tag-inv {{
  background: rgba(59,165,165,.18); border: 1px solid rgba(59,165,165,.3);
  color: var(--morning-teal-light);
  padding: 4px 12px; border-radius: var(--radius-full);
  font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;
}}
.art-title {{
  color: var(--warm-light);
  font-size: clamp(1.8rem, 4vw, 3rem);
  line-height: 1.2; margin-bottom: 20px;
}}
.art-meta {{
  color: rgba(251,246,239,.5); font-size: 13px;
  display: flex; align-items: center; gap: 10px;
}}
.art-meta-dot {{ width: 3px; height: 3px; border-radius: 50%; background: rgba(251,246,239,.35); }}
.article-wrap {{ max-width: 760px; margin: 0 auto; padding: 64px 24px 80px; }}
.article-cover {{
  width: 100%; aspect-ratio: 16/9;
  border-radius: var(--radius-lg); overflow: hidden; margin-bottom: 48px;
}}
.article-cover img {{ width: 100%; height: 100%; object-fit: cover; }}
.article-cover iframe {{ width: 100%; height: 100%; border: none; }}
.article-body {{ font-size: 1.05rem; line-height: 1.85; color: var(--warm-dark); }}
.article-body p {{ margin-bottom: 1.4em; }}
.article-body p:last-child {{ margin-bottom: 0; }}
.article-body h2 {{
  font-family: var(--font-display); font-size: 1.5rem;
  color: var(--deep-horizon); margin: 2em 0 0.6em; line-height: 1.3;
}}
.article-body h3 {{
  font-family: var(--font-display); font-size: 1.2rem;
  color: var(--deep-horizon); margin: 1.5em 0 0.5em;
}}
.article-body strong {{ color: var(--deep-horizon); font-weight: 600; }}
.article-body ul, .article-body ol {{ padding-left: 1.6em; margin-bottom: 1.4em; }}
.article-body li {{ margin-bottom: 0.5em; }}
.article-body a {{ color: var(--morning-teal); }}
.article-body a:hover {{ text-decoration: underline; }}
.article-body blockquote {{
  border-left: 3px solid var(--morning-teal);
  margin: 1.5em 0; padding: 0.5em 1.2em;
  color: var(--warm-stone); font-style: italic;
}}
@media (max-width: 768px) {{
  .article-wrap {{ padding: 40px 20px 60px; }}
  .article-hero {{ padding: 80px 0 48px; }}
}}
</style>
</head>

<body>
{nav}

<div class="article-hero">
  <div class="container">
    <div class="article-hero-inner">
      <a href="../../insights/" class="back-link">
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
          <path d="M10 7H4M6 4L3 7l3 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        All Insights
      </a>
      <div class="art-tags">{tags_html}</div>
      <h1 class="art-title">{title}</h1>
      <div class="art-meta">{meta_html}</div>
    </div>
  </div>
</div>

<div class="article-wrap">
  {cover_html}
  <div class="article-body">{body}</div>
</div>

<section class="section newsletter" id="connect">
  <div class="container">
    <div class="nl-inner">
      <div class="label">Stay Connected</div>
      <h2>The GoodFuture.ai Newsletter</h2>
      <p>
        One email every few weeks. Honest takes on AI, practical ideas you can use, and
        a little perspective on where we're all headed. No spam, no fluff.
      </p>
      <form class="nl-form" onsubmit="handleSubscribe(event)" novalidate>
        <input type="email" class="nl-input" placeholder="your@email.com" required aria-label="Email address">
        <button type="submit" class="btn btn-primary">Subscribe &rarr;</button>
      </form>
    </div>
  </div>
</section>

{foot}

<script src="../../assets/js/layout.js"></script>
<script src="../../assets/js/newsletter.js"></script>

</body>
</html>"""


# ── Main build ─────────────────────────────────────────────────────────────

def build():
    if not CONTENT_DIR.exists():
        print(f"ERROR: content directory not found: {CONTENT_DIR}", file=sys.stderr)
        sys.exit(1)

    md_files = sorted(
        p for p in CONTENT_DIR.glob("*.md")
        if not p.name.startswith("_")
    )

    if not md_files:
        print("No .md files found in content/insights/ (skipping _* files). Writing empty data file.")

    entries = []
    errors  = []

    for path in md_files:
        try:
            fm, body_raw = parse_md_file(path)
        except ValueError as e:
            errors.append(str(e))
            continue

        for field in ("slug", "title", "date"):
            if field not in fm:
                errors.append(f"{path.name}: missing required field '{field}'")
                continue

        body_html    = md_to_html(body_raw)
        reading_time = fm.get("readingTime") or estimate_reading_time(body_html)

        entries.append({
            "slug":        fm["slug"],
            "title":       fm["title"],
            "date":        fm["date"],
            "tags":        fm.get("tags") or [],
            "excerpt":     fm.get("excerpt", ""),
            "body":        body_html,
            "coverImage":  fm.get("coverImage"),
            "youtubeId":   fm.get("youtubeId"),
            "readingTime": reading_time,
            "featured":    fm.get("featured", False),
        })

    if errors:
        print("Errors found — fix these before continuing:\n", file=sys.stderr)
        for e in errors:
            print(f"  * {e}", file=sys.stderr)
        sys.exit(1)

    # Sort newest first
    entries.sort(key=lambda e: str(e["date"]), reverse=True)

    # Enforce at most one featured article
    featured_count = sum(1 for e in entries if e.get("featured"))
    if featured_count > 1:
        print(f"Warning: {featured_count} articles marked featured=true. Only the first (newest) will be kept.")
        found = False
        for e in entries:
            if e.get("featured"):
                if found:
                    e["featured"] = False
                else:
                    found = True

    # ── 1. Generate data/insights.js ───────────────────────────────────────
    entry_blocks = ",\n".join(render_js_entry(e) for e in entries)

    js = f"""\
/**
 * GoodFuture.ai — Insights Content Data
 *
 * !! AUTO-GENERATED — do not edit directly !!
 * Edit or add files in content/insights/ then run:
 *
 *     python scripts/build_insights.py
 *
 * AVAILABLE TAGS (add new ones as needed):
 * "AI & Work", "Skills", "Leadership", "Education", "Tools", "Strategy", "Personal"
 */

const INSIGHTS = [
{entry_blocks}
];

/* Helper: format date for display */
function formatInsightDate(dateStr) {{
  const d = new Date(dateStr + 'T00:00:00');
  return d.toLocaleDateString('en-US', {{ month: 'short', year: 'numeric' }});
}}

/* Helper: get all unique tags */
function getInsightTags() {{
  const tags = new Set();
  INSIGHTS.forEach(a => a.tags.forEach(t => tags.add(t)));
  return Array.from(tags).sort();
}}
"""

    OUTPUT_FILE.write_text(js, encoding="utf-8")
    print(f"OK  data/insights.js ({len(entries)} article(s))")

    # ── 2. Generate standalone article pages ───────────────────────────────
    for entry in entries:
        page_dir  = PAGES_DIR / entry["slug"]
        page_dir.mkdir(parents=True, exist_ok=True)
        (page_dir / "index.html").write_text(render_article_page(entry), encoding="utf-8")
        print(f"    + insights/{entry['slug']}/index.html")

    # ── 3. Update insights/index.html static sections ──────────────────────
    insights_index = PAGES_DIR / "index.html"
    if insights_index.exists():
        try:
            replace_section(insights_index, "FILTERS",       render_filter_buttons(entries))
            replace_section(insights_index, "INSIGHTS_GRID", render_insights_grid(entries))
            print(f"OK  insights/index.html (filters + grid updated)")
        except ValueError as e:
            print(f"Warning: {e}", file=sys.stderr)
    else:
        print(f"Warning: {insights_index} not found — skipping static list update", file=sys.stderr)

    # ── 4. Update home page insights preview ───────────────────────────────
    if HOME_FILE.exists():
        try:
            replace_section(HOME_FILE, "HOME_INSIGHTS", render_home_insights(entries))
            print(f"OK  index.html (home insights preview updated)")
        except ValueError as e:
            print(f"Warning: {e}", file=sys.stderr)
    else:
        print(f"Warning: {HOME_FILE} not found — skipping home insights update", file=sys.stderr)


if __name__ == "__main__":
    build()
