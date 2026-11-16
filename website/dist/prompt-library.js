const find = (id) => document.getElementById(id);
const stageLinks = ["idea", "literature", "draft", "code", "review", "results"];
const stageByPrompt = { "novelty-attack": "literature", "novelty-matrix": "literature", "write-results": "results", "journal-ready": "draft", "format-paper": "draft" };
const skillLinks = {
  "method-figure": "https://github.com/raja21068/claude-chatgpt-academic-research-skills/tree/main/8-Paper-Figure-Generation",
  "research-slides": "https://github.com/raja21068/claude-chatgpt-academic-research-skills/tree/main/6-paper-slides"
};
const list = find("prompt-list");
const controls = find("category-buttons");
const search = find("prompt-search");
let activeCategory = -1;

function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text) node.textContent = text;
  if (className) node.className = className;
  return node;
}

function templateText([, , title, skill, inputs, task, output]) {
  return [
    "Goal: " + title.replace(/^Phase \d+ · /, ""),
    "Skill: Use the attached " + skill + " instructions when available.",
    "Task: " + task,
    "Background: [describe your project and list any supplied files or source links]. Prepare: " + inputs,
    "Output: " + output,
    "State which sources, files, or checks you could not verify. Label assumptions and use only supplied or verified evidence."
  ].join("\n\n");
}

async function copyPrompt(value, button, details) {
  try {
    await navigator.clipboard.writeText(value);
    find("copy-announcement").textContent = "Prompt copied.";
    button.textContent = "Copied";
    setTimeout(() => { button.textContent = "Copy prompt"; }, 1600);
  } catch {
    details.open = true;
    const field = details.querySelector("textarea");
    field.focus();
    field.select();
    find("copy-announcement").textContent = "Prompt selected. Use your device’s copy command.";
  }
}

function promptCard(entry, openId) {
  const [id, category, title, skill, inputs, , output] = entry;
  const article = element("article", "", "card prompt-card");
  article.id = id;
  article.setAttribute("aria-labelledby", id + "-title");
  const categoryLabel = element("p", promptCategories[category], "eyebrow");
  const heading = element("h2", title);
  heading.id = id + "-title";
  const skillLabel = element("p", skill, "prompt-skill");
  const materials = element("p", "Bring " + inputs.charAt(0).toLowerCase() + inputs.slice(1));
  const deliverable = element("p", "Save " + output.charAt(0).toLowerCase() + output.slice(1));
  const details = element("details", "", "prompt-preview");
  details.open = id === openId;
  details.append(element("summary", "Preview prompt"));
  const field = element("textarea");
  field.readOnly = true;
  field.rows = 10;
  field.spellcheck = false;
  field.value = templateText(entry);
  field.setAttribute("aria-label", title + " prompt");
  details.append(field);
  const copy = element("button", "Copy prompt", "button primary");
  copy.type = "button";
  copy.addEventListener("click", () => copyPrompt(field.value, copy, details));
  const skillLink = skillLinks[id];
  const stage = element("a", skillLink ? "Open skill guide ↗" : "Open workflow stage →", "prompt-stage-link");
  stage.href = skillLink || "./#" + (stageByPrompt[id] || stageLinks[category]);
  const actions = element("div", "", "prompt-actions");
  actions.append(copy, stage);
  article.append(categoryLabel, heading, skillLabel, materials, deliverable, actions, details);
  return article;
}

function render(openId = "") {
  const query = search.value.trim().toLowerCase();
  const filtered = promptEntries.filter((entry) => (activeCategory === -1 || entry[1] === activeCategory)
    && query.split(/\s+/).every((term) => [...entry.slice(2), promptCategories[entry[1]]].join(" ").toLowerCase().includes(term)));
  list.replaceChildren(...filtered.map((entry) => promptCard(entry, openId)));
  find("prompt-count").textContent = filtered.length + " " + (filtered.length === 1 ? "prompt" : "prompts");
  if (!filtered.length) list.append(element("p", "No prompts match. Try a different search or category.", "card"));
  for (const button of controls.children) {
    button.setAttribute("aria-pressed", String(Number(button.dataset.category) === activeCategory));
  }
}

for (const [index, label] of ["All prompts", ...promptCategories].entries()) {
  const button = element("button", label, "button secondary");
  button.type = "button";
  button.dataset.category = String(index - 1);
  button.addEventListener("click", () => {
    activeCategory = index - 1;
    render();
  });
  controls.append(button);
}
search.addEventListener("input", () => render());
function openLinkedPrompt() {
  const id = location.hash.slice(1);
  if (!promptEntries.some((entry) => entry[0] === id)) return;
  activeCategory = -1;
  search.value = "";
  render(id);
  find(id).scrollIntoView();
}
window.addEventListener("hashchange", openLinkedPrompt);
render();
openLinkedPrompt();
