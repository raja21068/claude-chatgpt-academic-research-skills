"""Build the fictional excerpts used in the worked review lesson."""
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

output = Path(__file__).resolve().parents[1] / "dist/demo/review-case-exercise.pdf"
ink = colors.HexColor("#16372b")
heading = ParagraphStyle("heading", fontName="Helvetica-Bold", fontSize=12, leading=16,
                         textColor=ink, spaceBefore=13, spaceAfter=5)
title = ParagraphStyle("title", fontName="Times-Bold", fontSize=26, leading=30, textColor=ink)
body = ParagraphStyle("body", fontName="Helvetica", fontSize=11, leading=16)
versions = [
    ("Original draft", "The study tool improved quiz performance.", "The tool improves quiz performance."),
    ("First revision", "Tool use was associated with higher self-reported preparation.", "The tool improves quiz performance."),
    ("Second revision", "Tool use was associated with higher self-reported preparation.",
     "In the surveyed class, tool use was associated with higher self-reported preparation. Self-selection and the absence of quiz scores limit the interpretation."),
]
methods = "Students reported whether they felt better prepared. Quiz scores were not collected. Students chose whether to use the tool."
result = "Students who used the tool more often reported feeling prepared. This exercise supplies no group sizes or uncertainty estimates."
pages = []
for index, (version, abstract, conclusion) in enumerate(versions):
    if index:
        pages.append(PageBreak())
    pages.extend([
        Paragraph("WORKED REVIEW CASE · FICTIONAL EXCERPTS", heading),
        Paragraph(version, title),
        Spacer(1, 12),
        Paragraph("Compare each version against issue R1 from the worked lesson. These excerpts are fictional. They contain no empirical estimates.", body),
    ])
    for label, passage in (("Abstract", abstract), ("Methods", methods), ("Results", result),
                           ("Figure 1 caption", "Self-reported preparation by tool-use group."),
                           ("Conclusion", conclusion)):
        pages.extend((Paragraph(label, heading), Paragraph(passage, body)))
SimpleDocTemplate(str(output), title="Worked review case: original draft and two revisions").build(pages)
