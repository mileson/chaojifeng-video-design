"""Showcase videos stay inside the native-player budget; both README pages list them, each with a one-sentence instruction.

Reads committed files only: no network, no media tools, no rendering.
"""
import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOWCASE = ROOT / "examples" / "showcase"
README = ROOT / "README.md"
CASE_PAGE = SHOWCASE / "README.md"
ORIGINALS = ROOT / "assets" / "gallery" / "originals.json"
# GitHub's native player accepts videos up to 10 MB on a free plan; keep a margin.
MAX_BYTES = 8_000_000
ATTACHMENT_URL = re.compile(r"https://github\.com/user-attachments/assets/[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}")
NOT_CATEGORIES = {"创作背景与溯源", "使用范围"}
# README grid: at most four cells per row. A category with four or more works spans the page at 25 % per cell;
# one with fewer keeps the same cell size through a fixed width, so a lone cell is not stretched across the page.
CELLS_PER_ROW = 4
FIXED_CELL_WIDTH = "209"
INSTRUCTION_PREFIX = "用 $chaojifeng-video-design"
INSTRUCTION_LABEL = "一句话指令："
MAX_INSTRUCTION_CHARS = 100
TABLE = re.compile(r"<table([^>]*)>(.*?)</table>", re.S)
ROW = re.compile(r"<tr>(.*?)</tr>", re.S)
CELL = re.compile(r"<td([^>]*)>(.*?)</td>", re.S)


def headings(text, level):
    return re.findall(r"^%s (.+?)\s*$" % ("#" * level), text, re.M)


def block(text, title, level):
    """Lines under the `level`-hash heading `title`, up to the next heading of the same or a higher level."""
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if line.strip() == "#" * level + " " + title) + 1
    stop = next((i for i in range(start, len(lines)) if re.match(r"#{1,%d} " % level, lines[i])), len(lines))
    return "\n".join(lines[start:stop])


def attribute(attrs, name):
    found = re.search(r'\b%s="([^"]*)"' % name, attrs)
    return found.group(1) if found else None


def grids(text):
    """Every <table> in `text`: its width and rows of cells, each cell with its width and non-empty lines."""
    tables = []
    for attrs, body in TABLE.findall(text):
        rows = [
            [
                {"width": attribute(cell_attrs, "width"), "lines": [line.strip() for line in inner.splitlines() if line.strip()]}
                for cell_attrs, inner in CELL.findall(row)
            ]
            for row in ROW.findall(body)
        ]
        tables.append({"width": attribute(attrs, "width"), "rows": rows})
    return tables


def cell_title(cell):
    return cell["lines"][1].strip("*")


class ShowcaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        manifest = json.loads((SHOWCASE / "manifest.json").read_text(encoding="utf-8"))
        cls.items = manifest["items"]
        cls.prompts = manifest["prompt_examples"]
        originals = json.loads(ORIGINALS.read_text(encoding="utf-8"))["samples"]
        # Every case video on the README: the music works from the gallery, then the films kept in examples/showcase.
        cls.works = [{"id": w["id"], "title": w["name"], "url": w["github_video_attachment"]["url"]} for w in originals]
        cls.works += [{"id": i["id"], "title": i["title"], "url": i["github_video_attachment"]["url"]} for i in cls.items]
        cls.readme = README.read_text(encoding="utf-8")
        cls.case_page = CASE_PAGE.read_text(encoding="utf-8")
        cls.readme_cases = block(cls.readme, "创作案例", 2)

    def test_every_video_is_listed_and_matches_size_hash_and_budget(self):
        listed = {item["output"]["file"] for item in self.items}
        self.assertEqual(listed, {p.name for p in SHOWCASE.glob("*.mp4")}, "a video is missing from manifest.json, or the other way round")
        for item in self.items:
            out = item["output"]
            data = (SHOWCASE / out["file"]).read_bytes()
            self.assertEqual(len(data), out["bytes"], out["file"])
            self.assertEqual(hashlib.sha256(data).hexdigest(), out["sha256"], out["file"])
            self.assertLessEqual(len(data), MAX_BYTES, f"{out['file']} is over the {MAX_BYTES} byte budget for the native player")

    def test_native_player_links_are_distinct_and_stand_alone_on_both_pages(self):
        urls = [work["url"] for work in self.works]
        self.assertEqual(len(urls), len(set(urls)))
        for url in urls:
            self.assertTrue(ATTACHMENT_URL.fullmatch(url), url)
            for name, text in (("README.md", self.readme_cases), ("examples/showcase/README.md", self.case_page)):
                self.assertIn(f"\n{url}\n", f"\n{text}\n", f"{name}: the link must sit on its own line to render as a player")

    def test_case_titles_are_page_headings_and_bold_readme_cell_titles(self):
        readme_lines = self.readme_cases.splitlines()
        for work in self.works:
            self.assertIn(work["title"], headings(self.case_page, 3), f"examples/showcase/README.md: {work['title']}")
            self.assertEqual(readme_lines.count(f"**{work['title']}**"), 1, f"README.md: {work['title']}")

    def test_readme_categories_match_the_case_page(self):
        readme_categories = headings(self.readme_cases, 3)
        page_categories = [h for h in headings(self.case_page, 2) if h not in NOT_CATEGORIES]
        self.assertEqual(readme_categories, page_categories)
        self.assertIn("产品宣传片", readme_categories)

    def test_every_work_has_a_one_sentence_instruction(self):
        self.assertEqual(set(self.prompts), {work["id"] for work in self.works}, "prompt_examples must cover every case video and nothing else")
        for work in self.works:
            text = self.prompts[work["id"]]
            self.assertTrue(text.startswith(INSTRUCTION_PREFIX), work["id"])
            self.assertTrue(text.endswith("。") and text.count("。") == 1, f"{work['id']}: one sentence, ending in a full stop")
            self.assertNotIn("\n", text, work["id"])
            self.assertLessEqual(len(text), MAX_INSTRUCTION_CHARS, work["id"])
            self.assertEqual(text.count("$"), 1, f"{work['id']}: a second $ in one paragraph can turn the text between them into a formula")
            self.assertRegex(text, r"【[^】]+】", f"{work['id']}: mark what the reader swaps for their own material")

    def test_readme_cells_stack_player_title_and_instruction_with_at_most_four_per_row(self):
        by_title = {work["title"]: work for work in self.works}
        for category in headings(self.readme_cases, 3):
            tables = grids(block(self.readme_cases, category, 3))
            self.assertEqual(len(tables), 1, f"{category}: one table per category")
            table = tables[0]
            widest = max(len(row) for row in table["rows"])
            self.assertLessEqual(widest, CELLS_PER_ROW, f"{category}: at most {CELLS_PER_ROW} cells per row")
            full = widest == CELLS_PER_ROW
            self.assertEqual(table["width"], "100%" if full else None, f"{category}: table width")
            for cell in (cell for row in table["rows"] for cell in row):
                self.assertEqual(cell["width"], "25%" if full else FIXED_CELL_WIDTH, f"{category}: cell width")
                self.assertEqual(len(cell["lines"]), 3, f"{category}: a cell holds the player link, the title and the instruction, nothing else")
                url, title_line, instruction = cell["lines"]
                work = by_title[cell_title(cell)]
                self.assertEqual(title_line, f"**{work['title']}**")
                self.assertEqual(url, work["url"], work["title"])
                self.assertEqual(instruction, self.prompts[work["id"]], work["title"])
        placed = [cell_title(cell) for table in grids(self.readme_cases) for row in table["rows"] for cell in row]
        self.assertEqual(sorted(placed), sorted(work["title"] for work in self.works), "every case video sits in exactly one cell")

    def test_readme_cells_follow_the_case_page_categories_and_order(self):
        for category in headings(self.readme_cases, 3):
            cells = [cell for row in grids(block(self.readme_cases, category, 3))[0]["rows"] for cell in row]
            self.assertEqual([cell_title(cell) for cell in cells], headings(block(self.case_page, category, 2), 3), category)

    def test_case_page_repeats_each_instruction_under_its_title(self):
        for work in self.works:
            section = block(self.case_page, work["title"], 3)
            self.assertEqual(section.splitlines().count(INSTRUCTION_LABEL + self.prompts[work["id"]]), 1, work["title"])

    def test_relative_links_on_the_case_pages_resolve(self):
        broken = []
        for page, text in ((README, self.readme_cases), (CASE_PAGE, self.case_page)):
            for target in re.findall(r"\]\(([^)\s]+)\)", text):
                if re.match(r"[a-z]+:", target) or target.startswith("#"):
                    continue
                if not (page.parent / target.split("#")[0]).exists():
                    broken.append(f"{page.name}: {target}")
        self.assertEqual(broken, [])


if __name__ == "__main__":
    unittest.main()
