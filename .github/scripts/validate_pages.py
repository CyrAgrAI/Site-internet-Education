from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


root = Path(sys.argv[1]).resolve()
base_path = sys.argv[2].rstrip("/")
missing = []
checked = 0


def check_reference(value, source):
    global checked
    url = urlsplit(value)
    if url.scheme or url.netloc or not url.path:
        return

    path = unquote(url.path)
    if path == base_path or path == base_path + "/":
        target = root / "index.html"
    elif path.startswith(base_path + "/"):
        target = root / path[len(base_path) + 1 :]
    elif path.startswith("/"):
        missing.append(f"{source.relative_to(root)}: path sans préfixe GitHub Pages {value}")
        return
    else:
        target = source.parent / path

    if target.is_dir():
        target = target / "index.html"
    checked += 1
    if not target.is_file():
        missing.append(f"{source.relative_to(root)}: fichier absent pour {value}")


class ReferenceParser(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.source = source

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in {"href", "src", "poster", "action"} and value:
                check_reference(value, self.source)


quoted_css_url = re.compile(r"url\(\s*['\"]([^'\"]+)['\"]\s*\)", re.IGNORECASE)
plain_css_url = re.compile(r"url\(\s*([^'\"\s)][^)'\"\s]*)\s*\)", re.IGNORECASE)

for source in root.rglob("*"):
    if source.suffix.lower() not in {".html", ".css"}:
        continue
    content = source.read_text(encoding="utf-8")
    if "localhost:8767" in content:
        missing.append(f"{source.relative_to(root)}: contient encore localhost:8767")
    if source.suffix.lower() == ".html":
        parser = ReferenceParser(source)
        parser.feed(content)
    for pattern in (quoted_css_url, plain_css_url):
        for match in pattern.finditer(content):
            check_reference(match.group(1), source)

if missing:
    print("\n".join(missing))
    raise SystemExit(f"Échec : {len(missing)} référence(s) locale(s) invalide(s).")

print(f"OK : {checked} références locales vérifiées pour {base_path}.")
