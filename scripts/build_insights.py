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


if __name__ == "__main__":
    build()
