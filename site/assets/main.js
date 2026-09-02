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

  /* ---- the download card, filled in from the newest release ----
     The markup already links releases/latest/download/<fixed name>, which is
     all a visitor needs. This only adds what the static page cannot know --
     the version and the size -- and, should that fixed name ever be missing
     from the newest release, points the button at whatever Windows asset the
     release does carry instead of leaving a dead link. Every step is optional:
     any failure leaves the markup exactly as served. */
  var card = document.querySelector("[data-release]");
  if (card && window.fetch) fillIn(card);

  function fillIn(card) {
    var link = card.querySelector("[data-release-link]");
    var fallbackName = link ? link.href.split("/").pop() : "";

    fetch("https://api.github.com/repos/aquaxs1/Explorer-Manager/releases/latest", {
      headers: { Accept: "application/vnd.github+json" }
    }).then(function (res) {
      if (!res.ok) throw new Error("release lookup failed: " + res.status);
      return res.json();
    }).then(function (release) {
      var assets = release.assets || [];
      var asset = pick(assets, fallbackName);
      if (!asset) return;

      if (link) link.href = asset.browser_download_url;

      var name = card.querySelector("[data-release-name]");
      if (name) name.textContent = asset.name;

      var meta = card.querySelector("[data-release-meta]");
      if (meta) meta.textContent = describe(release, asset);

      var sha = document.querySelector("[data-release-sha]");
      var digest = byName(assets, asset.name + ".sha256");
      if (sha && digest) sha.href = digest.browser_download_url;
    }).catch(function () { /* the static link stands on its own */ });
  }

  /* the published archive first, then any other Windows build */
  function pick(assets, wanted) {
    return byName(assets, wanted) || matching(assets, ".zip") || matching(assets, ".exe");
  }

  function byName(assets, wanted) {
    return assets.filter(function (a) { return a.name === wanted; })[0];
  }

  function matching(assets, suffix) {
    return assets.filter(function (a) {
      return a.name.slice(-suffix.length).toLowerCase() === suffix;
    })[0];
  }

  function describe(release, asset) {
    var parts = [];
    var version = (release.tag_name || "").replace(/^v/, "");
    if (version) parts.push("Version " + version);
    if (asset.size) parts.push((asset.size / 1048576).toFixed(1) + " MB");
    parts.push("Windows 10 / 11 · 64-bit");
    return parts.join(" · ");
  }

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
