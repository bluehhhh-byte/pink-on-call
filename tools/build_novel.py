"""Build the reader data from novel.md. Run with Python 3."""

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
chapters = []
epilogue = {"title": "", "paragraphs": [], "images": {}}
section = None

for line in (ROOT / "novel.md").read_text(encoding="utf-8-sig").splitlines():
    line = line.strip()
    if not line or line == "---":
        continue
    heading = re.fullmatch(r"## (제(\d+)장)\. (.+)", line)
    if heading:
        number, index, subtitle = heading.groups()
        section = {
            "id": int(index), "number": number, "subtitle": subtitle,
            "fullTitle": f"{number}. {subtitle}", "paragraphs": [], "images": {},
        }
        chapters.append(section)
        continue
    if line.startswith("### 후일담. "):
        section = epilogue
        section["title"] = line.removeprefix("### 후일담. ")
        continue
    if section is None:
        continue
    if line.startswith("!["):
        asset = re.fullmatch(r"!\[(.+)\]\((scenes/[a-z0-9-]+\.png)\)", line)
        if not asset or not (ROOT / asset[2]).is_file() or not section["paragraphs"]:
            raise ValueError(f"Invalid illustration: {line}")
        section["images"][len(section["paragraphs"]) - 1] = {"alt": asset[1], "src": asset[2]}
        continue
    line = line.removeprefix("### ")
    line = re.sub(r"^\*\*([^*]+)\*\*\s+", r"\1 : ", line)
    line = line.replace("**", "")
    section["paragraphs"].append(line)

data = {
    "title": "핑크는 통화 중",
    "chapterCount": len(chapters),
    "totalParagraphs": sum(len(chapter["paragraphs"]) for chapter in chapters),
    "chapters": chapters,
    "epilogue": epilogue,
}
(ROOT / "novel-data.js").write_text(
    "window.NOVEL_DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n",
    encoding="utf-8",
)
