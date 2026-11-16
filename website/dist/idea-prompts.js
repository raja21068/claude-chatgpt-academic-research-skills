// Prompts by level: pick a research step (6) and a level (3); each step has 3 prompts.
const $ = (id) => document.getElementById(id);
const topic = $("in-topic"), res = $("in-res");
let level = "beginner";
let stage = LEVEL_STAGES[0];
const bValues = {}; // second box is per-stage

const icon = (k) => `<svg viewBox="0 0 24 24" aria-hidden="true">${ICONS[k] || ICONS.doc}</svg>`;
const escHtml = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;");

function fill(tpl) {
  const a = topic.value.trim() || "[describe your topic or idea]";
  const b = res.value.trim() || "[" + stage.bLabel.toLowerCase() + "]";
  return tpl.replaceAll("{A}", a).replaceAll("{B}", b).replaceAll("{HONEST}", HONEST).replaceAll("{SCORE}", SCORE_TABLE);
}

function renderTabs() {
  $("stage-tabs").innerHTML = LEVEL_STAGES.map((s) =>
    `<a href="#${s.id}" class="stage-tab"${s === stage ? ' aria-current="page"' : ""}>${s.nav}</a>`).join("");
}

function renderChain() {
  const n = LEVEL_STAGES.indexOf(stage) + 1;
  $("chain-eyebrow").textContent = `Step ${n} of 6 · how the three prompts connect`;
  $("chain-title").textContent = stage.title;
  $("chain").innerHTML = stage.steps.map((s, i) => `<li>
      <span class="chain-num">${i + 1}</span>${icon(s.icon)}
      <strong>${s.title}</strong><span>${s.line}</span><em>${s.chip}</em></li>`).join("");
  $("chain-loop").textContent = stage.loop;
}

function renderInputs() {
  $("in-res-label").textContent = stage.bLabel;
  topic.placeholder = stage.aHolder;
  res.placeholder = stage.bHolder;
  res.value = bValues[stage.id] || "";
}

// Beginner mode: one prompt at a time, big copy button, prompt text hidden.
const beginnerPos = {};
function renderBeginner() {
  const cur = beginnerPos[stage.id] || 0;
  const next = LEVEL_STAGES[LEVEL_STAGES.indexOf(stage) + 1];
  $("prompt-steps").replaceChildren(...stage.steps.map((s, i) => {
    const card = document.createElement("article");
    if (i !== cur) {
      card.className = "card ip-step ip-mini " + (i < cur ? "is-done" : "is-later");
      card.innerHTML = `<span class="chain-num">${i < cur ? "✓" : i + 1}</span><strong>${s.title}</strong>
        <span class="ip-mini-note">${i < cur ? "Done" : "Comes next"}</span>
        ${i < cur ? `<button type="button" class="button secondary" data-goto="${i}">Open again</button>` : ""}`;
      return card;
    }
    const last = i === stage.steps.length - 1;
    card.className = "card ip-step ip-now";
    card.innerHTML = `
      <div class="ip-step-head"><span class="chain-num">${i + 1}</span><div><p class="eyebrow">Prompt ${i + 1} of ${stage.steps.length}</p><h3>${s.title}</h3></div></div>
      <ol class="ip-howto">
        <li><button type="button" class="button primary ip-bigcopy" data-copy="p${i}">Copy prompt ${i + 1}</button><span class="hint" role="status"></span></li>
        <li>Paste it into <a href="https://chatgpt.com/" target="_blank" rel="noopener noreferrer">ChatGPT ↗</a> or <a href="https://claude.ai/" target="_blank" rel="noopener noreferrer">Claude ↗</a>${i ? " — in the <strong>same chat</strong> as before" : ""}.${s.attachB ? ` ${s.attachB}` : ""}</li>
        <li>Wait for the answer. You should get: ${s.get.beginner.join(" · ")}.</li>
      </ol>
      <details class="ip-show"><summary>Show the prompt text</summary><textarea id="p${i}" readonly rows="12" spellcheck="false"></textarea></details>
      ${s.example ? `<p class="ip-example-line"><button type="button" class="button secondary ip-example" data-file="${s.example.file}">${s.example.label} →</button></p>` : ""}
      ${s.sample ? `<details class="ip-sample"><summary>See a short sample answer</summary>${s.sample}</details>` : ""}
      <div class="ip-next-row">${last
        ? `<strong>That's the last prompt for this step.</strong> ${next ? `<a class="button primary" href="#${next.id}">Go to ${next.nav} →</a>` : `<a class="button primary" href="./">Back to the workflow →</a>`}`
        : `<button type="button" class="button primary" data-goto="${i + 1}">I have the answer → next prompt</button>`}</div>`;
    card.querySelector("textarea").value = fill(s.prompts.beginner);
    return card;
  }));
}

function renderPrompts() {
  if (level === "beginner") return renderBeginner();
  $("prompt-steps").replaceChildren(...stage.steps.map((s, i) => {
    const card = document.createElement("article");
    card.className = "card ip-step";
    card.innerHTML = `
      <div class="ip-step-head"><span class="chain-num">${i + 1}</span><div><p class="eyebrow">Prompt ${i + 1} · ${level}</p><h3>${s.title}</h3></div></div>
      <p class="ip-attach"><strong>Attach:</strong> ${s.attach}</p>
      <div class="ip-grid">
        <div class="ip-prompt">
          <label for="p${i}">Your prompt</label>
          <textarea id="p${i}" readonly rows="14" spellcheck="false"></textarea>
          <div class="prompt-actions"><button type="button" class="button primary" data-copy="p${i}">Copy prompt ${i + 1}</button><a href="https://chatgpt.com/" target="_blank" rel="noopener noreferrer">ChatGPT ↗</a><a href="https://claude.ai/" target="_blank" rel="noopener noreferrer">Claude ↗</a><span class="hint" role="status"></span></div>
        </div>
        <div class="ip-get">
          <h4>What you get back</h4>
          <ol>${s.get[level].map((g) => `<li>${g}</li>`).join("")}</ol>
          ${s.sample ? `<details class="ip-sample"><summary>See a short example answer</summary>${s.sample}</details>` : ""}
          ${s.example ? `<button type="button" class="button secondary ip-example" data-file="${s.example.file}">${s.example.label} →</button><p class="hint">${s.example.note}${level === "beginner" ? " Your answer will be shorter and simpler." : ""}</p>` : ""}
        </div>
      </div>`;
    card.querySelector("textarea").value = fill(s.prompts[level]);
    return card;
  }));
}

function renderNext() {
  const i = LEVEL_STAGES.indexOf(stage);
  const prev = LEVEL_STAGES[i - 1], next = LEVEL_STAGES[i + 1];
  $("stage-next").innerHTML =
    (prev ? `<a class="button secondary" href="#${prev.id}">← ${prev.nav}</a>` : "<span></span>") +
    (next ? `<a class="button primary" href="#${next.id}">Next: ${next.nav} →</a>` : `<a class="button primary" href="./">Back to the workflow →</a>`);
}

function renderAll() { renderTabs(); renderChain(); renderInputs(); renderPrompts(); renderNext(); }

function fromHash(initial) {
  const found = LEVEL_STAGES.find((s) => s.id === location.hash.slice(1));
  if (found && found !== stage) { stage = found; renderAll(); if (!initial) $("chain-title").scrollIntoView({block: "center"}); }
  else if (initial) renderAll();
}

document.querySelectorAll(".level").forEach((b) => b.addEventListener("click", () => {
  level = b.dataset.level;
  document.querySelectorAll(".level").forEach((x) => x.setAttribute("aria-checked", String(x === b)));
  try { localStorage.setItem("level-prompts:level", level); } catch {}
  renderPrompts();
}));
topic.addEventListener("input", () => { try { localStorage.setItem("level-prompts:topic", topic.value); } catch {} renderPrompts(); });
res.addEventListener("input", () => { bValues[stage.id] = res.value; renderPrompts(); });
$("fill-example").addEventListener("click", () => { topic.value = stage.exA; res.value = bValues[stage.id] = stage.exB; renderPrompts(); });
window.addEventListener("hashchange", () => fromHash(false));

$("prompt-steps").addEventListener("click", async (e) => {
  const copy = e.target.closest("[data-copy]");
  if (copy) {
    const field = $(copy.dataset.copy), msg = copy.parentElement.querySelector("[role=status]");
    try { await navigator.clipboard.writeText(field.value); msg.textContent = "Copied. Paste it into your chat."; }
    catch { field.focus(); field.select(); msg.textContent = "Selected. Press Ctrl+C to copy."; }
    return;
  }
  const go = e.target.closest("[data-goto]");
  if (go) {
    beginnerPos[stage.id] = +go.dataset.goto;
    renderPrompts();
    $("prompt-steps").querySelector(".ip-now")?.scrollIntoView({block: "start", behavior: "smooth"});
    return;
  }
  const ex = e.target.closest(".ip-example");
  if (ex) openExample(ex.dataset.file, ex.textContent.trim().replace(/\s*→$/, ""));
});

// Tiny Markdown renderer for example answers (headings, tables, lists, bold, italics, links).
function inline(s) {
  return escHtml(s).replace(/>/g, "&gt;")
    .replace(/\[([^\]]+)\]\((https?:[^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>')
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/(^|[\s(])\*([^*]+)\*/g, "$1<em>$2</em>");
}
function markdown(md) {
  const lines = md.split(/\r?\n/), out = [];
  for (let i = 0; i < lines.length; i++) {
    const l = lines[i];
    if (!l.trim()) continue;
    if (/^-{3,}\s*$/.test(l)) { out.push("<hr>"); continue; }
    if (l.trim().startsWith("\\[")) {
      const block = [];
      while (i < lines.length) { block.push(lines[i]); if (lines[i].includes("\\]")) break; i++; }
      out.push(`<div class="md-math">${escHtml(block.join("\n")).replace(/>/g, "&gt;")}</div>`);
      continue;
    }
    if (l.startsWith("> ")) { out.push(`<blockquote>${inline(l.slice(2))}</blockquote>`); continue; }
    const h = l.match(/^(#{1,4})\s+(.*)/);
    if (h) { const n = Math.min(h[1].length + 1, 5); out.push(`<h${n}>${inline(h[2])}</h${n}>`); continue; }
    if (l.startsWith("|")) {
      const rows = [];
      while (i < lines.length && lines[i].startsWith("|")) rows.push(lines[i++]);
      i--;
      const cells = (r) => r.replace(/^\||\|$/g, "").split("|").map((c) => c.trim());
      const body = rows.slice(2).map((r) => "<tr>" + cells(r).map((c) => `<td>${inline(c)}</td>`).join("") + "</tr>").join("");
      out.push(`<div class="md-table"><table><thead><tr>${cells(rows[0]).map((c) => `<th>${inline(c)}</th>`).join("")}</tr></thead><tbody>${body}</tbody></table></div>`);
      continue;
    }
    const li = l.match(/^\s*(-|\d+\.)\s+(.*)/);
    if (li) {
      const tag = li[1] === "-" ? "ul" : "ol", items = [];
      while (i < lines.length && /^\s*(-|\d+\.)\s+/.test(lines[i])) items.push(lines[i++].replace(/^\s*(-|\d+\.)\s+/, ""));
      i--;
      out.push(`<${tag}>${items.map((x) => `<li>${inline(x)}</li>`).join("")}</${tag}>`);
      continue;
    }
    out.push(`<p>${inline(l)}</p>`);
  }
  return out.join("");
}
function showTab(visual) {
  $("tab-visual").setAttribute("aria-selected", String(visual));
  $("tab-full").setAttribute("aria-selected", String(!visual));
  $("example-visual").hidden = !visual;
  $("example-body").hidden = visual;
}
$("tab-visual").addEventListener("click", () => showTab(true));
$("tab-full").addEventListener("click", () => showTab(false));

function showAnswer(text, title, file) {
  $("example-dialog-title").textContent = title;
  const raw = $("example-raw");
  raw.hidden = !file;
  if (file) raw.href = file;
  $("example-visual").innerHTML = window.visualizeAnswer(text);
  $("example-body").innerHTML = markdown(text);
  if (text.includes("\\(") || text.includes("\\[")) renderMath($("example-body"));
  showTab(true);
  if (!$("example-dialog").open) $("example-dialog").showModal();
}

async function openExample(file, title) {
  $("example-visual").innerHTML = "<p>Loading…</p>";
  $("example-body").innerHTML = "";
  showTab(true);
  $("example-dialog-title").textContent = title;
  $("example-dialog").showModal();
  try {
    const r = await fetch(file);
    if (!r.ok) throw new Error();
    showAnswer(await r.text(), title, file);
  } catch {
    $("example-visual").innerHTML = `<p>Could not load the example here. <a href="${file}" target="_blank">Open it directly</a>.</p>`;
  }
}

$("paste-go").addEventListener("click", () => {
  const text = $("paste-answer").value.trim();
  if (!text) { $("paste-msg").textContent = "Paste an answer first."; return; }
  $("paste-msg").textContent = addRound(text);
  showAnswer(text, "Your answer", null);
});

// ── Score over rounds (saved in this browser only) ──
const ROUNDS_KEY = "level-prompts:rounds";
const loadRounds = () => { try { return JSON.parse(localStorage.getItem(ROUNDS_KEY) || "[]"); } catch { return []; } };
const saveRounds = (r) => { try { localStorage.setItem(ROUNDS_KEY, JSON.stringify(r)); } catch {} };
const hashText = (s) => { let h = 0; for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) | 0; return h; };

function addRound(text) {
  if (/Sample answer, made up/i.test(text)) return "Sample answers are not added to your rounds.";
  const s = window.answerScore(text);
  if (!s) return "No score found in this answer, so it was not added to your rounds.";
  const rounds = loadRounds(), h = hashText(text);
  if (rounds.some((r) => r.h === h)) return "This answer is already in your rounds.";
  rounds.push({h, value: s.value, max: s.max, pct: Math.round((s.value / s.max) * 1000) / 10, step: stage.nav.replace(/^\d+\s·\s/, ""), date: new Date().toISOString().slice(0, 10)});
  saveRounds(rounds);
  renderRounds();
  return `Added as round ${rounds.length}: ${s.value}/${s.max}.`;
}

function renderRounds() {
  const rounds = loadRounds(), box = $("rounds-chart");
  $("rounds-actions").hidden = !rounds.length;
  if (!rounds.length) { box.innerHTML = `<p class="rounds-empty">No rounds yet. Paste your first scored answer above.</p>`; return; }
  const W = 640, H = 230, L = 44, R = 20, T = 20, B = 40;
  const n = rounds.length, x = (i) => L + (n === 1 ? (W - L - R) / 2 : (i * (W - L - R)) / (n - 1)), y = (p) => T + (1 - p / 100) * (H - T - B);
  const grid = [0, 25, 50, 75, 100].map((g) => `<line x1="${L}" x2="${W - R}" y1="${y(g)}" y2="${y(g)}" class="${g === 75 ? "rc-target" : "rc-grid"}"/><text x="${L - 8}" y="${y(g) + 4}" class="rc-axis" text-anchor="end">${g}</text>`).join("");
  const path = rounds.map((r, i) => `${i ? "L" : "M"}${x(i)},${y(r.pct)}`).join(" ");
  const best = rounds.reduce((a, b, i) => (b.pct > rounds[a].pct ? i : a), 0);
  const labelled = new Set([0, n - 1, best]);
  const pts = rounds.map((r, i) => `<g class="rc-pt" tabindex="0"><title>Round ${i + 1} (${r.step}, ${r.date}): ${r.value}/${r.max}</title>
      <circle cx="${x(i)}" cy="${y(r.pct)}" r="14" class="rc-hit"/><circle cx="${x(i)}" cy="${y(r.pct)}" r="5" class="rc-dot"/>
      ${labelled.has(i) ? `<text x="${x(i)}" y="${y(r.pct) - 12}" text-anchor="middle" class="rc-val">${r.value}${r.max !== 100 ? "/" + r.max : ""}</text>` : ""}
      <text x="${x(i)}" y="${H - B + 18}" text-anchor="middle" class="rc-axis">R${i + 1}</text></g>`).join("");
  const first = rounds[0], last = rounds[n - 1], diff = Math.round((last.pct - first.pct) * 10) / 10;
  box.innerHTML = `
    <p class="rounds-summary">${n === 1 ? `Round 1: <strong>${first.value}/${first.max}</strong>. Paste the next round's answer to see the trend.` : `Round 1 → round ${n}: <strong>${diff >= 0 ? "+" : ""}${diff} points</strong> (out of 100). ${last.pct >= 75 ? "Above the 75 line — strong enough to move on." : "Below the 75 line — run prompts 2 and 3 again."}`}</p>
    <svg viewBox="0 0 ${W} ${H}" class="rc" role="img" aria-label="Score over ${n} rounds, from ${first.pct} to ${last.pct} out of 100">
      ${grid}<text x="${L + 6}" y="${y(75) - 6}" text-anchor="start" class="rc-target-label">75 = strong</text>
      <path d="${path}" class="rc-line"/>${pts}</svg>
    <details class="rounds-table"><summary>See as a table</summary><table><thead><tr><th>Round</th><th>Step</th><th>Date</th><th>Score</th><th>Out of 100</th></tr></thead><tbody>
      ${rounds.map((r, i) => `<tr><td>${i + 1}</td><td>${r.step}</td><td>${r.date}</td><td>${r.value}/${r.max}</td><td>${r.pct}</td></tr>`).join("")}</tbody></table></details>`;
}
$("rounds-undo").addEventListener("click", () => { const r = loadRounds(); r.pop(); saveRounds(r); renderRounds(); });
$("rounds-clear").addEventListener("click", () => { if (confirm("Remove all saved rounds from this browser?")) { saveRounds([]); renderRounds(); } });
renderRounds();

// copy button inside the visual summary's follow-up box
$("example-visual").addEventListener("click", async (e) => {
  const b = e.target.closest("[data-copy-followup]"); if (!b) return;
  const field = b.parentElement.querySelector("textarea"), msg = b.parentElement.querySelector("[role=status]");
  try { await navigator.clipboard.writeText(field.value); msg.textContent = "Copied."; }
  catch { field.focus(); field.select(); msg.textContent = "Selected. Press Ctrl+C."; }
});
$("paste-sample").addEventListener("click", async () => {
  try {
    const r = await fetch("demo/sample-review-revision-plan.md");
    $("paste-answer").value = await r.text();
    $("paste-msg").textContent = "Sample pasted. Now press “Show it visually”.";
  } catch { $("paste-msg").textContent = "Could not load the sample."; }
});
// Equations: load KaTeX on first need; if offline, the raw LaTeX stays readable.
let katexReady;
function loadKatex() {
  if (katexReady) return katexReady;
  const base = "https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/";
  const css = document.createElement("link");
  css.rel = "stylesheet"; css.href = base + "katex.min.css";
  document.head.append(css);
  const script = (src) => new Promise((ok, fail) => { const s = document.createElement("script"); s.src = src; s.onload = ok; s.onerror = fail; document.head.append(s); });
  katexReady = script(base + "katex.min.js").then(() => script(base + "contrib/auto-render.min.js"));
  return katexReady;
}
async function renderMath(el) {
  try {
    await loadKatex();
    window.renderMathInElement(el, {delimiters: [{left: "\\[", right: "\\]", display: true}, {left: "\\(", right: "\\)", display: false}], throwOnError: false});
  } catch { /* offline: keep raw LaTeX */ }
}
$("example-close").addEventListener("click", () => $("example-dialog").close());
$("example-dialog").addEventListener("click", (e) => { if (e.target === e.currentTarget) e.currentTarget.close(); });

try {
  topic.value = localStorage.getItem("level-prompts:topic") || "";
  const saved = localStorage.getItem("level-prompts:level");
  if (saved && ["beginner", "researcher", "expert"].includes(saved)) {
    level = saved;
    document.querySelectorAll(".level").forEach((x) => x.setAttribute("aria-checked", String(x.dataset.level === saved)));
  }
} catch {}
fromHash(true);
