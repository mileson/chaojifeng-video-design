"""Product ledger: survey a source tree and check that the ledger closes. Stdlib only, no network."""
import contextlib
import copy
import io
import json
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

import product_ledger as pl

ROOT = Path(__file__).resolve().parents[1]


def png(width, height):
    def chunk(kind, data):
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)
    raw = b"".join(b"\x00" + b"\xff\x00\x00" * width for _ in range(height))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def run(argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        status = pl.main(argv)
    return status, out.getvalue(), err.getvalue()


def make_product(root):
    (root / "docs").mkdir()
    (root / "store").mkdir()
    (root / "node_modules" / "dep").mkdir(parents=True)
    (root / ".codex").mkdir()
    (root / "manifest.json").write_text(json.dumps({"manifest_version": 3, "name": "测试产品", "version": "1.2.3"}, ensure_ascii=False, indent=2), encoding="utf-8")
    (root / "README.md").write_text("# 测试产品\n\n可一次发到多个平台。\n免费用户每天 3 次，会员不限。\n", encoding="utf-8")
    (root / "docs" / "guide.md").write_text("# 使用指南\n\n第一步。\n", encoding="utf-8")
    (root / "AGENTS.md").write_text("# agent rules\n会员 付费 试用\n", encoding="utf-8")
    (root / "store" / "shot1.png").write_bytes(png(3, 2))
    (root / "node_modules" / "dep" / "notes.md").write_text("会员 付费\n", encoding="utf-8")
    (root / ".codex" / "note.md").write_text("会员 付费\n", encoding="utf-8")


def good_ledger():
    return {
        "schema_version": 1,
        "product": {"name": "测试产品", "version": "1.2.3", "audience": "运营同学", "positioning": "一次发到多个平台"},
        "emphasis": [{"id": "E1", "user_phrase": "一次发多个平台", "public_phrase": "一次发到多个平台", "viewer_gain": "省下重复操作",
                      "fact_ids": ["F01"], "chapter_id": "ch1", "status": "supported"}],
        "facts": [{"id": "F01", "statement": "可一次发到多个平台", "sources": [{"path": "README.md", "line": 3}],
                   "status": "verified", "public": True, "verified_by": ["source"]},
                  {"id": "F02", "statement": "会员不限次数", "sources": [{"path": "README.md", "line": 4}],
                   "status": "verified", "public": False, "verified_by": ["source"]},
                  {"id": "F03", "statement": "某渠道是否支持待查", "sources": [], "status": "unknown", "public": True}],
        "boundaries": [{"id": "B1", "kind": "membership", "statement": "不报价格", "reason": "价格易变",
                        "sources": [{"path": "README.md", "line": 4}], "avoid_terms": ["永久免费"]}],
        "evidence": [{"id": "V01", "kind": "run", "level": 1, "path": "assets/v01.png", "how": "本机加载当前版本后截图",
                      "build": "1.2.3", "captured_on": "2026-11-05", "fact_ids": ["F01"], "shows": "多平台选择",
                      "privacy": "clean", "status": "ready", "in_film": True}],
        "chapters": [{"id": "open", "role": "opening", "claim_ids": [], "evidence_ids": []},
                     {"id": "ch1", "role": "chapter", "emphasis_id": "E1", "claim_ids": ["C01"], "evidence_ids": ["V01"]}],
        "claims": [{"id": "C01", "text": "一次发到多个平台，不用重复操作", "fact_ids": ["F01"], "chapter_id": "ch1"}],
    }


class SurveyTests(unittest.TestCase):
    def test_init_reads_product_facts_and_skips_noise(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "product"
            source.mkdir()
            make_product(source)
            out = Path(tmp) / "ledger.json"
            status, stdout, _ = run(["init", str(source), "--out", str(out)])
            self.assertEqual(status, 0, stdout)
            ledger = json.loads(out.read_text(encoding="utf-8"))
            product = ledger["product"]
            self.assertEqual(product["name"], "测试产品")
            self.assertEqual(product["version"], "1.2.3")
            self.assertEqual(product["version_source"], "manifest.json:4")
            self.assertTrue(any("浏览器扩展" in p for p in product["platforms"]))
            candidates = ledger["candidates"]
            doc_paths = [d["path"] for d in candidates["docs"]]
            self.assertIn("README.md", doc_paths)
            self.assertIn("docs/guide.md", doc_paths)
            self.assertNotIn("AGENTS.md", doc_paths)
            visuals = {v["path"]: v for v in candidates["visuals"]}
            self.assertEqual(visuals["store/shot1.png"]["size"], [3, 2])
            self.assertTrue(visuals["store/shot1.png"]["store_like"])
            limit_paths = {x["path"] for x in candidates["limits"]}
            self.assertIn("README.md", limit_paths)
            self.assertFalse({"AGENTS.md", "node_modules/dep/notes.md", ".codex/note.md"} & limit_paths)
            for section in ("emphasis", "facts", "boundaries", "evidence", "chapters", "claims", "framings"):
                self.assertEqual(ledger[section], [])

    def test_init_does_not_overwrite_without_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "product"
            source.mkdir()
            make_product(source)
            out = Path(tmp) / "ledger.json"
            out.write_text("{}", encoding="utf-8")
            status, _, err = run(["init", str(source), "--out", str(out)])
            self.assertEqual(status, 2)
            self.assertIn("--force", err)
            self.assertEqual(out.read_text(encoding="utf-8"), "{}")
            status, _, _ = run(["init", str(source), "--out", str(out), "--force"])
            self.assertEqual(status, 0)

    def test_image_size_reads_png_header(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "a.png"
            path.write_bytes(png(7, 5))
            self.assertEqual(tuple(pl.image_size(path)), (7, 5))
            (Path(tmp) / "b.png").write_bytes(b"not an image")
            self.assertIsNone(pl.image_size(Path(tmp) / "b.png"))

    def test_init_rejects_missing_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            status, _, err = run(["init", str(Path(tmp) / "nope"), "--out", str(Path(tmp) / "l.json")])
            self.assertEqual(status, 2)
            self.assertIn("not a directory", err)


class CheckTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.source = Path(self.tmp.name) / "product"
        self.source.mkdir()
        make_product(self.source)
        self.evidence_root = Path(self.tmp.name) / "video"
        (self.evidence_root / "assets").mkdir(parents=True)
        (self.evidence_root / "assets" / "v01.png").write_bytes(png(2, 2))

    def check(self, ledger, **kwargs):
        kwargs.setdefault("source_root", self.source)
        kwargs.setdefault("evidence_root", self.evidence_root)
        return pl.check_ledger(ledger, **kwargs)

    def codes(self, issues, level="error"):
        return sorted({i["code"] for i in issues.items if i["level"] == level})

    def test_a_closed_ledger_passes(self):
        issues = self.check(good_ledger())
        self.assertEqual(self.codes(issues), [], issues.items)

    def test_missing_source_file_and_line_are_caught(self):
        ledger = good_ledger()
        ledger["facts"][0]["sources"] = [{"path": "nope.md", "line": 1}]
        self.assertIn("source_missing", self.codes(self.check(ledger)))
        ledger = good_ledger()
        ledger["facts"][0]["sources"] = [{"path": "README.md", "line": 99}]
        self.assertIn("line_out_of_range", self.codes(self.check(ledger)))
        ledger = good_ledger()
        ledger["facts"][0]["sources"] = [{"path": "../outside.md", "line": 1}]
        self.assertIn("path_escape", self.codes(self.check(ledger)))

    def test_without_source_root_the_gap_is_a_warning(self):
        issues = pl.check_ledger(good_ledger(), source_root=None, evidence_root=self.evidence_root)
        self.assertEqual(self.codes(issues), [])
        self.assertIn("source_not_checked", self.codes(issues, "warn"))

    def test_claims_may_only_use_verified_public_facts(self):
        ledger = good_ledger()
        ledger["claims"][0]["fact_ids"] = ["F03"]
        self.assertIn("fact_not_verified", self.codes(self.check(ledger)))
        ledger = good_ledger()
        ledger["claims"][0]["fact_ids"] = ["F02"]
        self.assertIn("fact_not_public", self.codes(self.check(ledger)))
        ledger = good_ledger()
        ledger["claims"][0]["fact_ids"] = ["F99"]
        self.assertIn("unknown_ref", self.codes(self.check(ledger)))

    def test_verified_fact_needs_a_source(self):
        ledger = good_ledger()
        ledger["facts"][0]["sources"] = []
        self.assertIn("fact_without_source", self.codes(self.check(ledger)))

    def test_every_claim_needs_evidence_for_the_same_fact(self):
        ledger = good_ledger()
        ledger["facts"].append({"id": "F04", "statement": "另一件事", "sources": [{"path": "README.md", "line": 3}],
                                "status": "verified", "public": True, "verified_by": ["source"]})
        ledger["claims"].append({"id": "C02", "text": "另一件事", "fact_ids": ["F04"], "chapter_id": "ch1"})
        ledger["chapters"][1]["claim_ids"].append("C02")
        self.assertIn("claim_without_evidence", self.codes(self.check(ledger)))
        ledger["evidence"][0]["fact_ids"].append("F04")
        self.assertEqual(self.codes(self.check(ledger)), [])

    def test_chapter_with_claims_but_no_ready_evidence_fails(self):
        ledger = good_ledger()
        ledger["evidence"][0]["status"] = "missing"
        issues = self.check(ledger)
        self.assertIn("chapter_without_evidence", self.codes(issues))
        self.assertIn("evidence_not_ready", self.codes(issues, "warn"))

    def test_supported_emphasis_needs_a_chapter_with_claims(self):
        ledger = good_ledger()
        ledger["chapters"][1]["claim_ids"] = []
        ledger["claims"] = []
        self.assertIn("emphasis_without_chapter", self.codes(self.check(ledger)))

    def test_narrowed_and_unsupported_need_a_reason(self):
        ledger = good_ledger()
        ledger["emphasis"][0]["status"] = "narrowed"
        self.assertIn("narrowed_without_note", self.codes(self.check(ledger)))
        ledger["emphasis"][0]["note"] = "只讲已核实的平台"
        self.assertEqual(self.codes(self.check(ledger)), [])
        ledger = good_ledger()
        ledger["emphasis"].append({"id": "E2", "user_phrase": "做不到的事", "status": "unsupported"})
        self.assertIn("unsupported_without_note", self.codes(self.check(ledger)))
        ledger["emphasis"][1]["note"] = "产品没有这个能力"
        self.assertEqual(self.codes(self.check(ledger)), [])

    def test_rebuilt_ui_in_the_film_needs_a_real_cross_check(self):
        ledger = good_ledger()
        ledger["evidence"].append({"id": "V02", "kind": "rebuild", "level": 4, "path": "assets/v01.png", "how": "按组件状态重建",
                                   "fact_ids": ["F01"], "privacy": "clean", "status": "ready", "in_film": True})
        self.assertIn("rebuild_in_film", self.codes(self.check(ledger)))
        ledger["evidence"][1]["cross_checked_with"] = "V01"
        self.assertEqual(self.codes(self.check(ledger)), [])

    def test_ready_evidence_must_be_redacted_and_present(self):
        ledger = good_ledger()
        ledger["evidence"][0]["privacy"] = "unchecked"
        self.assertIn("evidence_privacy", self.codes(self.check(ledger)))
        ledger = good_ledger()
        ledger["evidence"][0]["path"] = "assets/missing.png"
        self.assertIn("evidence_file_missing", self.codes(self.check(ledger)))
        ledger = good_ledger()
        ledger["evidence"][0]["level"] = 3
        self.assertIn("bad_level", self.codes(self.check(ledger)))

    def test_duplicate_ids_and_chapter_claim_mismatch(self):
        ledger = good_ledger()
        ledger["facts"].append(copy.deepcopy(ledger["facts"][0]))
        self.assertIn("duplicate_id", self.codes(self.check(ledger)))
        ledger = good_ledger()
        ledger["claims"][0]["chapter_id"] = "open"
        self.assertIn("claim_chapter_mismatch", self.codes(self.check(ledger)))

    def test_placeholders_block_an_unfinished_ledger(self):
        ledger = good_ledger()
        ledger["product"]["positioning"] = "<一句话定位>"
        self.assertIn("placeholder_left", self.codes(self.check(ledger)))

    def test_candidates_section_is_ignored(self):
        ledger = good_ledger()
        ledger["candidates"] = {"docs": [{"path": "<anything>"}]}
        self.assertEqual(self.codes(self.check(ledger)), [])

    def test_avoid_terms_are_scanned_with_line_numbers(self):
        script = Path(self.tmp.name) / "narration.txt"
        script.write_text("第一句。\n这个产品永久免费。\n一次发到多个平台，不用重复操作。\n", encoding="utf-8")
        issues = self.check(good_ledger(), scripts=[script])
        hits = [i for i in issues.items if i["code"] == "avoid_term_hit"]
        self.assertEqual(len(hits), 1)
        self.assertTrue(hits[0]["where"].endswith("narration.txt:2"))
        self.assertEqual(self.codes(issues, "warn"), [])

    def test_claim_missing_from_the_script_is_a_warning_only(self):
        script = Path(self.tmp.name) / "narration.txt"
        script.write_text("完全不同的一句话。\n", encoding="utf-8")
        issues = self.check(good_ledger(), scripts=[script])
        self.assertEqual(self.codes(issues), [])
        self.assertIn("claim_not_in_script", self.codes(issues, "warn"))

    def framed(self):
        ledger = good_ledger()
        ledger["framings"] = [
            {"id": "P01", "kind": "pain", "chapter_id": "open", "text": "一份内容要发好几个平台，是不是很费时间？", "boundary_ids": []},
            {"id": "P02", "kind": "worry", "chapter_id": "open", "text": "又怕被平台限流。", "boundary_ids": ["B1"],
             "note": "只是观众的顾虑，片中不承诺结果"},
            {"id": "P03", "kind": "question", "chapter_id": "open", "text": "有没有一款能一次发到多个平台的？", "boundary_ids": []},
        ]
        return ledger

    def test_framings_are_optional_and_a_valid_set_passes(self):
        self.assertEqual(self.codes(self.check(good_ledger())), [])
        issues = self.check(self.framed())
        self.assertEqual(self.codes(issues), [], issues.items)
        self.assertEqual(self.codes(issues, "warn"), [])

    def test_framing_needs_a_kind_a_chapter_and_a_text(self):
        ledger = self.framed()
        ledger["framings"][0]["kind"] = "claim"
        self.assertIn("bad_kind", self.codes(self.check(ledger)))
        ledger = self.framed()
        ledger["framings"][0]["chapter_id"] = "nope"
        self.assertIn("unknown_ref", self.codes(self.check(ledger)))
        ledger = self.framed()
        ledger["framings"][0]["text"] = ""
        self.assertIn("missing_field", self.codes(self.check(ledger)))
        ledger = self.framed()
        ledger["framings"][2]["boundary_ids"] = ["B9"]
        self.assertIn("unknown_ref", self.codes(self.check(ledger)))

    def test_a_framing_outside_the_opening_is_only_a_warning(self):
        ledger = self.framed()
        ledger["framings"][0]["chapter_id"] = "ch1"
        issues = self.check(ledger)
        self.assertEqual(self.codes(issues), [])
        self.assertIn("framing_outside_opening", self.codes(issues, "warn"))

    def test_a_worry_must_name_its_boundary_and_say_it_is_no_promise(self):
        ledger = self.framed()
        ledger["framings"][1]["boundary_ids"] = []
        self.assertIn("worry_without_boundary", self.codes(self.check(ledger)))
        ledger = self.framed()
        del ledger["framings"][1]["note"]
        self.assertIn("worry_without_note", self.codes(self.check(ledger)))

    def test_framings_are_not_claims_and_need_no_fact(self):
        ledger = self.framed()
        for framing in ledger["framings"]:
            self.assertNotIn("fact_ids", framing)
        self.assertEqual(self.codes(self.check(ledger)), [])

    def test_avoid_terms_also_cover_framing_lines_through_the_script(self):
        script = Path(self.tmp.name) / "narration.txt"
        script.write_text("有没有一款永久免费的？\n一次发到多个平台，不用重复操作。\n", encoding="utf-8")
        issues = self.check(self.framed(), scripts=[script])
        self.assertEqual(len([i for i in issues.items if i["code"] == "avoid_term_hit"]), 1)

    def test_framing_missing_from_the_script_is_a_warning_only(self):
        script = Path(self.tmp.name) / "narration.txt"
        script.write_text("一份内容要发好几个平台，是不是很费时间？\n又怕被平台限流。\n一次发到多个平台，不用重复操作。\n", encoding="utf-8")
        issues = self.check(self.framed(), scripts=[script])
        self.assertEqual(self.codes(issues), [])
        warns = [i for i in issues.items if i["code"] == "framing_not_in_script"]
        self.assertEqual([w["where"] for w in warns], ["framings[P03]"])

    def test_cli_exit_codes_and_json(self):
        ledger_path = Path(self.tmp.name) / "ledger.json"
        ledger_path.write_text(json.dumps(good_ledger(), ensure_ascii=False), encoding="utf-8")
        status, stdout, _ = run(["check", str(ledger_path), "--source", str(self.source), "--evidence-root", str(self.evidence_root), "--json"])
        self.assertEqual(status, 0, stdout)
        self.assertTrue(json.loads(stdout)["ok"])
        broken = good_ledger()
        broken["facts"][0]["sources"] = []
        ledger_path.write_text(json.dumps(broken, ensure_ascii=False), encoding="utf-8")
        status, stdout, _ = run(["check", str(ledger_path), "--source", str(self.source)])
        self.assertEqual(status, 1)
        self.assertIn("NOT CLOSED", stdout)
        status, _, err = run(["check", str(Path(self.tmp.name) / "none.json")])
        self.assertEqual(status, 2)
        self.assertIn("cannot read ledger", err)


class TemplateTests(unittest.TestCase):
    def test_shipped_template_is_structurally_valid_and_only_has_placeholders(self):
        template = json.loads((ROOT / "templates" / "product-ledger.json").read_text(encoding="utf-8"))
        issues = pl.check_ledger(template)
        errors = {i["code"] for i in issues.items if i["level"] == "error"}
        self.assertEqual(errors, {"placeholder_left"}, issues.items)

    def test_template_without_placeholders_closes(self):
        text = (ROOT / "templates" / "product-ledger.json").read_text(encoding="utf-8")
        text = pl.PLACEHOLDER.sub("已填写", text)
        issues = pl.check_ledger(json.loads(text))
        self.assertEqual([i for i in issues.items if i["level"] == "error"], [], issues.items)


if __name__ == "__main__":
    unittest.main()
