#!/usr/bin/env python3
"""
extract_writing_style.py
========================
Generate references/my_writing_style.md from your personal corpus.
Reads the corpus/ folder created by build_corpus.py.

Usage:
    python extract_writing_style.py

Output:
    ../references/my_writing_style.md
"""

import re
import json
import random
from pathlib import Path
from collections import Counter

# --- optional NLTK (graceful fallback if not installed) ---
try:
    import nltk
    nltk.download("punkt", quiet=True)
    nltk.download("punkt_tab", quiet=True)
    from nltk.tokenize import sent_tokenize, word_tokenize
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    def sent_tokenize(text):
        return re.split(r'(?<=[.!?])\s+', text.strip())
    def word_tokenize(text):
        return re.findall(r"\b\w+\b", text)

# ──────────────────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────────────────
CORPUS_FOLDER   = Path("corpus")
OUTPUT_FILE     = Path("../references/my_writing_style.md")
SECTIONS        = ["abstract", "introduction", "methods", "results", "discussion", "conclusion"]
MIN_SENT_LEN    = 40    # ignore very short sentences when picking examples
MAX_EXAMPLES    = 5     # max example sentences per section
# ──────────────────────────────────────────────────────────

TRANSITION_WORDS = [
    "however", "therefore", "moreover", "furthermore", "nevertheless",
    "consequently", "in contrast", "on the other hand", "for example",
    "for instance", "in addition", "accordingly", "thus", "hence",
    "nonetheless", "instead", "meanwhile", "overall", "specifically",
]


def load_corpus(corpus_folder: Path):
    """Load .txt section files grouped by section name."""
    by_section = {s: [] for s in SECTIONS}
    all_texts = []
    for subdir in sorted(corpus_folder.iterdir()):
        if not subdir.is_dir():
            continue
        for sec in SECTIONS:
            f = subdir / f"{sec}.txt"
            if f.exists():
                text = f.read_text(encoding="utf-8", errors="replace").strip()
                if len(text) > 200:
                    by_section[sec].append(text)
                    all_texts.append(text)
    return by_section, all_texts


def avg_sentence_length(texts):
    lengths = []
    for t in texts:
        for s in sent_tokenize(t):
            words = word_tokenize(s)
            if len(words) >= 4:
                lengths.append(len(words))
    return round(sum(lengths) / len(lengths), 1) if lengths else 0.0


def common_starters(texts, top_n=10):
    starters = []
    for t in texts:
        for s in sent_tokenize(t):
            cleaned = re.sub(r'^[\W\d]+', '', s)
            words = word_tokenize(cleaned)
            if len(words) >= 3:
                starters.append(' '.join(words[:3]).lower())
    counts = Counter(starters).most_common(top_n * 3)
    return [f'"{w}" ({c}×)' for w, c in counts if c >= 2][:top_n]


def common_transitions(texts, top_n=10):
    joined = ' '.join(texts).lower()
    counts = {t: joined.count(t) for t in TRANSITION_WORDS}
    ranked = sorted(((t, c) for t, c in counts.items() if c > 0), key=lambda x: -x[1])
    return [f'"{t}" ({c}×)' for t, c in ranked[:top_n]]


def pick_examples(by_section):
    examples = {}
    for sec, texts in by_section.items():
        candidates = []
        for t in texts:
            for s in sent_tokenize(t):
                s = ' '.join(s.split())
                if MIN_SENT_LEN < len(s) < 300:
                    candidates.append(s)
        unique = list(dict.fromkeys(candidates))
        if len(unique) > MAX_EXAMPLES:
            step = len(unique) // MAX_EXAMPLES
            picked = [unique[i * step] for i in range(MAX_EXAMPLES)]
        else:
            picked = unique
        examples[sec] = picked
    return examples


def section_openings(by_section):
    openings = {}
    for sec, texts in by_section.items():
        firsts = []
        for t in texts:
            sents = sent_tokenize(t)
            if sents:
                first = ' '.join(sents[0].split())
                firsts.append(first[:100] + "…" if len(first) > 100 else first)
        openings[sec] = firsts[:3]
    return openings


def write_style_file(by_section, all_texts, output_path: Path):
    avg_len = avg_sentence_length(all_texts)
    starters = common_starters(all_texts)
    transitions = common_transitions(all_texts)
    examples = pick_examples(by_section)
    openings = section_openings(by_section)

    total_sents = sum(len(sent_tokenize(t)) for t in all_texts)
    total_docs = sum(len(v) for v in by_section.values())

    lines = [
        "# My Academic Writing Style",
        "",
        f"*Auto-generated from your personal corpus of {total_docs} section files.*  ",
        f"*Average sentence length: {avg_len} words. Total sentences analysed: {total_sents}.*",
        "",
        "---",
        "",
        "## 1. Global Style Traits",
        "",
        "### Common sentence starters (first 3 words)",
    ]
    for s in starters:
        lines.append(f"- {s}")

    lines += [
        "",
        "### Preferred transition words / phrases",
    ]
    for t in transitions:
        lines.append(f"- {t}")

    lines += [
        "",
        "### Sentence rhythm",
        f"- Typical sentence length: {avg_len} words per sentence.",
        "- Mix declarative sentences with occasional complex clauses.",
        "",
        "---",
        "",
        "## 2. Section-Specific Openings",
        "",
        "How you typically begin each section:",
    ]
    for sec in SECTIONS:
        lines.append(f"\n### {sec.capitalize()}")
        for i, o in enumerate(openings.get(sec, []), 1):
            lines.append(f'{i}. "{o}"')

    lines += [
        "",
        "---",
        "",
        "## 3. Example Paragraphs (from your own writing)",
        "",
        "*Real sentences from your papers — use as reference for tone, vocabulary, structure.*",
    ]
    for sec in SECTIONS:
        ex_list = examples.get(sec, [])
        if not ex_list:
            continue
        lines.append(f"\n### {sec.capitalize()}")
        for i, ex in enumerate(ex_list, 1):
            lines.append(f"\n**Example {i}:** {ex}")

    lines += [
        "",
        "---",
        "",
        "## 4. Stylistic Rules (paste into Claude / ChatGPT)",
        "",
        "```text",
        "You are writing an academic paper in my personal style. Follow these rules:",
        "",
    ]
    if starters:
        lines.append(f"- Sentence starters: {', '.join(starters[:5])}")
    if transitions:
        lines.append(f"- Use transitions: {', '.join(transitions[:5])}")
    lines += [
        f"- Keep sentences at around {avg_len} words.",
        "- Structure each section as shown in the examples above.",
        "- Never invent citations or data. I will provide those.",
        "```",
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text('\n'.join(lines), encoding="utf-8")
    print(f"✓ Written: {output_path}")


def main():
    if not CORPUS_FOLDER.exists():
        print(f"ERROR: corpus folder not found at '{CORPUS_FOLDER}'.")
        print("Run build_corpus.py first, or create corpus/ manually with section text files.")
        return

    by_section, all_texts = load_corpus(CORPUS_FOLDER)
    total = sum(len(v) for v in by_section.values())
    if total == 0:
        print("No corpus texts found. Check that corpus/ contains subfolders with section .txt files.")
        return

    print(f"Loaded {total} section files from {CORPUS_FOLDER}")
    write_style_file(by_section, all_texts, OUTPUT_FILE)


if __name__ == "__main__":
    main()
