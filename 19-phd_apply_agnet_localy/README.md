# Professor Outreach Agent v2 — ChatGPT Workflow + Local Helper Code

This package helps you run a simple professor outreach workflow **inside ChatGPT**.

The main idea:

```text
You upload this package + your CV/profile to ChatGPT
→ You ask for one university batch
→ ChatGPT finds professors from public pages
→ ChatGPT writes CSV + email drafts + tailored CV drafts
→ You download the ZIP
→ You review and send emails manually on your own computer
```

No OpenAI API key is required for the ChatGPT-side workflow.

The included Python helper code is optional. It does **not** send emails. It only creates:

```text
send_queue.csv
send_queue.html
.eml draft files
final ZIP package
```

---

## What this package contains

```text
professor_outreach_agent_v2_code/
  README.md
  SKILL.md

  prompts/
    PROJECT_SETUP_PROMPT.md
    ONE_COMMAND_BATCH_PROMPT.md
    NEXT_UNIVERSITY_PROMPT.md

  inputs/
    APPLICANT_PROFILE_FORM.md
    BATCH_REQUEST_FORM.md

  templates/
    email_template_short.txt
    email_template_with_paper.txt
    cv_tailoring_template.txt
    send_queue_template.html

  schemas/
    professors_schema.csv
    send_queue_schema.csv

  local_tools/
    make_send_queue.py
    validate_professors_csv.py
    build_batch_zip.py
    requirements.txt
    README.md

  examples/
    batch_example/
      professors/professors.csv
      emails_txt/
      tailored_cvs/
      reports/batch_summary.md

  $out/
    professors/
    emails_txt/
    emails_eml/
    tailored_cvs/
    send_queue/
    reports/
```

---

# Best way to use it

## Step 1 — Create a ChatGPT Project

Create a new ChatGPT Project, for example:

```text
Professor Outreach
```

Upload these files or the ZIP package into the project.

Also upload your:

```text
CV
research profile
SOP draft
project list
publication list, if any
```

## Step 2 — Give ChatGPT the setup prompt

Open:

```text
prompts/PROJECT_SETUP_PROMPT.md
```

Copy the prompt into ChatGPT.

This tells ChatGPT how to use your CV/profile and how to avoid fake claims.

## Step 3 — Run one university batch

Open:

```text
prompts/ONE_COMMAND_BATCH_PROMPT.md
```

Copy it and fill in:

```text
University:
Department/field:
Target:
Number of professors:
Preferred subfields:
```

Example:

```text
Use the Professor Outreach Agent v2 instructions and my uploaded CV/profile.

Run one professor outreach batch.

University: National University of Singapore
Department/field: Computer Science, AI and cybersecurity
Faculty page URL, if known:
Target: PhD
Number of professors: 15
Preferred subfields: AI security, privacy, machine learning, data science
Excluded subfields: pure hardware
Email style: concise, respectful, personalized

Output: Create a ZIP containing:
- professors.csv
- professors.json
- email drafts as .txt
- tailored CV drafts
- send_queue.csv
- send_queue.html
- batch_summary.md

Rules:
- Use official university/faculty pages first.
- Use only public emails.
- Do not invent CV facts.
- Mark missing emails as "Not found".
- Make every email specific to the professor.
```

## Step 4 — Download the ZIP from ChatGPT

ChatGPT should return a ZIP like:

```text
professor_outreach_[university]_[date].zip
```

Inside it:

```text
professors/professors.csv
emails_txt/*.txt
tailored_cvs/*.txt
send_queue/send_queue.csv
send_queue/send_queue.html
reports/batch_summary.md
```

## Step 5 — Review and send manually

Open:

```text
send_queue/send_queue.html
```

This gives you a simple review page.

You can then:

1. Open each email draft.
2. Review the professor research match.
3. Review the tailored CV draft.
4. Copy email into Gmail/Outlook.
5. Attach CV if needed.
6. Send manually.

---

# Optional local helper code

The helper code is useful if ChatGPT creates only these files:

```text
professors/professors.csv
emails_txt/*.txt
tailored_cvs/*.txt
reports/batch_summary.md
```

Then locally you can run:

```bash
python local_tools/make_send_queue.py examples/batch_example
```

This creates:

```text
examples/batch_example/send_queue/send_queue.csv
examples/batch_example/send_queue/send_queue.html
examples/batch_example/emails_eml/*.eml
```

Then create a ZIP:

```bash
python local_tools/build_batch_zip.py examples/batch_example
```

This creates:

```text
examples/batch_example.zip
```

## Validate CSV

```bash
python local_tools/validate_professors_csv.py examples/batch_example/professors/professors.csv
```

---

# Required professor CSV columns

ChatGPT should create:

```csv
rank,professor_name,last_name,title,university,department,email,profile_url,source_url,research_areas,specific_research_evidence,match_score,match_reason,key_overlap_terms,email_file,cv_file,eml_file,mailto_link,status,notes
```

The most important columns are:

```text
rank
professor_name
email
profile_url
research_areas
match_score
match_reason
email_file
cv_file
status
```

---

# Email rules

Every email must be:

```text
personalized
honest
short
specific
respectful
reviewable
```

Do not say:

```text
I read your paper ...
```

unless the paper was actually verified.

Do not say:

```text
I know you are accepting students ...
```

unless the official source explicitly says so.

---

# CV tailoring rules

Tailored CV drafts may:

```text
reorder real experience
highlight relevant skills
write a tailored objective
summarize real projects
remove irrelevant details
```

Tailored CV drafts must not:

```text
invent publications
invent degrees
invent GPA
invent skills
invent job titles
invent dates
invent awards
invent research experience
```

Every CV draft should include:

```text
Draft for review. This version only reorganizes and highlights information from the original CV. Verify before sending.
```

---

# Recommended batch size

Use:

```text
10–20 professors per batch
```

For quality, 15 is usually best.

---

# What this package does not do

This package does **not**:

```text
send emails automatically
store Gmail credentials
need Gmail API
need OpenAI API
bypass website restrictions
guarantee professors are accepting students
```

You remain responsible for reviewing and sending each email.

---

# Recommended repeat workflow

For every new university:

```text
Now do the same for [University Name], [Department/Field].
Use the same CV/profile.
Find 15 professors.
Create a new ZIP.
Avoid duplicate professors from previous batches.
```

Use the prompt in:

```text
prompts/NEXT_UNIVERSITY_PROMPT.md
```
