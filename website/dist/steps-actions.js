// Home page: "Copy" buttons on each step card copy a ready prompt (beginner by default,
// or the level and topic chosen on the Prompts page). Download links are plain links.
(function () {
  function level() { try { const v = localStorage.getItem("level-prompts:level"); return ["beginner", "researcher", "expert"].includes(v) ? v : "beginner"; } catch { return "beginner"; } }
  function topic() { try { return (localStorage.getItem("level-prompts:topic") || "").trim(); } catch { return ""; } }

  function promptText(stageId, i) {
    const stage = LEVEL_STAGES.find((s) => s.id === stageId);
    if (!stage) return "";
    const tpl = stage.steps[i].prompts[level()];
    const a = topic() || "[describe your topic or idea]";
    const b = "[" + stage.bLabel.toLowerCase() + "]";
    return tpl.replaceAll("{A}", a).replaceAll("{B}", b).replaceAll("{HONEST}", HONEST).replaceAll("{SCORE}", SCORE_TABLE);
  }

  async function copy(text) {
    try { await navigator.clipboard.writeText(text); return true; }
    catch {
      const t = document.createElement("textarea");
      t.value = text; t.setAttribute("readonly", ""); t.style.cssText = "position:fixed;left:-9999px;top:0";
      document.body.append(t); t.select();
      let ok = false; try { ok = document.execCommand("copy"); } catch {}
      t.remove(); return ok;
    }
  }

  document.addEventListener("click", async (e) => {
    const b = e.target.closest(".sm-copy");
    if (!b || typeof LEVEL_STAGES === "undefined") return;
    const label = b.querySelector("b");
    const ok = await copy(promptText(b.dataset.stage, +b.dataset.i));
    label.textContent = ok ? "Copied ✓" : "Press Ctrl+C";
    b.classList.toggle("is-done", ok);
    setTimeout(() => { label.textContent = "Copy"; b.classList.remove("is-done"); }, 1800);
  });

  // exposed for testing and for other pages
  window.stepPromptText = promptText;
})();
