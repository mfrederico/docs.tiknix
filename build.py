#!/usr/bin/env python3
"""
Tiknix docs builder.

Wraps each body fragment in src/articles/<slug>.html with the shared Tiknix
app-shell chrome (dark sidebar + slim topbar) and writes flat HTML into public/.
The output is plain static HTML — no server, no runtime dependency.

    python3 build.py

Edit fragments in src/articles/, edit metadata in ARTICLES below, then rebuild.
"""

import html
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "src" / "articles"
OUT = ROOT / "public"

SITE_NAME = "Tiknix"
SITE_TAGLINE = "Build on primitives that already work"

# slug, title, category, one-line card/meta description, read time
ARTICLES = [
    ("build-on-primitives",
     "Start From Primitives, Not From Scratch",
     "Foundations",
     "Every app needs the same twenty things before it needs anything interesting. Inheriting them is the whole point.",
     "8 min"),
    ("php-sqlite-substrate",
     "Why PHP and SQLite Are a Serious Choice in 2026",
     "Foundations",
     "Two of the most-deployed pieces of software on earth, chosen on merit: boring operations, a copy-the-file backup story, and an ecosystem now moving toward Turso and in-database vector search.",
     "11 min"),
    ("membership-and-settings",
     "The Members Table Is the Spine",
     "Foundations",
     "One identity table, one privilege number, and a key/value settings store that absorbs everything which would otherwise become a column.",
     "9 min"),
    ("convention-routing",
     "Convention-Based Routing: A URL Is a Method Name",
     "Foundations",
     "How Tiknix maps /member/profile to Member->profile() with no route table — and why that makes a codebase legible to humans and agents alike.",
     "7 min"),
    ("data-without-migrations",
     "Modeling Data Without a Migration Backlog",
     "Foundations",
     "RedBeanPHP's fluid schema lets the database follow your code while you explore, then freezes for production. What that buys and what it costs.",
     "9 min"),
    ("bootstrap-design-primitive",
     "Bootstrap as a Design Primitive",
     "Foundations",
     "Accessible components and a responsive grid you inherit; palette, type, and identity you own — because 5.3 puts its decisions in variables.",
     "10 min"),

    ("authentication-included",
     "The Login You Don't Have to Write",
     "Security & Access",
     "Registration, sessions, password hashing, reset flows, Google OAuth, CSRF, rate limiting — shipped, wired, and already exercised.",
     "9 min"),
    ("two-factor-included",
     "Two-Factor Authentication as a Config Switch",
     "Security & Access",
     "TOTP, QR enrollment, recovery codes, and 30-day device trust with three policy states: off, optional, required.",
     "8 min"),
    ("permissions-as-data",
     "Permissions as Data, Not If-Statements",
     "Security & Access",
     "One authcontrol row per route, four privilege levels, and a build mode that writes the rows as you develop.",
     "9 min"),
    ("teams-and-ownership",
     "Teams, Ownership, and Sharing Work Safely",
     "Security & Access",
     "Personal vs. team resources, four roles, and a single access-control service the rest of the app asks before it shows you anything.",
     "7 min"),

    ("codebase-map-for-agents",
     "Give Your AI Assistant a Map, Not a Flashlight",
     "Building with AI",
     "Tiknix ships MCP tools that hand an agent a structured inventory of what already exists — so its first instinct is reuse, not reinvention.",
     "10 min"),
    ("mcp-gateway",
     "MCP as a Primitive: One Endpoint for Every Agent",
     "Building with AI",
     "A gateway that aggregates tools, namespaces them, authenticates per key, and logs every call — so agent access is managed like user access.",
     "10 min"),
    ("agent-orchestration",
     "Plan With the Expensive Model, Execute With the Cheap One",
     "Building with AI",
     "The planner/worker/auditor pipeline: who is allowed to make design decisions, who merges, and why concurrency stays at three.",
     "11 min"),
    ("pipelines",
     "Pipelines: Automation That Ships With the App",
     "Building with AI",
     "Declarative JSON steps — HTTP, DB, shell, agent, MCP call, branch, notify — versioned in the repo next to the code they automate.",
     "9 min"),
    ("scaffolding-and-reuse",
     "Scaffolding Is a Reading Exercise",
     "Building with AI",
     "Generated code is only a gift if it looks like the code around it. How conventions turn a generator into a teacher.",
     "8 min"),

    ("data-integration",
     "Five Ways Data Crosses the Boundary",
     "Operations",
     "Outbound connectors, inbound API keys, signed webhooks, two-way email threads, and pipelines — sharing one set of auth, logging, and revocation machinery.",
     "11 min"),
    ("connections-and-broker-keys",
     "Third-Party Credentials Without Sprawl",
     "Operations",
     "Encrypted-at-rest tokens on the control plane, OAuth connectors behind one interface, and revocable broker keys instead of shared secrets.",
     "10 min"),
    ("caching-by-default",
     "Caching You Don't Have to Think About",
     "Operations",
     "A transparent query cache, a three-tier permission cache, and OPcache preloading — with an honest look at when each one earns its keep.",
     "9 min"),
    ("feature-flags-and-sidecars",
     "Growing Without Bloating the Core",
     "Operations",
     "Per-member feature flags with a privilege floor, and sidecar apps that live in their own repo but log in through yours.",
     "8 min"),
    ("production-checklist",
     "From Localhost to Production: The Honest Checklist",
     "Operations",
     "Defaults that are right for development are wrong for the internet. The specific switches to flip, and what breaks if you don't.",
     "10 min"),
]

CATEGORIES = [
    ("Foundations", "foundations",
     "The substrate: language, storage, routing, and data modeling. Choices you make once and live inside for years."),
    ("Security & Access", "security",
     "Identity, authorization, and sharing. The parts that are unglamorous to build and expensive to get wrong."),
    ("Building with AI", "ai",
     "How an agent works inside a codebase that can describe itself — and the guardrails that keep the output coherent."),
    ("Operations", "ops",
     "Integrations, performance, growth, and the move to production. What happens after it works on your laptop."),
]

CHIP_CLASS = {
    "Foundations": "chip-foundations",
    "Security & Access": "chip-security",
    "Building with AI": "chip-ai",
    "Operations": "chip-ops",
}

HEAD = """<!doctype html>
<html lang="en" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="icon" href="/img/tiknix.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,300..800&family=Figtree:ital,wght@0,300..900;1,300..900&family=DM+Mono:wght@400;500&family=Fraunces:ital,opsz,wght,SOFT@0,9..144,100..900,0..100&family=Playfair+Display:wght@500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/docs.css">
<script src="/assets/docs.js"></script>
</head>
<body>
<div class="shell">
<div class="sidebar-backdrop" id="sidebarBackdrop"></div>
<aside class="sidebar" id="sidebar">
  <a class="sidebar-brand" href="/index.html">
    <span class="brand-logo"></span>
    <span class="brand-word">tiknix</span>
    <span class="brand-sub">docs</span>
  </a>
  <nav class="nav">
{nav}
  </nav>
  <div class="sidebar-foot">
    Written against the Tiknix source. <a href="/index.html">All articles</a>
  </div>
</aside>
<div class="main">
  <header class="topbar">
    <button class="btn-icon menu-toggle" id="menuToggle" type="button" aria-label="Open menu">&#9776;</button>
    <div class="topbar-title">
      <span class="eyebrow">{eyebrow}</span>
      <strong>{topbar}</strong>
    </div>
    <div class="topbar-actions">
      <button class="btn-icon" id="themeToggle" type="button" aria-label="Toggle theme"><span id="themeIcon">&#9728;</span></button>
    </div>
  </header>
  <main class="content">
"""

FOOT = """  </main>
  <footer class="site-footer">
    <div class="footer-inner">
      <div class="footer-brand">
        <span class="brand-logo footer-logo"></span>
        <div>
          <div class="footer-word">tiknix</div>
          <div class="footer-tag">Build on primitives that already work</div>
        </div>
      </div>
      <nav class="footer-links">
        <a href="https://tiknix.com">Homepage</a>
        <a href="https://github.com/mfrederico/tiknix">GitHub</a>
        <a href="https://github.com/mfrederico/tiknix-tutorials">Tutorials</a>
        <a href="/index.html">All articles</a>
      </nav>
    </div>
    <div class="footer-fine">
      Documentation written against the Tiknix source. Tiknix is released under the MIT License.
    </div>
  </footer>
</div>
</div>
</body>
</html>
"""


def nav_html(active_slug):
    parts = []
    parts.append('    <div class="nav-heading">Index</div>')
    cls = " active" if active_slug is None else ""
    parts.append(f'    <a class="nav-link{cls}" href="/index.html"><span class="nav-num">&#9737;</span>All articles</a>')
    n = 0
    for cat, _key, _blurb in CATEGORIES:
        parts.append(f'    <div class="nav-heading">{html.escape(cat)}</div>')
        for slug, title, acat, _desc, _rt in ARTICLES:
            if acat != cat:
                continue
            n += 1
            cls = " active" if slug == active_slug else ""
            parts.append(
                f'    <a class="nav-link{cls}" href="/{slug}.html">'
                f'<span class="nav-num">{n:02d}</span>{html.escape(title)}</a>'
            )
    return "\n".join(parts)


def article_index(slug):
    for i, a in enumerate(ARTICLES):
        if a[0] == slug:
            return i
    raise KeyError(slug)


def build_article(slug, title, cat, desc, read_time):
    body = (SRC / f"{slug}.html").read_text(encoding="utf-8").strip()
    idx = article_index(slug)
    num = idx + 1

    prev_a = ARTICLES[idx - 1] if idx > 0 else None
    next_a = ARTICLES[idx + 1] if idx < len(ARTICLES) - 1 else None
    nav_links = []
    if prev_a:
        nav_links.append(
            f'<a class="prev" href="/{prev_a[0]}.html"><span class="dir">&#8592; Previous</span>'
            f'<span class="ttl">{html.escape(prev_a[1])}</span></a>'
        )
    if next_a:
        nav_links.append(
            f'<a class="next" href="/{next_a[0]}.html"><span class="dir">Next &#8594;</span>'
            f'<span class="ttl">{html.escape(next_a[1])}</span></a>'
        )

    page = HEAD.format(
        title=html.escape(f"{title} — {SITE_NAME} Docs"),
        description=html.escape(desc),
        nav=nav_html(slug),
        eyebrow=html.escape(cat),
        topbar=html.escape(title),
    )
    page += f"""    <article class="narrow">
      <header class="article-header">
        <div class="meta">
          <span class="chip {CHIP_CLASS[cat]}">{html.escape(cat)}</span>
          <span class="eyebrow">Article {num:02d} of {len(ARTICLES):02d}</span>
          <span class="eyebrow">{html.escape(read_time)} read</span>
        </div>
        <h1>{html.escape(title)}</h1>
        <p class="lede">{html.escape(desc)}</p>
      </header>
      <div class="article-body">
{body}
      </div>
      <nav class="article-nav">
        {''.join(nav_links)}
      </nav>
    </article>
"""
    page += FOOT
    (OUT / f"{slug}.html").write_text(page, encoding="utf-8")


def build_index():
    intro = (ROOT / "src" / "index-intro.html").read_text(encoding="utf-8").strip()
    page = HEAD.format(
        title=html.escape(f"{SITE_NAME} Docs — {SITE_TAGLINE}"),
        description=html.escape(
            "Articles on building real systems with Tiknix: PHP, SQLite, authentication, "
            "2FA, permissions, and AI-assisted development on primitives that already work."
        ),
        nav=nav_html(None),
        eyebrow="Tiknix Documentation",
        topbar="Articles",
    )
    page += '    <div class="wide">\n' + intro + "\n"

    n = 0
    for cat, key, blurb in CATEGORIES:
        page += f"""      <section class="section-head" id="{key}">
        <span class="eyebrow">Track</span>
        <h2>{html.escape(cat)}</h2>
        <p>{html.escape(blurb)}</p>
      </section>
      <div class="cards">
"""
        for slug, title, acat, desc, read_time in ARTICLES:
            if acat != cat:
                continue
            n += 1
            page += f"""        <a class="card" href="/{slug}.html">
          <span class="card-num">{n:02d}</span>
          <h3>{html.escape(title)}</h3>
          <p>{html.escape(desc)}</p>
          <span class="card-foot"><span class="chip {CHIP_CLASS[cat]}">{html.escape(cat)}</span> {html.escape(read_time)}</span>
        </a>
"""
        page += "      </div>\n"

    page += "    </div>\n" + FOOT
    (OUT / "index.html").write_text(page, encoding="utf-8")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    missing = [s for s, *_ in ARTICLES if not (SRC / f"{s}.html").exists()]
    if missing:
        print("Missing fragments: " + ", ".join(missing))
    for slug, title, cat, desc, rt in ARTICLES:
        if (SRC / f"{slug}.html").exists():
            build_article(slug, title, cat, desc, rt)
    build_index()
    built = len([1 for s, *_ in ARTICLES if (SRC / f"{s}.html").exists()])
    print(f"Built index.html + {built} article(s) into {OUT}")


if __name__ == "__main__":
    main()
