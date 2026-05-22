# Skills Database — schema and provenance

This directory holds a curated, extensible skills taxonomy used by the v6
keyword-evidence stage. Files are JSON for easy programmatic access.

## Files

| File | Source | Purpose |
|---|---|---|
| `skills_core.json` | Hand-curated from O*NET 28.0 + ESCO v1.1.1 categorizations | Master skill list with synonyms, categories, and role weightings. |
| `role_profiles.json` | Hand-curated from O*NET occupation profiles (research, AI, medical AI) | Maps role family → expected skill clusters with importance weights. |
| `compliance_skills.json` | Hand-curated from `references/18-academic-research-compliance.md` | Domain compliance skills (IRB, HIPAA, GCP) with expansion rules. |
| `synonyms.json` | Hand-curated tokenization-safety variants | Maps common misspellings and equivalent forms (e.g. "py torch" → "PyTorch"). |
| `personal_additions.json` | Empty template — grows from your applications | Skills you add manually that aren't yet in the core DB. |

## Provenance and updating

This is a SEED database — about 400 skills curated to cover academic, research,
ML/AI, medical AI, data science, and software engineering roles. It is NOT the
full O*NET (~17,000 skills) or ESCO (~13,890 skills) database.

To extend it from authoritative sources:

- **O*NET**: download from <https://www.onetcenter.org/database.html>. The
  `Technology Skills.txt` and `Tools Used.txt` files are most useful. License:
  public domain (US government work).
- **ESCO**: download from <https://esco.ec.europa.eu/en/use-esco/download>.
  The `skills_en.csv` file lists ~13,890 skills with hierarchical IDs.
  License: free reuse with attribution.

After downloading either, run:

```bash
python scripts/seed_skills_db.py path/to/onet_or_esco_dump.csv
```

Note: the seed loader is provided as a template — adapt it to the actual
column layout of whichever export you download.

## Schema — `skills_core.json`

```json
{
  "version": "6.0.0",
  "skills": [
    {
      "id": "skill_pytorch",
      "canonical": "PyTorch",
      "category": "ml_framework",
      "synonyms": ["pytorch", "torch", "py-torch"],
      "common_misspellings": ["py torch", "pytourch"],
      "esco_id": null,
      "onet_id": null,
      "applies_to_roles": ["research_scientist", "research_engineer", "ml_engineer", "data_scientist"],
      "weight_by_role": {
        "research_scientist": 0.9,
        "research_engineer": 1.0,
        "ml_engineer": 1.0,
        "data_scientist": 0.7
      }
    }
  ]
}
```

## Schema — `role_profiles.json`

```json
{
  "version": "6.0.0",
  "profiles": [
    {
      "role_family": "research_scientist",
      "canonical_title": "Research Scientist (AI/ML)",
      "tier_1_skills": ["skill_id_1", "..."],
      "tier_2_skills": ["..."],
      "tier_3_skills": ["..."],
      "compliance_skills_if_medical": ["compliance_id_1", "..."]
    }
  ]
}
```

## How the skill uses this database

1. `auto_profile_detector` reads the JD, picks the closest `role_family` from
   `role_profiles.json`.
2. `keyword_evidence_mapper` cross-references JD tokens against
   `skills_core.json` synonyms to canonicalize them.
3. If a candidate's CV mentions "py torch", the parser normalizes via
   `synonyms.json` to "PyTorch" before computing match strength.
4. If the role is medical AI, compliance skills from `compliance_skills.json`
   are surfaced as Tier 1 even if not explicitly in the JD.

## Truth rule

The skills database is a **vocabulary aid**. It does NOT add skills to the
candidate's CV. Only skills demonstrated in the candidate's actual evidence
are scored as `strong`. The database tells the system what to LOOK for,
never what to INVENT.
