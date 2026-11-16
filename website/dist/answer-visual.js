// Turns a Markdown answer (review / rebuild / revision plan) into a visual summary.
// Works on any answer that uses the table shapes our prompts ask for. Runs fully in the browser.
(function () {
  const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  const clean = (s) => s.replace(/\*\*/g, "").replace(/\\\(|\\\)/g, "").replace(/\[([^\]]+)\]\([^)]+\)/g, "$1").trim();

  // "**12**" -> {v:12}, "10/15" -> {v:10,max:15}, "8.5–9.0" -> {v:8.75}, "~6.0" -> {v:6}, "8.0+" -> {v:8}
  function num(cell) {
    const c = clean(cell).replace(/[~≈]/g, "");
    let m = c.match(/^(\d+(?:\.\d+)?)\s*\/\s*(\d+(?:\.\d+)?)/);
    if (m) return {v: +m[1], max: +m[2]};
    m = c.match(/^(\d+(?:\.\d+)?)\s*[–-]\s*(\d+(?:\.\d+)?)/);
    if (m) return {v: (+m[1] + +m[2]) / 2, range: c.match(/^[\d.\s–-]+/)[0].trim()};
    m = c.match(/^(\d+(?:\.\d+)?)/);
    return m ? {v: +m[1]} : null;
  }

  function tables(md) {
    const lines = md.split(/\r?\n/), out = [];
    for (let i = 0; i < lines.length; i++) {
      if (!lines[i].trim().startsWith("|")) continue;
      const rows = [];
      while (i < lines.length && lines[i].trim().startsWith("|")) rows.push(lines[i++].trim());
      if (rows.length < 3) continue;
      const cells = (r) => r.replace(/^\||\|$/g, "").split("|").map((c) => c.trim());
      out.push({head: cells(rows[0]).map(clean), rows: rows.slice(2).map(cells)});
    }
    return out;
  }

  const col = (t, re) => t.head.findIndex((h) => re.test(h));
  const isTotal = (row) => /total|overall/i.test(clean(row[0]));

  // ── pieces ──
  function hero(md, scoreT, ba) {
    const s = scoreOf(md, scoreT, ba);
    if (!s) return "";
    const {value, max, other, otherText} = s;
    const fin = [...md.matchAll(/\*\*([^*\n]{0,160}?(revis|accept|reject|proceed|fund|ready|worth)[^*\n]{0,160}?)\*\*([^\n]{0,140})/gi)].pop();
    const verdict = fin ? clean(fin[1] + (fin[3] || "")).replace(/\s*[|#].*$/, "") : "";
    const pct = Math.max(0, Math.min(100, (value / max) * 100));
    const band = pct >= 75 ? ["Strong", "good"] : pct >= 60 ? ["Promising, needs work", "warn"] : ["Needs major revision", "bad"];
    return `<section class="av-hero">
      <div class="av-big"><b>${value}</b><span>/ ${max}</span>${other !== null ? `<small>${esc(otherText)}</small>` : ""}</div>
      <div class="av-hero-side">
        <span class="av-chip av-${band[1]}">${band[0]}</span>
        <div class="av-meter" role="img" aria-label="Score ${value} of ${max}"><i style="width:${pct}%"></i><s style="left:75%" title="75% — a common bar for 'strong'"></s></div>
        ${verdict ? `<p>${esc(verdict)}</p>` : ""}
      </div></section>`;
  }

  // The answer's main score: for a review = the current score; for a rebuild = the new score.
  function scoreOf(md, scoreT, ba) {
    let value = null, max = 100, other = null, otherText = "";
    if (ba) {
      const total = ba.t.rows.find(isTotal);
      const x = total && num(total[ba.a]), y = total && num(total[ba.b]);
      if (x && y) {
        max = y.max || x.max || (Math.max(x.v, y.v) <= 10 ? 10 : 100);
        // "Rebuilt/Revised" = the new version is the score now; "Potential/After" = a forecast.
        if (/rebuilt|revised/i.test(ba.t.head[ba.b])) { value = y.v; other = x.v; otherText = `up from ${x.v}`; }
        else { value = x.v; other = y.range || y.v; otherText = `→ ${other} possible after fixes`; }
      }
    }
    if (value === null && scoreT) {
      const total = scoreT.t.rows.find(isTotal);
      if (total) { const n = num(total[scoreT.score]); if (n) { value = n.v; max = n.max || (n.v <= 10 ? 10 : 100); } }
    }
    if (value === null) {
      const m = clean(md).match(/(\d+(?:\.\d+)?)\s*\/\s*(100|10)\b/);
      if (m) { value = +m[1]; max = +m[2]; }
    }
    return value === null ? null : {value, max, other, otherText};
  }

  // ── Answer checker: the "How to tell if the answer is good" list, done automatically ──
  function checks(md, scoreT) {
    const text = clean(md);
    const links = (md.match(/https?:\/\/[^\s)]+/g) || []).length;
    const dois = (md.match(/\b10\.\d{4,}\/\S+/g) || []).length;
    const paperMentions = (text.match(/\b(et al\.|Paper [A-Z]\b|\(\d{4}\)|, \d{4}\b|arXiv|Proceedings|Journal)/g) || []).length;
    const placeholders = /\bPaper [A-Z]\b/.test(text);
    const honest = /could not|couldn't|unable to|not (been )?verif|unverif|needs? checking|did not (open|run|see|search)|cannot be guaranteed|no .{0,20}guarantee|not checked|assumption/i.test(text);
    const nextAction = /decisive experiment|run .{0,40}first|first thing|next step|strongest advice|start with|do this first|top (3 )?(revision )?priorit/i.test(text);
    const over = [...new Set((text.match(/\b(proves?|guarantees?|definitely|always works|undoubtedly|breakthrough|first ever|state-of-the-art by far)\b/gi) || []).map((w) => w.toLowerCase()))];
    const numsWithSource = /\.(csv|json|log|ya?ml)\b|run ?id|runs\//i.test(text);
    const out = [];
    // 1. Links for papers
    if (paperMentions === 0) out.push({s: "na", t: "Papers have links", d: "No papers mentioned, so nothing to check."});
    else if (links + dois > 0) out.push({s: "ok", t: "Papers have links", d: `${links + dois} link${links + dois > 1 ? "s" : ""}/DOI${links + dois > 1 ? "s" : ""} found. Open 2–3 to make sure they are real and say what the answer claims.`});
    else out.push({s: "bad", t: "Papers have links", d: placeholders ? "Only placeholder names (Paper A, B…). In a real answer every paper needs a link or DOI." : `${paperMentions} paper mention${paperMentions > 1 ? "s" : ""} but no links or DOIs. Unlinked papers may be made up.`, fix: "Give a working link or DOI for every paper you mentioned. Remove any paper you cannot link to."});
    // 2. Scores have reasons
    if (!scoreT) out.push({s: "na", t: "Every score has a reason", d: "No scoring table in this answer."});
    else {
      const rows = scoreT.t.rows.filter((r) => !isTotal(r));
      const why = scoreT.why;
      const empty = why < 0 ? rows.length : rows.filter((r) => clean(r[why] || "").length < 8).length;
      out.push(empty === 0 ? {s: "ok", t: "Every score has a reason", d: `All ${rows.length} criteria explain their score.`}
        : {s: "bad", t: "Every score has a reason", d: `${empty} of ${rows.length} scores have no reason.`, fix: "Add a one-sentence reason, with evidence, for every score in the table."});
    }
    // 3. Honest about limits
    out.push(honest ? {s: "ok", t: "Says what it could not check", d: "The answer states limits or unverified points."}
      : {s: "bad", t: "Says what it could not check", d: "No statement about what was not verified, searched or run.", fix: "List what you could not verify, search, open or run, and mark those claims as unverified."});
    // 4. Overclaiming words
    out.push(over.length ? {s: "warn", t: "No overclaiming words", d: `Watch these words: ${over.join(", ")}. Check each is really supported.`, fix: `Replace strong words (${over.join(", ")}) with wording the evidence supports.`}
      : {s: "ok", t: "No overclaiming words", d: "No “proves / guarantees / definitely”-type words found."});
    // 5. Numbers traced to files (only matters for results-type answers)
    if (/results?|metrics?|MAE|accuracy|table \d/i.test(text) && /\d+(\.\d+)?\s*%/.test(text)) {
      out.push(numsWithSource ? {s: "ok", t: "Numbers point to result files", d: "Result files or run IDs are mentioned."}
        : {s: "warn", t: "Numbers point to result files", d: "Percentages appear but no result file or run ID is named.", fix: "For each number, name the result file and run ID it came from."});
    }
    // 6. Clear next action
    out.push(nextAction ? {s: "ok", t: "Ends with a clear next action", d: "It tells you what to do first."}
      : {s: "bad", t: "Ends with a clear next action", d: "No single first step is given.", fix: "End with the one experiment or change I should do first, and why."});
    return out;
  }

  function checkerCard(list) {
    const counted = list.filter((c) => c.s !== "na");
    const passed = counted.filter((c) => c.s === "ok").length;
    const fixes = list.filter((c) => c.fix);
    const icon = {ok: "✓", bad: "✗", warn: "!", na: "–"};
    const label = {ok: "Pass", bad: "Missing", warn: "Check", na: "N/A"};
    const followUp = fixes.length ? "Please improve your last answer:\n" + fixes.map((c, i) => `${i + 1}. ${c.fix}`).join("\n") + "\nKeep everything else the same. Do not invent papers or results." : "";
    return `<section class="av-card av-check"><h3>Answer quality check <span class="av-score-pill">${passed} / ${counted.length} passed</span></h3>
      <p class="av-sub">Automatic first check. It looks for signs of a good answer — it cannot tell if a paper or number is real, so still open a few links.</p>
      <ul class="av-checks">${list.map((c) => `<li class="ck-${c.s}"><span class="ck-icon" aria-hidden="true">${icon[c.s]}</span><div><strong>${esc(c.t)}</strong> <span class="ck-label">${label[c.s]}</span><p>${esc(c.d)}</p></div></li>`).join("")}</ul>
      ${followUp ? `<div class="av-followup"><label for="av-followup-text">Ask the AI to fix this — paste into the same chat:</label><textarea id="av-followup-text" readonly rows="${fixes.length + 3}">${esc(followUp)}</textarea><button type="button" class="button primary" data-copy-followup>Copy follow-up prompt</button><span class="hint" role="status"></span></div>` : `<p class="av-allgood">Looks good. Still open 2–3 links and numbers yourself.</p>`}
    </section>`;
  }

  function criterionBars(st) {
    const rows = st.t.rows.filter((r) => !isTotal(r));
    const items = rows.map((r) => {
      const s = num(r[st.score]); if (!s) return null;
      const w = st.weight >= 0 ? num(r[st.weight]) : null;
      const max = s.max || (w && w.v) || null;
      return max ? {name: clean(r[0]), v: s.v, max, why: st.why >= 0 ? clean(r[st.why] || "") : ""} : null;
    }).filter(Boolean);
    if (items.length < 2) return "";
    const weakest = items.reduce((a, b) => (a.v / a.max <= b.v / b.max ? a : b));
    return `<section class="av-card"><h3>Score by criterion</h3>
      <p class="av-sub">Bar = points earned out of that criterion's weight. Weakest: <strong>${esc(weakest.name)}</strong>.</p>
      <div class="av-bars">${items.map((it) => {
        const pct = (it.v / it.max) * 100;
        return `<div class="av-row" tabindex="0" title="${esc(it.name)}: ${it.v} of ${it.max}${it.why ? " — " + esc(it.why) : ""}">
          <span class="av-label">${esc(it.name)}</span>
          <span class="av-track"><i class="${pct < 50 ? "low" : ""}" style="width:${pct}%"></i></span>
          <span class="av-val">${it.v}<small>/${it.max}</small></span></div>`;
      }).join("")}</div></section>`;
  }

  function beforeAfter(t, a, b, weights) {
    const items = t.rows.map((r) => {
      const x = num(r[a]), y = num(r[b]);
      return x && y ? {name: clean(r[0]), x, y, total: isTotal(r)} : null;
    }).filter(Boolean);
    if (items.length < 2) return "";
    const key = (s) => s.toLowerCase().replace(/[^a-z ]/g, "").split(" ").slice(0, 2).join(" ");
    const allSmall = items.filter((i) => !i.total).every((i) => Math.max(i.x.v, i.y.v) <= 10);
    const scaleOf = (i) => i.x.max || i.y.max || weights[key(i.name)] || weights[key(i.name).split(" ")[0]] || (allSmall ? 10 : 100);
    const rows = items.filter((i) => !i.total);
    const tot = items.find((i) => i.total);
    return `<section class="av-card"><h3>Before → after the fixes</h3>
      <p class="av-legend"><span><i class="before"></i>${esc(t.head[a])}</span><span><i class="after"></i>${esc(t.head[b])}</span>${tot ? `<strong class="av-total">Total: ${tot.x.v} → ${tot.y.range || tot.y.v}</strong>` : ""}</p>
      <div class="av-bars">${rows.map((i) => {
        const s = scaleOf(i), up = i.y.v - i.x.v;
        return `<div class="av-row av-pair" tabindex="0" title="${esc(i.name)}: ${i.x.v} → ${i.y.range || i.y.v} (of ${s})">
          <span class="av-label">${esc(i.name)}</span>
          <span class="av-track2"><i class="before" style="width:${(i.x.v / s) * 100}%"></i><i class="after" style="width:${(i.y.v / s) * 100}%"></i></span>
          <span class="av-val">${up > 0 ? "+" : ""}${+up.toFixed(2)}</span></div>`;
      }).join("")}</div></section>`;
  }

  function priorityMap(t, imp) {
    const level = (s) => /critical|fatal|very high/i.test(s) ? "bad" : /high/i.test(s) ? "warn" : /medium|moderate/i.test(s) ? "mid" : "low";
    const order = {bad: 0, warn: 1, mid: 2, low: 3};
    const items = t.rows.map((r) => ({what: clean(r[0]), fix: clean(r[1] === r[imp] ? "" : r[1] || ""), imp: clean(r[imp]), lv: level(clean(r[imp]))}))
      .sort((a, b) => order[a.lv] - order[b.lv]);
    const count = (lv) => items.filter((i) => i.lv === lv).length;
    return `<section class="av-card"><h3>${esc(t.head[imp])} — what to fix first</h3>
      <p class="av-sub">${count("bad")} critical · ${count("warn")} high · ${count("mid") + count("low")} other</p>
      <ol class="av-fixes">${items.map((i) => `<li class="av-${i.lv}">
        <span class="av-chip av-${i.lv}">${esc(i.imp)}</span>
        <div><strong>${esc(i.what)}</strong>${i.fix ? `<p>→ ${esc(i.fix)}</p>` : ""}</div></li>`).join("")}</ol></section>`;
  }

  function sayPairs(md) {
    const re = /Do not say:?\s*\n+\s*>\s*(.+)\n+\s*Say(?: instead| something like)?:?\s*\n+\s*>\s*(.+)/gi;
    const pairs = []; let m;
    while ((m = re.exec(md))) pairs.push([clean(m[1]), clean(m[2])]);
    if (!pairs.length) return "";
    return `<section class="av-card"><h3>Claim rewrites</h3>${pairs.map(([a, b]) => `
      <div class="av-say"><p class="no"><span>✗ Don't say</span>${esc(a)}</p><p class="yes"><span>✓ Say</span>${esc(b)}</p></div>`).join("")}</section>`;
  }

  function outline(md) {
    const hs = [...md.matchAll(/^#{1,2}\s+(.+)$/gm)].map((m) => clean(m[1])).slice(1, 16);
    if (hs.length < 3) return "";
    return `<section class="av-card"><h3>What the answer covers</h3><ol class="av-outline">${hs.map((h) => `<li>${esc(h.replace(/^\d+\.\s*/, ""))}</li>`).join("")}</ol></section>`;
  }

  // criterion name -> weight, from the scoring table, so other tables can be drawn on the right scale
  function weightMap(st) {
    const map = {};
    if (!st || st.weight < 0) return map;
    for (const r of st.t.rows) {
      const w = num(r[st.weight]); if (!w || isTotal(r)) continue;
      const k = clean(r[0]).toLowerCase().replace(/[^a-z ]/g, "").split(" ");
      map[k.slice(0, 2).join(" ")] = w.v; map[k[0]] = map[k[0]] || w.v;
    }
    return map;
  }

  function analyze(md) {
    const ts = tables(md);
    let scoreT = null, ba = null, pm = null;
    for (const t of ts) {
      const score = col(t, /^score$/i), weight = col(t, /weight/i), why = col(t, /rationale|reason|limits/i);
      if (!scoreT && score >= 0) scoreT = {t, score, weight, why};
      const a = col(t, /^(current|original|before)/i), b = col(t, /potential|after|rebuilt|revised/i);
      if (!ba && a >= 0 && b >= 0 && a !== b) ba = {t, a, b};
      const imp = col(t, /importance|severity|priority/i);
      if (!pm && imp >= 0) pm = {t, imp};
    }
    const realScoreT = scoreT;
    // A "current vs rebuilt" table with "x/15" cells can also serve as the score table.
    if (!scoreT && ba) scoreT = {t: ba.t, score: ba.b, weight: -1, why: col(ba.t, /limits|rationale/i)};
    return {scoreT, realScoreT, ba, pm};
  }

  // Main score of an answer, for the score-over-rounds chart.
  window.answerScore = function (md) {
    const {scoreT, ba} = analyze(md);
    return scoreOf(md, scoreT, ba);
  };

  window.visualizeAnswer = function (md, opts) {
    opts = opts || {};
    const {scoreT, realScoreT, ba, pm} = analyze(md);
    const parts = [
      hero(md, scoreT, ba),
      opts.compact ? "" : checkerCard(checks(md, realScoreT)),
      scoreT && !(ba && scoreT.t === ba.t) ? criterionBars(scoreT) : "",
      ba && !opts.compact ? beforeAfter(ba.t, ba.a, ba.b, weightMap(scoreT)) : "",
      pm ? priorityMap(pm.t, pm.imp) : "",
      sayPairs(md),
      opts.compact ? "" : outline(md)
    ].filter(Boolean);
    const note = !scoreT && !ba && !pm ? `<p class="av-empty">No score or fix tables found, so only the quality check is shown. The full picture works best with answers from the Researcher or Expert prompts, which ask for tables.</p>` : "";
    return `<div class="av">${parts.join("")}${note}</div>`;
  };
})();
