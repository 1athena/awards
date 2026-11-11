"""Read contribution roles from the shared public Candidate register."""

import re


HEADERS = ["Problem ID", "Solver review start (UTC)", "Mathematical solver",
           "Lean review start (UTC)", "Lean formalizer"]
EXPOSITION_HEADERS = ["Exposition review start (UTC)", "Exposition author"]


def candidate_records(root):
    """Return (JSP, category, contributor cell), including linked claim evidence."""
    path = root / "candidates/README.md"
    if (not path.is_file() or path.is_symlink()
            or not path.resolve().is_relative_to(root.resolve())):
        raise ValueError("Missing/unsafe candidate register")
    content = path.read_text(encoding="utf-8")
    marker = "## Candidate register\n"
    if content.count(marker) != 1:
        raise ValueError("Missing/duplicate Candidate register")
    content = re.split(r"(?m)^#{1,3} ", content.split(marker, 1)[1], maxsplit=1)[0]
    rows = [[cell.strip() for cell in line.split("|")[1:-1]]
            for line in content.splitlines() if line.startswith("| ")]
    if (len(rows) < 2 or rows[0] not in (HEADERS, HEADERS + EXPOSITION_HEADERS)
            or rows[1] != ["---"] * len(rows[0])):
        raise ValueError("Invalid Candidate register header")
    records = []
    for cells in rows[2:]:
        identifier = re.fullmatch(r"\[(JSP-\d{6})\]\([^\s]+\)", cells[0]) if cells else None
        if len(cells) != len(rows[0]) or not identifier:
            raise ValueError("Invalid Candidate register row")
        for offset, category in ((1, "Solution"), (3, "Lean"), (5, "Exposition")):
            if offset >= len(cells):
                continue
            start, contributor = cells[offset:offset + 2]
            if not start and (not contributor or re.fullmatch(
                    r"\[[^\]]+\]\(\.\./awards/README\.md#[^\s)]+\)", contributor)):
                continue
            if not start or not contributor:
                raise ValueError("Candidate role requires both review start and contributor")
            records.append((identifier[1], category, contributor))
    return records


def public_name(cell):
    """Compare public names independently of Markdown links to claims/profiles."""
    return re.sub(r"\[([^\]]+)\]\([^\s)]+\)", r"\1", cell).strip()
