"""Render the silent student walkthrough. Requires Pillow, FFmpeg, and DejaVu fonts."""
from functools import lru_cache
from pathlib import Path
import subprocess
from PIL import Image, ImageDraw, ImageFont

SIZE = (1120, 630)
FPS = 18
BEAT = 6
ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / "dist/media"
INK = "#16372b"
LIGHT = "#f7f8ef"
MUTED = "#42594b"
GREEN = "#265945"
MINT = "#dcebcf"
WHITE = "#fffefa"
GOLD = "#f1dfa0"
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")

@lru_cache(maxsize=None)
def font(size, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(str(FONT_DIR / name), size)

def text(draw, x, y, value, size=25, fill=INK, bold=False):
    draw.text((x, y), value, font=font(size, bold), fill=fill, anchor="lt")

def rect(draw, x, y, w, h, fill, radius=16, outline=None):
    draw.rounded_rectangle((x, y, x+w, y+h), radius, fill=fill, outline=outline, width=2)

def panel(draw, x, y, w, h, color=WHITE):
    rect(draw, x+9, y+10, w, h, "#c3d8c8")
    rect(draw, x, y, w, h, color, outline="#bad1bf")

def arrow(draw, x, y, width):
    draw.line((x, y, x+width, y), fill=GREEN, width=6)
    draw.line((x+width-12, y-10, x+width, y, x+width-12, y+10), fill=GREEN, width=6, joint="curve")

def wrap(draw, value, max_width, size):
    lines, line = [], ""
    for word in value.split():
        candidate = (line + " " + word).strip()
        if line and draw.textlength(candidate, font=font(size)) > max_width:
            lines.append(line)
            line = word
        else:
            line = candidate
    return [*lines, line]

SCENES = [
    ("Build a structured prompt", "Give the chat tool the task, evidence, and format it needs."),
    ("Prepare your three review files", "Download the practice kit below this video and try it yourself."),
    ("Attach, paste, and send", "Open a new chat. In ChatGPT, choose Temporary and then Unpersonalized for this exercise."),
    ("Check the review before you revise", "Open the cited passage. Check the criticism, make the fix, and test whether it resolves the issue."),
]

def frame(index):
    step = index // (FPS * BEAT)
    t = (index % (FPS * BEAT)) / FPS
    motion = 1 - (1 - min(1, t / .65)) ** 3
    image = Image.new("RGB", SIZE, LIGHT)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 1120, 167), fill=INK)
    text(draw, 57, 40, "RESEARCH WORKFLOW   /   " + str(step+1) + " OF 4", 18, MINT, True)
    text(draw, 57, 84, SCENES[step][0], 44, WHITE, True)
    if step == 0:
        for row, (label, value) in enumerate([
            ("Goal", "Check whether the conclusion is supported."),
            ("Skill", "Use the attached review instructions."),
            ("Task", "Review the study design and interpretation."),
            ("Background", "The attached manuscript is a teaching example."),
            ("Output", "Return a Markdown report with evidence anchors."),
        ]):
            y = 196 + row * 61
            rect(draw, 58, y, 727, 49, WHITE, outline="#cbdbca")
            text(draw, 76, y+11, label, 22, GREEN, True)
            text(draw, 245, y+12, value, 21)
        arrow(draw, 807, 338, 49)
        x = 875+int(35*(1-motion))
        panel(draw, x, 267, 171, 145, MINT)
        text(draw, x+20, 303, "Your", 26, INK, True)
        text(draw, x+20, 342, "prompt", 26, INK, True)
    elif step == 1:
        files = [
            ("TXT", "referee-prompt.txt", "The question and the", "report you want."),
            ("TXT", "referee-instructions.txt", "The review workflow", "for this exercise."),
            ("PDF", "practice-manuscript.pdf", "A fictional paper", "to review."),
        ]
        for i, (ext, name, line1, line2) in enumerate(files):
            x = 60 + i * 342
            p = 1 - (1 - min(1, max(0, t-i*.12)/.55)) ** 3
            y = 242 + int(26 * (1-p))
            panel(draw, x, y, 312, 188, [MINT, WHITE, "#fbefcb"][i])
            text(draw, x+20, y+19, ext, 18, GREEN, True)
            text(draw, x+20, y+57, name, 19, INK, True)
            text(draw, x+20, y+108, line1, 21, MUTED)
            text(draw, x+20, y+139, line2, 21, MUTED)
    elif step == 2:
        panel(draw, 110, 203, 900, 307)
        text(draw, 140, 227, "ChatGPT", 29, INK, True)
        text(draw, 845, 235, "Illustration", 18, MUTED)
        for i, (word, start, width) in enumerate([("Temporary", 338, 170), ("Unpersonalized", 523, 230)]):
            rect(draw, start, 223, width, 41, MINT if t > .4 + i*.4 else LIGHT)
            text(draw, start+12, 233, word, 19, INK, True)
        rect(draw, 139, 281, 842, 201, LIGHT, outline="#cbdacb")
        labels = ["referee-prompt.txt", "referee-instructions.txt", "practice-manuscript.pdf"]
        for i, name in enumerate(labels):
            if t < .7+i*.31:
                continue
            x = 160+i*250
            rect(draw, x, 301, 237, 38, MINT, 9)
            text(draw, x+9, 312, name, 17, INK, True)
        if t > 1.9:
            text(draw, 162, 367, "Read the attached prompt and instructions.", 25, INK)
            text(draw, 162, 410, "Review the manuscript and ground each concern in the text.", 22, INK)
        if t > 2.65:
            rect(draw, 870, 430, 90, 39, GREEN, 10)
            text(draw, 889, 439, "Send", 20, WHITE, True)
    else:
        panel(draw, 74, 219+int(17*(1-motion)), 972, 280)
        rect(draw, 100, 242, 381, 37, GOLD, 10)
        text(draw, 113, 251, "Major concern · teaching example", 19, INK, True)
        for i, (label, value) in enumerate([
            ("Evidence", "Page 1, Methods · Students chose whether to receive reminders."),
            ("Concern", "Self-selection weakens the causal claim."),
            ("Fix", "Report the observed association and state the limitation."),
            ("Closure test", "Check that the conclusion matches the design."),
        ]):
            if t < .3 + i*.44:
                continue
            y = 306 + i*43
            text(draw, 104, y, label, 22, GREEN, True)
            text(draw, 270, y+1, value, 21)
    draw.rectangle((0, 539, 1120, 630), fill="#e4eee0")
    for i, line in enumerate(wrap(draw, SCENES[step][1], 1005, 24)):
        text(draw, 57, 557+i*30, line, 24)
    return image

def main():
    MEDIA.mkdir(parents=True, exist_ok=True)
    frame(FPS*2).save(MEDIA/"walkthrough-poster.webp", quality=88)
    command = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo",
        "-pix_fmt", "rgb24", "-s", f"{SIZE[0]}x{SIZE[1]}", "-r", str(FPS), "-i", "-",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-crf", "20",
        "-movflags", "+faststart", str(MEDIA/"research-walkthrough.mp4"),
    ]
    with subprocess.Popen(command, stdin=subprocess.PIPE) as ffmpeg:
        for index in range(FPS*BEAT*len(SCENES)):
            ffmpeg.stdin.write(frame(index).tobytes())
        ffmpeg.stdin.close()
        if ffmpeg.wait():
            raise RuntimeError("FFmpeg could not encode the walkthrough")

if __name__ == "__main__":
    main()
