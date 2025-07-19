import requests
import datetime

USERNAME = "weskerty" 
GIST_COUNT = 5
README_FILE = "README.md"
START = "<!-- GIST-LIST:START -->"
END = "<!-- GIST-LIST:END -->"

def fetch_gists():
    res = requests.get(f"https://api.github.com/users/{USERNAME}/gists")
    res.raise_for_status()
    gists = res.json()
    return gists[:GIST_COUNT]

def format_gists(gists):
    lines = []
    for gist in gists:
        desc = gist["description"] or "(Sin descripción)"
        url = gist["html_url"]
        created = gist["created_at"][:10]
        lines.append(f"- [{desc}]({url}) ({created})")
    return "\n".join(lines)

def update_readme(new_content):
    with open(README_FILE, "r", encoding="utf-8") as f:
        readme = f.read()

    start_idx = readme.find(START)
    end_idx = readme.find(END)
    if start_idx == -1 or end_idx == -1:
        print("Marcadores no encontrados.")
        return

    updated = (
        readme[:start_idx + len(START)]
        + "\n" + new_content + "\n"
        + readme[end_idx:]
    )

    if updated != readme:
        with open(README_FILE, "w", encoding="utf-8") as f:
            f.write(updated)
        print("README.md actualizado.")
    else:
        print("Sin cambios.")

if __name__ == "__main__":
    gists = fetch_gists()
    md = format_gists(gists)
    update_readme(md)
