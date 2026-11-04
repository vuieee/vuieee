#!/usr/bin/env python3
import json, os, sys, urllib.request, urllib.parse
from html import escape

USER = os.environ.get("GITHUB_USER", "vuieee")
TOKEN = os.environ.get("GITHUB_TOKEN")
OUT = os.environ.get("OUT_DIR", "generated")
EXCLUDE_LANGS = {l.strip().lower() for l in os.environ.get("EXCLUDE_LANGS", "").split(",") if l.strip()}

BG, BORDER, TITLE, TEXT, ICON = "#0d1117", "#30363d", "#58a6ff", "#c9d1d9", "#1f6feb"
LANG_COLORS = {
    "Python": "#3572A5", "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "HTML": "#e34c26",
    "CSS": "#563d7c", "PHP": "#4F5D95", "C": "#555555", "C++": "#f34b7d", "C#": "#178600",
    "Shell": "#89e051", "Go": "#00ADD8", "Lua": "#000080", "Vue": "#41b883",
}
FALLBACK = "#8b949e"

def api(path, params=None):
    url = "https://api.github.com" + path
    if params: url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "profile-readme-cards",
        **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}),
    })
    with urllib.request.urlopen(req, timeout=30) as r: return json.load(r)

def paged(path, params=None):
    page, items = 1, []
    while True:
        chunk = api(path, {**(params or {}), "per_page": 100, "page": page})
        items += chunk
        if len(chunk) < 100: return items
        page += 1

def search_count(kind, q):
    try: return api(f"/search/{kind}", {"q": q, "per_page": 1})["total_count"]
    except Exception: return 0

def fmt(n): return f"{n/1000:.1f}k" if n >= 1000 else str(n)

user = api(f"/users/{USER}")
own = [r for r in paged(f"/users/{USER}/repos", {"type": "owner"}) if not r["fork"]]
stars = sum(r["stargazers_count"] for r in own)
commits = search_count("commits", f"author:{USER}")
prs = search_count("issues", f"author:{USER} type:pr")
issues = search_count("issues", f"author:{USER} type:issue")

langs = {}
for r in own:
    try:
        for lang, n in api(f"/repos/{r['full_name']}/languages").items():
            if lang.lower() not in EXCLUDE_LANGS: langs[lang] = langs.get(lang, 0) + n
    except Exception: pass

FONT = "font-family=\"'Segoe UI',Ubuntu,Sans-Serif\""
ICONS = {
    "star": "M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.75.75 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z",
    "commit": "M11.93 8.5a4.002 4.002 0 0 1-7.86 0H.75a.75.75 0 0 1 0-1.5h3.32a4.002 4.002 0 0 1 7.86 0h3.32a
