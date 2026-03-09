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


if __name__ == "__main__":
    build()
