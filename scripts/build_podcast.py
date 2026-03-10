#!/usr/bin/env python3
"""
build_podcast.py
────────────────
Reads:
  content/podcast/_show.yaml              — show-level metadata
  content/podcast/episodes/*.md           — individual episodes
  content/podcast/appearances/*.md        — guest appearances

And regenerates data/podcast.js.

Usage:
    python scripts/build_podcast.py

Run this whenever you add or update any file in content/podcast/.
"""

import os
import sys
import yaml
import markdown
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
ROOT             = Path(__file__).resolve().parent.parent
EPISODES_DIR     = ROOT / "content" / "podcast" / "episodes"
APPEARANCES_DIR  = ROOT / "content" / "podcast" / "appearances"
SHOW_FILE        = ROOT / "content" / "podcast" / "_show.yaml"
OUTPUT_FILE      = ROOT / "data" / "podcast.js"
PAGES_DIR        = ROOT / "podcast"
SITE_URL         = "https://goodfuture.ai"
FONTS_URL        = ("https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@"
                    "0,9..144,300;0,9..144,400;0,9..144,500;0,9..144,600;0,9..144,700;"
                    "0,9..144,800;0,9..144,900;1,9..144,400;1,9..144,500;1,9..144,600"
                    "&family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;"
                    "1,400;1,500&display=swap")

MD = markdown.Markdown(extensions=["extra", "nl2br"])


# ── Parsing helpers ────────────────────────────────────────────────────────

def parse_md_file(path: Path) -> tuple[dict, str]:
    """Parse YAML frontmatter + body from a .md file."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"{path.name}: missing YAML frontmatter")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"{path.name}: malformed frontmatter")
    try:
        fm = yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        raise ValueError(f"{path.name}: YAML error — {e}")
    if not isinstance(fm, dict):
        raise ValueError(f"{path.name}: frontmatter must be a YAML mapping")
    return fm, parts[2].strip()


def load_show_config() -> dict:
    """Load _show.yaml; return defaults if file is missing."""
    if not SHOW_FILE.exists():
        print(f"Warning: {SHOW_FILE} not found — using defaults.")
        return {
            "name": "Building a Better Future Together",
            "tagline": "with GoodFuture.ai",
            "description": "Real conversations about navigating the AI era.",
            "platforms": [
                {"name": "Apple Podcasts", "url": "#", "icon": "apple"},
                {"name": "Spotify",        "url": "#", "icon": "spotify"},
                {"name": "YouTube",        "url": "#", "icon": "youtube"},
            ],
            "listenUrl": "#",
        }
    try:
        cfg = yaml.safe_load(SHOW_FILE.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        print(f"ERROR: could not parse _show.yaml — {e}", file=sys.stderr)
        sys.exit(1)
    return cfg


# ── JS rendering helpers ───────────────────────────────────────────────────

def js_string(value) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list):
        return "[" + ", ".join(js_string(v) for v in value) + "]"
    if isinstance(value, dict):
        pairs = ", ".join(f"{k}: {js_string(v)}" for k, v in value.items())
        return "{" + pairs + "}"
    if isinstance(value, (int, float)):
        return str(value)
    s = (str(value)
         .replace("\\", "\\\\")
         .replace('"', '\\"')
         .replace("\r", "")
         .replace("\n", "\\n"))
    return f'"{s}"'


def render_episode(ep: dict) -> str:
    lines = [
    "  {",
    f"    slug:             {js_string(ep['slug'])},",
    f"    title:            {js_string(ep['title'])},",
    f"    date:             {js_string(str(ep['date']))},",
    f"    tags:             {js_string(ep.get('tags', []))},",
    f"    excerpt:          {js_string(ep.get('excerpt', ''))},",
    f"    duration:         {js_string(ep.get('duration'))},",
    f"    youtubeId:        {js_string(ep.get('youtubeId'))},",
    f"    spotifyEmbedUrl:  {js_string(ep.get('spotifyEmbedUrl'))},",
    f"    applePodcastsUrl: {js_string(ep.get('applePodcastsUrl'))},",
    f"    spotifyUrl:       {js_string(ep.get('spotifyUrl'))},",
    f"    coverImage:       {js_string(ep.get('coverImage'))},",
    "  }",
    ]
    return "\n".join(lines)


def render_appearance(ap: dict) -> str:
    lines = [
    "  {",
    f"    show:        {js_string(ap['show'])},",
    f"    title:       {js_string(ap['title'])},",
    f"    date:        {js_string(str(ap['date']))},",
    f"    description: {js_string(ap.get('description', ''))},",
    f"    url:         {js_string(ap.get('url', '#'))},",
    f"    tags:        {js_string(ap.get('tags', []))},",
    "  }",
    ]
    return "\n".join(lines)


def render_show(show: dict) -> str:
    platforms_js = "[\n" + ",\n".join(
        f'    {{ name: {js_string(p["name"])}, url: {js_string(p["url"])}, icon: {js_string(p["icon"])} }}'
        for p in show.get("platforms", [])
    ) + "\n  ]"

    return f"""\
const PODCAST_SHOW = {{
  name:        {js_string(show.get('name', ''))},
  tagline:     {js_string(show.get('tagline', ''))},
  description: {js_string(show.get('description', ''))},
  platforms:   {platforms_js},
  listenUrl:   {js_string(show.get('listenUrl', '#'))},
}};"""


# ── Standalone episode page ────────────────────────────────────────────────

def html_esc(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")


def format_date(date_val) -> str:
    from datetime import date as date_type
    MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    d = date_val if hasattr(date_val, "month") else date_type.fromisoformat(str(date_val))
    return f"{MONTHS[d.month - 1]} {d.year}"


def render_episode_page(ep: dict) -> str:
    title    = ep.get("title", "")
    slug     = ep.get("slug", "")
    excerpt  = ep.get("excerpt", "")
    tags     = ep.get("tags", [])
    duration = ep.get("duration", "")
    youtube  = ep.get("youtubeId", "")
    spotify_embed = ep.get("spotifyEmbedUrl", "")
    apple_url     = ep.get("applePodcastsUrl", "")
    spotify_url   = ep.get("spotifyUrl", "")
    date_str = str(ep.get("date", ""))
    body     = ""
    MD.reset()
    if ep.get("_body"):
        body = MD.convert(ep["_body"])

    date_display = format_date(ep.get("date", date_str))
    canonical    = f"{SITE_URL}/podcast/{slug}/"

    tags_html = "".join(f'<span class="a-tag a-tag-inv">{t}</span>' for t in tags)

    meta_parts = [date_display]
    if duration:
        meta_parts.append(duration)
    meta_html = '<span class="ep-meta-dot"></span>'.join(f"<span>{p}</span>" for p in meta_parts)

    og_image_tag = f'<meta property="og:image" content="https://img.youtube.com/vi/{youtube}/maxresdefault.jpg">' if youtube else ""

    if youtube:
        player_html = (
            '<div class="ep-cover">'
            '<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;">'
            f'<iframe src="https://www.youtube.com/embed/{youtube}"'
            f' title="{html_esc(title)}" allowfullscreen loading="lazy"'
            ' style="position:absolute;top:0;left:0;width:100%;height:100%;border:none;"></iframe>'
            "</div></div>"
        )
    elif spotify_embed:
        player_html = (
            f'<div class="ep-cover"><iframe src="{html_esc(spotify_embed)}" height="152"'
            ' allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"'
            ' loading="lazy" style="border-radius:8px;border:none;width:100%;"></iframe></div>'
        )
    else:
        player_html = ""

    links = []
    if apple_url:
        links.append(f'<a href="{html_esc(apple_url)}" class="ep-ext-link" target="_blank" rel="noopener noreferrer">Apple Podcasts →</a>')
    if spotify_url:
        links.append(f'<a href="{html_esc(spotify_url)}" class="ep-ext-link" target="_blank" rel="noopener noreferrer">Spotify →</a>')
    links_html = "".join(links)

    body_section = f'<div class="ep-body-text">{body}</div>' if body else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html_esc(title)} — GoodFuture.ai Podcast</title>
<meta name="description" content="{html_esc(excerpt)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
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
.ep-hero {{
  background: var(--night-sky);
  padding: 100px 0 56px;
  position: relative; overflow: hidden;
}}
.ep-hero::before {{
  content: '';
  position: absolute; inset: 0;
  background: radial-gradient(ellipse at 20% 60%, rgba(242,169,59,.12) 0%, transparent 55%);
  pointer-events: none;
}}
.ep-hero-inner {{ position: relative; z-index: 1; }}
.back-link {{
  display: inline-flex; align-items: center; gap: 6px;
  color: rgba(251,246,239,.5); font-size: 13px; font-weight: 600;
  text-decoration: none; margin-bottom: 28px; transition: color .2s;
}}
.back-link:hover {{ color: var(--warm-light); }}
.ep-tags {{ display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 20px; }}
.a-tag-inv {{
  background: rgba(59,165,165,.18); border: 1px solid rgba(59,165,165,.3);
  color: var(--morning-teal-light);
  padding: 4px 12px; border-radius: var(--radius-full);
  font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;
}}
.ep-title {{
  color: var(--warm-light);
  font-size: clamp(1.8rem, 4vw, 3rem);
  line-height: 1.2; margin-bottom: 20px;
}}
.ep-meta {{
  color: rgba(251,246,239,.5); font-size: 13px;
  display: flex; align-items: center; gap: 10px;
}}
.ep-meta-dot {{ width: 3px; height: 3px; border-radius: 50%; background: rgba(251,246,239,.35); }}
.ep-wrap {{ max-width: 760px; margin: 0 auto; padding: 64px 24px 80px; }}
.ep-cover {{ margin-bottom: 40px; border-radius: var(--radius-lg); overflow: hidden; }}
.ep-cover iframe {{ border: none; }}
.ep-ext-links {{ display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 40px; }}
.ep-ext-link {{
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 14px; font-weight: 600; color: var(--morning-teal);
  transition: gap .2s;
}}
.ep-ext-link:hover {{ gap: 10px; }}
.ep-body-text {{ font-size: 1.05rem; line-height: 1.85; color: var(--warm-dark); }}
.ep-body-text p {{ margin-bottom: 1.4em; }}
.ep-body-text p:last-child {{ margin-bottom: 0; }}
.ep-body-text h2, .ep-body-text h3 {{
  font-family: var(--font-display); color: var(--deep-horizon); margin: 2em 0 0.6em;
}}
.ep-body-text strong {{ color: var(--deep-horizon); font-weight: 600; }}
.ep-body-text ul, .ep-body-text ol {{ padding-left: 1.6em; margin-bottom: 1.4em; }}
.ep-body-text li {{ margin-bottom: 0.5em; }}
@media (max-width: 768px) {{
  .ep-wrap {{ padding: 40px 20px 60px; }}
  .ep-hero {{ padding: 80px 0 48px; }}
}}
</style>
</head>
<body>
<header></header>

<div class="ep-hero">
  <div class="container">
    <div class="ep-hero-inner">
      <a href="../../podcast/" class="back-link">
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
          <path d="M10 7H4M6 4L3 7l3 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        All Episodes
      </a>
      <div class="ep-tags">{tags_html}</div>
      <h1 class="ep-title">{html_esc(title)}</h1>
      <div class="ep-meta">{meta_html}</div>
    </div>
  </div>
</div>

<div class="ep-wrap">
  {player_html}
  {f'<div class="ep-ext-links">{links_html}</div>' if links_html else ""}
  {body_section}
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
<script>
function handleSubscribe(e) {{
  e.preventDefault();
  var input = e.target.querySelector('input');
  var btn   = e.target.querySelector('button');
  var orig  = btn.textContent;
  btn.textContent = "You're in!";
  btn.style.background = 'var(--morning-teal)';
  input.value = '';
  setTimeout(function() {{ btn.textContent = orig; btn.style.background = ''; }}, 3500);
}}
</script>
</body>
</html>"""


# ── Main build ─────────────────────────────────────────────────────────────

def load_items(directory: Path, required_fields: list[str]) -> tuple[list[dict], list[str]]:
    """Load and parse all non-_ md files from a directory."""
    items  = []
    errors = []

    if not directory.exists():
        return items, errors

    for path in sorted(directory.glob("*.md")):
        if path.name.startswith("_"):
            continue
        try:
            fm, body_raw = parse_md_file(path)
        except ValueError as e:
            errors.append(str(e))
            continue

        for field in required_fields:
            if field not in fm:
                errors.append(f"{path.name}: missing required field '{field}'")

        fm["_body"] = body_raw
        items.append(fm)

    return items, errors


def build():
    show = load_show_config()

    episodes,    ep_errors = load_items(EPISODES_DIR,    ["slug", "title", "date"])
    appearances, ap_errors = load_items(APPEARANCES_DIR, ["show", "title", "date"])

    all_errors = ep_errors + ap_errors
    if all_errors:
        print("Errors found — fix these before continuing:\n", file=sys.stderr)
        for e in all_errors:
            print(f"  • {e}", file=sys.stderr)
        sys.exit(1)

    # Sort newest first
    episodes.sort(   key=lambda e: str(e["date"]), reverse=True)
    appearances.sort(key=lambda a: str(a["date"]), reverse=True)

    # Build appearance descriptions from body text (plain text, strip blank lines)
    for ap in appearances:
        body = ap.get("_body", "").strip()
        # Use body as description if not already set in frontmatter
        if not ap.get("description") and body:
            ap["description"] = " ".join(body.split())

    # ── Render JS ──────────────────────────────────────────────────────────
    ep_blocks = ",\n".join(render_episode(ep) for ep in episodes)
    ap_blocks = ",\n".join(render_appearance(ap) for ap in appearances)

    if not episodes:
        episodes_section = """\
const PODCAST_EPISODES = [
  /* No episodes yet — add .md files to content/podcast/episodes/ */
];"""
    else:
        episodes_section = f"const PODCAST_EPISODES = [\n{ep_blocks}\n];"

    js = f"""\
/**
 * GoodFuture.ai — Podcast Content Data
 *
 * !! AUTO-GENERATED — do not edit directly !!
 * Edit files in content/podcast/ then run:
 *
 *     python scripts/build_podcast.py
 *
 *   _show.yaml        — show name, description, platform links
 *   episodes/*.md     — individual episodes (newest first)
 *   appearances/*.md  — guest appearances on other shows
 */

{render_show(show)}

/**
 * Episodes — newest first.
 * Fields: slug, title, date, tags, excerpt, duration,
 *         youtubeId, spotifyEmbedUrl, applePodcastsUrl, spotifyUrl, coverImage
 */
{episodes_section}

/**
 * Podcast appearances — guest spots on other shows — newest first.
 * Fields: show, title, date, description, url, tags
 */
const PODCAST_APPEARANCES = [
{ap_blocks}
];

/* Helper: format date for display */
function formatPodcastDate(dateStr) {{
  const d = new Date(dateStr + 'T00:00:00');
  return d.toLocaleDateString('en-US', {{ month: 'short', year: 'numeric' }});
}}

/* Helper: SVG icons for platforms */
const PLATFORM_ICONS = {{
  apple: `<svg width="15" height="15" viewBox="0 0 15 15" fill="currentColor" aria-hidden="true">
    <path d="M7.5 0C3.4 0 0 3.4 0 7.5S3.4 15 7.5 15 15 11.6 15 7.5 11.6 0 7.5 0zm0 2.5a5 5 0 110 10 5 5 0 010-10zm.5 2H7v4.5l3.5 2-.5-.8-3-1.7V4.5z" opacity=".8"/>
  </svg>`,
  spotify: `<svg width="15" height="15" viewBox="0 0 15 15" fill="currentColor" aria-hidden="true">
    <path d="M7.5 0C3.4 0 0 3.4 0 7.5S3.4 15 7.5 15 15 11.6 15 7.5 11.6 0 7.5 0zm3.3 10.7c-.1.2-.4.3-.6.1-1.6-1-3.5-1.2-5.8-.7-.2.1-.4-.1-.5-.3-.1-.2.1-.4.3-.5 2.5-.6 4.6-.3 6.3.8.3.1.3.4.3.6zm.9-2c-.2.2-.5.3-.7.1-1.8-1.1-4.5-1.4-6.7-.8-.3.1-.5-.1-.6-.4-.1-.3.1-.5.4-.6 2.4-.7 5.4-.4 7.5.9.2.1.3.5.1.8zm.1-2.1c-2.2-1.3-5.8-1.4-7.9-.8-.3.1-.6-.1-.7-.4-.1-.3.1-.6.4-.7 2.4-.7 6.4-.6 8.9.9.3.2.4.5.2.8-.2.3-.6.4-.9.2z" opacity=".8"/>
  </svg>`,
  youtube: `<svg width="15" height="15" viewBox="0 0 15 15" fill="currentColor" aria-hidden="true">
    <path d="M7.5 0C3.4 0 0 3.4 0 7.5S3.4 15 7.5 15 15 11.6 15 7.5 11.6 0 7.5 0zm-1.5 4.5l6 3-6 3V4.5z" opacity=".8"/>
  </svg>`,
}};
"""

    OUTPUT_FILE.write_text(js, encoding="utf-8")
    print(f"OK: Wrote {len(episodes)} episode(s) + {len(appearances)} appearance(s) "
          f"to {OUTPUT_FILE.relative_to(ROOT)}")

    # ── Generate standalone episode pages ───────────────────────────────────
    for ep in episodes:
        slug = ep.get("slug")
        if not slug:
            continue
        page_dir = PAGES_DIR / slug
        page_dir.mkdir(parents=True, exist_ok=True)
        (page_dir / "index.html").write_text(render_episode_page(ep), encoding="utf-8")
        print(f"   + podcast/{slug}/index.html")


if __name__ == "__main__":
    build()
