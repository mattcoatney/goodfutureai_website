/**
 * layout.js — nav behaviour for GoodFuture.ai
 *
 * Nav and footer HTML are now written statically into each page by the
 * build scripts (build_insights.py / build_podcast.py).  This file only
 * provides the runtime behaviour: scroll-shadow on the nav bar and the
 * mobile hamburger menu.
 */

(function () {

  // ── Nav scroll shadow ─────────────────────────────────────────────────────
  var nav = document.getElementById('nav');
  if (nav) {
    window.addEventListener('scroll', function () {
      nav.classList.toggle('scrolled', window.scrollY > 20);
    }, { passive: true });
  }

  // ── Mobile nav ────────────────────────────────────────────────────────────
  var hamburger = document.getElementById('hamburger');
  var mobileNav = document.getElementById('mobileNav');
  var navClose  = document.getElementById('navClose');

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
