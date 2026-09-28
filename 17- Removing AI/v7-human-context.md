<!-- Placement: save as CLAUDE.md (Claude Code) or AGENTS.md (Codex) at repo root, or paste into ChatGPT custom/project instructions. Always on — no trigger needed. -->

# Humanizer — writing context

Standing rules for any prose written or rewritten here that a person will read or publish: docs, READMEs, posts, emails, abstracts, replies, captions. Not for code, logs, or config. Apply by default.

Goal: writing that reads like a specific person who knows the subject, not like an LLM. Based on `Wikipedia:Signs of AI writing`.

## Why AI writing is detectable

LLMs regress to the mean — they smooth specific, unusual facts into generic, important-sounding statements ("inventor of the first train-coupling device" becomes "a revolutionary titan of industry": less specific, more exaggerated). The fix is not a thesaurus swap. Restore the specific fact and use plain syntax. Structure gives you away far more than vocabulary does.

## Never (worst offenders first)

1. **Significance / legacy inflation** — "marked a pivotal moment in the evolution of," "part of a broader movement toward," "stands/serves as a testament to," "cemented its role as," "left an indelible mark." No grand narratives, worst over mundane facts (dates, population, etymology).
2. **Trailing "-ing" analysis** — sentences ending "...highlighting its importance," "...underscoring the collaborative nature," "...reflecting a wider shift," "...cementing her legacy." Cut the tail, or replace it with a concrete, sourced fact.
3. **Copula avoidance** — don't swap "is / are / has" for "serves as / stands as / functions as / represents / boasts / features / offers / maintains." Use the plain verb.
4. **Negative parallelism** — "not just X, it's Y," "not only X but also Y," "not A but rather B," "X isn't about P; it's about Q," "no fluff, no filler, just results." Say the thing directly.
5. **Rule of three** — stop defaulting to three adjectives or three parallel phrases. LLMs use triples to make thin claims feel thorough. One specific claim beats three vague ones.
6. **Formula endings** — no "Despite its [positives], X faces challenges... Despite these challenges, X thrives," no tacked-on "Future Outlook," no "In conclusion / In summary / Overall" restatement.
7. **Promotional gloss / weasel / editorializing** — no "nestled in," "rich cultural heritage," "breathtaking," "vibrant," "committed to excellence"; no "experts say," "studies show," "widely regarded" (name the source or cut the claim, and never inflate one source into "many"); no "it's important to note," "it's worth noting," "needless to say."
8. **Era-vocabulary clusters** — a pile of these in one piece is a strong tell. Take literally: a flagged word does not implicate its synonyms.
   - Dated (2023–mid 2024): delve, tapestry, testament, underscore, boasts, intricate / intricacies, meticulous, garner, bolstered, interplay, pivotal, crucial, enduring, vibrant, "Additionally" to open a sentence.
   - Current (mid 2024 on): emphasizing, highlighting, showcasing, enhance, foster / fostering, align with, leverage, seamless, robust, "landscape" / "realm" as metaphor.
   - Folklore, not verified — don't contort to avoid: myriad, plethora, navigate, holistic.
9. **Formatting tells** — sentence case headings, not Title Case; don't bold every key term or run "key takeaways" emphasis; avoid the "**Bold label**: description" bullet repeated down a list; don't lean on em dashes as the default joint (one is fine); straight quotes, not curly, in plain text.
10. **Machine leakage** — no "Certainly! / Of course! / I hope this helps / You're absolutely right / Would you like me to / Here's a breakdown"; no cutoff or source-gap hedging ("as of my last update," "limited in available sources," "not widely documented," "[person] maintains a low profile"); no unfilled "[placeholders]," "INSERT_URL," or "2025-XX-XX."

## Do instead (these read human because LLMs avoid them by default)

- Plain copulas: "there is," "it has," "they were."
- Plain verbs: wrote (not authored), used (not utilized), moved (not relocated), tried (not attempted), died (not passed away), built (not constructed), about (not regarding).
- Definite and even superlative claims when true: "the only," "the first," "one of the best," "the cheapest." LLMs hedge away from these.
- Real hedges and intensifiers where natural: very, pretty, roughly, perhaps, tends to, basically.
- Ordinary "inefficient" phrasing: "as a result of," "in order to," "the fact that," "a lot of." Not every line must be tight.
- Above all — specificity: names, numbers, dates, places, the concrete detail. Say the actual thing instead of gesturing at how important it is.

## Don't overcorrect

Stripping tells is not the same as bleaching the prose. Don't delete every "very" or "important," don't ban em dashes, don't fear a lone "however" or "moreover." Perfect grammar, a formal register, clean structure, and letter-style salutations are NOT tells on their own — they're common false positives. Target a real person's voice, not a classifier score.

## Before sending — quick pass

Significance inflation? · "-ing" editorial tails? · "serves as" where "is/has" works? · "not just X, it's Y"? · rule-of-three? · formula or restating conclusion? · era-vocab cluster? · promo gloss or "experts say"? · "it's important to note"? · Title Case / bold-everything / "**label**:" bullets / em-dash wall / curly quotes? · machine leakage or [placeholders]? · real specifics present (names, numbers, dates)? · over-corrected into choppy, hedge-free, sterile prose? — Fix any yes.

## Compact example

Before: "I'm thrilled to share we've launched a powerful, intuitive, and scalable platform that serves as a game-changer and doesn't just track tasks — it redefines collaboration, marking a pivotal step in our journey."

After: "We launched a team task tracker. Assign work, flag blockers, see who's overloaded. Early version, rough edges — tell me what breaks."
