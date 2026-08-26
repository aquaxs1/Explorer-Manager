/* Explorer Manager — site behaviour: copy buttons, scroll reveal */
(function () {
  "use strict";

  /* ---- copy to clipboard ---- */
  document.querySelectorAll("[data-copy]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var code = btn.closest(".term__body").querySelector("code").cloneNode(true);
      code.querySelectorAll(".prompt").forEach(function (p) { p.remove(); });
      var text = code.textContent.trim();

      var done = function () {
        var label = btn.querySelector("span");
        var old = label.textContent;
        label.textContent = "Copied";
        btn.classList.add("is-done");
        setTimeout(function () {
          label.textContent = old;
          btn.classList.remove("is-done");
        }, 1800);
      };

      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(done, fallback);
      } else {
        fallback();
      }

      function fallback() {
        var ta = document.createElement("textarea");
        ta.value = text;
        ta.setAttribute("readonly", "");
        ta.style.position = "fixed";
        ta.style.opacity = "0";
        document.body.appendChild(ta);
        ta.select();
        try { document.execCommand("copy"); done(); } catch (e) { /* nothing to do */ }
        document.body.removeChild(ta);
      }
    });
  });

  /* ---- scroll reveal ---- */
  var items = document.querySelectorAll(".reveal");
  if (!("IntersectionObserver" in window)) {
    items.forEach(function (el) { el.classList.add("is-in"); });
    return;
  }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      entry.target.classList.add("is-in");
      io.unobserve(entry.target);
    });
  }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });

  items.forEach(function (el, i) {
    el.style.transitionDelay = (i % 3) * 70 + "ms";
    io.observe(el);
  });
})();
