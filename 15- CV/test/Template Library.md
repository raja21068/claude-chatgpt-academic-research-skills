# Template Library — v6

A curated set of ATS-safe, evidence-first templates for the academic / research /
ML-AI track. Pick the one that matches your target role family from the
auto-profile detector's output, then fill in your verified evidence.

## Resumes (1–2 pages, industry-flavored)

| File | When to use |
|---|---|
| `resumes/research_scientist_resume.md` | Industry research scientist (DeepMind, FAIR, MSR, Anthropic, OpenAI). |
| `resumes/research_engineer_resume.md` | Research engineer / member of technical staff at AI labs. |
| `resumes/ml_engineer_resume.md` | Production ML engineer at tech companies. |
| `resumes/clinical_ai_resume.md` | Medical / clinical AI roles (industry side, e.g. PathAI, Tempus). |
| `resumes/phd_student_industry_resume.md` | PhD student applying for internships or post-graduation industry roles. |
| `resumes/data_scientist_resume.md` | Data scientist / applied scientist. |

## CVs (2+ pages, academic-flavored)

| File | When to use |
|---|---|
| `cvs/academic_cv_full.md` | Full academic CV (faculty applications, fellowships, grants). |
| `cvs/postdoc_application_cv.md` | Postdoc applications (concise but publication-forward). |
| `cvs/phd_application_cv.md` | Applying to a PhD program (research statement adjacent). |

## Cover letters

| File | When to use |
|---|---|
| `cover_letters/cover_letter_academic.md` | Faculty / postdoc / academic positions. |
| `cover_letters/cover_letter_industry_research.md` | Industry research scientist roles. |
| `cover_letters/cover_letter_phd_application.md` | PhD program applications. |

## Emails

| File | When to use |
|---|---|
| `emails/email_referral_request.md` | Asking a contact for a referral. |
| `emails/email_cold_outreach_researcher.md` | Cold-emailing a researcher whose lab interests you. |
| `emails/email_followup.md` | Following up after submitting an application. |

## LinkedIn

| File | When to use |
|---|---|
| `linkedin/linkedin_headline_research_track.md` | Headline patterns for research / AI roles. |
| `linkedin/linkedin_about_section.md` | About section structure with examples. |

## Conventions

1. Every template uses ATS-safe formatting per `references/02-ats-and-formatting.md`.
2. Single-column layout. Standard section names.
3. Bullets follow: action + scope + method + outcome.
4. Placeholders use `{Curly Braces}`. TODOs use `[TODO: ...]`.
5. Dates use `Mon YYYY – Mon YYYY` consistently.
6. Acronyms are expanded at first use (`Institutional Review Board (IRB)`).
7. Compliance vocabulary (IRB, HIPAA, GCP) only appears when the template
   is for medical-AI / clinical roles; remove if not applicable.

## How the skill picks a template

The orchestrator reads `session_context.yaml.role_profile.detected_role_family`
and picks the matching template automatically. You can override at any stage
by passing `--template path/to/template.md`.
