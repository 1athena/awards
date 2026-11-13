"""Read contribution roles from the shared public Award register."""

import re


HEADERS = ["Problem ID", "Contribution type", "Recipients",
           "Public-review start (UTC)", "Public-review end (UTC)"]
CATEGORIES = {
    "Mathematical solution": "Solution",
    "Lean formalization": "Lean",
    "Exposition": "Exposition",
    "Solution": "Solution",
    "Lean": "Lean",
}


def award_records(root):
    """Return (JSP, category, recipient cell), including linked claim evidence."""
    path = root / "awards/README.md"
    if (not path.is_file() or path.is_symlink()
            or not path.resolve().is_relative_to(root.resolve())):
        raise ValueError("Missing/unsafe award register")
    content = path.read_text(encoding="utf-8")
    marker = "## Award register\n"
    if content.count(marker) != 1:
        raise ValueError("Missing/duplicate Award register")
    content = re.split(r"(?m)^#{1,3} ", content.split(marker, 1)[1], maxsplit=1)[0]
    rows = [[cell.strip() for cell in line.split("|")[1:-1]]
            for line in content.splitlines() if line.startswith("| ")]
    if len(rows) < 2 or rows[0] != HEADERS or rows[1] != ["---"] * len(HEADERS):
        raise ValueError("Invalid Award register header")
    records = []
    for cells in rows[2:]:
        identifier = re.fullmatch(r"\[(JSP-\d{6})\]\([^\s]+\)", cells[0]) if cells else None
        if len(cells) != len(HEADERS) or not identifier:
            raise ValueError("Invalid Award register row")
        category = CATEGORIES.get(cells[1])
        if category is None or not all(cells[2:]):
            raise ValueError("Award requires a known role, recipients and review dates")
        records.append((identifier[1], category, cells[2]))
    return records
