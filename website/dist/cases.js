for (const button of document.querySelectorAll(".copy-case")) {
  button.addEventListener("click", async () => {
    const prompt = button.closest(".prompt-copy").querySelector("pre");
    try {
      await navigator.clipboard.writeText(prompt.textContent);
      button.textContent = "Copied";
    } catch {
      const selection = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(prompt);
      selection.removeAllRanges();
      selection.addRange(range);
      button.textContent = "Selected · use your copy command";
    }
  });
}

for (const exercise of document.querySelectorAll("[data-exercise]")) {
  const buttons = exercise.querySelectorAll("button");
  const output = exercise.querySelector(".exercise-feedback");
  for (const button of buttons) {
    button.setAttribute("aria-pressed", "false");
    button.addEventListener("click", () => {
      for (const option of buttons) option.setAttribute("aria-pressed", String(option === button));
      output.textContent = button.dataset.feedback;
    });
  }
}

for (const chapter of document.querySelectorAll("[data-case-time]")) {
  chapter.addEventListener("click", async () => {
    const video = chapter.closest(".case").querySelector("video");
    video.currentTime = Number(chapter.dataset.caseTime);
    try {
      await video.play();
    } catch {
      video.focus();
    }
  });
}
