// Paper gallery: category chips, previous/next, Open, PDF, Hide, and an in-page PDF viewer drawn with PDF.js.
// Pages are drawn only when they scroll near the viewer, so phones stay light.
(function () {
  const PAPERS = [
    { id: "01", domain: "Others", name: "DynaSpec-RAG", title: "Adaptive Spectral Retrieval and Reliability-Guided Fusion for Zero-Shot Time-Series Forecasting", file: "papers/01_Others_DynaSpec-RAG_Audited.pdf", size: "1.7 MB" },
    { id: "02", domain: "LLMs", name: "Mem-MaxRL", title: "Stabilizing Reasoning Diversity in Large Language Models Through Memory-Guided Reinforcement Learning", file: "papers/02_LLMs_Mem-MaxRL_Audited.pdf", size: "0.8 MB" },
    { id: "03", domain: "Foundation", name: "UNI-XDLM", title: "Distribution-Aware Noise Calibration for Efficient Discrete Diffusion Language Modeling", file: "papers/03_Foundation_UNI-XDLM_Audited.pdf", size: "0.6 MB" },
    { id: "04", domain: "Interpretability", name: "Overdamped DAVE", title: "Efficient Vision Transformer Attribution Through Rank-Preserving Concentration Dynamics", file: "papers/04_Interpretability_Overdamped_DAVE_Audited.pdf", size: "3.0 MB" },
    { id: "05", domain: "Alignment", name: "CHVA", title: "Hierarchical Value Representation and Calibration for Reliable Large Language Model Alignment", file: "papers/05_Alignment_CHVA_Audited.pdf", size: "4.2 MB" },
    { id: "06", domain: "Neuroscience", name: "Simplified DWGR-SVL", title: "Simplifying Spike-Driven Vision-Language Pretraining for Efficient Open-World 3D Recognition", file: "papers/06_Neuroscience_Simplified_DWGR-SVL_Audited.pdf", size: "2.4 MB" },
    { id: "07", domain: "Neuroscience", name: "FCD-Engram", title: "Curvature-Guided Parameter Editing for Selective Knowledge Removal in Large Language Models", file: "papers/07_Neuroscience_FCD-Engram_Audited.pdf", size: "2.6 MB" },
  ];
  const DOMAINS = [...new Set(PAPERS.map((p) => p.domain))];
  const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");

  let pdfReady;
  function loadPdfJs() {
    if (pdfReady) return pdfReady;
    pdfReady = new Promise((ok, no) => {
      if (window.pdfjsLib) return ok();
      const s = document.createElement("script");
      s.src = "vendor/pdfjs/pdf.min.js?v=3.11.174";
      s.onload = () => { window.pdfjsLib.GlobalWorkerOptions.workerSrc = "vendor/pdfjs/pdf.worker.min.js?v=3.11.174"; ok(); };
      s.onerror = () => { pdfReady = null; no(new Error("pdf.js failed to load")); };
      document.head.append(s);
    });
    return pdfReady;
  }

  function init(root) {
    let domain = "All", pos = 0, open = root.dataset.open !== "false", token = 0, current = null;
    const list = () => (domain === "All" ? PAPERS : PAPERS.filter((p) => p.domain === domain));

    root.classList.add("gal");
    root.innerHTML = `
      <div class="gal-chips" role="group" aria-label="Filter by area"></div>
      <div class="gal-panel">
        <div class="gal-head"><span class="gal-tag"></span><strong class="gal-name"></strong></div>
        <p class="gal-title"></p>
        <div class="gal-bar">
          <button type="button" class="gal-btn gal-prev" aria-label="Previous paper">‹</button>
          <span class="gal-count" aria-live="polite"></span>
          <button type="button" class="gal-btn gal-next" aria-label="Next paper">›</button>
          <a class="gal-btn gal-open" target="_blank" rel="noopener">Open ↗</a>
          <a class="gal-btn gal-dl" download>PDF ↓ <small></small></a>
          <button type="button" class="gal-btn gal-toggle" aria-expanded="true">Hide</button>
        </div>
        <div class="gal-body">
          <div class="gal-viewer" tabindex="0" aria-label="PDF viewer. Page 1 is our audit; the pages after it are the original paper."></div>
          <p class="gal-note">Papers by ScientistTwo (Google Cloud AI Research). Page 1 is our audit; the pages after it are the original paper, unchanged. <a class="gal-audit" href="#">Read the audit notes ↓</a></p>
        </div>
      </div>`;
    const $ = (s) => root.querySelector(s);
    const chips = $(".gal-chips"), viewer = $(".gal-viewer"), body = $(".gal-body"), toggle = $(".gal-toggle");

    function renderChips() {
      const all = ["All", ...DOMAINS];
      chips.innerHTML = all.map((d) => {
        const n = d === "All" ? PAPERS.length : PAPERS.filter((p) => p.domain === d).length;
        return `<button type="button" class="gal-chip" data-d="${esc(d)}" aria-pressed="${d === domain}">${esc(d)} <span>${n}</span></button>`;
      }).join("");
    }

    function renderMeta() {
      const l = list(), p = l[pos];
      current = p;
      $(".gal-tag").textContent = p.domain;
      $(".gal-name").textContent = p.name;
      $(".gal-title").textContent = p.title;
      $(".gal-count").textContent = `${pos + 1} / ${l.length}`;
      $(".gal-open").href = p.file;
      $(".gal-dl").href = p.file;
      $(".gal-dl small").textContent = p.size;
      const a = $(".gal-audit");
      a.href = "#p" + p.id;
      a.hidden = !document.getElementById("p" + p.id);
      $(".gal-prev").disabled = l.length < 2;
      $(".gal-next").disabled = l.length < 2;
    }

    async function showPdf() {
      if (!open) return;
      const my = ++token, p = current;
      viewer.innerHTML = '<p class="gal-status">Loading the paper…</p>';
      viewer.scrollTop = 0;
      try {
        await loadPdfJs();
        const pdf = await window.pdfjsLib.getDocument(p.file).promise;
        if (my !== token) return;
        const first = await pdf.getPage(1);
        const vp = first.getViewport({ scale: 1 });
        viewer.innerHTML = "";
        const holder = document.createElement("div");
        holder.className = "gal-pages";
        const slots = [];
        for (let i = 1; i <= pdf.numPages; i++) {
          const d = document.createElement("div");
          d.className = "gal-page";
          d.style.aspectRatio = `${vp.width} / ${vp.height}`;
          d.dataset.n = i;
          d.innerHTML = `<span class="gal-pn">${i}</span>`;
          holder.append(d); slots.push(d);
        }
        viewer.append(holder);

        const done = new Set();
        const draw = async (slot) => {
          const n = +slot.dataset.n;
          if (done.has(n)) return; done.add(n);
          const page = n === 1 ? first : await pdf.getPage(n);
          if (my !== token) return;
          const base = page.getViewport({ scale: 1 });
          const css = slot.clientWidth || 700;
          const dpr = Math.min(Math.max(window.devicePixelRatio || 1, 1.6), 2.2);
          const scale = (css / base.width) * dpr;
          const v = page.getViewport({ scale });
          const c = document.createElement("canvas");
          c.width = Math.floor(v.width); c.height = Math.floor(v.height);
          const ctx = c.getContext("2d");
          ctx.fillStyle = "#fff"; ctx.fillRect(0, 0, c.width, c.height);
          // "print" intent renders without waiting for animation frames, so it also works in background tabs and slow phones.
          await page.render({ canvasContext: ctx, viewport: v, intent: "print" }).promise;
          if (my !== token) return;
          slot.style.aspectRatio = `${base.width} / ${base.height}`;
          slot.replaceChildren(c);
          slot.classList.add("drawn");
        };
        const check = () => {
          if (my !== token) return;
          const r = viewer.getBoundingClientRect();
          for (const s of slots) {
            if (s.classList.contains("drawn") || done.has(+s.dataset.n)) continue;
            const b = s.getBoundingClientRect();
            if (b.bottom > r.top - 400 && b.top < r.bottom + 900) draw(s);
          }
        };
        let queued = false;
        const onScroll = () => { if (queued) return; queued = true; setTimeout(() => { queued = false; check(); }, 60); };
        viewer.onscroll = onScroll;
        check();
        // First two pages always, even if layout is not measured yet.
        slots.slice(0, 2).forEach(draw);
      } catch (e) {
        if (my !== token) return;
        viewer.innerHTML = `<p class="gal-status">The preview could not load here. <a href="${esc(p.file)}" target="_blank" rel="noopener">Open the PDF ↗</a></p>`;
      }
    }

    function go(delta) {
      const l = list();
      pos = (pos + delta + l.length) % l.length;
      renderMeta(); showPdf();
    }
    chips.addEventListener("click", (e) => {
      const b = e.target.closest(".gal-chip"); if (!b) return;
      domain = b.dataset.d; pos = 0; renderChips(); renderMeta(); showPdf();
    });
    $(".gal-prev").addEventListener("click", () => go(-1));
    $(".gal-next").addEventListener("click", () => go(1));
    toggle.addEventListener("click", () => {
      open = !open;
      body.hidden = !open;
      toggle.textContent = open ? "Hide" : "Show";
      toggle.setAttribute("aria-expanded", String(open));
      if (open) showPdf(); else { token++; viewer.innerHTML = ""; }
    });
    root.addEventListener("keydown", (e) => {
      if (e.target.closest("a,button") && !e.target.closest(".gal-viewer")) return;
      if (e.key === "ArrowLeft" && e.altKey) go(-1);
      if (e.key === "ArrowRight" && e.altKey) go(1);
    });

    body.hidden = !open;
    toggle.textContent = open ? "Hide" : "Show";
    toggle.setAttribute("aria-expanded", String(open));
    renderChips(); renderMeta(); showPdf();
  }

  document.querySelectorAll("[data-gallery]").forEach(init);
})();
