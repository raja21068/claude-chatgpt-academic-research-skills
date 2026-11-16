// First-screen video: only a local cover picture is loaded. YouTube is contacted when you press play.
(function () {
  const btn = document.querySelector(".hv-play");
  if (!btn) return;
  btn.addEventListener("click", () => {
    const frame = document.createElement("iframe");
    frame.className = "hv-frame";
    frame.src = "https://www.youtube-nocookie.com/embed/vhvtOVsnYLg?start=120&autoplay=1&rel=0";
    frame.title = "How to Create a Full Research Paper with Claude Skills";
    frame.allow = "autoplay; encrypted-media; picture-in-picture; fullscreen";
    frame.allowFullscreen = true;
    frame.referrerPolicy = "strict-origin-when-cross-origin";
    btn.replaceWith(frame);
    frame.focus();
  });
})();
