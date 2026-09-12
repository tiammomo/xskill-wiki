/* xskill wiki — sidebar active-section highlight + section reveal + TOC fold */
(function () {
  "use strict";
  const responsiveToc = document.querySelector("[data-responsive-toc]");
  if (responsiveToc) {
    const narrow = window.matchMedia("(max-width: 900px)");
    function sizeToc() { responsiveToc.open = !narrow.matches; }
    sizeToc();
    narrow.addEventListener("change", sizeToc);
  }
  const links = Array.prototype.slice.call(document.querySelectorAll('.wiki-toc nav a[href^="#"]'));
  const map = {};
  links.forEach(function (a) { map[a.getAttribute("href").slice(1)] = a; });

  function setFoldOpen(group, open) {
    if (!group) return;
    group.classList.toggle("is-open", open);
    const btn = group.querySelector(".wiki-toc__toggle");
    if (btn) btn.setAttribute("aria-expanded", open ? "true" : "false");
  }

  function openFoldForId(id) {
    const a = map[id];
    if (!a) return;
    const sub = a.closest(".wiki-toc__sub");
    if (sub) setFoldOpen(sub.closest("[data-toc-fold]"), true);
  }

  document.querySelectorAll("[data-toc-fold]").forEach(function (group) {
    const btn = group.querySelector(".wiki-toc__toggle");
    if (!btn) return;
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      setFoldOpen(group, !group.classList.contains("is-open"));
    });
  });

  const spy = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      links.forEach(function (a) { a.classList.remove("is-active"); });
      const a = map[e.target.id];
      if (a) a.classList.add("is-active");
    });
  }, { rootMargin: "-20% 0px -70% 0px", threshold: 0 });

  document.querySelectorAll(".doc-sec").forEach(function (s) { spy.observe(s); });

  const rev = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.add("in"); rev.unobserve(e.target); }
    });
  }, { threshold: 0.08 });
  document.querySelectorAll(".doc-sec").forEach(function (s) { s.classList.add("reveal"); rev.observe(s); });

  openFoldForId((location.hash || "").replace(/^#/, ""));
  window.addEventListener("hashchange", function () {
    openFoldForId((location.hash || "").replace(/^#/, ""));
  });
})();
