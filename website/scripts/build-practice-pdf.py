from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

output = Path(__file__).resolve().parents[1] / "dist/demo/practice-manuscript.pdf"
ink = colors.HexColor("#17382c")
title = ParagraphStyle("Title", fontName="Times-Bold", fontSize=28, leading=32, textColor=ink)
body = ParagraphStyle("Body", fontName="Helvetica", fontSize=11, leading=17, alignment=TA_LEFT)
heading = ParagraphStyle("Heading", parent=body, fontName="Helvetica-Bold", textColor=ink, spaceBefore=14, spaceAfter=4)
content = [
    Paragraph("TEACHING EXERCISE · FICTIONAL MANUSCRIPT", heading),
    Paragraph("Does a reading reminder improve quiz scores?", title),
    Spacer(1, 0.16 * inch),
    Paragraph("All descriptions in this one-page example are fictional and supplied for a manuscript-review exercise.", body),
]
sections = [
    ("Research question", "We ask whether a weekly reading reminder improves performance on a course quiz."),
    ("Methods", "In one course section, students chose whether to receive a weekly reminder. At the end of the term, we compared quiz scores between students who opted in and those who did not. We collected no baseline quiz scores. The analysis plan did not specify how to handle missing quiz scores."),
    ("Results", "The reminder group had a higher mean quiz score among students who completed the quiz. The draft does not report group sizes, missing scores, the size of the difference, or an uncertainty interval."),
    ("Conclusion", "The weekly reminder caused the improvement in quiz scores and should be adopted in every first-year course."),
]
for name, description in sections:
    content.extend((Paragraph(name, heading), Paragraph(description, body)))
SimpleDocTemplate(str(output), title="Practice manuscript for peer review", author="Student Research Workflow").build(content)
