#!/usr/bin/env python3
"""
build_podcast.py
────────────────
Reads:
  content/podcast/_show.yaml              — show-level metadata
  content/podcast/episodes/*.md           — individual episodes
  content/podcast/appearances/*.md        — guest appearances

And regenerates:
  1. data/podcast.js                      (JS data for any dynamic use)
  2. podcast/{slug}/index.html            (standalone episode pages)
  3. Static sections in podcast/index.html
  4. Home appearances preview in index.html

Sections are delimited by <!-- GF:MARKER:START --> / <!-- GF:MARKER:END --> comments.

Usage:
    python scripts/build_podcast.py
"""

import sys
import yaml
import markdown
from pathlib import Path
from datetime import date as date_type

sys.path.insert(0, str(Path(__file__).parent))
from html_parts import nav_html, footer_html, replace_section

# ── Paths ──────────────────────────────────────────────────────────────────
ROOT            = Path(__file__).resolve().parent.parent
EPISODES_DIR    = ROOT / "content" / "podcast" / "episodes"
APPEARANCES_DIR = ROOT / "content" / "podcast" / "appearances"
SHOW_FILE       = ROOT / "content" / "podcast" / "_show.yaml"
OUTPUT_FILE     = ROOT / "data" / "podcast.js"
PAGES_DIR       = ROOT / "podcast"
HOME_FILE       = ROOT / "index.html"
SITE_URL        = "https://goodfuture.ai"
FONTS_URL       = (
    "https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@"
    "0,9..144,300;0,9..144,400;0,9..144,500;0,9..144,600;0,9..144,700;"
    "0,9..144,800;0,9..144,900;1,9..144,400;1,9..144,500;1,9..144,600"
    "&family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;"
    "1,400;1,500&display=swap"
)

MD     = markdown.Markdown(extensions=["extra", "nl2br"])
MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

ARROW_SVG = (
    '<svg width="13" height="13" viewBox="0 0 13 13" fill="none" aria-hidden="true">'
    '<path d="M2 6.5h9M7 3l3.5 3.5L7 10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>'
    '</svg>'
)
MIC_SVG = (
    '<svg width="36" height="36" viewBox="0 0 48 48" fill="none" aria-hidden="true">'
    '<circle cx="24" cy="20" r="8" stroke="var(--morning-teal)" stroke-width="2"/>'
    '<path d="M12 20a12 12 0 0024 0" stroke="var(--morning-teal)" stroke-width="2" fill="none" stroke-linecap="round"/>'
    '<path d="M24 32v8M20 40h8" stroke="var(--morning-teal)" stroke-width="2" stroke-linecap="round"/>'
    '</svg>'
)


# ── Helpers ────────────────────────────────────────────────────────────────

def html_esc(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")


def format_date(date_val) -> str:
    d = date_val if hasattr(date_val, "month") else date_type.fromisoformat(str(date_val))
    return f"{MONTHS[d.month - 1]} {d.year}"


def parse_md_file(path: Path) -> tuple:
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
    if not SHOW_FILE.exists():
        print(f"Warning: {SHOW_FILE} not found — using defaults.")
        return {
            "name":        "Building a Better Future Together",
            "tagline":     "with GoodFuture.ai",
            "description": "Real conversations about navigating the AI era.",
            "platforms":   [],
            "listenUrl":   "#",
        }
    try:
        cfg = yaml.safe_load(SHOW_FILE.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        print(f"ERROR: could not parse _show.yaml — {e}", file=sys.stderr)
        sys.exit(1)
    return cfg


def load_items(directory: Path, required_fields: list) -> tuple:
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


# ── JS string helpers ──────────────────────────────────────────────────────

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


def render_episode_js(ep: dict) -> str:
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


def render_appearance_js(ap: dict) -> str:
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


def render_show_js(show: dict) -> str:
    platforms_js = "[\n" + ",\n".join(
        f'    {{ name: {js_string(p["name"])}, url: {js_string(p["url"])}, icon: {js_string(p["icon"])} }}'
        for p in show.get("platforms", [])
    ) + "\n  ]"
    return (
        f"const PODCAST_SHOW = {{\n"
        f"  name:        {js_string(show.get('name', ''))},\n"
        f"  tagline:     {js_string(show.get('tagline', ''))},\n"
        f"  description: {js_string(show.get('description', ''))},\n"
        f"  platforms:   {platforms_js},\n"
        f"  listenUrl:   {js_string(show.get('listenUrl', '#'))},\n"
        f"}};"
    )


# ── Static HTML renderers ──────────────────────────────────────────────────

def render_show_description(show: dict) -> str:
    """Render the show description paragraph for GF:SHOW_DESC."""
    return html_esc(show.get("description", "Real conversations about navigating the AI era."))


def render_episodes_html(episodes: list) -> str:
    """Render the episodes section for GF:EPISODES."""
    if not episodes:
        return (
            '      <div class="episode-coming fade-up">\n'
            '        <div class="ec-icon">' + MIC_SVG + '</div>\n'
            '        <h3>First episode coming soon</h3>\n'
            '        <p>I&rsquo;m working on something good. Subscribe to the newsletter and you&rsquo;ll be the first to know when it drops.</p>\n'
            '        <a href="../#connect" class="btn btn-teal">Get notified &rarr;</a>\n'
            '      </div>'
        )

    cards = []
    for i, ep in enumerate(episodes):
        title    = html_esc(ep.get("title", ""))
        excerpt  = html_esc(ep.get("excerpt", ""))
        slug     = ep.get("slug", "")
        date_d   = format_date(ep.get("date", ""))
        duration = ep.get("duration", "")
        youtube  = ep.get("youtubeId", "")
        spotify_embed = ep.get("spotifyEmbedUrl", "")
        apple_url     = ep.get("applePodcastsUrl", "")
        spotify_url   = ep.get("spotifyUrl", "")
        tags     = ep.get("tags", [])

        tags_html = "".join(f'<span class="a-tag">{html_esc(t)}</span>' for t in tags) if tags else ""

        meta = f'<span>{date_d}</span>'
        if duration:
            meta += f'<span class="ep-dot"></span><span>{html_esc(duration)}</span>'

        if youtube:
            player = (
                '<div class="ep-player">'
                '<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;border-radius:var(--radius-md);">'
                f'<iframe src="https://www.youtube.com/embed/{html_esc(youtube)}"'
                f' style="position:absolute;top:0;left:0;width:100%;height:100%;border:none;"'
                f' title="{title}" allowfullscreen loading="lazy"></iframe>'
                '</div></div>'
            )
        elif spotify_embed:
            player = (
                '<div class="ep-player">'
                f'<iframe src="{html_esc(spotify_embed)}" height="152"'
                ' allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"'
                ' loading="lazy" style="border-radius:var(--radius-md);border:none;width:100%;"></iframe>'
                '</div>'
            )
        else:
            player = ""

        links = ""
        if apple_url:
            links += f'<a href="{html_esc(apple_url)}" class="ep-link" target="_blank" rel="noopener noreferrer">Apple Podcasts &rarr;</a>'
        if spotify_url:
            links += f'<a href="{html_esc(spotify_url)}" class="ep-link" target="_blank" rel="noopener noreferrer">Spotify &rarr;</a>'
        links_html = f'<div class="ep-links">{links}</div>' if links else ""

        num = str(i + 1).zfill(2)
        delay = (i % 3) + 1
        card = (
            f'      <div class="episode-card fade-up delay-{delay}">\n'
            f'        <div class="ep-inner">\n'
            f'          <div class="ep-number">{num}</div>\n'
            f'          <div class="ep-body">\n'
            f'            <div class="ep-meta-row">{meta}</div>\n'
            f'            {"<div class=\"ep-tags\">" + tags_html + "</div>" if tags_html else ""}\n'
            f'            <h3>{title}</h3>\n'
            f'            <p>{excerpt}</p>\n'
            f'            {player}\n'
            f'            {links_html}\n'
            f'          </div>\n'
            f'        </div>\n'
            f'      </div>'
        )
        cards.append(card)

    return f'      <div class="episodes-grid">\n' + "\n".join(cards) + '\n      </div>'


def render_appearances_html(appearances: list, limit: int = 0) -> str:
    """Render appearance cards. limit=0 means all."""
    items = appearances[:limit] if limit else appearances
    if not items:
        return '      <p style="color:var(--warm-stone)">No appearances listed yet.</p>'

    cards = []
    for i, app in enumerate(items):
        show    = html_esc(app.get("show", ""))
        title   = html_esc(app.get("title", ""))
        desc    = html_esc(app.get("description", ""))
        url     = html_esc(app.get("url", "#"))
        date_d  = format_date(app.get("date", ""))
        tags    = app.get("tags", [])
        tags_html = "".join(f'<span class="a-tag">{html_esc(t)}</span>' for t in tags) if tags else ""
        delay   = (i % 3) + 1

        card = (
            f'      <div class="appear-card fade-up delay-{delay}">\n'
            f'        <div class="appear-show">{show}</div>\n'
            f'        <div class="appear-date">{date_d}</div>\n'
            f'        {"<div class=\"appear-tags\">" + tags_html + "</div>" if tags_html else ""}\n'
            f'        <h4>{title}</h4>\n'
            f'        <p>{desc}</p>\n'
            f'        <a href="{url}" class="appear-link" target="_blank" rel="noopener noreferrer">'
            f'Listen {ARROW_SVG}</a>\n'
            f'      </div>'
        )
        cards.append(card)
    return "\n".join(cards)


def render_home_appearances_html(appearances: list) -> str:
    """Render 3 appearance cards for the home page GF:HOME_APPEARANCES section."""
    return render_appearances_html(appearances, limit=3)


# ── Standalone episode page ────────────────────────────────────────────────

def render_episode_page(ep: dict) -> str:
    title         = ep.get("title", "")
    slug          = ep.get("slug", "")
    excerpt       = ep.get("excerpt", "")
    tags          = ep.get("tags", [])
    duration      = ep.get("duration", "")
    youtube       = ep.get("youtubeId", "")
    spotify_embed = ep.get("spotifyEmbedUrl", "")
    apple_url     = ep.get("applePodcastsUrl", "")
    spotify_url   = ep.get("spotifyUrl", "")
    date_str      = str(ep.get("date", ""))

    MD.reset()
    body = MD.convert(ep["_body"]) if ep.get("_body") else ""

    date_display = format_date(ep.get("date", date_str))
    canonical    = f"{SITE_URL}/podcast/{slug}/"

    tags_html    = "".join(f'<span class="a-tag a-tag-inv">{t}</span>' for t in tags)
    meta_parts   = [date_display] + ([duration] if duration else [])
    meta_html    = '<span class="ep-meta-dot"></span>'.join(f"<span>{p}</span>" for p in meta_parts)

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
        links.append(f'<a href="{html_esc(apple_url)}" class="ep-ext-link" target="_blank" rel="noopener noreferrer">Apple Podcasts &rarr;</a>')
    if spotify_url:
        links.append(f'<a href="{html_esc(spotify_url)}" class="ep-ext-link" target="_blank" rel="noopener noreferrer">Spotify &rarr;</a>')
    links_html    = f'<div class="ep-ext-links">{"".join(links)}</div>' if links else ""
    body_section  = f'<div class="ep-body-text">{body}</div>' if body else ""

    nav  = nav_html("../../", active="podcast")
    foot = footer_html("../../")

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
{nav}

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
  {links_html}
  {body_section}
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
    show = load_show_config()

    episodes,    ep_errors = load_items(EPISODES_DIR,    ["slug", "title", "date"])
    appearances, ap_errors = load_items(APPEARANCES_DIR, ["show", "title", "date"])

    all_errors = ep_errors + ap_errors
    if all_errors:
        print("Errors found — fix these before continuing:\n", file=sys.stderr)
        for e in all_errors:
            print(f"  * {e}", file=sys.stderr)
        sys.exit(1)

    episodes.sort(   key=lambda e: str(e.get("date", "")), reverse=True)
    appearances.sort(key=lambda a: str(a.get("date", "")), reverse=True)

    # Build descriptions from body text if not set in frontmatter
    for ap in appearances:
        body = ap.get("_body", "").strip()
        if not ap.get("description") and body:
            ap["description"] = " ".join(body.split())

    # ── 1. Generate data/podcast.js ────────────────────────────────────────
    ep_blocks = ",\n".join(render_episode_js(ep) for ep in episodes)
    ap_blocks = ",\n".join(render_appearance_js(ap) for ap in appearances)

    episodes_section = (
        f"const PODCAST_EPISODES = [\n{ep_blocks}\n];"
        if episodes else
        "const PODCAST_EPISODES = [\n  /* No episodes yet — add .md files to content/podcast/episodes/ */\n];"
    )

    js = f"""\
/**
 * GoodFuture.ai — Podcast Content Data
 *
 * !! AUTO-GENERATED — do not edit directly !!
 * Edit files in content/podcast/ then run:
 *
 *     python scripts/build_podcast.py
 */

{render_show_js(show)}

{episodes_section}

const PODCAST_APPEARANCES = [
{ap_blocks}
];

/* Helper: format date for display */
function formatPodcastDate(dateStr) {{
  const d = new Date(dateStr + 'T00:00:00');
  return d.toLocaleDateString('en-US', {{ month: 'short', year: 'numeric' }});
}}
"""

    OUTPUT_FILE.write_text(js, encoding="utf-8")
    print(f"OK  data/podcast.js ({len(episodes)} episode(s), {len(appearances)} appearance(s))")

    # ── 2. Generate standalone episode pages ───────────────────────────────
    for ep in episodes:
        slug = ep.get("slug")
        if not slug:
            continue
        page_dir = PAGES_DIR / slug
        page_dir.mkdir(parents=True, exist_ok=True)
        (page_dir / "index.html").write_text(render_episode_page(ep), encoding="utf-8")
        print(f"    + podcast/{slug}/index.html")

    # ── 3. Update podcast/index.html static sections ───────────────────────
    podcast_index = PAGES_DIR / "index.html"
    if podcast_index.exists():
        try:
            replace_section(podcast_index, "SHOW_DESC",   render_show_description(show))
            replace_section(podcast_index, "EPISODES",    render_episodes_html(episodes))
            replace_section(podcast_index, "APPEARANCES", render_appearances_html(appearances))
            print(f"OK  podcast/index.html (show desc + episodes + appearances updated)")
        except ValueError as e:
            print(f"Warning: {e}", file=sys.stderr)
    else:
        print(f"Warning: {podcast_index} not found — skipping static list update", file=sys.stderr)

    # ── 4. Update home page appearances preview ────────────────────────────
    if HOME_FILE.exists():
        try:
            replace_section(HOME_FILE, "HOME_APPEARANCES", render_home_appearances_html(appearances))
            print(f"OK  index.html (home appearances preview updated)")
        except ValueError as e:
            print(f"Warning: {e}", file=sys.stderr)
    else:
        print(f"Warning: {HOME_FILE} not found — skipping home appearances update", file=sys.stderr)


if __name__ == "__main__":
    build()
