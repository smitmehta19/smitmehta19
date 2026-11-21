"""Refresh the "Recently worked on" line in README.md.

Finds my most recently updated public repos and writes them between the
RECENT markers in the README. Runs daily from a GitHub Action.
"""
import json
import os
import re
import urllib.request
from datetime import datetime
from pathlib import Path

USER = "smitmehta19"
HOW_MANY = 3

# Repos that should never show up in the line.
SKIP = {"smitmehta19", "sm-arcade", "photographer-comparison"}

# Nicer display names for repos whose name isn't the product name.
DISPLAY_NAMES = {
    "home-workout-app": "Home Gym",
    "pixrow-play": "PixRow",
    "cookflow": "CookFlow",
    "fovea": "Fovea",
    "todo-app": "To-do app",
    "smitmehta19.github.io": "Terminal Portfolio",
}

README = Path(__file__).resolve().parents[2] / "README.md"
START, END = "<!--RECENT:START-->", "<!--RECENT:END-->"


def fetch_repos():
    url = f"https://api.github.com/users/{USER}/repos?per_page=100&sort=pushed"
    request = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request) as response:
        return json.load(response)


def main():
    repos = fetch_repos()
    print(f"Fetched {len(repos)} public repos")

    picked = [
        r for r in repos
        if r["name"] not in SKIP and not r["fork"] and not r["archived"]
    ][:HOW_MANY]

    parts = []
    for repo in picked:
        name = DISPLAY_NAMES.get(repo["name"], repo["name"])
        link = repo["homepage"] or repo["html_url"]
        date = datetime.fromisoformat(repo["pushed_at"].replace("Z", "+00:00"))
        parts.append(f"[{name}]({link}) ({date.day} {date:%b})")
        print(f"  - {name}: last updated {date:%d %b %Y}")

    line = "**Recently worked on:** " + ", ".join(parts)
    text = README.read_text()
    new_text = re.sub(
        f"{re.escape(START)}.*?{re.escape(END)}",
        f"{START}\n{line}\n{END}",
        text,
        flags=re.DOTALL,
    )

    if new_text == text:
        print("No change to the README")
    else:
        README.write_text(new_text)
        print("README updated:", line)


if __name__ == "__main__":
    main()
