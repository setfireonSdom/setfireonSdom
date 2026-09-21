#!/usr/bin/env python3
import html
import re
import urllib.request

INDEX = "https://setfireonsdom.github.io/Blog/"
README = "README.md"
START = "<!-- BLOG-POST-LIST:START -->"
END = "<!-- BLOG-POST-LIST:END -->"
LIMIT = 6

MONTHS = {
    "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
    "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
    "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12",
}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", "ignore")


def to_iso_date(text):
    match = re.match(r"([A-Za-z]{3}) (\d{1,2}), (\d{4})", text.strip())
    if not match:
        return text.strip()
    month = MONTHS.get(match.group(1))
    if not month:
        return text.strip()
    return f"{match.group(3)}-{month}-{int(match.group(2)):02d}"


def main():
    page = fetch(INDEX)

    posts = []
    for block in page.split('<div class="quarto-post')[1:]:
        title_match = re.search(
            r'<h3 class="no-anchor listing-title">\s*<a href="([^"]+)"[^>]*>(.*?)</a>',
            block,
            re.S,
        )
        if not title_match:
            continue
        href = title_match.group(1)
        title = re.sub(r"<[^>]+>", "", title_match.group(2))
        title = html.unescape(re.sub(r"\s+", " ", title)).strip()
        date_match = re.search(r'<div class="listing-date">\s*(.*?)\s*</div>', block, re.S)
        date = to_iso_date(date_match.group(1)) if date_match else ""
        path = href[2:] if href.startswith("./") else href
        posts.append((title, INDEX + path, date))
        if len(posts) >= LIMIT:
            break

    lines = [f"- [{title}]({url})" + (f" · {date}" if date else "") for title, url, date in posts]
    new_block = f"{START}\n" + "\n".join(lines) + f"\n{END}"

    readme = open(README, encoding="utf-8").read()
    updated = re.sub(
        re.escape(START) + r".*?" + re.escape(END),
        lambda _: new_block,
        readme,
        flags=re.S,
    )
    with open(README, "w", encoding="utf-8") as f:
        f.write(updated)
    print(f"Updated {len(lines)} posts")


if __name__ == "__main__":
    main()
