"""Render the two silent case lessons with Pillow and FFmpeg."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess
import runpy

base = runpy.run_path(str(Path(__file__).with_name("render-walkthrough.py")))
Image, ImageDraw = base["Image"], base["ImageDraw"]
text, wrap, rect, panel = (base[key] for key in ("text", "wrap", "rect", "panel"))
SIZE, MEDIA = base["SIZE"], base["MEDIA"]
INK, WHITE, LIGHT, MINT, GREEN, MUTED, GOLD = (base[key] for key in ("INK", "WHITE", "LIGHT", "MINT", "GREEN", "MUTED", "GOLD"))
FPS, HOLD = 12, 12

LESSONS = {
    "idea-case": ("DEVELOP A RESEARCH IDEA", [
        ("Start with a problem", "What happens to learned equations when conditions change?",
         "Three possible questions", "Recover a formula, detect a bad equation, or identify a change in regime.",
         "Save the candidates and your real constraints. Here: four weeks and a laptop."),
        ("Score and shortlist", "Which option can I test with accessible data and a simple baseline?",
         "Shortlist one question", "Can choosing the next measurement reveal when an equation breaks?",
         "Phase 10 ranks candidates. Gap and novelty scores stay provisional."),
        ("Search for an overlap", "Find papers using equation disagreement to select new experiments.",
         "The mechanism already exists", "Medina and White use a committee of symbolic equations to propose experiments.",
         "Phase 11: open the source and record what the paper actually demonstrates."),
        ("Challenge the contribution", "What would the closest paper make a reviewer reject?",
         "Drop the novelty claim", "The sampling mechanism overlaps. A test under shift could be a different question.",
         "Phases 12 and 13: compare the mechanism and evaluation before deciding."),
        ("Narrow and search again", "Has anyone compared detection of wrong equations under equal budgets?",
         "Keep the benchmark conditional", "Search for the narrower evaluation. Stop if the same comparison already exists.",
         "Save the revised question and the specific reason the earlier version changed."),
        ("Design a pilot that can fail", "Can the pilot beat random sampling at the same measurement budget?",
         "Freeze the comparisons", "Use known equations and held-out shifts. Count measurements to detection and false alarms.",
         "If the simple baseline matches, reconsider the contribution. No pilot has been run here."),
    ]),
    "review-case": ("REVIEW AND REVISE A PAPER", [
        ("Prepare a review packet", "Review this numbered manuscript and identify the claim that matters most.",
         "Save the inputs", "Attach the manuscript, review instructions, and any evidence the central claim depends on.",
         "Ask for evidence locations, the smallest adequate fix, and a closure test."),
        ("Compare claim and evidence", "The abstract says: “The study tool improved quiz performance.”",
         "Check what was measured", "Students reported how prepared they felt. The study collected no quiz scores.",
         "Record issue R1. Students also chose whether to use the tool."),
        ("Request the minimum fix", "What wording does this observational survey support?",
         "Rewrite the claim", "“Tool use was associated with higher self-reported preparation in the surveyed class.”",
         "Set a closure test covering the abstract, results, captions, and conclusion."),
        ("Check the first revision", "The abstract now says “self-reported preparation.”",
         "R1 remains PARTIAL", "The conclusion still says that the tool improves quiz performance.",
         "Record the location that still fails the test, then revise it."),
        ("Verify the second revision", "Check the revised PDF against the original R1 closure test.",
         "R1 can be VERIFIED CLOSED", "The checked sections now report an association, and the Methods explain self-selection.",
         "Save the issue ID, old and new evidence, and the verified status."),
        ("Match evidence to each claim", "A synthetic fixture shows that the reporting code runs.",
         "The scientific result is pending", "Check the actual run outputs before reporting a measured effect or a reproduction.",
         "Keep the evidence status attached to each claim."),
    ]),
}

def draw_lines(draw, x, y, value, width, size, color, gap):
    for i, line in enumerate(wrap(draw, value, width, size)):
        text(draw, x, y + i * gap, line, size, color)

def frame(label, scenes, index):
    number, local = divmod(index, FPS * HOLD)
    title, question, result_title, result, takeaway = scenes[number]
    elapsed = local / FPS
    image = Image.new("RGB", SIZE, LIGHT)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, SIZE[0], 155), fill=INK)
    text(draw, 52, 34, f"{label}  /  {number + 1} OF {len(scenes)}", 19, MINT, True)
    text(draw, 52, 79, title, 45, WHITE, True)
    panel(draw, 52, 189, 480, 279, WHITE)
    text(draw, 76, 216, "QUESTION OR CLAIM", 19, GREEN, True)
    draw_lines(draw, 76, 269, question, 425, 30, INK, 42)
    if elapsed >= 1.4:
        phase = min(1, (elapsed - 1.4) / .5)
        x = 580 + int(20 * (1 - phase) ** 2)
        panel(draw, x, 189, 481, 279, MINT)
        size = 22 if len(result_title) > 29 else 25
        text(draw, x + 23, 218, result_title, size, GREEN, True)
        draw_lines(draw, x + 23, 270, result, 433, 28, INK, 39)
    rect(draw, 52, 506, 1009, 76, "#e5eee0", 10)
    draw_lines(draw, 72, 526, takeaway, 967, 23, MUTED, 27)
    draw.rectangle((0, 622, SIZE[0] * (index + 1) / (FPS * HOLD * len(scenes)), 629), fill=GREEN)
    return image

def render(name, label, scenes):
    frame(label, scenes, 3 * FPS).save(MEDIA / f"{name}-poster.webp", quality=89)
    command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo",
               "-pix_fmt", "rgb24", "-s", f"{SIZE[0]}x{SIZE[1]}", "-r", str(FPS), "-i", "-",
               "-c:v", "libx264", "-threads", "2", "-preset", "fast", "-crf", "22",
               "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(MEDIA / f"{name}.mp4")]
    with subprocess.Popen(command, stdin=subprocess.PIPE) as encoder:
        for index in range(FPS * HOLD * len(scenes)):
            encoder.stdin.write(frame(label, scenes, index).tobytes())
        encoder.stdin.close()
        if encoder.wait():
            raise RuntimeError(f"Could not render {name}")

if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs = [pool.submit(render, name, *lesson) for name, lesson in LESSONS.items()]
        for job in jobs:
            job.result()
