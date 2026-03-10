#!/usr/bin/env python3
"""
build_insights.py
─────────────────
Reads every .md file in content/insights/ (skipping _template.md and any
file starting with _), converts the body to HTML, and regenerates
data/insights.js.

Usage:
    python scripts/build_insights.py

Run this whenever you add or update a file in content/insights/.
"""

import os
import sys
import re
import yaml
import markdown
from pathlib import Path
from datetime import date

# ── Paths (relative to repo root) ─────────────────────────────────────────
ROOT        = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content" / "insights"
OUTPUT_FILE = ROOT / "data" / "insights.js"
PAGES_DIR   = ROOT / "insights"           # where slug/index.html pages are written
SITE_URL    = "https://goodfuture.ai"

# ── Markdown converter ─────────────────────────────────────────────────────
MD = markdown.Markdown(extensions=["extra", "nl2br"])


def parse_md_file(path: Path) -> dict:
    """Parse a markdown file with YAML frontmatter. Returns a dict."""
    text = path.read_text(encoding="utf-8")

    # Split frontmatter from body
    if not text.startswith("---"):
        raise ValueError(f"{path.name}: missing YAML frontmatter (must start with ---)")

    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"{path.name}: malformed frontmatter (need opening and closing ---)")

    fm_raw, body_raw = parts[1], parts[2].strip()

    try:
        fm = yaml.safe_load(fm_raw)
    except yaml.YAMLError as e:
        raise ValueError(f"{path.name}: YAML parse error — {e}")

    if not isinstance(fm, dict):
        raise ValueError(f"{path.name}: frontmatter is not a YAML mapping")

    return fm, body_raw


def md_to_html(text: str) -> str:
    """Convert markdown body to HTML."""
    MD.reset()
    return MD.convert(text)


def estimate_reading_time(html: str) -> str:
    """Estimate reading time from word count (200 wpm)."""
    words = len(re.sub(r"<[^>]+>", "", html).split())
    minutes = max(1, round(words / 200))
    return f"{minutes} min read"


def js_string(value) -> str:
    """Render a Python value as a JS literal (string, null, bool, array)."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list):
        items = ", ".join(f'"{v}"' for v in value)
        return f"[{items}]"
    if isinstance(value, (int, float)):
        return str(value)
    # String — escape backticks and backslashes for a JS template literal
    s = (str(value)
         .replace("\\", "\\\\")
         .replace('"', '\\"')
         .replace("\r", "")
         .replace("\n", "\\n")
         .replace("`", "\\`")
         .replace("${", "\\${"))
    return f'"{s}"'


def js_body(html: str) -> str:
    """Render body HTML as a JS template literal (backtick string)."""
    escaped = html.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
    return f"`{escaped}`"


def render_entry(entry: dict) -> str:
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


FONTS_URL = ("https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@"
             "0,9..144,300;0,9..144,400;0,9..144,500;0,9..144,600;0,9..144,700;"
             "0,9..144,800;0,9..144,900;1,9..144,400;1,9..144,500;1,9..144,600"
             "&family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;"
             "1,400;1,500&display=swap")


def html_esc(s: str) -> str:
    """Escape a string for use in an HTML attribute value."""
    return (s or "").replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")


def format_date(date_val) -> str:
    MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    d = date_val if hasattr(date_val, "month") else date.fromisoformat(str(date_val))
    return f"{MONTHS[d.month - 1]} {d.year}"


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
    date_str = str(entry["date"])

    date_display = format_date(entry["date"])

    # Tags HTML — displayed on dark hero background
    tags_html = "".join(
        f'<span class="a-tag a-tag-inv">{t}</span>' for t in tags
    )

    # Meta row (date + reading time)
    meta_parts = [date_display]
    if rt:
        meta_parts.append(rt)
    meta_html = '<span class="art-meta-dot"></span>'.join(
        f"<span>{p}</span>" for p in meta_parts
    )

    # Cover image — path adjustment from ../images/ (insights-relative) to ../../images/
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
<header></header>

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
      <h2>The AI Signal</h2>
      <p>
        One email every few weeks. Honest takes on AI, practical ideas you can use, and
        a little perspective on where we're all headed. No spam, no fluff.
      </p>
      <form class="nl-form" onsubmit="handleSubscribe(event)" novalidate>
        <input type="email" class="nl-input" placeholder="your@email.com" required aria-label="Email address">
        <button type="submit" class="btn btn-primary">Subscribe →</button>
      </form>
    </div>
  </div>
</section>

<footer class="footer"></footer>

<script src="../../assets/js/layout.js"></script>
<script src="../../assets/js/newsletter.js"></script>

</body>
</html>"""


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

        # Required fields
        for field in ("slug", "title", "date"):
            if field not in fm:
                errors.append(f"{path.name}: missing required field '{field}'")
                continue

        # Convert body
        body_html = md_to_html(body_raw)

        # Auto reading time if not set
        reading_time = fm.get("readingTime") or estimate_reading_time(body_html)

        entry = {
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
        }
        entries.append(entry)

    if errors:
        print("Errors found — fix these before continuing:\n", file=sys.stderr)
        for e in errors:
            print(f"  • {e}", file=sys.stderr)
        sys.exit(1)

    # Sort newest first
    entries.sort(key=lambda e: str(e["date"]), reverse=True)

    # Enforce at most one featured (most recent wins if multiple are set)
    featured_count = sum(1 for e in entries if e.get("featured"))
    if featured_count > 1:
        print(f"Warning: {featured_count} articles marked featured=true. "
              "Only the first (most recent) will be kept featured.")
        found = False
        for e in entries:
            if e.get("featured"):
                if found:
                    e["featured"] = False
                else:
                    found = True

    # ── Generate JS file ───────────────────────────────────────────────────
    entry_blocks = ",\n".join(render_entry(e) for e in entries)

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
    print(f"OK: Wrote {len(entries)} insight(s) to {OUTPUT_FILE.relative_to(ROOT)}")

    # ── Generate standalone HTML pages ─────────────────────────────────────
    for entry in entries:
        page_dir  = PAGES_DIR / entry["slug"]
        page_dir.mkdir(parents=True, exist_ok=True)
        page_html = render_article_page(entry)
        (page_dir / "index.html").write_text(page_html, encoding="utf-8")
        print(f"   + insights/{entry['slug']}/index.html")


if __name__ == "__main__":
    build()
