from __future__ import annotations

import csv
import html
import sys
from email.message import EmailMessage
from pathlib import Path
from urllib.parse import quote


def safe_slug(text: str) -> str:
    import re
    text = (text or "professor").lower().strip()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_") or "professor"


def parse_email_txt(path: Path) -> tuple[str, str, str]:
    """
    Parse a simple email text file:

    To: professor@example.edu
    Subject: Example subject

    Body...
    """
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    to = ""
    subject = ""
    body_start = 0

    for i, line in enumerate(lines[:10]):
        low = line.lower()
        if low.startswith("to:"):
            to = line.split(":", 1)[1].strip()
        elif low.startswith("subject:"):
            subject = line.split(":", 1)[1].strip()
        elif line.strip() == "":
            body_start = i + 1
            break

    if body_start == 0:
        body_start = 2 if len(lines) > 2 else 0

    body = "\n".join(lines[body_start:]).strip()
    return to, subject, body


def create_eml(to_email: str, subject: str, body: str, output_path: Path) -> None:
    msg = EmailMessage()
    msg["To"] = to_email
    msg["Subject"] = subject
    msg["X-Unsent"] = "1"
    msg.set_content(body)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(bytes(msg))


def make_mailto(to_email: str, subject: str, body: str) -> str:
    return f"mailto:{quote(to_email)}?subject={quote(subject)}&body={quote(body)}"


def read_professors(batch_dir: Path) -> list[dict]:
    csv_path = batch_dir / "professors" / "professors.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing {csv_path}")

    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_html(rows: list[dict]) -> str:
    table_rows = []
    for row in rows:
        table_rows.append(f"""
        <tr>
          <td>{html.escape(row.get('rank', ''))}</td>
          <td>{html.escape(row.get('professor_name', ''))}</td>
          <td>{html.escape(row.get('email', ''))}</td>
          <td>{html.escape(row.get('subject', ''))}</td>
          <td><a href="{html.escape(row.get('mailto_link', ''))}">Open mail draft</a></td>
          <td>{html.escape(row.get('email_file', ''))}</td>
          <td>{html.escape(row.get('cv_file', ''))}</td>
          <td>{html.escape(row.get('notes', ''))}</td>
        </tr>
        """)

    table = f"""
    <table>
      <thead>
        <tr>
          <th>Rank</th>
          <th>Professor</th>
          <th>Email</th>
          <th>Subject</th>
          <th>Mailto</th>
          <th>Email file</th>
          <th>CV file</th>
          <th>Notes</th>
        </tr>
      </thead>
      <tbody>
        {''.join(table_rows)}
      </tbody>
    </table>
    """

    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Professor Outreach Send Queue</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; line-height: 1.4; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 16px; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; vertical-align: top; font-size: 14px; }}
    th {{ background: #f2f2f2; }}
    .warning {{ background: #fff3cd; padding: 12px; border: 1px solid #ffeeba; margin-bottom: 16px; }}
  </style>
</head>
<body>
  <h1>Professor Outreach Send Queue</h1>
  <div class="warning">
    Review every email and CV before sending. This page does not send anything automatically.
  </div>
  {table}
</body>
</html>
"""


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python local_tools/make_send_queue.py path/to/batch_folder")
        raise SystemExit(2)

    batch_dir = Path(sys.argv[1]).resolve()
    professors = read_professors(batch_dir)

    send_queue_dir = batch_dir / "send_queue"
    eml_dir = batch_dir / "emails_eml"
    send_queue_dir.mkdir(parents=True, exist_ok=True)
    eml_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for row in professors:
        email_file = row.get("email_file", "").strip()
        if not email_file:
            slug = safe_slug(row.get("professor_name", "professor"))
            email_file = f"emails_txt/{row.get('rank', '')}_{slug}_email.txt"

        email_path = batch_dir / email_file
        if not email_path.exists():
            # Try just filename inside emails_txt.
            email_path = batch_dir / "emails_txt" / Path(email_file).name

        if email_path.exists():
            parsed_to, subject, body = parse_email_txt(email_path)
        else:
            parsed_to, subject, body = "", "", ""

        to_email = row.get("email", "").strip()
        if not to_email or to_email.lower() == "not found":
            to_email = parsed_to

        professor_name = row.get("professor_name", "Professor")
        slug = safe_slug(professor_name)
        rank = row.get("rank", "")
        eml_rel = f"emails_eml/{rank}_{slug}.eml"
        eml_path = batch_dir / eml_rel

        mailto_link = ""
        if to_email and subject and body:
            mailto_link = make_mailto(to_email, subject, body)
            create_eml(to_email, subject, body, eml_path)

        cv_file = row.get("cv_file", "").strip()
        if not cv_file:
            cv_file = f"tailored_cvs/{rank}_{slug}_cv.txt"

        rows.append({
            "rank": rank,
            "professor_name": professor_name,
            "email": to_email or "Not found",
            "subject": subject,
            "email_file": str(email_path.relative_to(batch_dir)) if email_path.exists() else email_file,
            "cv_file": cv_file,
            "eml_file": eml_rel if mailto_link else "",
            "mailto_link": mailto_link,
            "send_status": "not_sent",
            "sent_date": "",
            "reply_status": "",
            "notes": row.get("notes", ""),
        })

    fieldnames = [
        "rank", "professor_name", "email", "subject", "email_file", "cv_file",
        "eml_file", "mailto_link", "send_status", "sent_date", "reply_status", "notes"
    ]

    write_csv(send_queue_dir / "send_queue.csv", rows, fieldnames)
    (send_queue_dir / "send_queue.html").write_text(build_html(rows), encoding="utf-8")

    print(f"Created {send_queue_dir / 'send_queue.csv'}")
    print(f"Created {send_queue_dir / 'send_queue.html'}")
    print(f"Created .eml files in {eml_dir}")


if __name__ == "__main__":
    main()
