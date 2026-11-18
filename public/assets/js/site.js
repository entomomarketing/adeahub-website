/*!
 * adeahub — shared behaviour for every page.
 * Loaded once (deferred) from the <head>; page-specific scripts stay inline at the bottom of each page.
 * Covers: header scroll state, desktop dropdown menus, mobile menu, scroll reveal,
 * count-up numbers and the solution-card tilt.
 */
(function () {
  'use strict';

  var doc = document;
  var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var finePointer = window.matchMedia && window.matchMedia('(hover: hover) and (pointer: fine)').matches;

  /* ── Header: deeper shadow once the page has scrolled ── */
  var nav = doc.getElementById('main-nav');
  if (nav) {
    var onScroll = function () { nav.classList.toggle('nav-scrolled', window.scrollY > 10); };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* ── Desktop dropdowns: hover/focus open them in CSS; click and Escape make them work for touch and keyboard ── */
  var dropdowns = Array.prototype.slice.call(doc.querySelectorAll('.snav-dd'));
  function closeDropdowns(except) {
    dropdowns.forEach(function (dd) {
      if (dd === except) return;
      dd.classList.remove('is-open');
      var b = dd.querySelector('.snav-link');
      if (b) b.setAttribute('aria-expanded', 'false');
    });
  }
  dropdowns.forEach(function (dd) {
    var btn = dd.querySelector('button.snav-link');
    if (!btn) return;
    btn.setAttribute('aria-expanded', 'false');
    btn.addEventListener('click', function () {
      var open = !dd.classList.contains('is-open');
      closeDropdowns(dd);
      dd.classList.toggle('is-open', open);
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  });
  doc.addEventListener('click', function (e) {
    if (!e.target.closest || !e.target.closest('.snav-dd')) closeDropdowns();
  });

  /* ── Mobile menu ── */
  var menuBtn = doc.getElementById('mobile-menu-btn');
  var menu = doc.getElementById('mobile-menu');
  var ham = doc.getElementById('hamburger-icon');
  var cls = doc.getElementById('close-icon');
  function setMenu(open) {
    if (!menu) return;
    menu.classList.toggle('hidden', !open);
    if (ham) ham.classList.toggle('hidden', open);
    if (cls) cls.classList.toggle('hidden', !open);
    if (menuBtn) menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
  }
  if (menuBtn && menu) {
    menuBtn.addEventListener('click', function () { setMenu(menu.classList.contains('hidden')); });
    menu.addEventListener('click', function (e) { if (e.target.closest && e.target.closest('a')) setMenu(false); });
  }

  doc.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    closeDropdowns();
    if (menu && !menu.classList.contains('hidden')) { setMenu(false); if (menuBtn) menuBtn.focus(); }
  });

  /* ── Scroll reveal: .reveal / .reveal-left / .reveal-right get .visible when they enter the viewport ── */
  var reveals = doc.querySelectorAll('.reveal, .reveal-left, .reveal-right');
  if (!('IntersectionObserver' in window) || reduceMotion) {
    Array.prototype.forEach.call(reveals, function (el) { el.classList.add('visible'); });
  } else {
    // anything already on screen starts its entrance immediately instead of waiting for the observer
    var vh = window.innerHeight;
    Array.prototype.forEach.call(reveals, function (el) {
      var r = el.getBoundingClientRect();
      if (r.top < vh && r.bottom > 0) el.classList.add('visible');
    });
    var revealObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) { entry.target.classList.add('visible'); revealObserver.unobserve(entry.target); }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    Array.prototype.forEach.call(reveals, function (el) { revealObserver.observe(el); });
  }

  /* ── Count-up numbers: <span class="counter">30,000+</span>
     The final figure stays in the HTML (what crawlers and no-JS visitors read); the animation counts up to it
     using the same prefix, suffix and thousands separators, then restores the exact original text. ── */
  function animateCounter(el) {
    var finalText = el.textContent;
    var m = finalText.match(/^(\D*?)(\d[\d,]*(?:\.\d+)?)(.*)$/);
    if (!m) return;
    var prefix = m[1], digits = m[2], suffix = m[3];
    var target = parseFloat(digits.replace(/,/g, ''));
    var useCommas = digits.indexOf(',') !== -1;
    var decimals = (digits.split('.')[1] || '').length;
    function fmt(n) {
      var s = n.toFixed(decimals);
      if (useCommas) s = s.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
      return prefix + s + suffix;
    }
    var duration = 1600, start = null;
    function step(ts) {
      if (start === null) start = ts;
      var p = Math.min((ts - start) / duration, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = p < 1 ? fmt(decimals ? eased * target : Math.round(eased * target)) : finalText;
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  var counters = doc.querySelectorAll('.counter');
  if (counters.length && 'IntersectionObserver' in window && !reduceMotion) {
    var counterObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) { animateCounter(entry.target); counterObserver.unobserve(entry.target); }
      });
    }, { threshold: 0.5 });
    Array.prototype.forEach.call(counters, function (el) { counterObserver.observe(el); });
  }

  /* ── Solution cards: 3D tilt + cursor glow (mouse/trackpad only, never with reduced motion) ── */
  Array.prototype.forEach.call(doc.querySelectorAll('.solution-card'), function (card) {
    card.style.position = 'relative';
    var glow = card.querySelector('.card-glow-layer');
    if (!glow) {
      glow = doc.createElement('div');
      glow.className = 'card-glow-layer';
      card.insertBefore(glow, card.firstChild);
    }
    if (!finePointer || reduceMotion) return;
    {
      card.addEventListener('mousemove', function (e) {
        var r = card.getBoundingClientRect();
        var x = e.clientX - r.left, y = e.clientY - r.top;
        var cx = r.width / 2, cy = r.height / 2;
        var tiltY = ((x - cx) / cx) * 6, tiltX = -((y - cy) / cy) * 6;
        card.style.transform = 'perspective(900px) rotateX(' + tiltX + 'deg) rotateY(' + tiltY + 'deg) scale(1.018)';
        card.style.boxShadow = '0 28px 56px -8px rgba(82,152,248,0.22), 0 8px 20px -4px rgba(82,152,248,0.14)';
        glow.style.background = 'radial-gradient(280px circle at ' + x + 'px ' + y + 'px, rgba(82,152,248,0.13) 0%, transparent 70%)';
      });
      card.addEventListener('mouseleave', function () {
        card.style.transform = '';
        card.style.boxShadow = '';
        glow.style.background = '';
      });
    }
  });
})();
