from pathlib import Path
import re
import sys


root = Path(sys.argv[1])
base_path = sys.argv[2].rstrip("/")
quoted_root_path = re.compile(r'''(?P<quote>["'])/(?P<path>(?!/)[^"']*)''')
unquoted_css_root_path = re.compile(r'''url\(\s*/(?P<path>(?!/)[^)'"\s]*)''')
local_server_url = re.compile(r'''https?://localhost:8767/(?P<path>[^"'\s]*)''')


def prefix_quoted_path(match):
    path = match["path"]
    base_relative = base_path.lstrip("/")
    if path == base_relative or path.startswith(base_relative + "/"):
        return match.group(0)
    return f"{match['quote']}{base_path}/{path}"


def prefix_css_path(match):
    path = match["path"]
    base_relative = base_path.lstrip("/")
    if path == base_relative or path.startswith(base_relative + "/"):
        return match.group(0)
    return f"url({base_path}/{path}"


for file_path in root.rglob("*"):
    if file_path.suffix.lower() not in {".html", ".css", ".js"}:
        continue
    content = file_path.read_text(encoding="utf-8")
    content = quoted_root_path.sub(prefix_quoted_path, content)
    content = unquoted_css_root_path.sub(prefix_css_path, content)
    content = local_server_url.sub(lambda match: f"{base_path}/{match['path']}", content)
    file_path.write_text(content, encoding="utf-8")
