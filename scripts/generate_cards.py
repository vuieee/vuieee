#!/usr/bin/env python3
"""Generate GitHub stats + top-languages SVG cards (no third-party services).

Usage:  GITHUB_USER=vuieee GITHUB_TOKEN=xxx python scripts/generate_cards.py
Only the Python standard library is needed.
"""
import json, os, sys, urllib.request, urllib.parse
from html import escape

USER = os.environ.get("GITHUB_USER", "vuieee")
TOKEN = os.environ.get("GITHUB_TOKEN")
OUT = os.environ.get("OUT_DIR", "generated")
EXCLUDE_LANGS = {l.strip().lower() for l in os.environ.get("EXCLUDE_LANGS", "").split(",") if l.strip()}

# Theme (github_dark)
BG, BORDER, TITLE, TEXT, ICON = "#0d1117", "#30363d", "#58a6ff", "#c9d1d9", "#1f6feb"

LANG_COLORS = {
    "Python": "#3572A5", "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "HTML": "#e34c26",
    "CSS": "#563d7c", "PHP": "#4F5D95", "C": "#555555", "C++": "#f34b7d", "C#": "#178600",
    "Java": "#b07219", "Kotlin": "#A97BFF", "Shell": "#89e051", "PowerShell": "#012456",
    "Batchfile": "#C1F12E", "Go": "#00ADD8", "Rust": "#dea584", "Lua": "#000080",
    "Dart": "#00B4AB", "Ruby": "#701516", "Vue": "#41b883", "SCSS": "#c6538c",
    "Hack": "#878787", "Dockerfile": "#384d54", "Makefile": "#427819", "Swift": "#F05138",
}
FALLBACK = "#8b949e"

def api(path, params=None):
    url = "https://api.github.com" + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "profile-readme-cards",
        **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}),
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def paged(path, params=None):
    page, items = 1, []
    while True:
        chunk = api(path, {**(params or {}), "per_page": 100, "page": page})
        items += chunk
        if len(chunk) < 100:
            return items
        page += 1

def search_count(kind, q):
    try:
        return api(f"/search/{kind}", {"q": q, "per_page": 1})["total_count"]
    except Exception:
        return 0

def fmt(n):
    return f"{n/1000:.1f}k" if n >= 1000 else str(n)

# ---------- collect data ----------
user = api(f"/users/{USER}")
repos = paged(f"/users/{USER}/repos", {"type": "owner"})
own = [r for r in repos if not r["fork"]]

stars = sum(r["stargazers_count"] for r in own)
commits = search_count("commits", f"author:{USER}")
prs = search_count("issues", f"author:{USER} type:pr")
issues = search_count("issues", f"author:{USER} type:issue")

langs = {}
for r in own:
    try:
        for lang, n in api(f"/repos/{r['full_name']}/languages").items():
            if lang.lower() not in EXCLUDE_LANGS:
                langs[lang] = langs.get(lang, 0) + n
    except Exception as e:
        print(f"skip {r['name']}: {e}", file=sys.stderr)

# ---------- SVG helpers ----------
FONT = "font-family=\"'Segoe UI',Ubuntu,Sans-Serif\""

def card(w, h, body):
    # Removed the <rect> tag that generates the background and border
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'{body}</svg>')

ICONS = {
    "star": "M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.75.75 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z",
    "commit": "M11.93 8.5a4.002 4.002 0 0 1-7.86 0H.75a.75.75 0 0 1 0-1.5h3.32a4.002 4.002 0 0 1 7.86 0h3.32a.75.75 0 0 1 0 1.5Zm-1.43-.75a2.5 2.5 0 1 0-5 0 2.5 2.5 0 0 0 5 0Z",
    "pr": "M1.5 3.25a2.25 2.25 0 1 1 3 2.122v5.256a2.251 2.251 0 1 1-1.5 0V5.372A2.25 2.25 0 0 1 1.5 3.25Zm5.677-.177L9.573.677A.25.25 0 0 1 10 .854V2.5h1A2.5 2.5 0 0 1 13.5 5v5.628a2.251 2.251 0 1 1-1.5 0V5a1 1 0 0 0-1-1h-1v1.646a.25.25 0 0 1-.427.177L7.177 3.427a.25.25 0 0 1 0-.354Z",
    "issue": "M8 9.5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3Z M8 0a8 8 0 1 1 0 16A8 8 0 0 1 8 0ZM1.5 8a6.5 6.5 0 1 0 13 0 6.5 6.5 0 0 0-13 0Z",
    "repo": "M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5Zm10.5-1h-8a1 1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8ZM5 12.25a.25.25 0 0 1 .25-.25h3.5a.25.25 0 0 1 .25.25v3.25a.25.25 0 0 1-.4.2l-1.45-1.087a.249.249 0 0 0-.3 0L5.4 15.7a.25.25 0 0 1-.4-.2Z",
    "people": "M2 5.5a3.5 3.5 0 1 1 5.898 2.549 5.508 5.508 0 0 1 3.034 4.084.75.75 0 1 1-1.482.235 4 4 0 0 0-7.9 0 .75.75 0 0 1-1.482-.236A5.507 5.507 0 0 1 3.102 8.05 3.493 3.493 0 0 1 2 5.5ZM11 4a3.001 3.001 0 0 1 2.22 5.018 5.01 5.01 0 0 1 2.56 3.012.749.749 0 0 1-.885.954.752.752 0 0 1-.549-.514 3.507 3.507 0 0 0-2.522-2.372.75.75 0 0 1-.574-.73v-.352a.75.75 0 0 1 .416-.672A1.5 1.5 0 0 0 11 5.5.75.75 0 0 1 11 4Zm-5.5-.5a2 2 0 1 0-.001 3.999A2 2 0 0 0 5.5 3.5Z",
}

def stat_row(i, icon, label, value):
    # Changed to a 1-column layout
    x, y = 25, 30 + i * 32
    return (f'<g transform="translate({x},{y})">'
            f'<svg x="0" y="-13" width="16" height="16" viewBox="0 0 16 16"><path fill="{ICON}" d="{ICONS[icon]}"/></svg>'
            f'<text x="26" y="0" fill="{TEXT}" font-size="14" {FONT}>{escape(label)}:</text>'
            f'<text x="200" y="0" fill="{TEXT}" font-size="14" font-weight="700" {FONT}>{escape(value)}</text></g>')

def stats_svg():
    rows = [("star", "Total Stars", fmt(stars)), ("commit", "Total Commits", fmt(commits)),
            ("pr", "Total PRs", fmt(prs)), ("issue", "Total Issues", fmt(issues)),
            ("repo", "Public Repos", fmt(len(own))), ("people", "Followers", fmt(user["followers"]))]
    # Removed the title text block completely
    body = "".join(stat_row(i, *r) for i, r in enumerate(rows))
    # Reduced width to 350px so it fits horizontally next to the languages card
    return card(350, 230, body)

def langs_svg(top=8):
    total = sum(langs.values()) or 1
    items = sorted(langs.items(), key=lambda kv: -kv[1])[:top]
    shown = sum(v for _, v in items)
    # Reduced width to 450px so it fits horizontally next to the stats card
    W, PAD = 450, 25
    bar_w = W - 2 * PAD
    body = f'<text x="{PAD}" y="35" fill="{TITLE}" font-size="18" font-weight="600" {FONT}>Most Used Languages</text>'
    body += f'<clipPath id="c"><rect x="{PAD}" y="50" width="{bar_w}" height="8" rx="4"/></clipPath><g clip-path="url(#c)">'
    x = PAD
    for lang, v in items:
        w = bar_w * v / shown
        body += f'<rect x="{x:.2f}" y="50" width="{w:.2f}" height="8" fill="{LANG_COLORS.get(lang, FALLBACK)}"/>'
        x += w
    body += "</g>"
    for i, (lang, v) in enumerate(items):
        col, row = i % 2, i // 2
        cx, cy = PAD + col * 200, 90 + row * 25
        body += (f'<circle cx="{cx+5}" cy="{cy-4}" r="5" fill="{LANG_COLORS.get(lang, FALLBACK)}"/>'
                 f'<text x="{cx+18}" y="{cy}" fill="{TEXT}" font-size="12" {FONT}>{escape(lang)} '
                 f'<tspan fill="#8b949e">{v/total*100:.1f}%</tspan></text>')
    h = 90 + ((len(items) + 1) // 2) * 25 + 5
    return card(W, h, body)

os.makedirs(OUT, exist_ok=True)
open(f"{OUT}/stats.svg", "w", encoding="utf-8").write(stats_svg())
open(f"{OUT}/top-langs.svg", "w", encoding="utf-8").write(langs_svg())
print(f"Wrote {OUT}/stats.svg and {OUT}/top-langs.svg for {USER}")
