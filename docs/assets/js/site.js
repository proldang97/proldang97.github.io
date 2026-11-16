// P-Recetas: cookie consent, GA4 and custom events.
// GA4 only loads after the visitor accepts cookies. Until a real Measurement ID
// is set in config.json, events are printed to the browser console instead.
(function () {
  var PC = window.PC || {};
  // Add ?debug to any page address to see its events live in GA4's DebugView.
  PC.debug = /[?&]debug\b/.test(location.search);
  var GA_READY_ID = /^G-[A-Z0-9]+$/.test(PC.gaId || "") && PC.gaId !== "G-XXXXXXXXXX";
  var CONSENT_KEY = "pc_consent";
  var LANG_KEY = "pc_lang";

  function store(key, value) {
    try {
      if (value === undefined) return localStorage.getItem(key);
      localStorage.setItem(key, value);
    } catch (e) { return null; }
  }

  // --- GA4 -----------------------------------------------------------------
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = gtag;
  gtag("consent", "default", { analytics_storage: "denied", ad_storage: "denied", ad_user_data: "denied", ad_personalization: "denied" });

  var gaLoaded = false;
  function loadGA() {
    if (gaLoaded || !GA_READY_ID) return;
    gaLoaded = true;
    gtag("consent", "update", { analytics_storage: "granted" });
    var s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(PC.gaId);
    document.head.appendChild(s);
    gtag("js", new Date());
    var settings = { site_language: PC.lang, content_group: PC.page };
    if (PC.debug) settings.debug_mode = true;
    gtag("config", PC.gaId, settings);
  }

  function track(name, params) {
    params = Object.assign({ site_language: PC.lang }, params || {});
    if (gaLoaded) gtag("event", name, params);
    if (!GA_READY_ID || PC.debug) console.info("[GA4 event]", name, params);
  }
  window.pcTrack = track;

  // --- Cookie banner -------------------------------------------------------
  var banner = document.getElementById("consent");
  function setConsent(value) {
    store(CONSENT_KEY, value);
    if (banner) banner.hidden = true;
    if (value === "granted") loadGA();
  }
  if (banner) {
    var saved = store(CONSENT_KEY);
    if (saved === "granted") loadGA();
    else if (saved !== "denied") banner.hidden = false;
    document.getElementById("consent-accept").addEventListener("click", function () { setConsent("granted"); });
    document.getElementById("consent-reject").addEventListener("click", function () { setConsent("denied"); });
  }
  var settings = document.getElementById("cookie-settings");
  if (settings && banner) settings.addEventListener("click", function () { banner.hidden = false; });

  // --- Remember language ---------------------------------------------------
  store(LANG_KEY, PC.lang);

  // --- Click tracking via data attributes ----------------------------------
  document.addEventListener("click", function (e) {
    var el = e.target.closest("[data-track]");
    if (!el) return;
    var name = el.getAttribute("data-track");
    var params = {};
    Array.prototype.forEach.call(el.attributes, function (a) {
      if (a.name.indexOf("data-p-") === 0) params[a.name.slice(7).replace(/-/g, "_")] = a.value;
    });
    if (name === "language_switch") store(LANG_KEY, params.to_language);
    track(name, params);
  });

  // --- Recipe page buttons -------------------------------------------------
  var copyBtn = document.getElementById("copy-ingredients");
  if (copyBtn) {
    copyBtn.addEventListener("click", function () {
      var title = document.querySelector("h1").textContent.trim();
      var lines = Array.prototype.map.call(document.querySelectorAll(".ingredients .item"), function (el) {
        return "- " + el.textContent.trim();
      });
      var text = title + "\n" + lines.join("\n");
      var label = copyBtn.textContent;
      function done() {
        copyBtn.textContent = copyBtn.getAttribute("data-done");
        setTimeout(function () { copyBtn.textContent = label; }, 1800);
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, function () { selectList(); });
      } else { selectList(); }
      track("copy_ingredients", { recipe_name: PC.recipe });
    });
  }
  function selectList() {
    var list = document.querySelector(".ingredients");
    var range = document.createRange();
    range.selectNodeContents(list);
    var sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(range);
  }

  var printBtn = document.getElementById("print-recipe");
  if (printBtn) {
    printBtn.addEventListener("click", function () {
      track("print_recipe", { recipe_name: PC.recipe });
      window.print();
    });
  }

  // Ticking ingredients shows how people use the page while cooking.
  var ticked = false;
  document.addEventListener("change", function (e) {
    if (!ticked && e.target.matches(".ingredients input")) {
      ticked = true;
      track("ingredient_check", { recipe_name: PC.recipe });
    }
  });
})();
