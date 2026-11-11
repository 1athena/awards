#!/usr/bin/env python3
"""Check pilot mappings and render their public Markdown using only the stdlib.

This checks repository consistency, not mathematical or reward qualification.
It makes no network calls and never executes submitted proof code.
"""

import argparse
from datetime import datetime
import json
from pathlib import Path
import re
import sys

from candidate_register import candidate_records, public_name

ROOT = Path(__file__).resolve().parents[1]
BEGIN = "<!-- BEGIN MathDB pilot metadata -->"
END = "<!-- END MathDB pilot metadata -->"
ELIGIBILITY = "[See MathDB pilot](mathdb-pilot.md#pilot-register)"
CATEGORIES = ("Solution", "Lean", "Exposition")
INDEX_CATEGORIES = ("Solution", "Lean")
INDEX_COLUMNS = ("No.", "Problem", "Current status", "Lean proof", "Eligible to claim",
                 "Solver claim status", "Lean claim status")


class InvalidPilot(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise InvalidPilot(message)


def is_safe_relative(path, root):
    """Check that path resolves safely inside root across Python versions."""
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (ValueError, AttributeError):
        return False


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def plain(value, label):
    require(isinstance(value, str) and value.strip(), f"Missing {label}")
    require(not any(c in value for c in "\n\r|<"), f"Unsafe Markdown in {label}")


def https_link(value, label):
    require(isinstance(value, str) and re.fullmatch(r"https://[^\s<>\[\]()]+", value),
            f"Expected a public HTTPS URL for {label}")


def load_manifest(root=ROOT):
    value = json.loads((root / "problems/mathdb-pilot.json").read_text(encoding="utf-8"),
                       object_pairs_hook=unique_object)
    validate_manifest(value, root)
    return value


def validate_manifest(value, root=ROOT):
    require(isinstance(value, dict), "Pilot must be an object")
    require(set(value) == {"schema_version", "rules_version", "rollout", "problems"},
            "Unknown or missing pilot fields; do not include levels or estimates")
    require(value["schema_version"] == 1 and value["rules_version"] == "mathdb",
            "Unsupported schema/rules version")
    rollout = value["rollout"]
    require(isinstance(rollout, dict) and set(rollout) ==
            {"status", "effective_at", "activation_evidence"}, "Invalid rollout fields")
    require(rollout["status"] in {"prepared", "active"}, "Invalid rollout status")
    if rollout["status"] == "prepared":
        require(rollout["effective_at"] is None and rollout["activation_evidence"] is None,
                "Prepared rollout cannot assert activation")
    else:
        require(isinstance(rollout["effective_at"], str) and re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", rollout["effective_at"]),
            "Active rollout requires a precise UTC activation time")
        datetime.fromisoformat(rollout["effective_at"].replace("Z", "+00:00"))
        https_link(rollout["activation_evidence"], "activation evidence")
    problems = value["problems"]
    require(isinstance(problems, list) and problems, "Empty pilot")
    jsps, mathdb_ids, titles = set(), set(), set()
    for p in problems:
        require(isinstance(p, dict) and set(p) == {"jsp", "title", "catalog",
                "workflow", "scope", "mathdb"},
                "Unknown/missing problem fields; levels and estimates are not allowed")
        jsp = p["jsp"]
        require(isinstance(jsp, str) and re.fullmatch(r"JSP-\d{6}", jsp), "Invalid JSP")
        require(jsp not in jsps, f"Duplicate JSP: {jsp}")
        jsps.add(jsp)
        for field in ("title", "scope"):
            plain(p[field], f"{jsp} {field}")
        require(p["title"] not in titles, "Duplicate pilot problem title")
        titles.add(p["title"])
        require(p["workflow"] == value["rules_version"], "Problem/rules mismatch")
        require(isinstance(p["catalog"], str) and re.fullmatch(
            r"problems/catalog-\d{4}-\d{4}\.md", p["catalog"]), "Unsafe catalog path")
        path = root / p["catalog"]
        require(path.is_file() and not path.is_symlink() and
                is_safe_relative(path, root), "Missing/unsafe catalog")
        require(f"## {jsp} · {p['title']}\n" in path.read_text(encoding="utf-8"),
                f"Missing/mismatched catalog heading: {jsp}")
        m = p["mathdb"]
        require(isinstance(m, dict) and set(m) == {"status", "id", "url", "title",
                "checked_at", "evidence", "note"}, "Invalid mapping fields")
        require(m["status"] in {"confirmed", "pending"}, "Invalid mapping status")
        plain(m["note"], f"{jsp} mapping note")
        if m["id"] is None:
            require(m["status"] == "pending" and m["url"] is None and m["title"] is None
                    and m["checked_at"] is None and m["evidence"] == [],
                    "An unlocated mapping must be pending and cannot assert evidence")
            continue
        require(type(m["id"]) is int and m["id"] > 0, "Invalid MathDB ID")
        require(m["id"] not in mathdb_ids, "Duplicate MathDB mapping: review consolidation")
        mathdb_ids.add(m["id"])
        require(isinstance(m["url"], str) and re.fullmatch(
            rf"https://mathdb\.com/p/{m['id']}/[a-z0-9-]+", m["url"]),
            "MathDB URL must be canonical and match its numeric ID")
        plain(m["title"], "MathDB title")
        require(isinstance(m["checked_at"], str) and re.fullmatch(
            r"\d{4}-\d{2}-\d{2}", m["checked_at"]), "Missing mapping check date")
        datetime.fromisoformat(m["checked_at"])
        require(isinstance(m["evidence"], list) and m["url"] in m["evidence"],
                "Mapping requires page evidence")
        for url in m["evidence"]:
            https_link(url, "mapping evidence")


def catalog_link(p):
    return f"{Path(p['catalog']).name}#{p['jsp']}"


def mapping_link(m):
    if not m["url"]:
        return "Matching page pending"
    return f"[MathDB #{m['id']}]({m['url']})"


def metadata(p):
    m = p["mathdb"]
    status = ("Statement match checked" if m["status"] == "confirmed" else
              "Scope / page-statement confirmation pending" if m["url"] else
              "Matching page pending")
    return "\n".join([
        BEGIN,
        "",
        "| Field | Content |",
        "| --- | --- |",
        "| Award process | [MathDB pilot: mathdb](../docs/award-process-mathdb.md); category-specific qualification. |",
        f"| MathDB problem | {mapping_link(m)} |",
        f"| Mapping status | {status}; {m['note']} |",
        "",
        END,
    ])


def claim_states(root, value):
    """Aggregate public registration independently of mathematical eligibility."""
    states = {p["jsp"]: {category: "" for category in CATEGORIES}
              for p in value["problems"]}
    records = {}
    try:
        candidates = candidate_records(root)
    except (OSError, ValueError) as error:
        raise InvalidPilot(str(error)) from error
    for jsp, category, claimant in candidates:
        if jsp in states:
            records[(jsp, category, public_name(claimant))] = "Candidate"
            states[jsp][category] = "Candidate"
    path = root / "awards/README.md"
    require(path.is_file() and not path.is_symlink() and
            is_safe_relative(path, root), "Missing/unsafe public register")
    content = path.read_text(encoding="utf-8")
    marker = "### MathDB pilot awards\n"
    require(content.count(marker) == 1, "Missing/duplicate MathDB register section")
    content = content.split(marker, 1)[1]
    content = re.split(r"(?m)^#{1,3} ", content, maxsplit=1)[0]
    for line in content.splitlines():
        if not line.startswith("| "):
            continue
        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        require(cells, "Empty public register row")
        if cells[0] == "Problem ID" or all(cell == "---" for cell in cells):
            continue
        require(len(cells) == 9,
                "Incorrect public register columns")
        identifier = re.fullmatch(r"\[(JSP-\d{6})\]\([^\s]+\)", cells[0])
        require(identifier and identifier[1] in states, "Register contains an out-of-scope JSP")
        jsp, category = identifier[1], cells[1]
        require(category in CATEGORIES, "Unknown pilot contribution category")
        require(cells[3] == value["rules_version"], "Public register rules-version mismatch")
        record_key = (jsp, category, public_name(cells[2]))
        require(records.get(record_key) in {None, "Awarded"},
                "The same claimant/category cannot be both active candidate and awarded")
        records[record_key] = "Awarded"
        # The problem-level cell records an announced award's existence;
        # coauthors' individual pending conditions remain in the registers.
        if states[jsp][category] != "Awarded":
            states[jsp][category] = "Awarded"
    return states


def render(value, states):
    problems = value["problems"]
    lines = ["# MathDB cooperation pilot", "",
        "[Problem index](README.md) · [New process](../docs/award-process-mathdb.md) · [Legacy process](../docs/award-process.md)", "",
        "<!-- Generated by scripts/mathdb_pilot.py from mathdb-pilot.json. -->", "",
        f"This pilot covers **{len(problems)} problems** under the [new process](../docs/award-process-mathdb.md).",
        "Solution, Lean and Exposition are reviewed and qualified independently.", "",
        "**Claim status:** empty = no public record; **Candidate** = publicly registered",
        "candidate; **Awarded** = announced award. These statuses do not indicate",
        "technical/committee approval, claim-issue progress or payment.", "",
        "Other problems follow the [legacy process](../docs/award-process.md) until a reviewed",
        "scope update and migration announcement. Contribution dates and notice periods remain unchanged.", "",
        '<a id="pilot-register"></a>', "",
        "## Pilot problem register", "",
        "| JSP | Problem | MathDB page | Solution claim status | Lean claim status | Exposition claim status |",
        "| --- | --- | --- | --- | --- | --- |"]
    for p in problems:
        lines.append(f"| {p['jsp']} | [{p['title']}]({catalog_link(p)}) | {mapping_link(p['mathdb'])} | "
                     + " | ".join(states[p["jsp"]][c] for c in CATEGORIES) + " |")
    return "\n".join(lines) + "\n"


def verify_catalog_index(root, value, states, check_states=True):
    headings = []
    for path in sorted((root / "problems").glob("catalog-*.md")):
        headings += re.findall(r"^## (JSP-\d{6}) · (.+)$", path.read_text(encoding="utf-8"), re.M)
    ids = [jsp for jsp, _ in headings]
    require(len(ids) == len(set(ids)), "Duplicate catalog JSP")
    require(sorted(ids) == [f"JSP-{i:06d}" for i in range(1, len(ids)+1)],
            "Catalog numbering is not consecutive")
    index = (root / "problems/README.md").read_text(encoding="utf-8")
    expected_header = "| " + " | ".join(INDEX_COLUMNS) + " |"
    headers = re.findall(r"^\| No\. \|.*$", index, re.M)
    require(headers and all(header == expected_header for header in headers),
            "Index headers must display separate Solver and Lean claim-status columns")
    index_ids = re.findall(r"^\| (JSP-\d{6}) \|", index, re.M)
    require(index_ids == sorted(ids), "Problem index/catalog numbering mismatch")
    for row in re.findall(r"^\| JSP-\d{6} \|.*$", index, re.M):
        require(len(row.split("|")[1:-1]) == len(INDEX_COLUMNS), "Index row/column mismatch")
    for p in value["problems"]:
        text = (root / p["catalog"]).read_text(encoding="utf-8")
        start = text.index(f"## {p['jsp']} · ")
        end = text.find('\n<a id=', start)
        block = text[start:end if end >= 0 else None]
        require(f"| Eligible to claim | {ELIGIBILITY} |" in block,
                f"Pilot uses a legacy shared eligibility flag: {p['jsp']}")
        row = next(line for line in index.splitlines() if line.startswith(f"| {p['jsp']} |"))
        cells = [c.strip() for c in row.split('|')[1:-1]]
        require(len(cells) == len(INDEX_COLUMNS) and cells[4] == ELIGIBILITY,
                f"Pilot index needs Solver/Lean columns and the qualification route: {p['jsp']}")
        if check_states:
            require(cells[5:] == [states[p["jsp"]][c] for c in INDEX_CATEGORIES],
                    f"Pilot category status drift: {p['jsp']}; run build")
        require(cells[1] == f"[{p['title']}]({catalog_link(p)})", "Index title/link drift")
        status = re.search(r"^\| Current status \| (Open|Solved)(?:<br>[^\n]*)? \|$", block, re.M)
        require(status is not None and cells[2] == status[1], "Index/detail status drift")


def synchronize(root=ROOT, write=False):
    value = load_manifest(root)
    states = claim_states(root, value)
    verify_catalog_index(root, value, states, check_states=not write)
    index_path = root / "problems/README.md"
    index_lines = index_path.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(index_lines):
        match = re.match(r"^\| (JSP-\d{6}) \|", line)
        if match and match[1] in states:
            cells = [c.strip() for c in line.split("|")[1:-1]]
            cells[5:] = [states[match[1]][c] for c in INDEX_CATEGORIES]
            index_lines[i] = "| " + " | ".join(cells) + " |"
    catalogs = {}
    for p in value["problems"]:
        path = root / p["catalog"]
        text = catalogs.get(path, path.read_text(encoding="utf-8"))
        start = text.index(f"## {p['jsp']} · ")
        end = text.find('\n<a id=', start)
        if end < 0:
            end = len(text)
        block = text[start:end]
        if BEGIN in block:
            require(block.count(BEGIN) == block.count(END) == 1, "Invalid metadata markers")
            block = re.sub(re.escape(BEGIN)+r".*?"+re.escape(END)+r"\n?",
                           "", block, flags=re.S)
        require(END not in block, "Orphaned metadata end")
        table = re.search(r"(?m)^\| Field \| Content \|\n\| --- \| --- \|\n(?:\|[^\n]*\|\n?)+", block)
        require(table is not None, "Missing catalog field table")
        block = (block[:table.end()].rstrip() + "\n\n" + metadata(p) + "\n\n"
                 + block[table.end():].lstrip("\n"))
        catalogs[path] = text[:start] + block + text[end:]
    catalogs = {path: text.rstrip()+"\n" for path, text in catalogs.items()}
    outputs = {**catalogs, root / "problems/mathdb-pilot.md": render(value, states),
               index_path: "\n".join(index_lines)+"\n"}
    for path, expected in outputs.items():
        if write:
            path.write_text(expected, encoding="utf-8")
        else:
            require(path.is_file() and path.read_text(encoding="utf-8") == expected,
                    f"Generated mapping drift: {path.relative_to(root)}; run build")
    return len(value["problems"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "check"))
    args = parser.parse_args()
    try:
        count = synchronize(write=args.command == "build")
    except (InvalidPilot, OSError, ValueError, TypeError, KeyError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"{args.command}: OK ({count} pilot problems)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
