# Student Research Workflow — website

Live site: **https://raja21068.github.io/claude-chatgpt-academic-research-skills/**

A static website (plain HTML, CSS and JavaScript, no build step) that guides students through six research steps with ChatGPT or Claude: idea, literature, first draft, code, results, review.

## Pages

| File | What it is |
|---|---|
| `dist/index.html` | Home: "How it works" diagram, the six steps, and a 5-minute practice review |
| `dist/idea-prompts.html` | Prompts for every step in Beginner / Researcher / Expert versions, sample answers, answer check and score-over-rounds chart |
| `dist/cases.html` | Two worked examples told as 6-card picture stories |
| `dist/prompts.html` | All prompt templates (for advanced users) |

Prompt text lives in `dist/level-prompts-data.js`. Sample answers live in `dist/demo/sample-*.md` and are made up to show the format.

## Run it locally

```bash
cd website/dist
python -m http.server 8765
```

Then open http://127.0.0.1:8765/

## Update the live site

The site is served by GitHub Pages from the `gh-pages` branch, which holds a copy of `website/dist`. After committing changes to `main`, publish them with:

```bash
git subtree push --prefix website/dist origin gh-pages
```

GitHub usually updates the page within a minute or two.
