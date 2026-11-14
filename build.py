#!/usr/bin/env python3
"""Builds the Pablo Cocina website.

Edit src/config.json (site name, GA4 ID, links, texts) or add a recipe file in
src/recipes/, then run:  python3 build.py
The finished website is written to the docs/ folder, ready for GitHub Pages.
"""
import json
import shutil
from html import escape
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
OUT = ROOT / "docs"
LANGS = ["es", "en"]

config = json.loads((SRC / "config.json").read_text(encoding="utf-8"))
recipes = sorted(
    (json.loads(p.read_text(encoding="utf-8")) for p in (SRC / "recipes").glob("*.json")),
    key=lambda r: (r.get("order", 999), r["slug"]),
)
about = json.loads((SRC / "about.json").read_text(encoding="utf-8"))
work = json.loads((SRC / "work.json").read_text(encoding="utf-8"))
NAME = config["site_name"]
BASE = config["site_url"].rstrip("/")


# The logo: a round stamp with an italic "P" and a small chili. Also saved as the favicon.
LOGO = (
    '<svg class="logo" viewBox="0 0 48 48" aria-hidden="true">'
    '<circle cx="24" cy="24" r="23" fill="var(--accent)"/>'
    '<text x="21.5" y="34" text-anchor="middle" font-family="Fraunces, Georgia, serif" font-style="italic" '
    'font-weight="600" font-size="30" fill="var(--on-accent)">P</text>'
    '<path d="M33 13.5c2.6.4 4 2.6 3.4 5.6-.6 3-2.6 5.8-5.2 7.4.9-2.6 1.4-5 1.2-7.4-.1-2-.6-3.8.6-5.6z" fill="var(--on-accent)"/>'
    '<path d="M33.2 13.6c.2-1.4 1-2.4 2.3-2.9" stroke="var(--on-accent)" stroke-width="1.4" fill="none" stroke-linecap="round"/>'
    "</svg>"
)


def T(lang, key):
    return config["text"][lang][key]


def other(lang):
    return "en" if lang == "es" else "es"


def home_path(lang):
    return f"{lang}/index.html"


def recipe_path(lang, slug):
    return f"{lang}/{T(lang, 'recipes_dir')}/{slug}.html"


def about_path(lang):
    return f"{lang}/{about[lang]['path']}.html"


def work_path(lang):
    return f"{lang}/{work[lang]['path']}.html"


def social_links(location):
    return "".join(
        f'<a href="{escape(s["url"])}" target="_blank" rel="noopener" data-track="social_click" '
        f'data-p-platform="{s["id"]}" data-p-location="{location}">{escape(s["label"])}</a>'
        for s in config["socials"]
    )


def photo_html(lang, rel, rec, title, cls_attrs=''):
    """The recipe photo, or a placeholder while the photo is missing."""
    if rec.get("image"):
        return f'<img src="{rel}assets/img/{rec["image"]}" alt="{escape(title)}"{cls_attrs}>'
    return f'<div class="photo-soon" role="img" aria-label="{escape(title)}"><span>{escape(T(lang, "photo_soon"))}</span></div>'


def page(lang, rel, title, description, body, page_type, alternates, recipe_name="", extra_head=""):
    """Wraps a page body in the shared layout. `rel` is the path back to the site root."""
    pc = json.dumps({"gaId": config["ga_id"], "lang": lang, "page": page_type, "recipe": recipe_name})
    alt_links = "\n".join(
        f'<link rel="alternate" hreflang="{l}" href="{BASE}/{p}">' for l, p in alternates.items()
    )
    other_lang = other(lang)
    socials = "".join(
        f'<a href="{escape(s["url"])}" target="_blank" rel="noopener" data-track="social_click" '
        f'data-p-platform="{s["id"]}" data-p-location="footer">{escape(s["label"])}</a> · '
        for s in config["socials"]
    ).rstrip(" · ")
    return f"""<!doctype html>
<html lang="{T(lang, 'html_lang')}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{escape(title)}</title>
<meta name="description" content="{escape(description)}">
<link rel="canonical" href="{BASE}/{alternates[lang]}">
{alt_links}
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(description)}">
<meta property="og:site_name" content="{escape(NAME)}">
<link rel="icon" href="{rel}assets/img/logo.svg" type="image/svg+xml">
<link rel="preload" href="{rel}assets/fonts/fraunces-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{rel}assets/css/style.css">
<script>window.PC = {pc};</script>
{extra_head}
</head>
<body>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="{rel}{home_path(lang)}">{LOGO}<span>{escape(NAME)}</span></a>
    <nav class="site-nav">
    <a class="nav-link{' active' if page_type == 'about' else ''}" href="{rel}{about_path(lang)}">{escape(about[lang]['nav'])}</a>
    <a class="nav-link{' active' if page_type == 'work' else ''}" href="{rel}{work_path(lang)}">{escape(work[lang]['nav'])}</a>
    <a class="lang-switch" href="{rel}{alternates[other_lang]}" hreflang="{other_lang}" lang="{other_lang}"
       aria-label="{escape(T(lang, 'switch_label'))}" data-track="language_switch"
       data-p-from-language="{lang}" data-p-to-language="{other_lang}">{T(lang, 'switch_short')}</a>
    </nav>
  </div>
</header>
<main>
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <span>© 2026 {escape(NAME)} · {socials}</span>
    <button type="button" class="linklike" id="cookie-settings">{escape(T(lang, 'cookie_settings'))}</button>
  </div>
</footer>
<div class="consent" id="consent" role="dialog" aria-live="polite" hidden>
  <div class="wrap">
    <p>{escape(T(lang, 'cookies_text'))}</p>
    <div class="row">
      <button type="button" id="consent-reject">{escape(T(lang, 'reject'))}</button>
      <button type="button" id="consent-accept">{escape(T(lang, 'accept'))}</button>
    </div>
  </div>
</div>
<script src="{rel}assets/js/site.js"></script>
</body>
</html>
"""


def build_home(lang):
    rel = "../"
    feat = next((r for r in recipes if r.get("image")), None)
    social_links = "".join(
        f'<a href="{escape(s["url"])}" target="_blank" rel="noopener" data-track="social_click" '
        f'data-p-platform="{s["id"]}" data-p-location="hero">{escape(s["label"])}</a>'
        for s in config["socials"]
    )
    photo = ""
    if feat:
        r = feat[lang]
        photo = (
            f'<a class="hero-photo" href="{T(lang, "recipes_dir")}/{feat["slug"]}.html" '
            f'data-track="select_recipe" data-p-recipe-name="{feat["slug"]}" data-p-location="hero">'
            f'<img src="{rel}assets/img/{feat["image"]}" alt="{escape(r["title"])}" width="680" height="1400">'
            f'<span class="tag">{escape(r["title"])} →</span></a>'
        )
    cards = []
    for rec in recipes:
        r = rec[lang]
        cards.append(
            f'<a class="card" href="{T(lang, "recipes_dir")}/{rec["slug"]}.html" data-track="select_recipe" '
            f'data-p-recipe-name="{rec["slug"]}" data-p-location="grid">'
            + photo_html(lang, rel, rec, r["title"], ' loading="lazy"')
            + f'<div class="card-body"><h3>{escape(r["title"])}</h3><p>{escape(r["summary"])}</p>'
            f'<span class="more">{escape(T(lang, "view_recipe"))} →</span></div></a>'
        )
    for soon in config["coming_soon"][lang]:
        cards.append(
            f'<div class="card soon"><div class="placeholder">{escape(T(lang, "coming_soon"))}</div>'
            f'<div class="card-body"><h3>{escape(soon)}</h3></div></div>'
        )
    body = f"""<section class="hero">
  <div class="wrap">
    <div class="hero-text">
      <span class="eyebrow">{escape(T(lang, 'eyebrow'))}</span>
      <h1>{escape(T(lang, 'tagline'))}</h1>
      <p>{escape(T(lang, 'intro'))}</p>
      <div class="socials" aria-label="{escape(T(lang, 'follow'))}">{social_links}</div>
    </div>
    {photo}
  </div>
</section>
<section class="recipes" id="recetas">
  <div class="wrap">
    <h2>{escape(T(lang, 'recipes'))}</h2>
    <div class="grid">{''.join(cards)}</div>
  </div>
</section>"""
    alternates = {l: home_path(l) for l in LANGS}
    title = f"{NAME} · {T(lang, 'tagline')}"
    return page(lang, rel, title, T(lang, "intro"), body, "home", alternates)


def build_recipe(lang, rec):
    rel = "../../"
    r = rec[lang]
    items = []
    for i, ing in enumerate(r["ingredients"]):
        note = f'<span class="note">{escape(ing["note"])}</span>' if ing.get("note") else ""
        items.append(
            f'<li><label><input type="checkbox" id="ing-{i}"><span><span class="item">{escape(ing["item"])}</span>{note}</span></label></li>'
        )
    steps = "".join(f"<li><span>{escape(s)}</span></li>" for s in r["steps"])
    video = rec.get("video")
    video_btn = ""
    if video:
        video_btn = (
            f'<a class="btn primary" href="{escape(video["url"])}" target="_blank" rel="noopener" '
            f'data-track="watch_video_click" data-p-recipe-name="{rec["slug"]}" '
            f'data-p-platform="{video["platform"].lower()}">{escape(T(lang, "watch"))} ({escape(video["platform"])})</a>'
        )
    body = f"""<div class="wrap recipe-head">
  <a class="back" href="../index.html#recetas">← {escape(T(lang, 'back'))}</a>
</div>
<div class="wrap recipe-layout">
  <div class="recipe-photo">{photo_html(lang, rel, rec, r['title'], ' width="680" height="1400"')}</div>
  <article class="recipe-main">
    <div class="recipe-intro">
      <h1>{escape(r['title'])}</h1>
      <p class="summary">{escape(r['summary'])}</p>
      <div class="actions">
        {video_btn}
        <button type="button" class="btn" id="copy-ingredients" data-done="{escape(T(lang, 'copied'))} ✓">{escape(T(lang, 'copy'))}</button>
        <button type="button" class="btn" id="print-recipe">{escape(T(lang, 'print'))}</button>
      </div>
    </div>
    <section class="panel">
      <h2>{escape(T(lang, 'ingredients'))} <small>{escape(T(lang, 'tick_hint'))}</small></h2>
      <ul class="ingredients">{''.join(items)}</ul>
    </section>
    <section class="panel">
      <h2>{escape(T(lang, 'steps'))}</h2>
      <ol class="steps">{steps}</ol>
    </section>
  </article>
</div>"""
    alternates = {l: recipe_path(l, rec["slug"]) for l in LANGS}
    schema = {
        "@context": "https://schema.org",
        "@type": "Recipe",
        "name": r["title"],
        "description": r["summary"],
        "author": {"@type": "Person", "name": config["author"]},
        "recipeCuisine": rec.get("cuisine", ""),
        "inLanguage": lang,
        "recipeIngredient": [i["item"] for i in r["ingredients"]],
        "recipeInstructions": [{"@type": "HowToStep", "text": s} for s in r["steps"]],
    }
    if rec.get("image"):
        schema["image"] = [f"{BASE}/assets/img/{rec['image']}"]
    head = f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>'
    title = f"{r['title']} · {NAME}"
    return page(lang, rel, title, r["summary"], body, "recipe", alternates, rec["slug"], head)


def build_about(lang):
    rel = "../"
    a = about[lang]
    blocks = []
    for p in a["paragraphs"]:
        if p == "[socials]":
            blocks.append(f'<div class="socials">{social_links("about")}</div>')
        else:
            blocks.append(f"<p>{escape(p)}</p>")
    body = f"""<div class="wrap about-layout">
  <div class="about-photo"><img src="{rel}assets/img/{about['photo']}" alt="Pablo Roldán Gómez" width="933" height="1400"></div>
  <article class="about-main">
    <span class="eyebrow">{escape(a['title'])}</span>
    <h1>{escape(a['lead'])}</h1>
    <div class="about-text">{''.join(blocks)}</div>
    <p class="closing">{escape(a['closing'])}</p>
    <a class="btn primary" href="index.html#recetas" data-track="select_recipe_list" data-p-location="about">{escape(a['cta'])} →</a>
  </article>
</div>"""
    alternates = {l: about_path(l) for l in LANGS}
    return page(lang, rel, f"{a['title']} · {NAME}", a["description"], body, "about", alternates,
                extra_head=f'<meta property="og:image" content="{BASE}/assets/img/{about["photo"]}">')


def build_work(lang):
    rel = "../"
    w = work[lang]
    contact = (
        f'<a class="btn primary" href="{escape(work["contact_url"])}" target="_blank" rel="noopener" '
        f'data-track="contact_click" data-p-platform="instagram" data-p-location="{{loc}}">{escape(w["cta"])} →</a>'
    )
    stats = ""
    if work["stats"]:
        items = "".join(
            f'<li><strong>{escape(st["value"])}</strong><span>{escape(st["label"][lang])}</span></li>'
            for st in work["stats"]
        )
        stats = f'<section class="work-section"><h2>{escape(w["stats_title"])}</h2><ul class="stats">{items}</ul></section>'
    services = "".join(
        f'<li><span class="icon" aria-hidden="true">{sv["icon"]}</span><h3>{escape(sv["title"])}</h3><p>{escape(sv["text"])}</p></li>'
        for sv in w["services"]
    )
    shots = "".join(
        f'<a href="{escape(rec["video"]["url"])}" target="_blank" rel="noopener" data-track="watch_video_click" '
        f'data-p-recipe-name="{rec["slug"]}" data-p-platform="{rec["video"]["platform"].lower()}" data-p-location="work">'
        f'<img src="{rel}assets/img/{rec["image"]}" alt="{escape(rec[lang]["title"])}" loading="lazy">'
        f'<span>{escape(rec[lang]["title"])} ▶</span></a>'
        for rec in recipes if rec.get("image") and rec.get("video")
    )
    body = f"""<div class="wrap work">
  <section class="work-hero">
    <span class="eyebrow">{escape(w['title'])}</span>
    <h1>{escape(w['lead'])}</h1>
    <p>{escape(w['intro'])}</p>
    {contact.format(loc="top")}
  </section>
  {stats}
  <section class="work-section">
    <h2>{escape(w['services_title'])}</h2>
    <ul class="services">{services}</ul>
  </section>
  <section class="work-section">
    <h2>{escape(w['work_title'])}</h2>
    <div class="shots">{shots}</div>
  </section>
  <section class="work-cta">
    <h2>{escape(w['cta_title'])}</h2>
    <p>{escape(w['cta_text'])}</p>
    {contact.format(loc="bottom")}
  </section>
</div>"""
    alternates = {l: work_path(l) for l in LANGS}
    return page(lang, rel, f"{w['title']} · {NAME}", w["description"], body, "work", alternates,
                extra_head=f'<meta property="og:image" content="{BASE}/assets/img/{about["photo"]}">')


ROOT_INDEX = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{name}</title>
<link rel="alternate" hreflang="es" href="{base}/es/index.html">
<link rel="alternate" hreflang="en" href="{base}/en/index.html">
<link rel="alternate" hreflang="x-default" href="{base}/es/index.html">
<script>
  var lang = null;
  try {{ lang = localStorage.getItem("pc_lang"); }} catch (e) {{}}
  if (lang !== "es" && lang !== "en") {{
    lang = (navigator.language || "es").toLowerCase().indexOf("es") === 0 ? "es" : "en";
  }}
  location.replace(lang + "/index.html" + location.search);
</script>
</head>
<body>
<p><a href="es/index.html">Español</a> · <a href="en/index.html">English</a></p>
</body>
</html>
"""


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(SRC / "assets", OUT / "assets")
    urls = []
    for lang in LANGS:
        write(home_path(lang), build_home(lang))
        urls.append(home_path(lang))
        write(about_path(lang), build_about(lang))
        urls.append(about_path(lang))
        write(work_path(lang), build_work(lang))
        urls.append(work_path(lang))
        for rec in recipes:
            write(recipe_path(lang, rec["slug"]), build_recipe(lang, rec))
            urls.append(recipe_path(lang, rec["slug"]))
    write("index.html", ROOT_INDEX.format(name=escape(NAME), base=BASE))
    sitemap = "\n".join(f"  <url><loc>{BASE}/{u}</loc></url>" for u in urls)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sitemap}\n</urlset>\n')
    write(".nojekyll", "")  # tells GitHub Pages to serve the files as they are
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
    print(f"Built {len(urls)} pages into {OUT}")


def write(rel_path, content):
    path = OUT / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    main()
