const byId = (id) => document.getElementById(id);
const lesson = byId("lesson");
const navigation = byId("stage-nav");
const task = byId("task");
const firstField = byId("field-one");
const secondField = byId("field-two");
const linksField = byId("links");
const promptOutput = byId("prompt-output");
const status = byId("status");
const progressKey = "student-research-workflow:completed-v1";
const drafts = new Map();
let activeStage;
let completed = new Set();

try {
  const stored = JSON.parse(localStorage.getItem(progressKey) || "[]");
  if (Array.isArray(stored)) {
    completed = new Set(stored.filter((id) => stages.some((stage) => stage.id === id)));
  }
} catch {
  document.querySelector(".local-note").textContent = "Progress is available while this page is open.";
}

function renderProgress() {
  byId("progress").value = completed.size;
  byId("progress-text").textContent = completed.size + " / " + stages.length;
  navigation.innerHTML = stages.map((stage, index) => {
    const done = completed.has(stage.id);
    const current = stage === activeStage ? ' aria-current="step"' : "";
    const completeLabel = done ? ' aria-label="' + stage.nav + ', complete"' : "";
    return '<a class="stage-link" href="#' + stage.id + '"' + current + completeLabel + '><span class="stage-index" aria-hidden="true">' + (done ? '✓' : index + 1) + '</span>' + stage.nav + '</a>';
  }).join("");
  document.querySelectorAll(".flow-step").forEach((step) => {
    const id = step.dataset.stage;
    step.classList.toggle("is-current", activeStage?.id === id);
    step.classList.toggle("is-done", completed.has(id));
  });
}

function updateCompletion() {
  const button = byId("complete");
  const isComplete = completed.has(activeStage.id);
  button.textContent = isComplete ? "✓ Complete · undo" : "Mark stage complete";
  button.setAttribute("aria-pressed", String(isComplete));
}

function renderLesson(stage) {
  const index = stages.indexOf(stage);
  const next = stages[index + 1];
  const back = stages[index - 1];
  const skillLinks = stage.links.map((link) =>
    '<a href="' + link.url + '"' + (!link.url.startsWith('https://') ? '' : ' target="_blank" rel="noopener noreferrer"') + '>' + link.label + ' ↗</a>'
  ).join("");
  lesson.innerHTML = `
    <p class="eyebrow">Stage ${index + 1} of ${stages.length}</p>
    <h2 id="lesson-title">${stage.title}</h2>
    <p class="intro">${stage.intro}</p>
    <p class="lesson-get"><strong>You'll get:</strong> ${stage.output}</p>
    <div class="skill"><strong>${stage.skill}</strong>${skillLinks}</div>
    <p class="level-link"><a class="button primary" href="idea-prompts.html#${stage.id}">Get ready prompts for this step →</a></p>
    <div class="lesson-columns">
      <div><h3>What you need</h3><ul>${stage.inputs.map((item) => "<li>" + item + "</li>").join("")}</ul></div>
      <div><h3>What to do</h3><ol>${stage.steps.map((item) => "<li>" + item + "</li>").join("")}</ol></div>
    </div>
    ${stage.id === "draft" ? `
      <details class="draft-example">
        <summary>See an example of an empty results section</summary>
        <table>
          <caption>Table 1. Forecast accuracy on the held-out period (pending)</caption>
          <thead><tr><th scope="col">Model</th><th scope="col">MAE (visits)</th></tr></thead>
          <tbody><tr><th scope="row">Same-weekday baseline</th><td></td></tr><tr><th scope="row">Lag-based model</th><td></td></tr></tbody>
        </table>
        <figure><div class="empty-figure">Plot area reserved</div><figcaption>Figure 1. Daily forecast error over time (pending).</figcaption></figure>
      </details>` : ""}
    <div class="handoff"><strong>Save the ${stage.output.charAt(0).toLowerCase() + stage.output.slice(1)}</strong><p>${stage.check}</p></div>
    <div class="lesson-actions">
      <button id="complete" class="button secondary" type="button"></button>
      <div class="stage-actions">
        ${back ? '<a href="#' + back.id + '" class="button secondary">← Previous</a>' : ""}
        <a href="idea-prompts.html#${stage.id}" class="button secondary">Get prompts →</a>
        ${next ? '<a href="#' + next.id + '" class="button primary">Next stage →</a>' : ""}
      </div>
    </div>`;
  byId("complete").addEventListener("click", () => {
    if (completed.has(stage.id)) completed.delete(stage.id);
    else completed.add(stage.id);
    try {
      localStorage.setItem(progressKey, JSON.stringify([...completed]));
    } catch {
      document.querySelector(".local-note").textContent = "Progress is available while this page is open.";
    }
    renderProgress();
    updateCompletion();
  });
  updateCompletion();
}

function parseLinks(text) {
  const valid = new Set();
  let invalid = 0;
  for (const line of text.split(/\n/).map((part) => part.trim()).filter(Boolean)) {
    try {
      const url = new URL(line);
      if (!["http:", "https:"].includes(url.protocol) || url.username || url.password) {
        invalid++;
        continue;
      }
      valid.add(url.href);
    } catch {
      invalid++;
    }
  }
  return {valid: [...valid], invalid};
}

function buildPrompt() {
  const stage = activeStage;
  const {valid, invalid} = parseLinks(linksField.value);
  drafts.set(stage.id, {task: task.value, fields: [firstField.value, secondField.value], links: linksField.value});
  const context = stage.fields.map((label, index) => {
    const field = index === 0 ? firstField : secondField;
    return label + ": " + (field.value.trim() || "[add your " + label.toLowerCase() + "]");
  }).join("\n");
  const parts = [
    "Goal: " + stage.title + ".",
    "Skill: Use the " + stage.skill + " instructions if provided. Ask for critical missing materials before making claims that depend on them.",
    "Task: " + stage.tasks[Number(task.value)].name + ". " + stage.tasks[Number(task.value)].body,
    "Background\n" + context,
    valid.length ? "Reference links\n" + valid.map((link) => "- " + link).join("\n") : "",
    "Identify any source or file you could not access. Label assumptions and unverified claims. Do not invent citations or results.",
    "Output: " + stage.output + "."
  ];
  promptOutput.value = parts.filter(Boolean).join("\n\n");
  status.textContent = invalid ? invalid + (invalid === 1 ? " line was" : " lines were") + " omitted. Add one complete HTTP or HTTPS link per line." : "";
}

function selectStage(stage, focus) {
  if (stage !== activeStage) {
    activeStage = stage;
    renderProgress();
    renderLesson(stage);
    task.replaceChildren(...stage.tasks.map((item, index) => new Option(item.name, String(index))));
    byId("label-one").textContent = stage.fields[0];
    byId("label-two").textContent = stage.fields[1];
    firstField.placeholder = stage.example[0];
    secondField.placeholder = stage.example[1];
    const draft = drafts.get(stage.id);
    task.value = draft?.task ?? "0";
    firstField.value = draft?.fields[0] ?? "";
    secondField.value = draft?.fields[1] ?? "";
    linksField.value = draft?.links ?? "";
    buildPrompt();
  }
  if (focus) {
    lesson.focus({preventScroll: true});
    lesson.scrollIntoView();
  }
}

function handleLocation(initial) {
  const id = location.hash.slice(1);
  const stage = stages.find((item) => item.id === id);
  if (stage) selectStage(stage, true);
  else if (initial) selectStage(stages[0], false);
}

byId("prompt-form").addEventListener("input", buildPrompt);
byId("prompt-form").addEventListener("submit", (event) => event.preventDefault());
byId("example").addEventListener("click", () => {
  [firstField.value, secondField.value] = activeStage.example;
  buildPrompt();
  firstField.focus();
});
byId("copy").addEventListener("click", async () => {
  const message = status.textContent.replace(/^Prompt copied\. ?/, "");
  try {
    await navigator.clipboard.writeText(promptOutput.value);
    status.textContent = ["Prompt copied.", message].filter(Boolean).join(" ");
  } catch {
    promptOutput.focus();
    promptOutput.select();
    status.textContent = ["Prompt selected. Use your device’s copy command.", message].filter(Boolean).join(" ");
  }
});
window.addEventListener("hashchange", () => handleLocation(false));
document.querySelectorAll('.hero a[href="#idea"], .brand').forEach((link) => {
  link.addEventListener("click", () => {
    if (location.hash === "#idea") selectStage(stages[0], true);
  });
});
navigation.addEventListener("click", (event) => {
  const link = event.target.closest("a");
  if (link?.hash === location.hash) lesson.scrollIntoView();
});
handleLocation(true);
