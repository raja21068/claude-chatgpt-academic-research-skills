// Video covers: only a local cover picture is loaded. YouTube (nocookie) is contacted when you press play.
(function () {
  document.querySelectorAll(".hv-play").forEach((btn) => {
    btn.addEventListener("click", () => {
      const id = btn.dataset.video || "vhvtOVsnYLg";
      const start = btn.dataset.start || "0";
      const frame = document.createElement("iframe");
      frame.className = "hv-frame";
      frame.src = "https://www.youtube-nocookie.com/embed/" + encodeURIComponent(id) + "?start=" + encodeURIComponent(start) + "&autoplay=1&rel=0";
      frame.title = btn.dataset.title || "Video";
      frame.allow = "autoplay; encrypted-media; picture-in-picture; fullscreen";
      frame.allowFullscreen = true;
      frame.referrerPolicy = "strict-origin-when-cross-origin";
      btn.replaceWith(frame);
      frame.focus();
    });
  });
})();
