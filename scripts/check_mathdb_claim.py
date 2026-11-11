#!/usr/bin/env python3
"""Check MathDB web-form claims without fetching links or executing issue text.

This checks required fields and category/material consistency, not authorship,
technical acceptance, qualification or the contents of linked review records.
"""

import argparse
import json
import os
from pathlib import Path
import re
from urllib.parse import urlsplit

from candidate_register import candidate_records

ROOT = Path(__file__).resolve().parents[1]
CATEGORY_FIELDS = {
    "Solution": "Solution material links",
    "Lean": "Lean material links",
    "Exposition": "Exposition material links",
}
ROLE_LABELS = {
    "Solution — mathematical solution author": "Solution",
    "Lean — Lean formalization author": "Lean",
    "Exposition — explanatory article, video or other material author": "Exposition",
}
ROLE_FIELD = "Contribution roles"
LEGACY_ROLE_FIELD = "Categories claimed"
REQUIRED_FIELDS = (
    "JSP identifier", "Catalog link", "MathDB problem link", "Contributor",
    ROLE_FIELD,
)
WEB_MARKERS = ("JSP identifier", "MathDB problem link", ROLE_FIELD, LEGACY_ROLE_FIELD,
               *CATEGORY_FIELDS.values(), "Review record links")
EMPTY_VALUES = {"", "_no response_", "no response", "n/a", "none", "not claimed"}


def sections(body):
    """Return all level-three sections, preserving duplicates for validation."""
    body = re.sub(r"<!--.*?-->", "", body.replace("\r\n", "\n"), flags=re.S)
    pieces = re.split(r"^### ([^\n]+)(?:\n|$)", body, flags=re.M)
    result = {}
    for label, content in zip(pieces[1::2], pieces[2::2]):
        result.setdefault(label.strip(), []).append(content.strip())
    return result


def empty(value):
    return value.strip().lower() in EMPTY_VALUES


def has_link(value):
    for candidate in re.findall(r"https?://[^\s<>\[\]()]+", value):
        try:
            url = urlsplit(candidate.rstrip(".,;"))
            hostname = url.hostname or ""
            if (url.scheme in {"http", "https"} and "." in hostname
                    and all(part for part in hostname.split("."))
                    and not url.username and not url.password):
                return True
        except ValueError:
            continue
    return False


def selected_roles(fields):
    """Read new checkboxes or an existing claim's legacy multi-select value."""
    selected, errors = [], []
    if ROLE_FIELD in fields and LEGACY_ROLE_FIELD in fields:
        errors.append("Use only one contribution-role section.")
    if ROLE_FIELD in fields:
        raw = fields[ROLE_FIELD][0]
        for line in raw.splitlines():
            if not line.strip():
                continue
            match = re.fullmatch(r"\s*- \[([ xX])\] (.+?)\s*", line)
            if not match or match[2] not in ROLE_LABELS:
                errors.append("Contribution roles must use the provided role checkboxes.")
            elif match[1].lower() == "x":
                selected.append(ROLE_LABELS[match[2]])
    elif LEGACY_ROLE_FIELD in fields and not empty(fields[LEGACY_ROLE_FIELD][0]):
        selected = [part.strip() for part in fields[LEGACY_ROLE_FIELD][0].split(",")]
        if any(category not in CATEGORY_FIELDS for category in selected):
            errors.append("Categories claimed must contain only Solution, Lean or Exposition.")
    if not selected:
        errors.append("Select at least one contribution role.")
    if len(set(selected)) != len(selected):
        errors.append("Do not repeat contribution roles.")
    return selected, errors


def validate_body(body):
    fields = sections(body)
    errors = []
    known_fields = (*REQUIRED_FIELDS, LEGACY_ROLE_FIELD, *CATEGORY_FIELDS.values(), "Review record links",
                    "Related claims or disputes (if any)")
    for label in known_fields:
        if len(fields.get(label, [])) > 1:
            errors.append(f"Duplicate section: {label}.")

    def value(label):
        if label == ROLE_FIELD and ROLE_FIELD not in fields:
            return fields.get(LEGACY_ROLE_FIELD, [""])[0]
        return fields.get(label, [""])[0]

    for label in REQUIRED_FIELDS:
        if empty(value(label)):
            errors.append(f"Missing required field: {label}.")

    jsp = value("JSP identifier")
    if not empty(jsp) and not re.fullmatch(r"JSP-\d{6}", jsp):
        errors.append("JSP identifier must use the format JSP-000001.")
    for label in ("Catalog link", "MathDB problem link", "Review record links"):
        if not empty(value(label)) and not has_link(value(label)):
            errors.append(f"Provide a valid HTTP(S) link in {label}.")

    selected, role_errors = selected_roles(fields)
    errors.extend(role_errors)

    for category, label in CATEGORY_FIELDS.items():
        material = value(label)
        if category in selected:
            if empty(material) or not has_link(material):
                errors.append(f"{category} is selected: provide a material link in {label}.")
            if category == "Lean" and not re.search(r"\b[0-9a-fA-F]{40}\b", material):
                errors.append("Lean is selected: provide the full commit SHA.")
        elif not empty(material):
            errors.append(f"{label} has content: select {category} or clear this field.")
    return errors


def published_role_errors(root, jsp, selected, issue_url):
    """Use maintained public registers; pending issues do not reserve roles."""
    occupied, own_roles = {}, set()

    def record(category, location, evidence):
        occupied.setdefault(category, set()).add(location)
        registered_issues = re.findall(
            r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/issues/[1-9]\d*", evidence)
        if issue_url and issue_url.rstrip("/") in registered_issues:
            own_roles.add(category)

    try:
        for identifier, category, contributor in candidate_records(root):
            if identifier == jsp and category in selected:
                record(category, "candidates", contributor)
        content = (root / "awards/README.md").read_text(encoding="utf-8")
        marker = "### MathDB pilot awards\n"
        if content.count(marker) != 1:
            raise ValueError("Missing or duplicate register section")
        legacy, content = content.split(marker, 1)
        for line in legacy.splitlines():
            if not line.startswith(f"| [{jsp}]("):
                continue
            cells = [cell.strip() for cell in line.split("|")[1:-1]]
            if len(cells) != 5:
                raise ValueError("Invalid legacy register row")
            category = {"Mathematical solution": "Solution",
                        "Lean formalization": "Lean"}.get(cells[1])
            if category is None:
                raise ValueError("Unknown legacy award role")
            if category in selected:
                occupied.setdefault(category, set()).add("awards")
        content = re.split(r"(?m)^#{1,3} ", content, maxsplit=1)[0]
        for line in content.splitlines():
            if not line.startswith("| "):
                continue
            cells = [cell.strip() for cell in line.split("|")[1:-1]]
            if cells and (cells[0] == "Problem ID" or all(cell == "---" for cell in cells)):
                continue
            identifier = re.fullmatch(r"\[(JSP-\d{6})\]\([^\s]+\)", cells[0]) if cells else None
            if (len(cells) != 9 or not identifier
                    or cells[1] not in CATEGORY_FIELDS or cells[3] != "mathdb"):
                raise ValueError("Invalid register row")
            if identifier[1] != jsp or cells[1] not in selected:
                continue
            category = cells[1]
            record(category, "awards", cells[5])
    except (OSError, ValueError):
        return ["Cannot check role availability: the candidates or awards register is missing or invalid."]
    return [f"{category} is already published in {' / '.join(sorted(occupied[category]))}; "
            "update its registered claim or use Correction / Formal dispute."
            for category in CATEGORY_FIELDS if category in occupied and category not in own_roles]


def check_event(event, root=ROOT):
    issue = event.get("issue", {})
    body = issue.get("body") or ""
    # API handoffs and legacy claims use different bodies and remain outside this
    # web-form check. Recognize web-form fields even if the title has been edited.
    fields = sections(body)
    title = issue.get("title", "")
    if ((title.startswith("[Correction]") and "Record or document" in fields
         and "Current text and proposed correction" in fields)
            or (title.startswith("[Dispute]") and "Disputed claim" in fields
                and "Evidence and requested resolution" in fields)):
        return None
    if not any(marker in fields for marker in WEB_MARKERS):
        if (not title.startswith("[Claim Reward]")
                or re.search(r"^## Handoff and actual claimant\s*$", body, flags=re.M)):
            return None
    errors = validate_body(body)
    if not errors:
        selected, _ = selected_roles(fields)
        errors.extend(published_role_errors(root, fields["JSP identifier"][0], selected,
                                           issue.get("html_url", "")))
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event", required=True, type=Path,
                        help="GitHub Actions event JSON file")
    args = parser.parse_args()
    errors = check_event(json.loads(args.event.read_text(encoding="utf-8")))
    if errors is None:
        message = "Skipped: this issue is not a MathDB web-form claim."
    elif errors:
        # Diagnostics contain only fixed labels, never untrusted issue contents.
        message = "MathDB claim check failed:\n" + "\n".join(f"- {error}" for error in errors)
    else:
        message = ("MathDB claim completeness check passed. Linked material and review "
                   "contents still require team review.")
    print(message)
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with Path(summary_path).open("a") as summary:
            summary.write(message + "\n")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
