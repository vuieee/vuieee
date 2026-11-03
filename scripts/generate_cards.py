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
        url += "?" + urllib.parse.urlencode(
