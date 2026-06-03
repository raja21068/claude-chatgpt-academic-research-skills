# One-Command Batch Prompt

Copy, edit, and send this to ChatGPT for each university.

```text
Use the Professor Outreach Agent v2 instructions and my uploaded CV/profile.

Run one professor outreach batch.

University: [UNIVERSITY NAME]
Department/field: [DEPARTMENT OR FIELD]
Faculty page URL, if known: [URL OR BLANK]
Target: [PhD / Master's / RA / postdoc / internship]
Number of professors: [10-20]
Preferred subfields: [YOUR SUBFIELDS]
Excluded subfields: [OPTIONAL]
Country/region: [OPTIONAL]
Email style: concise, respectful, personalized
CV output format: txt

Output: Create a ZIP containing:
- professors/professors.csv
- professors/professors.json
- emails_txt/*.txt
- tailored_cvs/*.txt
- send_queue/send_queue.csv
- send_queue/send_queue.html
- reports/batch_summary.md

Rules:
- Use official university/faculty pages first.
- Cite/record the profile/source URL for each professor.
- Use only public emails.
- Do not invent CV facts.
- Do not say a professor is accepting students unless the source explicitly says so.
- Exclude weak matches unless needed to reach the requested count.
- Mark missing emails as "Not found".
- Keep emails 150-250 words.
- Make every email specific to the professor.
- Create a tailored CV draft for every professor using only my real CV/profile information.
```
