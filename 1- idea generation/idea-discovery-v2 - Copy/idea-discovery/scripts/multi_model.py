"""
multi_model.py — Multi-Model Verification
Cross-checks novelty assessments across Claude + optional OpenAI/Gemini.
Consensus-based verdicts are more reliable than single-model.
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))
from utils import ClaudeClient, log

NOVELTY_PROMPT = """You are a research novelty assessor. Given a research idea and search results from academic databases, assess whether this idea is genuinely novel.

RESPOND WITH ONLY JSON:
{
  "idea_id": "IDEA-001",
  "novelty_score": 7,
  "verdict": "PROCEED | PROCEED_WITH_CAUTION | PIVOT | ABANDON",
  "closest_prior_work": "Title of closest existing paper",
  "overlap_percentage": 30,
  "key_differentiator": "What makes this unique",
  "concurrent_work_risk": "HIGH | MEDIUM | LOW",
  "reasoning": "2-3 sentences explaining the verdict"
}"""


class MultiModelVerifier:
    """
    Verify novelty across multiple LLM providers.
    Uses Claude as primary, optionally adds OpenAI and Gemini.
    Takes consensus verdict.
    """

    def __init__(self, config: dict):
        self.config = config
        self.models = {}

        # Always have Claude
        self.models["claude"] = {
            "name": "Claude (Sonnet)",
            "available": True,
        }

        # Check for OpenAI
        openai_key = os.environ.get("OPENAI_API_KEY")
        if openai_key:
            try:
                import openai
                self.models["openai"] = {
                    "name": "GPT-4",
                    "available": True,
                    "key": openai_key,
                }
                log.info("Multi-model: OpenAI GPT-4 available")
            except ImportError:
                log.info("Multi-model: openai package not installed, skipping")
        else:
            log.info("Multi-model: OPENAI_API_KEY not set, Claude-only mode")

        # Check for Gemini
        gemini_key = os.environ.get("GOOGLE_API_KEY")
        if gemini_key:
            try:
                import google.generativeai
                self.models["gemini"] = {
                    "name": "Gemini Pro",
                    "available": True,
                    "key": gemini_key,
                }
                log.info("Multi-model: Gemini Pro available")
            except ImportError:
                log.info("Multi-model: google-generativeai not installed, skipping")
        else:
            log.info("Multi-model: GOOGLE_API_KEY not set, skipping Gemini")

        n_models = sum(1 for m in self.models.values() if m.get("available"))
        log.info(f"Multi-model verifier: {n_models} model(s) active")

    def _ask_claude(self, idea_json: str, search_json: str) -> dict:
        """Query Claude for novelty assessment."""
        client = ClaudeClient(config=self.config)
        user_msg = f"""Assess novelty of this idea given search results.

IDEA:
{idea_json}

SEARCH RESULTS:
{search_json}

{NOVELTY_PROMPT}"""

        return client.ask_json(NOVELTY_PROMPT, user_msg)

    def _ask_openai(self, idea_json: str, search_json: str) -> Optional[dict]:
        """Query OpenAI GPT-4 for novelty assessment."""
        if "openai" not in self.models:
            return None
        try:
            import openai
            client = openai.OpenAI(api_key=self.models["openai"]["key"])
            resp = client.chat.completions.create(
                model="gpt-4o",
                temperature=0.1,
                messages=[
                    {"role": "system", "content": NOVELTY_PROMPT},
                    {"role": "user", "content": f"IDEA:\n{idea_json}\n\nSEARCH RESULTS:\n{search_json}"},
                ],
            )
            text = resp.choices[0].message.content.strip()
            if text.startswith("```"):
                lines = text.split("\n")
                lines = [l for l in lines if not l.strip().startswith("```")]
                text = "\n".join(lines)
            return json.loads(text)
        except Exception as e:
            log.warning(f"OpenAI query failed: {e}")
            return None

    def _ask_gemini(self, idea_json: str, search_json: str) -> Optional[dict]:
        """Query Gemini for novelty assessment."""
        if "gemini" not in self.models:
            return None
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.models["gemini"]["key"])
            model = genai.GenerativeModel("gemini-1.5-pro")
            prompt = f"""{NOVELTY_PROMPT}

IDEA:
{idea_json}

SEARCH RESULTS:
{search_json}"""
            resp = model.generate_content(prompt)
            text = resp.text.strip()
            if text.startswith("```"):
                lines = text.split("\n")
                lines = [l for l in lines if not l.strip().startswith("```")]
                text = "\n".join(lines)
            return json.loads(text)
        except Exception as e:
            log.warning(f"Gemini query failed: {e}")
            return None

    def verify(self, idea: dict, search_results: dict) -> dict:
        """
        Run multi-model novelty verification.
        Returns consensus result with individual model assessments.
        """
        idea_json = json.dumps(idea, indent=1, ensure_ascii=False)[:6000]
        search_json = json.dumps(search_results, indent=1, ensure_ascii=False)[:6000]

        assessments = {}

        # Claude (always runs)
        log.info("    [Claude] Assessing...")
        claude_result = self._ask_claude(idea_json, search_json)
        assessments["claude"] = claude_result

        # OpenAI (if available)
        if "openai" in self.models:
            log.info("    [GPT-4] Assessing...")
            openai_result = self._ask_openai(idea_json, search_json)
            if openai_result:
                assessments["openai"] = openai_result

        # Gemini (if available)
        if "gemini" in self.models:
            log.info("    [Gemini] Assessing...")
            gemini_result = self._ask_gemini(idea_json, search_json)
            if gemini_result:
                assessments["gemini"] = gemini_result

        # ── Compute Consensus ──────────────────────────────────────────────

        verdicts = []
        scores = []
        overlaps = []
        for model, result in assessments.items():
            if isinstance(result, dict):
                v = result.get("verdict", "PROCEED_WITH_CAUTION")
                verdicts.append(v)
                s = result.get("novelty_score", 5)
                scores.append(s)
                o = result.get("overlap_percentage", 50)
                overlaps.append(o)

        # Verdict hierarchy: ABANDON > PIVOT > PROCEED_WITH_CAUTION > PROCEED
        verdict_rank = {"ABANDON": 0, "PIVOT": 1, "PROCEED_WITH_CAUTION": 2, "PROCEED": 3}

        if len(verdicts) >= 2:
            # Conservative consensus: take the more cautious verdict if models disagree
            ranks = [verdict_rank.get(v, 2) for v in verdicts]
            # If majority says ABANDON/PIVOT, go with that
            if ranks.count(0) >= len(ranks) / 2:
                consensus_verdict = "ABANDON"
            elif ranks.count(0) + ranks.count(1) >= len(ranks) / 2:
                consensus_verdict = "PIVOT"
            else:
                # Take median rank
                median_rank = sorted(ranks)[len(ranks) // 2]
                consensus_verdict = {0: "ABANDON", 1: "PIVOT", 2: "PROCEED_WITH_CAUTION", 3: "PROCEED"}[median_rank]

            consensus_score = round(sum(scores) / len(scores), 1)
            consensus_overlap = round(sum(overlaps) / len(overlaps), 1)
        else:
            # Single model
            consensus_verdict = verdicts[0] if verdicts else "PROCEED_WITH_CAUTION"
            consensus_score = scores[0] if scores else 5
            consensus_overlap = overlaps[0] if overlaps else 50

        # Check for model disagreement
        agreement = len(set(verdicts)) == 1
        disagreement_flag = not agreement and len(verdicts) >= 2

        consensus = {
            "idea_id": idea.get("idea_id", ""),
            "n_models_used": len(assessments),
            "models_queried": list(assessments.keys()),
            "individual_assessments": assessments,
            "consensus": {
                "verdict": consensus_verdict,
                "novelty_score": consensus_score,
                "overlap_percentage": consensus_overlap,
                "models_agree": agreement,
                "disagreement_flag": disagreement_flag,
            },
        }

        if disagreement_flag:
            # Add disagreement details
            consensus["consensus"]["disagreement_details"] = {
                "verdicts_by_model": {m: r.get("verdict", "?") for m, r in assessments.items()},
                "scores_by_model": {m: r.get("novelty_score", "?") for m, r in assessments.items()},
                "interpretation": (
                    "Models disagree on novelty. Review individual assessments carefully. "
                    "Consensus used the more conservative verdict."
                ),
            }

        verdict_emoji = {"PROCEED": "✅", "PROCEED_WITH_CAUTION": "⚠️", "PIVOT": "🔄", "ABANDON": "❌"}
        log.info(f"    Consensus: {verdict_emoji.get(consensus_verdict, '?')} {consensus_verdict} "
                 f"(score: {consensus_score}/10, agreement: {agreement})")

        return consensus
