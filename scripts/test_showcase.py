"""Showcase videos stay inside the native-player budget and both README pages list them.

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
# GitHub's native player accepts videos up to 10 MB on a free plan; keep a margin.
MAX_BYTES = 8_000_000
ATTACHMENT_URL = re.compile(r"https://github\.com/user-attachments/assets/[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}")
NOT_CATEGORIES = {"创作背景与溯源", "使用范围"}


def headings(text, level):
    return re.findall(r"^%s (.+?)\s*$" % ("#" * level), text, re.M)


def block(text, title, level):
    """Lines under the `level`-hash heading `title`, up to the next heading of the same or a higher level."""
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if line.strip() == "#" * level + " " + title) + 1
    stop = next((i for i in range(start, len(lines)) if re.match(r"#{1,%d} " % level, lines[i])), len(lines))
    return "\n".join(lines[start:stop])


class ShowcaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items = json.loads((SHOWCASE / "manifest.json").read_text(encoding="utf-8"))["items"]
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
        urls = [item["github_video_attachment"]["url"] for item in self.items if "github_video_attachment" in item]
        self.assertEqual(len(urls), len(set(urls)))
        for url in urls:
            self.assertTrue(ATTACHMENT_URL.fullmatch(url), url)
            for name, text in (("README.md", self.readme_cases), ("examples/showcase/README.md", self.case_page)):
                self.assertIn(f"\n{url}\n", f"\n{text}\n", f"{name}: the link must sit on its own line to render as a player")

    def test_case_titles_are_headings_on_both_pages(self):
        for item in self.items:
            self.assertIn(item["title"], headings(self.readme_cases, 4), f"README.md: {item['title']}")
            self.assertIn(item["title"], headings(self.case_page, 3), f"examples/showcase/README.md: {item['title']}")

    def test_readme_categories_match_the_case_page(self):
        readme_categories = headings(self.readme_cases, 3)
        page_categories = [h for h in headings(self.case_page, 2) if h not in NOT_CATEGORIES]
        self.assertEqual(readme_categories, page_categories)
        self.assertIn("产品宣传片", readme_categories)

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
