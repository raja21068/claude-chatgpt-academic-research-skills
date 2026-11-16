// Home page: show a real rendering of the sample answer so visitors see what they get.
(async function () {
  const box = document.getElementById("sample-view");
  if (!box) return;
  try {
    const r = await fetch("demo/sample-idea-review.md");
    if (!r.ok) throw new Error();
    box.innerHTML = window.visualizeAnswer(await r.text(), {compact: true});
  } catch {
    box.innerHTML = '<p class="sample-loading">Could not load the sample here. <a href="demo/sample-idea-review.md">Open it directly</a>.</p>';
  }
})();
