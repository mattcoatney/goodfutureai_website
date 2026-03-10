/**
 * layout.js — shared header and footer for GoodFuture.ai
 *
 * Injects nav and footer HTML on every page.
 * Computes image paths relative to the current page depth so this works
 * both when served via HTTP and when opened directly via file://.
 */

(function () {
  // Compute path prefix back to site root.
  // e.g. at /insights/ → root = '../'
  //      at /index.html          → root = './'
  // Strip trailing slash, split into segments.
  // Also strip a trailing filename (has '.') so file:// URLs work the same as HTTP.
  var parts = window.location.pathname.replace(/\/$/, '').split('/').filter(Boolean);
  if (parts.length > 0 && parts[parts.length - 1].indexOf('.') !== -1) {
    parts = parts.slice(0, -1);
  }
  var known = ['insights', 'podcast', 'resources'];
  var last       = parts.length > 0 ? parts[parts.length - 1] : '';
  var secondLast = parts.length > 1 ? parts[parts.length - 2] : '';
  // root page → './'  |  /insights/ → '../'  |  /insights/{slug}/ → '../../'
  var root = known.indexOf(last) !== -1 ? '../'
           : known.indexOf(secondLast) !== -1 ? '../../'
           : './';

  // ── HEADER ──────────────────────────────────────────────────────────────
  var path = window.location.pathname;
  function isActive(seg) {
    return path.indexOf('/' + seg + '/') !== -1;
  }
  function activeClass(seg) {
    return isActive(seg) ? ' class="active"' : '';
  }

  var headerHTML =
    '<nav class="nav" id="nav">' +
    '<div class="container"><div class="nav-inner">' +
    '<a href="' + root + '" class="nav-logo">' +
    '<img src="' + root + 'images/wordmark-on-light.png" alt="GoodFuture.ai">' +
    '</a>' +
    '<ul class="nav-links">' +
    '<li><a href="' + root + 'insights/"' + activeClass('insights') + '>Insights</a></li>' +
    '<li><a href="' + root + 'podcast/"'  + activeClass('podcast')  + '>Podcast</a></li>' +
    '<li><a href="' + root + 'resources/"'+ activeClass('resources')+ '>Resources</a></li>' +
    '<li><a href="' + root + '#about">About</a></li>' +
    '<li><a href="' + root + '#connect" class="nav-cta">Newsletter</a></li>' +
    '</ul>' +
    '<button class="nav-hamburger" id="hamburger" aria-label="Open menu" aria-expanded="false">' +
    '<span></span><span></span><span></span>' +
    '</button>' +
    '</div></div></nav>' +
    '<div class="mobile-nav" id="mobileNav" role="dialog" aria-label="Navigation">' +
    '<button class="mobile-nav-close" id="navClose" aria-label="Close menu">\u2715</button>' +
    '<a href="' + root + 'insights/"  onclick="closeMobileNav()">Insights</a>' +
    '<a href="' + root + 'podcast/"   onclick="closeMobileNav()">Podcast</a>' +
    '<a href="' + root + 'resources/" onclick="closeMobileNav()">Resources</a>' +
    '<a href="' + root + '#about"     onclick="closeMobileNav()">About</a>' +
    '<a href="' + root + '#connect"   onclick="closeMobileNav()" style="color:var(--morning-teal)">Newsletter</a>' +
    '</div>';

  // ── FOOTER ──────────────────────────────────────────────────────────────
  var footerHTML =
    '<div class="container"><div class="footer-top">' +
    '<div class="footer-brand">' +
    '<a href="' + root + '" class="nav-logo">' +
    '<img src="' + root + 'images/wordmark-transparent-dark-text.png" alt="GoodFuture.ai">' +
    '</a>' +
    '<p>We help people make sense of AI \u2014 and feel a little more hopeful about where we\'re headed.</p>' +
    '</div>' +
    '<div class="footer-col"><h5>Explore</h5><ul>' +
    '<li><a href="' + root + 'insights/">Insights</a></li>' +
    '<li><a href="' + root + 'podcast/">Podcast</a></li>' +
    '<li><a href="' + root + 'resources/">Resources</a></li>' +
    '<li><a href="' + root + '#about">About</a></li>' +
    '</ul></div>' +
    '<div class="footer-col"><h5>Stay in Touch</h5><ul>' +
    '<li><a href="' + root + '#connect">Newsletter</a></li>' +
    '<li><a href="mailto:hello@goodfuture.ai">Email Me</a></li>' +
    '</ul></div>' +
    '<div class="footer-col"><h5>Also Worth Seeing</h5><ul>' +
    '<li><a href="https://www.youtube.com/watch?v=Hzy_GhX8_Cc" target="_blank" rel="noopener noreferrer">My TED Talk</a></li>' +
    '<li><a href="https://www.humancloudbook.com/" target="_blank" rel="noopener noreferrer">The Human Cloud</a></li>' +
    '<li><a href="' + root + 'resources/">All Resources</a></li>' +
    '</ul></div>' +
    '</div>' +
    '<div class="footer-bottom">' +
    '<p>\u00a9 2026 GoodFuture.ai \u00b7 Built with optimism</p>' +
    // Social icons commented out until accounts are established:
    // '<div class="socials">' +
    // '<a href="#" class="social" aria-label="LinkedIn" ...>LinkedIn SVG</a>' +
    // '<a href="#" class="social" aria-label="Twitter" ...>Twitter SVG</a>' +
    // '<a href="https://www.youtube.com/watch?v=Hzy_GhX8_Cc" class="social" aria-label="YouTube" ...>YouTube SVG</a>' +
    // '</div>' +
    '</div></div>';

  // ── INJECT ───────────────────────────────────────────────────────────────
  var header = document.querySelector('header');
  var footer = document.querySelector('footer');
  if (header) header.innerHTML = headerHTML;
  if (footer) footer.innerHTML = footerHTML;

  // Nav scroll effect
  var nav = document.getElementById('nav');
  if (nav) {
    window.addEventListener('scroll', function () {
      nav.classList.toggle('scrolled', window.scrollY > 20);
    }, { passive: true });
  }

  // Mobile nav
  var hamburger = document.getElementById('hamburger');
  var mobileNav  = document.getElementById('mobileNav');
  var navClose   = document.getElementById('navClose');

  window.closeMobileNav = function () {
    if (mobileNav) mobileNav.classList.remove('open');
    document.body.style.overflow = '';
    if (hamburger) hamburger.setAttribute('aria-expanded', 'false');
  };

  if (hamburger) {
    hamburger.addEventListener('click', function () {
      mobileNav.classList.add('open');
      document.body.style.overflow = 'hidden';
      hamburger.setAttribute('aria-expanded', 'true');
    });
  }
  if (navClose) navClose.addEventListener('click', window.closeMobileNav);
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') window.closeMobileNav();
  });

})();
