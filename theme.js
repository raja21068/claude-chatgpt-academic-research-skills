// Theme behaviour: highlight the current section in the section menu. Nothing is ever hidden by this script.
(function () {
  if (!("IntersectionObserver" in window)) return;

  // 1. Section menu: mark the link of the section you are reading.
  const links = [...document.querySelectorAll(".section-nav a[href^='#']")];
  const map = new Map();
  for (const a of links) {
    const el = document.querySelector(a.getAttribute("href"));
    if (el) map.set(el, a);
  }
  if (map.size) {
    const visible = new Map();
    const spy = new IntersectionObserver((entries) => {
      for (const e of entries) e.isIntersecting ? visible.set(e.target, e.intersectionRatio) : visible.delete(e.target);
      let best = null, top = Infinity;
      for (const el of visible.keys()) {
        const y = Math.abs(el.getBoundingClientRect().top - 120);
        if (y < top) { top = y; best = el; }
      }
      links.forEach((a) => a.classList.toggle("is-active", !!best && map.get(best) === a));
    }, { rootMargin: "-15% 0px -55% 0px", threshold: [0, 0.1] });
    map.forEach((_, el) => spy.observe(el));
  }

})();
