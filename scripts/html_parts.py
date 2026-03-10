"""
html_parts.py — shared HTML snippets and utilities for GoodFuture.ai build scripts.

Used by build_insights.py and build_podcast.py.
"""

import re
from pathlib import Path


# ── Section replacement ─────────────────────────────────────────────────────

def replace_section(filepath: Path, marker: str, new_content: str) -> None:
    """
    Replace the block between <!-- GF:MARKER:START --> and <!-- GF:MARKER:END -->
    in the given HTML file, then write the file back.
    Raises ValueError if the markers are not found.
    """
    html = filepath.read_text(encoding="utf-8")
    start_tag = f"<!-- GF:{marker}:START -->"
    end_tag   = f"<!-- GF:{marker}:END -->"
    pattern   = re.compile(re.escape(start_tag) + r".*?" + re.escape(end_tag), re.DOTALL)
    replacement = f"{start_tag}\n{new_content}\n{end_tag}"
    result, count = pattern.subn(replacement, html)
    if count == 0:
        raise ValueError(f"Markers GF:{marker}:START/END not found in {filepath.name}")
    filepath.write_text(result, encoding="utf-8")


# ── Nav HTML ────────────────────────────────────────────────────────────────

def nav_html(root: str, active: str = "") -> str:
    """
    Return the full <header>…</header> HTML block.

    root:   relative path back to site root — './', '../', or '../../'
    active: 'insights' | 'podcast' | 'resources' | '' (home, no active item)
    """
    def ac(seg: str) -> str:
        return ' class="active"' if active == seg else ""

    return (
        f'<header>'
        f'<nav class="nav" id="nav">'
        f'<div class="container"><div class="nav-inner">'
        f'<a href="{root}" class="nav-logo">'
        f'<img src="{root}images/wordmark-on-light.png" alt="GoodFuture.ai">'
        f'</a>'
        f'<ul class="nav-links">'
        f'<li><a href="{root}insights/"{ac("insights")}>Insights</a></li>'
        f'<li><a href="{root}podcast/"{ac("podcast")}>Podcast</a></li>'
        f'<li><a href="{root}resources/"{ac("resources")}>Resources</a></li>'
        f'<li><a href="{root}#about">About</a></li>'
        f'<li><a href="{root}#connect" class="nav-cta">Newsletter</a></li>'
        f'</ul>'
        f'<button class="nav-hamburger" id="hamburger" aria-label="Open menu" aria-expanded="false">'
        f'<span></span><span></span><span></span>'
        f'</button>'
        f'</div></div>'
        f'</nav>'
        f'<div class="mobile-nav" id="mobileNav" role="dialog" aria-label="Navigation">'
        f'<button class="mobile-nav-close" id="navClose" aria-label="Close menu">&#x2715;</button>'
        f'<a href="{root}insights/"  onclick="closeMobileNav()">Insights</a>'
        f'<a href="{root}podcast/"   onclick="closeMobileNav()">Podcast</a>'
        f'<a href="{root}resources/" onclick="closeMobileNav()">Resources</a>'
        f'<a href="{root}#about"     onclick="closeMobileNav()">About</a>'
        f'<a href="{root}#connect"   onclick="closeMobileNav()" style="color:var(--morning-teal)">Newsletter</a>'
        f'</div>'
        f'</header>'
    )


# ── Footer HTML ─────────────────────────────────────────────────────────────

def footer_html(root: str) -> str:
    """Return the full <footer class="footer">…</footer> HTML block."""
    return (
        f'<footer class="footer">'
        f'<div class="container"><div class="footer-top">'
        f'<div class="footer-brand">'
        f'<a href="{root}" class="nav-logo">'
        f'<img src="{root}images/wordmark-transparent-dark-text.png" alt="GoodFuture.ai">'
        f'</a>'
        f'<p>We help people make sense of AI &mdash; and feel a little more hopeful about where we&rsquo;re headed.</p>'
        f'</div>'
        f'<div class="footer-col"><h5>Explore</h5><ul>'
        f'<li><a href="{root}insights/">Insights</a></li>'
        f'<li><a href="{root}podcast/">Podcast</a></li>'
        f'<li><a href="{root}resources/">Resources</a></li>'
        f'<li><a href="{root}#about">About</a></li>'
        f'</ul></div>'
        f'<div class="footer-col"><h5>Stay in Touch</h5><ul>'
        f'<li><a href="{root}#connect">Newsletter</a></li>'
        f'<li><a href="mailto:hello@goodfuture.ai">Email Me</a></li>'
        f'</ul></div>'
        f'<div class="footer-col"><h5>Also Worth Seeing</h5><ul>'
        f'<li><a href="https://www.youtube.com/watch?v=Hzy_GhX8_Cc" target="_blank" rel="noopener noreferrer">My TED Talk</a></li>'
        f'<li><a href="https://www.humancloudbook.com/" target="_blank" rel="noopener noreferrer">The Human Cloud</a></li>'
        f'<li><a href="{root}resources/">All Resources</a></li>'
        f'</ul></div>'
        f'</div>'
        f'<div class="footer-bottom">'
        f'<p>&copy; 2026 GoodFuture.ai &middot; Built with optimism</p>'
        f'</div></div>'
        f'</footer>'
    )
