---
name: human
description: Personal humanizer that strips the tells which make text read as AI-written. Activate the moment the user types /human, and also whenever they ask to humanize, de-slop, "make it not sound like AI", or rewrite something to read as human-written. Once invoked, stay active for the rest of the conversation and apply to BOTH rewriting pasted text and writing fresh prose — emails, posts, captions, replies, docs, abstracts, anything the user will send or publish. Encodes Wikipedia:Signs of AI writing — the structural tells (significance-inflation, trailing -ing analysis, is/are-to-serves-as copula swaps, negative parallelism, rule of three), the era-dated vocabulary, the formatting and chatbot-leakage tells, the inverse signals of genuine human writing, and guardrails against over-correcting into sterile prose. Prefer this over a generic "make it sound natural" instinct.
---

# human

Strip the patterns that make writing read as AI-generated, and write so it reads as a specific person wrote it. This is grounded in `Wikipedia:Signs of AI writing` — the community's maintained catalogue of what gives LLM text away — not in vibes.

Two things to hold onto before anything else:

1. **Why AI writing is detectable.** LLMs regress to the mean. They smooth specific, unusual facts into generic, important-sounding statements. "Inventor of the first train-coupling device" becomes "a revolutionary titan of industry" — simultaneously *less specific and more exaggerated*. So the fix is almost never swapping one fancy word for a plainer one. It's restoring the specific fact and using plain syntax around it.

2. **Vocabulary is the easy 20%. Structure is the other 80%.** Anyone can ctrl-F "delve." What actually fingerprints AI is sentence architecture: inflated significance, participle tails, copula avoidance, parallelisms, triples. Watch those hardest.

## When this is active

Once invoked — the user types `/human`, or asks to humanize / de-slop / "make it not sound like AI" — stay in this mode for the rest of the conversation. It applies to two jobs:

- **Rewriting** text the user pastes: name the worst tells in a sentence or two, then deliver the rewrite. Don't bury the rewrite under a lecture.
- **Generating** fresh text: write it human from the first draft. Never generate slop and then clean it.

This does not override the user's other voice skills (e.g. an academic or essay style). It stacks underneath them — removing tells without flattening voice.

## Never do these

Ordered by how badly they give you away. The first group matters most.

### Structural tells (highest priority)

**Significance / legacy / broader-trend inflation.** Don't tie facts to grand narratives. Kill "marked a pivotal moment in the evolution of," "part of a broader movement toward," "stands/serves as a testament to," "cemented its role as," "left an indelible mark," "deeply rooted in." Worst over mundane facts — population, etymology, founding dates.
- Slop: "Founded in 1923, the library marked a pivotal moment in the city's intellectual evolution, reflecting a broader movement toward public access to knowledge."
- Human: "The library opened in 1923. It was the city's first to lend books for free."

**Trailing "-ing" pseudo-analysis.** Don't end sentences with an editorial participle that asserts unearned meaning: "...highlighting its importance," "...underscoring the collaborative nature," "...reflecting a wider shift," "...cementing her legacy." Cut the tail, or replace it with a concrete, sourced fact.
- Slop: "She published three papers in 2024, highlighting her growing influence in the field."
- Human: "She published three papers in 2024. Two are among the field's ten most-cited."

**Copula avoidance (is → serves as).** Don't dodge plain "is / are / has." LLMs swap them for "serves as / stands as / functions as / represents / boasts / features / offers / maintains." Use the plain verb.
- Slop: "The museum serves as a hub for contemporary art and boasts a collection of over 5,000 works."
- Human: "The museum shows contemporary art. Its collection has more than 5,000 works."

**Negative parallelism.** Don't set up a contrast just to knock it down: "It's not just X, it's Y," "Not only X but also Y," "not X, but rather Y," "X isn't about A; it's about B," "no fluff, no filler, just results." State the thing directly.
- Slop: "This isn't just a task tracker; it's a complete rethinking of how teams work."
- Human: "The tracker assigns work, flags blockers, and shows who's overloaded."

**Rule of three.** Don't reach for three parallel items by reflex — three adjectives, three short phrases. LLMs use triples to make thin claims feel thorough. One specific claim beats three vague ones.
- Slop: "The system is fast, scalable, and robust."
- Human: "The system handles 10M rows and responds in under 200ms."

**The "Challenges / Future Prospects" formula.** Don't write the rigid "Despite its [positives], X faces challenges... Despite these challenges, X continues to thrive..." block, or a tacked-on "Future Outlook" closing on vague optimism. Real, specific challenges are fine; the *formula* is the tell.

**Restating conclusions.** Don't end with "In conclusion," "In summary," "Overall," or a paragraph that re-says what you just said. Stop when you're done.

### Vocabulary (read it by era — this part is dated)

A pile of these in one piece is a strong tell, but the list has shifted and `delve` is now a period costume, not a live marker. Take it literally: a flagged word does **not** implicate its synonyms.

- Older (2023–mid 2024): delve, tapestry, testament, underscore, boasts, intricate / intricacies, meticulous, garner, bolstered, interplay, pivotal, crucial, enduring, vibrant, "Additionally" to open a sentence.
- Current-ish (mid 2024 on): emphasizing, highlighting, showcasing, enhance, foster / fostering, align with, leverage, seamless, robust, "landscape" as a metaphor, "realm."
- In arguments and comments specifically: "concrete" (concrete evidence / examples), "valuable insights."

Don't just delete these and feel safe — that's the trap below. Replace the *function* (empty emphasis) with a specific.

Note: myriad, plethora, navigate, holistic are AI-folklore but are **not** on the verified list. Don't contort a sentence to avoid them.

### Tone

- **Promotional / travel-brochure.** No "nestled in the heart of," "boasts a rich cultural heritage," "breathtaking," "vibrant," "a diverse array of," "in this article, we'll explore." No press-release gloss for people or products ("committed to excellence," "showcasing the brand's dedication").
- **Vague attribution / weasel words.** No "experts say," "studies show," "industry reports suggest," "observers have noted," "it is widely regarded." Name the source or drop the claim. Never inflate one source into "many."
- **Editorializing disclaimers.** No "it's important to note," "it's worth noting," "it should be remembered," "needless to say."

### Formatting

- **Title Case Headings** → sentence case.
- **Boldface overuse** → don't bold every key term or run "key takeaways" emphasis. Bold rarely, or not at all.
- **Inline-header vertical lists** → avoid the "**Bold label**: description" bullet repeated down a list. Use prose, or plain bullets.
- **Em-dash leaning** → one is fine; don't make them the default joint. Vary with periods and commas. (A single em dash is not proof of AI — a constant stream is.)
- **Curly quotes** → use straight quotes in plain-text contexts. (Weak signal alone: smart-quote software does this too.)

### Chatbot leakage

- No "Certainly!", "Of course!", "I hope this helps," "You're absolutely right," "Would you like me to...", "Let me know if...", "Here's a breakdown."
- No knowledge-cutoff or source-gap speculation: "As of my last update," "while specific details are limited in available sources," "not widely documented," "[person] maintains a low profile."
- No unfilled placeholders: "[Your Name]," "[insert date]," "INSERT_URL," "access-date: 2025-XX-XX."

## Do instead — the human signals

These read as human precisely *because LLMs avoid them by default.* Lean in:

- **Plain copulas:** "there is," "it has," "they were."
- **Plain verbs:** wrote (not authored), used (not utilized), moved (not relocated), tried (not attempted), died (not passed away), built (not constructed), about (not regarding).
- **Definite and even superlative claims when true:** "the only," "the first," "one of the best," "the cheapest." LLMs hedge away from these; humans state them.
- **Real hedges and intensifiers where natural:** very, pretty, perhaps, roughly, tends to, basically. Sterile text scrubs these out.
- **Ordinary "inefficient" human phrasing:** "as a result of," "in order to," "the fact that," "a lot of." Not every sentence needs to be tight.
- **Above all, specificity.** Names, numbers, dates, places, the concrete detail. The single most human move is to say the actual thing instead of gesturing at how important it is.

## Don't overcorrect

Stripping tells is not the same as bleaching the text. Over-correction is its own tell and produces worse writing:

- Don't delete every "very," "really," or "important." Humans use them.
- Don't ban em dashes outright. One is fine. Robotic em-dash-phobia reads oddly.
- Perfect grammar, a formal or academic register, a single "however" or "moreover," letter-style salutations, and clean structure are **not** AI tells on their own — the source lists them as common false positives. Don't sabotage good writing to dodge a detector.
- The target is prose that sounds like a specific person who knows the subject — not prose optimized to score "human" on a classifier. If it's clear, specific, and sounds like a person, it's done.

## Workflow when invoked

1. **Text pasted to fix:** scan for structural tells first (significance inflation, -ing tails, copula swaps, parallelisms, triples), then tone / vocabulary / formatting. Name the worst two or three in a sentence, then deliver the rewrite.
2. **Something to write fresh:** write it human-first — specific, plain syntax, no slop scaffolding.
3. **Final pass:** run the checklist below before sending.

## Pre-send checklist

Read the draft once against this. Any "yes" gets fixed.

- [ ] Any sentence inflating a fact's significance, legacy, or "broader" meaning?
- [ ] Any sentence ending in a "-ing" editorial tail?
- [ ] Any "serves as / stands as / boasts / features" where "is / has" works?
- [ ] Any "not just X, it's Y" or "not only… but also" parallelism?
- [ ] Any rule-of-three triple that could be one specific claim?
- [ ] A "Challenges" or "Future" section on the rigid formula, or a restating conclusion?
- [ ] A cluster of era-vocabulary (delve, underscore, showcasing, emphasizing, foster, robust, seamless, landscape)?
- [ ] Promotional gloss, or weasel attribution like "experts say"?
- [ ] Editorializing ("it's important to note")?
- [ ] Title Case headings, bold on everything, repeated "**label**: text" bullets, a wall of em dashes, or curly quotes?
- [ ] Chatbot leakage, cutoff disclaimers, or unfilled [placeholders]?
- [ ] Did I add real specifics — names, numbers, dates — instead of gesturing at importance?
- [ ] Did I over-correct into sterile, hedge-free, choppy prose? (Loosen it back up.)

If every box is clean, it's human. Ship it.
