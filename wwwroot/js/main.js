/* Broudo Holdings — site behaviour (no dependencies) */
(function () {
  'use strict';

  /* ---------- Mobile menu ---------- */
  var header = document.querySelector('.site-header');
  var toggle = document.querySelector('.nav-toggle');
  if (header && toggle) {
    toggle.addEventListener('click', function () {
      var open = header.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  /* ---------- Projects page: filters + grid/map view ---------- */
  var filterRoot = document.querySelector('[data-filters]');
  if (filterRoot) {
    var state = { market: 'All', type: 'All', status: 'All' };
    var cards = Array.prototype.slice.call(document.querySelectorAll('[data-project]'));
    var count = document.querySelector('[data-count]');
    var empty = document.querySelector('[data-empty]');

    var apply = function () {
      var shown = 0;
      cards.forEach(function (card) {
        var ok = ['market', 'type', 'status'].every(function (key) {
          return state[key] === 'All' || card.dataset[key] === state[key];
        });
        card.hidden = !ok;
        if (ok) shown++;
      });
      if (count) count.textContent = shown + (shown === 1 ? ' project' : ' projects');
      if (empty) empty.hidden = shown !== 0;
    };

    filterRoot.addEventListener('click', function (e) {
      var btn = e.target.closest('[data-filter]');
      if (!btn) return;
      var key = btn.dataset.filter;
      state[key] = btn.dataset.value;
      filterRoot.querySelectorAll('[data-filter="' + key + '"]').forEach(function (b) {
        b.setAttribute('aria-pressed', b === btn ? 'true' : 'false');
      });
      apply();
    });

    var viewBtns = document.querySelectorAll('[data-view]');
    var grid = document.querySelector('[data-grid]');
    var map = document.querySelector('[data-map]');
    viewBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var isMap = btn.dataset.view === 'map';
        viewBtns.forEach(function (b) { b.setAttribute('aria-pressed', b === btn ? 'true' : 'false'); });
        if (grid) grid.hidden = isMap;
        if (map) map.hidden = !isMap;
      });
    });

    apply();
  }

  /* ---------- Before / after slider ---------- */
  document.querySelectorAll('[data-compare]').forEach(function (el) {
    var range = el.querySelector('input[type="range"]');
    if (!range) return;
    var set = function () { el.style.setProperty('--pos', range.value + '%'); };
    range.addEventListener('input', set);
    set();
  });

  /* ---------- Forms (demo only) ----------
     Replace with your real form handler (Formspree, Netlify Forms,
     your CMS, or a server endpoint). Until then this just shows a
     thank-you message without sending anything. */
  document.querySelectorAll('form[data-demo-form]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      form.classList.add('is-sent');
      form.reset();
    });
  });

  /* ---------- Footer year ---------- */
  document.querySelectorAll('[data-year]').forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });
})();
