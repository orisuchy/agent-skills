"""Skill files hold steps and links only: no line of a skill file may repeat a line of AGENTS.md or docs/*.md.
Copy into the repo's structural tests (adjust ROOT if the file is not one level below the repo root)."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / ".claude" / "skills"  # or ".agents/skills"


def bare(line):
    return line.strip().lstrip("-* ").strip()


def prose_lines(path):
    """(line number, normalised text) of a markdown file, minus frontmatter and code fences."""
    lines = path.read_text().splitlines()
    start = 0
    if lines[:1] == ["---"] and "---" in lines[1:]:
        start = lines.index("---", 1) + 1
    in_fence = False
    for number, line in enumerate(lines[start:], start=start + 1):
        if line.strip().startswith("```"):
            in_fence = not in_fence
        elif not in_fence:
            yield number, bare(line)


class SkillOverlap(unittest.TestCase):
    def test_skill_files_repeat_no_line_of_agents_md_or_docs(self):
        doc_sources = {}
        for doc in [ROOT / "AGENTS.md", *sorted((ROOT / "docs").glob("*.md"))]:
            for _, text in prose_lines(doc):
                if len(text) >= 40 and not text.startswith("#"):
                    doc_sources.setdefault(text, doc.relative_to(ROOT))
        failures = []
        for skill in sorted(SKILLS_DIR.rglob("*.md")):
            for number, text in prose_lines(skill):
                if len(text) >= 40 and not text.startswith("#") and text in doc_sources:
                    failures.append(f"{skill.relative_to(ROOT)}:{number} repeats {doc_sources[text]}")
        if failures:
            self.fail("\n".join(failures))


if __name__ == "__main__":
    unittest.main()
