const walkthrough = document.getElementById("walkthrough-video");
for (const chapter of document.querySelectorAll("[data-time]")) {
  chapter.addEventListener("click", async () => {
    walkthrough.currentTime = Number(chapter.dataset.time);
    try {
      await walkthrough.play();
    } catch {
      walkthrough.focus();
    }
  });
}

document.getElementById("copy-demo").addEventListener("click", async () => {
  const message = document.getElementById("demo-message");
  const status = document.getElementById("demo-status");
  try {
    await navigator.clipboard.writeText(message.value);
    status.textContent = "Chat message copied.";
  } catch {
    message.focus();
    message.select();
    status.textContent = "Chat message selected. Use your device’s copy command.";
  }
});
