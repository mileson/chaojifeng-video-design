#!/usr/bin/env python3
"""Product source ledger for source-driven product explainer films.

init  SOURCE --out LEDGER   survey a product source tree and write a ledger skeleton
check LEDGER                check that facts, emphasis, evidence, chapters and claims close

The source tree is only read: nothing is executed, imported, installed or sent anywhere.
The check proves the ledger is internally closed and that cited sources exist; it cannot
prove a fact is true or replace running the real product to capture evidence.

Optional "framings" register the opening lines that speak for the viewer (a pain, a worry,
a question). They are not product claims, so they need no fact; a worry must name the
boundary that stops the film from promising its opposite.
"""
import argparse
import datetime
import json
import os
import re
import struct
import sys
from pathlib import Path

SCHEMA_VERSION = 1
SKIP_DIRS = {
    ".git", "node_modules", "dist", "build", "Output", "output", ".next", ".venv", "venv", "__pycache__",
    "Pods", "DerivedData", ".gradle", ".idea", ".cursor", ".claude", ".openprd", "coverage", "downloads",
    "tmp", ".cache", ".pytest_cache", ".smoketest", "vendor",
}
TEXT_SUFFIX = {
    ".md", ".txt", ".json", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".html", ".css", ".py", ".swift",
    ".kt", ".java", ".yaml", ".yml", ".toml", ".plist", ".gradle", ".kts", ".vue", ".dart", ".strings", ".go", ".rs",
}
DOC_SUFFIX = {".md", ".txt"}
AGENT_DOCS = {"AGENTS.md", "CLAUDE.md", "GEMINI.md"}
IMAGE_SUFFIX = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}
VIDEO_SUFFIX = {".mp4", ".mov", ".webm"}
LIMIT_PATTERN = re.compile(
    r"(配额|会员|付费|免费|限额|每日|每天|试用|订阅|默认关闭|默认开启|quota|limit|premium|subscription|trial|"
    r"free tier|paid|membership|enabled\s*[:=]\s*false|default\w*\s*[:=]\s*(false|off))",
    re.IGNORECASE,
)
MAX_TEXT_BYTES = 400_000
MAX_LIMIT_HITS = 60
MAX_VISUALS = 80
MAX_DOCS = 40

FACT_STATUS = {"verified", "unknown"}
EMPHASIS_STATUS = {"supported", "narrowed", "unsupported"}
BOUNDARY_KIND = {"membership", "reserved", "unverified", "policy", "license", "privacy", "other"}
EVIDENCE_LEVEL = {"run": 1, "store": 2, "fixture": 3, "rebuild": 4}
PRIVACY_OK = {"clean", "redacted"}
CHAPTER_ROLE = {"opening", "chapter", "closing"}
FRAMING_KIND = {"pain", "worry", "question"}
PLACEHOLDER = re.compile(r"<[^<>\n]{1,80}>")
PUNCT = re.compile(r"[\s，。、；：！？,.;:!?“”\"'‘’（）()\[\]【】《》—\-…·]+")


# ---------------------------------------------------------------- helpers

def read_text(path):
    try:
        if path.stat().st_size > MAX_TEXT_BYTES:
            return None
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def walk(root):
    """Visible product files only: hidden directories hold tool and agent configuration, not product facts."""
    for base, dirs, files in os.walk(str(root)):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not d.startswith("."))
        for name in sorted(files):
            yield Path(base) / name


def rel(root, path):
    return path.relative_to(root).as_posix()


def image_size(path):
    """Return (width, height) for PNG, GIF, JPEG and WebP headers, else None."""
    try:
        with open(str(path), "rb") as f:
            head = f.read(32)
            if head.startswith(b"\x89PNG\r\n\x1a\n") and len(head) >= 24:
                return struct.unpack(">II", head[16:24])
            if head[:6] in (b"GIF87a", b"GIF89a"):
                return struct.unpack("<HH", head[6:10])
            if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
                kind = head[12:16]
                if kind == b"VP8X":
                    return (1 + int.from_bytes(head[24:27], "little"), 1 + int.from_bytes(head[27:30], "little"))
                if kind == b"VP8L":
                    bits = int.from_bytes(head[21:25], "little")
                    return ((bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1)
                if kind == b"VP8 ":
                    return (int.from_bytes(head[26:28], "little") & 0x3FFF, int.from_bytes(head[28:30], "little") & 0x3FFF)
            if head[:2] == b"\xff\xd8":
                f.seek(2)
                while True:
                    byte = f.read(1)
                    if not byte:
                        return None
                    if byte != b"\xff":
                        continue
                    marker = f.read(1)
                    while marker == b"\xff":
                        marker = f.read(1)
                    if not marker:
                        return None
                    if marker in (b"\xd8", b"\x01") or b"\xd0" <= marker <= b"\xd7":
                        continue
                    length = struct.unpack(">H", f.read(2))[0]
                    if marker in (b"\xc0", b"\xc1", b"\xc2", b"\xc3", b"\xc5", b"\xc6", b"\xc7", b"\xc9", b"\xca", b"\xcb", b"\xcd", b"\xce", b"\xcf"):
                        f.read(1)
                        height, width = struct.unpack(">HH", f.read(4))
                        return (width, height)
                    f.seek(length - 2, 1)
    except (OSError, struct.error):
        return None
    return None


def find_line(text, pattern):
    regex = re.compile(pattern)
    for number, line in enumerate(text.splitlines(), 1):
        match = regex.search(line)
        if match:
            return number, match
    return None, None


# ---------------------------------------------------------------- survey

def survey_product(root):
    names, versions, platforms = [], [], []

    def add_version(path, value, line):
        versions.append({"value": value, "path": rel(root, path), "line": line})

    for path in walk(root):
        depth = len(path.relative_to(root).parts)
        if depth > 3:
            continue
        name = path.name
        text = None
        if name in ("manifest.json", "package.json", "pubspec.yaml", "pyproject.toml", "Cargo.toml", "project.config.json") or name.endswith(".gradle") or name.endswith(".kts") or name == "project.pbxproj":
            text = read_text(path)
        if text is None:
            if name == "Package.swift" or name == "AndroidManifest.xml":
                platforms.append("Apple 平台" if name == "Package.swift" else "Android")
            continue
        if name == "manifest.json":
            try:
                data = json.loads(text)
            except ValueError:
                data = {}
            if isinstance(data, dict) and "manifest_version" in data:
                platforms.append("浏览器扩展（MV%s）" % data.get("manifest_version"))
                if data.get("name"):
                    line, _ = find_line(text, r'"name"\s*:')
                    names.append({"value": data["name"], "path": rel(root, path), "line": line})
                if data.get("version"):
                    line, _ = find_line(text, r'"version"\s*:')
                    add_version(path, data["version"], line)
        elif name == "package.json":
            try:
                data = json.loads(text)
            except ValueError:
                data = {}
            if isinstance(data, dict):
                platforms.append("Web／Node")
                if data.get("name"):
                    line, _ = find_line(text, r'"name"\s*:')
                    names.append({"value": data["name"], "path": rel(root, path), "line": line})
                if data.get("version"):
                    line, _ = find_line(text, r'"version"\s*:')
                    add_version(path, data["version"], line)
        elif name == "pubspec.yaml":
            platforms.append("Flutter")
            for key, bucket in (("name", names), ("version", versions)):
                line, match = find_line(text, r"^%s:\s*(\S+)" % key)
                if match:
                    entry = {"value": match.group(1), "path": rel(root, path), "line": line}
                    bucket.append(entry)
        elif name in ("pyproject.toml", "Cargo.toml"):
            platforms.append("Python" if name == "pyproject.toml" else "Rust")
            for key, bucket in (("name", names), ("version", versions)):
                line, match = find_line(text, r'^%s\s*=\s*"([^"]+)"' % key)
                if match:
                    bucket.append({"value": match.group(1), "path": rel(root, path), "line": line})
        elif name == "project.pbxproj":
            platforms.append("Apple 平台")
            line, match = find_line(text, r"MARKETING_VERSION\s*=\s*([^;\s]+)")
            if match:
                add_version(path, match.group(1), line)
            line, match = find_line(text, r"PRODUCT_NAME\s*=\s*\"?([^;\"\s]+)")
            if match and "$(" not in match.group(1):
                names.append({"value": match.group(1), "path": rel(root, path), "line": line})
        elif name.endswith(".gradle") or name.endswith(".kts"):
            platforms.append("Android")
            line, match = find_line(text, r'versionName\s*[=\s]\s*"([^"]+)"')
            if match:
                add_version(path, match.group(1), line)
        elif name == "project.config.json":
            platforms.append("微信小程序")
    for readme in sorted(root.glob("README*")):
        text = read_text(readme)
        if text:
            line, match = find_line(text, r"^#\s+(.+)$")
            if match:
                names.append({"value": match.group(1).strip(), "path": rel(root, readme), "line": line})
            break
    return names, versions, sorted(set(platforms))


def survey_docs(root):
    docs = []
    for path in walk(root):
        suffix = path.suffix.lower()
        relative = rel(root, path)
        if suffix not in DOC_SUFFIX or path.name in AGENT_DOCS:
            continue
        parts = path.relative_to(root).parts
        interesting = (
            len(parts) == 1
            or parts[0].lower() in ("docs", "doc", "documentation")
            or any(key in relative.lower() for key in ("store", "listing", "changelog", "release", "商店", "发布"))
        )
        if not interesting:
            continue
        text = read_text(path) or ""
        _, match = find_line(text, r"^#\s+(.+)$")
        docs.append({"path": relative, "bytes": path.stat().st_size, "title": match.group(1).strip() if match else ""})
        if len(docs) >= MAX_DOCS:
            break
    return docs


def survey_visuals(root):
    visuals = []
    for path in walk(root):
        suffix = path.suffix.lower()
        if suffix not in IMAGE_SUFFIX and suffix not in VIDEO_SUFFIX:
            continue
        relative = rel(root, path)
        stat = path.stat()
        item = {
            "path": relative,
            "bytes": stat.st_size,
            "modified": datetime.date.fromtimestamp(stat.st_mtime).isoformat(),
            "store_like": any(key in relative.lower() for key in ("store", "screenshot", "商店", "截图", "preview")),
        }
        if suffix in IMAGE_SUFFIX and suffix != ".svg":
            size = image_size(path)
            if size:
                item["size"] = [int(size[0]), int(size[1])]
        visuals.append(item)
    # store-like first, newest first: freshness is the first thing to check against the current UI
    visuals.sort(key=lambda x: x["path"])
    visuals.sort(key=lambda x: x["modified"], reverse=True)
    visuals.sort(key=lambda x: not x["store_like"])
    return visuals[:MAX_VISUALS]


def survey_limits(root):
    hits = []
    order = {".md": 0, ".txt": 0, ".json": 1, ".yaml": 1, ".yml": 1, ".toml": 1, ".plist": 1}
    files = [p for p in walk(root) if p.suffix.lower() in TEXT_SUFFIX and p.name not in AGENT_DOCS]
    files.sort(key=lambda p: (order.get(p.suffix.lower(), 2), rel(root, p)))
    for path in files:
        text = read_text(path)
        if not text:
            continue
        count = 0
        for number, line in enumerate(text.splitlines(), 1):
            match = LIMIT_PATTERN.search(line)
            if match and len(line) <= 400:
                hits.append({"path": rel(root, path), "line": number, "term": match.group(1), "excerpt": line.strip()[:120]})
                count += 1
                if count >= 4:
                    break
        if len(hits) >= MAX_LIMIT_HITS:
            break
    return hits[:MAX_LIMIT_HITS]


def cmd_init(args):
    root = Path(args.source).expanduser().resolve()
    if not root.is_dir():
        print("source is not a directory: %s" % root, file=sys.stderr)
        return 2
    out = Path(args.out).expanduser()
    if out.exists() and not args.force:
        print("refusing to overwrite %s (use --force)" % out, file=sys.stderr)
        return 2
    names, versions, platforms = survey_product(root)
    ledger = {
        "schema_version": SCHEMA_VERSION,
        "product": {
            "name": names[0]["value"] if names else "",
            "dir_name": root.name,
            "version": versions[0]["value"] if versions else "",
            "version_source": ("%s:%s" % (versions[0]["path"], versions[0]["line"])) if versions else "",
            "platforms": platforms,
            "audience": "",
            "positioning": "",
            "positioning_source": "",
            "source_root": str(root),
            "surveyed_on": datetime.date.today().isoformat(),
        },
        "emphasis": [], "facts": [], "boundaries": [], "evidence": [], "chapters": [], "claims": [], "framings": [],
        "candidates": {
            "note": "起点而非事实：每一条都要打开原文核对，核对后写入 facts 或 boundaries。check 忽略本部分。",
            "names": names, "versions": versions, "docs": survey_docs(root),
            "visuals": survey_visuals(root), "limits": survey_limits(root),
        },
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    cand = ledger["candidates"]
    print("ledger skeleton: %s" % out)
    print("product=%r version=%r platforms=%s" % (ledger["product"]["name"], ledger["product"]["version"], platforms))
    print("candidates: docs=%d visuals=%d limits=%d versions=%d" % (len(cand["docs"]), len(cand["visuals"]), len(cand["limits"]), len(versions)))
    if len(versions) > 1 and len({v["value"] for v in versions}) > 1:
        print("warning: several different versions found; confirm which one ships")
    return 0


# ---------------------------------------------------------------- check

class Issues:
    def __init__(self):
        self.items = []

    def add(self, level, code, where, message):
        self.items.append({"level": level, "code": code, "where": where, "message": message})

    def error(self, code, where, message):
        self.add("error", code, where, message)

    def warn(self, code, where, message):
        self.add("warn", code, where, message)

    @property
    def errors(self):
        return [i for i in self.items if i["level"] == "error"]

    @property
    def warnings(self):
        return [i for i in self.items if i["level"] == "warn"]


def as_list(value):
    return value if isinstance(value, list) else []


def walk_strings(value, path=""):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from walk_strings(item, "%s.%s" % (path, key) if path else key)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from walk_strings(item, "%s[%d]" % (path, index))


def index_ids(items, section, issues):
    seen = {}
    for position, item in enumerate(as_list(items)):
        if not isinstance(item, dict):
            issues.error("bad_item", "%s[%d]" % (section, position), "条目必须是对象")
            continue
        ident = item.get("id")
        if not isinstance(ident, str) or not ident.strip():
            issues.error("missing_field", "%s[%d]" % (section, position), "缺少 id")
            continue
        if ident in seen:
            issues.error("duplicate_id", "%s[%s]" % (section, ident), "id 重复")
            continue
        seen[ident] = item
    return seen


def need(item, field, where, issues):
    value = item.get(field)
    if value is None or (isinstance(value, str) and not value.strip()) or (isinstance(value, list) and not value):
        issues.error("missing_field", where, "缺少 %s" % field)
        return False
    return True


def check_sources(item, where, root, issues):
    sources = as_list(item.get("sources"))
    for source in sources:
        if not isinstance(source, dict) or not isinstance(source.get("path"), str) or not source["path"].strip():
            issues.error("bad_source", where, "来源需要 path")
            continue
        if root is None:
            continue
        target = (root / source["path"]).resolve()
        if target != root and root not in target.parents:
            issues.error("path_escape", where, "来源路径越出源码根：%s" % source["path"])
            continue
        if not target.is_file():
            issues.error("source_missing", where, "来源不存在：%s" % source["path"])
            continue
        line = source.get("line")
        if line is not None:
            if not isinstance(line, int) or line < 1:
                issues.error("line_out_of_range", where, "行号必须是正整数：%s" % source["path"])
                continue
            try:
                with open(str(target), "r", encoding="utf-8", errors="replace") as handle:
                    total = sum(1 for _ in handle)
            except OSError:
                continue
            if line > total:
                issues.error("line_out_of_range", where, "%s 只有 %d 行，引用了第 %d 行" % (source["path"], total, line))


def normalize(text):
    return PUNCT.sub("", text).lower()


def check_ledger(ledger, source_root=None, evidence_root=None, scripts=None):
    issues = Issues()
    if not isinstance(ledger, dict):
        issues.error("schema_version", "ledger", "账本必须是对象")
        return issues
    if ledger.get("schema_version") != SCHEMA_VERSION:
        issues.error("schema_version", "schema_version", "schema_version 必须是 %d" % SCHEMA_VERSION)
    for where, text in walk_strings({k: v for k, v in ledger.items() if k != "candidates"}):
        if PLACEHOLDER.search(text):
            issues.error("placeholder_left", where, "仍有未填的占位：%s" % PLACEHOLDER.search(text).group(0))
    root = Path(source_root).expanduser().resolve() if source_root else None
    if root is not None and not root.is_dir():
        issues.error("source_root", "--source", "源码根不是目录")
        root = None
    if root is None:
        issues.warn("source_not_checked", "--source", "未提供源码根，来源是否存在没有核对")

    product = ledger.get("product") if isinstance(ledger.get("product"), dict) else {}
    if not product:
        issues.error("missing_field", "product", "缺少 product")
    for field in ("name", "audience", "positioning"):
        need(product, field, "product.%s" % field, issues)
    if not str(product.get("version") or "").strip():
        issues.warn("version_missing", "product.version", "没有版本号：取证和口径无法对应到具体版本")

    facts = index_ids(ledger.get("facts"), "facts", issues)
    emphasis = index_ids(ledger.get("emphasis"), "emphasis", issues)
    boundaries = index_ids(ledger.get("boundaries"), "boundaries", issues)
    evidence = index_ids(ledger.get("evidence"), "evidence", issues)
    chapters = index_ids(ledger.get("chapters"), "chapters", issues)
    claims = index_ids(ledger.get("claims"), "claims", issues)
    framings = index_ids(ledger.get("framings"), "framings", issues)

    for ident, fact in facts.items():
        where = "facts[%s]" % ident
        need(fact, "statement", where, issues)
        if fact.get("status") not in FACT_STATUS:
            issues.error("bad_status", where, "status 必须是 verified 或 unknown")
        if not isinstance(fact.get("public"), bool):
            issues.error("missing_field", where, "public 必须是 true 或 false")
        if fact.get("status") == "verified":
            if not as_list(fact.get("sources")):
                issues.error("fact_without_source", where, "verified 事实必须有来源")
            if not as_list(fact.get("verified_by")):
                issues.warn("verified_by_missing", where, "没有写 verified_by（源码、运行、商店文案、测试等）")
        check_sources(fact, where, root, issues)

    for ident, item in boundaries.items():
        where = "boundaries[%s]" % ident
        need(item, "statement", where, issues)
        need(item, "reason", where, issues)
        if item.get("kind") not in BOUNDARY_KIND:
            issues.error("bad_kind", where, "kind 必须是 %s" % "、".join(sorted(BOUNDARY_KIND)))
        if not as_list(item.get("avoid_terms")):
            issues.warn("boundary_without_terms", where, "没有禁用词，稿件扫描覆盖不到这条边界")
        check_sources(item, where, root, issues)

    for ident, item in evidence.items():
        where = "evidence[%s]" % ident
        kind = item.get("kind")
        if kind not in EVIDENCE_LEVEL:
            issues.error("bad_kind", where, "kind 必须是 run、store、fixture 或 rebuild")
            continue
        if item.get("level") != EVIDENCE_LEVEL[kind]:
            issues.error("bad_level", where, "kind=%s 对应 level=%d" % (kind, EVIDENCE_LEVEL[kind]))
        if item.get("status") not in ("ready", "missing"):
            issues.error("bad_status", where, "status 必须是 ready 或 missing")
        for ref in as_list(item.get("fact_ids")):
            if ref not in facts:
                issues.error("unknown_ref", where, "fact_ids 引用了不存在的事实 %s" % ref)
        if item.get("status") == "ready":
            need(item, "path", where, issues)
            need(item, "how", where, issues)
            need(item, "fact_ids", where, issues)
            if item.get("privacy") not in PRIVACY_OK:
                issues.error("evidence_privacy", where, "就绪的证据必须是 clean 或 redacted")
            if evidence_root and isinstance(item.get("path"), str) and item["path"].strip():
                if not (Path(evidence_root).expanduser() / item["path"]).is_file():
                    issues.error("evidence_file_missing", where, "文件不存在：%s" % item["path"])
        if kind == "rebuild" and item.get("in_film"):
            partner = evidence.get(item.get("cross_checked_with"))
            if not partner or partner.get("kind") == "rebuild" or partner.get("status") != "ready":
                issues.error("rebuild_in_film", where, "重建的界面进成片前，必须与一份就绪的真实证据对照（cross_checked_with）")

    for ident, item in claims.items():
        where = "claims[%s]" % ident
        need(item, "text", where, issues)
        need(item, "fact_ids", where, issues)
        for ref in as_list(item.get("fact_ids")):
            fact = facts.get(ref)
            if fact is None:
                issues.error("unknown_ref", where, "引用了不存在的事实 %s" % ref)
            elif fact.get("status") != "verified":
                issues.error("fact_not_verified", where, "主张引用了未核实的事实 %s" % ref)
            elif fact.get("public") is not True:
                issues.error("fact_not_public", where, "主张引用了不可对外的事实 %s" % ref)
        if item.get("chapter_id") not in chapters:
            issues.error("unknown_ref", where, "chapter_id 指向不存在的章节")

    chapter_of_emphasis = {}
    for ident, chapter in chapters.items():
        where = "chapters[%s]" % ident
        role = chapter.get("role")
        if role not in CHAPTER_ROLE:
            issues.error("bad_kind", where, "role 必须是 opening、chapter 或 closing")
        if role == "chapter":
            if chapter.get("emphasis_id") not in emphasis:
                issues.error("unknown_ref", where, "chapter 必须对应一个存在的侧重点")
            else:
                chapter_of_emphasis.setdefault(chapter["emphasis_id"], []).append(ident)
        claim_ids = [c for c in as_list(chapter.get("claim_ids"))]
        evidence_ids = [e for e in as_list(chapter.get("evidence_ids"))]
        for ref in claim_ids:
            if ref not in claims:
                issues.error("unknown_ref", where, "claim_ids 引用了不存在的主张 %s" % ref)
            elif claims[ref].get("chapter_id") != ident:
                issues.error("claim_chapter_mismatch", where, "主张 %s 属于另一个章节" % ref)
        for ref in evidence_ids:
            if ref not in evidence:
                issues.error("unknown_ref", where, "evidence_ids 引用了不存在的证据 %s" % ref)
        for ref, claim in claims.items():
            if claim.get("chapter_id") == ident and ref not in claim_ids:
                issues.error("claim_chapter_mismatch", where, "主张 %s 声明属于本章，但本章没有列出" % ref)
        ready = [evidence[e] for e in evidence_ids if e in evidence and evidence[e].get("status") == "ready"]
        for ref in evidence_ids:
            if ref in evidence and evidence[ref].get("status") != "ready":
                issues.warn("evidence_not_ready", where, "证据 %s 还没就绪，不计入覆盖" % ref)
        if claim_ids and not ready:
            issues.error("chapter_without_evidence", where, "章节有口播主张，却没有就绪的证据")
        covered = set()
        for item in ready:
            covered.update(as_list(item.get("fact_ids")))
        for ref in claim_ids:
            claim = claims.get(ref)
            if not claim:
                continue
            missing = [f for f in as_list(claim.get("fact_ids")) if f not in covered]
            if missing and ready:
                issues.error("claim_without_evidence", where, "主张 %s 的事实 %s 没有任何本章证据支撑同一件事" % (ref, "、".join(missing)))

    for ident, item in emphasis.items():
        where = "emphasis[%s]" % ident
        status = item.get("status")
        if status not in EMPHASIS_STATUS:
            issues.error("bad_status", where, "status 必须是 supported、narrowed 或 unsupported")
            continue
        need(item, "user_phrase", where, issues)
        if status in ("narrowed", "unsupported") and not str(item.get("note") or "").strip():
            issues.error("%s_without_note" % status, where, "%s 必须写明原因" % status)
        if status in ("supported", "narrowed"):
            need(item, "public_phrase", where, issues)
            need(item, "viewer_gain", where, issues)
            if need(item, "fact_ids", where, issues):
                for ref in as_list(item.get("fact_ids")):
                    fact = facts.get(ref)
                    if fact is None:
                        issues.error("unknown_ref", where, "引用了不存在的事实 %s" % ref)
                    elif fact.get("status") != "verified":
                        issues.error("fact_not_verified", where, "侧重点引用了未核实的事实 %s" % ref)
            linked = chapter_of_emphasis.get(ident, [])
            if not any(as_list(chapters[c].get("claim_ids")) for c in linked):
                issues.error("emphasis_without_chapter", where, "成立的侧重点没有带口播主张的章节")
            if item.get("chapter_id") and item["chapter_id"] not in linked:
                issues.error("emphasis_chapter_mismatch", where, "chapter_id 与章节里的 emphasis_id 对不上")
        elif chapter_of_emphasis.get(ident):
            issues.warn("unsupported_with_chapter", where, "不成立的侧重点不应有章节")

    for ident, item in framings.items():
        where = "framings[%s]" % ident
        need(item, "text", where, issues)
        kind = item.get("kind")
        if kind not in FRAMING_KIND:
            issues.error("bad_kind", where, "kind 必须是 %s" % "、".join(sorted(FRAMING_KIND)))
        chapter = chapters.get(item.get("chapter_id"))
        if chapter is None:
            issues.error("unknown_ref", where, "chapter_id 指向不存在的章节")
        elif chapter.get("role") != "opening":
            issues.warn("framing_outside_opening", where, "替观众说话的句子通常放在开场章节")
        boundary_ids = as_list(item.get("boundary_ids"))
        for ref in boundary_ids:
            if ref not in boundaries:
                issues.error("unknown_ref", where, "boundary_ids 引用了不存在的边界 %s" % ref)
        if kind == "worry":
            if not boundary_ids:
                issues.error("worry_without_boundary", where, "顾虑要登记由哪条边界收住：片中不能承诺它的反面")
            if not str(item.get("note") or "").strip():
                issues.error("worry_without_note", where, "顾虑必须写明：只是观众的顾虑，不是产品承诺，片中怎样收住")

    if scripts:
        check_scripts(scripts, boundaries, claims, issues, framings)
    return issues


def check_scripts(paths, boundaries, claims, issues, framings=None):
    texts = []
    for path in paths:
        try:
            text = Path(path).expanduser().read_text(encoding="utf-8")
        except OSError as exc:
            issues.error("script_unreadable", str(path), str(exc))
            continue
        texts.append((str(path), text))
        for ident, item in boundaries.items():
            for term in as_list(item.get("avoid_terms")):
                if not isinstance(term, str) or not term.strip():
                    continue
                for number, line in enumerate(text.splitlines(), 1):
                    if term.lower() in line.lower():
                        issues.error("avoid_term_hit", "%s:%d" % (path, number), "稿件出现边界 %s 的禁用词“%s”" % (ident, term))
    whole = normalize("\n".join(t for _, t in texts))
    if texts:
        for ident, claim in claims.items():
            text = claim.get("text")
            if isinstance(text, str) and text.strip() and normalize(text) not in whole:
                issues.warn("claim_not_in_script", "claims[%s]" % ident, "主张原句没有在稿件中找到，可能已改写，请同步账本")
        for ident, framing in (framings or {}).items():
            text = framing.get("text")
            if isinstance(text, str) and text.strip() and normalize(text) not in whole:
                issues.warn("framing_not_in_script", "framings[%s]" % ident, "开场句原文没有在稿件中找到，可能已改写，请同步账本")


def cmd_check(args):
    try:
        ledger = json.loads(Path(args.ledger).expanduser().read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print("cannot read ledger: %s" % exc, file=sys.stderr)
        return 2
    issues = check_ledger(ledger, args.source, args.evidence_root, args.script)
    if args.json:
        print(json.dumps({"ok": not issues.errors, "errors": len(issues.errors), "warnings": len(issues.warnings), "issues": issues.items}, ensure_ascii=False, indent=2))
    else:
        for item in issues.items:
            print("%s %s %s: %s" % (item["level"].upper(), item["code"], item["where"], item["message"]))
        print("ledger %s: %d error(s), %d warning(s)" % ("OK" if not issues.errors else "NOT CLOSED", len(issues.errors), len(issues.warnings)))
    return 1 if issues.errors else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="survey a source tree and write a ledger skeleton")
    init.add_argument("source")
    init.add_argument("--out", required=True)
    init.add_argument("--force", action="store_true")
    init.set_defaults(func=cmd_init)
    check = sub.add_parser("check", help="check that the ledger closes")
    check.add_argument("ledger")
    check.add_argument("--source", help="source root used to verify cited paths and lines")
    check.add_argument("--evidence-root", help="directory that evidence paths are relative to")
    check.add_argument("--script", action="append", help="narration or caption text to scan for avoid_terms (repeatable)")
    check.add_argument("--json", action="store_true")
    check.set_defaults(func=cmd_check)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
