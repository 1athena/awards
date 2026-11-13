"""Regression checks for pilot scope, activation and public-record consistency."""

import copy
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location("mathdb_pilot", ROOT / "scripts/mathdb_pilot.py")
pilot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pilot)


class PilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = pilot.load_manifest(ROOT)

    def modified(self):
        return copy.deepcopy(self.manifest)

    def copy_fixture(self, root):
        for location in ("problems", "candidates", "awards"):
            shutil.copytree(ROOT / location, root / location)

    def register_row(self, root, location, category, jsp="JSP-000001", claimant="Test contributor"):
        path = root / location / "README.md"
        content = path.read_text(encoding="utf-8")
        if location == "candidates":
            if category == "Exposition":
                lines = []
                for line in content.splitlines():
                    if line.startswith("| ") and len(line.split("|")[1:-1]) == 5:
                        if line.startswith("| Problem ID"):
                            line += " Exposition review start (UTC) | Exposition author |"
                        elif line.startswith("| ---"):
                            line += " --- | --- |"
                        else:
                            line += "  |  |"
                    lines.append(line)
                content = "\n".join(lines) + "\n"
            count = 7 if "| Exposition author |" in content else 5
            values = [f"[{jsp}](../problems/catalog-0001-0100.md#{jsp})"] + [""]*(count-1)
            offset = {"Solution": 1, "Lean": 3, "Exposition": 5}[category]
            values[offset:offset+2] = ["Pending actual publication", claimant]
        else:
            count = 9
            values = [f"[{jsp}](../problems/catalog-0001-0100.md#{jsp})",
                      category, claimant, "mathdb"] + ["test evidence"]*(count-4)
        row = "| " + " | ".join(values) + " |\n"
        separator = "| " + " | ".join(["---"]*count) + " |\n"
        path.write_text(content.replace(separator, separator+row, 1), encoding="utf-8")
        return row

    def test_approved_cohort_and_deduplication(self):
        problems = self.manifest["problems"]
        # The approved cohort includes 3D Poincaré and the renumbered catalog entries.
        existing = {f"JSP-{i:06d}" for i in
                            (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15,
                             16, 21, 24, 25, 28, 29, 30, 37)}
        new = {f"JSP-{i:06d}" for i in range(1023, 1050)} | {"JSP-001072"}
        self.assertEqual(len(problems), 50)
        self.assertEqual(existing | new, {p["jsp"] for p in problems})
        bombieri = [p for p in problems if "Bombieri" in p["title"]]
        self.assertEqual(len(bombieri), 1)

    def test_duplicate_jsp_and_mapping_are_rejected(self):
        for field in ("jsp", "mathdb"):
            value = self.modified()
            if field == "jsp":
                value["problems"][1][field] = value["problems"][0][field]
            else:
                value["problems"][1][field]["id"] = value["problems"][0][field]["id"]
            with self.assertRaises(pilot.InvalidPilot):
                pilot.validate_manifest(value, ROOT)

    def test_duplicate_json_keys_are_rejected(self):
        with self.assertRaises(pilot.InvalidPilot):
            json.loads('{"jsp":"JSP-000001","jsp":"JSP-000002"}',
                       object_pairs_hook=pilot.unique_object)

    def test_no_levels_estimates_or_private_fields(self):
        for field in ("level", "estimated_reward", "contact_email"):
            value = self.modified()
            value["problems"][0][field] = "unexpected"
            with self.assertRaises(pilot.InvalidPilot):
                pilot.validate_manifest(value, ROOT)

    def test_mapping_urls_must_match_id_and_trusted_host(self):
        for url in ("https://example.com/p/315854/riemann-hypothesis",
                    "https://mathdb.com/p/123/riemann-hypothesis",
                    "https://mathdb.com.evil.invalid/p/315854/riemann-hypothesis",
                    "http://mathdb.com/p/315854/riemann-hypothesis"):
            value = self.modified()
            value["problems"][1]["mathdb"]["url"] = url
            with self.assertRaises(pilot.InvalidPilot):
                pilot.validate_manifest(value, ROOT)

    def test_confirmed_mapping_needs_page_and_evidence(self):
        for field, replacement in (("id", None), ("evidence", []), ("checked_at", None)):
            value = self.modified()
            value["problems"][0]["mathdb"][field] = replacement
            with self.assertRaises(pilot.InvalidPilot):
                pilot.validate_manifest(value, ROOT)

    def test_activation_requires_evidence_and_precise_utc(self):
        value = self.modified()
        value["rollout"]["status"] = "active"
        with self.assertRaises(pilot.InvalidPilot):
            pilot.validate_manifest(value, ROOT)
        value["rollout"].update(effective_at="2026-10-12", activation_evidence="https://example.org/announcement")
        with self.assertRaises(pilot.InvalidPilot):
            pilot.validate_manifest(value, ROOT)
        value["rollout"]["effective_at"] = "2026-10-12T12:00:00Z"
        pilot.validate_manifest(value, ROOT)
        value["rollout"]["effective_at"] = "2026-02-30T12:00:00Z"
        with self.assertRaises(ValueError):
            pilot.validate_manifest(value, ROOT)

    def test_no_catalog_path_traversal(self):
        value = self.modified()
        value["problems"][0]["catalog"] = "../problems/catalog-0001-0100.md"
        with self.assertRaises(pilot.InvalidPilot):
            pilot.validate_manifest(value, ROOT)

    def test_provisional_scope_is_not_displayed_as_confirmed(self):
        value = self.modified()
        value["problems"][0]["mathdb"]["status"] = "pending"
        metadata = pilot.metadata(value["problems"][0])
        self.assertIn("| MathDB problem | [MathDB", metadata)
        self.assertNotIn("Scope pending —", metadata)
        self.assertIn("Scope / page-statement confirmation pending", metadata)
        self.assertNotIn("Candidate [MathDB", metadata)
        self.assertNotIn("Statement match checked", metadata)

    def test_unlocated_mapping_keeps_related_page_out_of_approved_link(self):
        value = self.modified()
        p = value["problems"][0]
        m = p["mathdb"]
        related_url = m["url"]
        m.update(status="pending", id=None, url=None, title=None, checked_at=None,
                 evidence=[], note=f"Related reference only: {related_url}")
        pilot.validate_manifest(value, ROOT)
        self.assertEqual(pilot.mapping_link(m), "Matching page pending")
        self.assertIn(related_url, pilot.metadata(p))
        for field, replacement in (("url", related_url), ("evidence", [related_url])):
            invalid = copy.deepcopy(value)
            invalid["problems"][0]["mathdb"][field] = replacement
            with self.assertRaises(pilot.InvalidPilot):
                pilot.validate_manifest(invalid, ROOT)

    def test_check_detects_generated_and_index_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.copy_fixture(root)
            pilot.synchronize(root)
            page = root / "problems/mathdb-pilot.md"
            page.write_text(page.read_text(encoding="utf-8") + "Changed mapping\n", encoding="utf-8")
            with self.assertRaises(pilot.InvalidPilot):
                pilot.synchronize(root)
            pilot.synchronize(root, write=True)
            pilot.synchronize(root)
            index = root / "problems/README.md"
            index.write_text(index.read_text(encoding="utf-8").replace(
                f"| {pilot.ELIGIBILITY} |  |  |",
                f"| {pilot.ELIGIBILITY} | Candidate |  |", 1), encoding="utf-8")
            with self.assertRaises(pilot.InvalidPilot):
                pilot.synchronize(root)

    def test_exposition_has_its_own_registration_and_award_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.copy_fixture(root)
            original_index = (root / "problems/README.md").read_text(encoding="utf-8")
            row = self.register_row(root, "candidates", "Exposition")
            states = pilot.claim_states(root, self.manifest)
            self.assertEqual(states["JSP-000001"], {
                "Solution": "", "Lean": "", "Exposition": "Candidate"})
            # An open problem with no Lean may have an independently reviewed exposition.
            with self.assertRaises(pilot.InvalidPilot):
                pilot.synchronize(root)
            pilot.synchronize(root, write=True)
            pilot.synchronize(root)
            self.assertEqual(original_index, (root / "problems/README.md").read_text(encoding="utf-8"))
            self.assertIn(" |  |  | Candidate |", (root / "problems/mathdb-pilot.md").read_text(encoding="utf-8"))
            candidates = root / "candidates/README.md"
            candidates.write_text(candidates.read_text(encoding="utf-8").replace(row, "", 1), encoding="utf-8")
            self.register_row(root, "awards", "Exposition")
            pilot.synchronize(root, write=True)
            pilot.synchronize(root)
            self.assertEqual(pilot.claim_states(root, self.manifest)["JSP-000001"], {
                "Solution": "", "Lean": "", "Exposition": "Awarded"})
            self.assertEqual(original_index, (root / "problems/README.md").read_text(encoding="utf-8"))
            self.assertIn(" |  |  | Awarded |", (root / "problems/mathdb-pilot.md").read_text(encoding="utf-8"))

    def test_solution_and_lean_records_do_not_claim_exposition(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.copy_fixture(root)
            self.register_row(root, "candidates", "Solution")
            self.register_row(root, "awards", "Lean")
            self.assertEqual(pilot.claim_states(root, self.manifest)["JSP-000001"], {
                "Solution": "Candidate", "Lean": "Awarded", "Exposition": ""})
            pilot.synchronize(root, write=True)
            pilot.synchronize(root)

    def test_out_of_scope_or_unknown_category_cannot_create_status(self):
        for category, jsp in (("Exposition", "JSP-000011"), ("Both", "JSP-000001")):
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.copy_fixture(root)
                self.register_row(root, "awards", category, jsp)
                with self.assertRaises(pilot.InvalidPilot):
                    pilot.claim_states(root, self.manifest)

    def test_shared_register_keeps_legacy_candidates_outside_pilot(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.copy_fixture(root)
            self.register_row(root, "candidates", "Solution", "JSP-000011")
            states = pilot.claim_states(root, self.manifest)
            self.assertNotIn("JSP-000011", states)
            self.assertEqual(states["JSP-000007"], {
                "Solution": "", "Lean": "Candidate", "Exposition": ""})

    def test_award_link_in_shared_register_is_not_an_active_candidate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.copy_fixture(root)
            row = self.register_row(root, "candidates", "Solution")
            path = root / "candidates/README.md"
            path.write_text(path.read_text().replace(row, row.replace(
                "Pending actual publication | Test contributor",
                " | [Awarded](../awards/README.md#mathdb-pilot-awards)")))
            self.register_row(root, "awards", "Solution")
            self.assertEqual(pilot.claim_states(root, self.manifest)["JSP-000001"], {
                "Solution": "Awarded", "Lean": "", "Exposition": ""})

    def test_malformed_shared_register_cannot_silently_remove_candidate_state(self):
        for old, new in (("## Candidate register", "## Unknown register"),
                         ("| Lean formalizer |", "| Unknown role |"),
                         (" | Pending actual publication |", " |  |")):
            with self.subTest(old=old), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.copy_fixture(root)
                self.register_row(root, "candidates", "Lean")
                path = root / "candidates/README.md"
                path.write_text(path.read_text().replace(old, new, 1))
                with self.assertRaises(pilot.InvalidPilot):
                    pilot.claim_states(root, self.manifest)

    def test_active_candidate_and_award_for_same_claimant_category_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.copy_fixture(root)
            self.register_row(root, "candidates", "Exposition", claimant=
                              "[Test contributor](https://github.com/TheJustinSunPrize/awards/issues/123)")
            self.register_row(root, "awards", "Exposition")
            with self.assertRaises(pilot.InvalidPilot):
                pilot.claim_states(root, self.manifest)

    def test_coauthors_can_have_separate_public_registration_states(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.copy_fixture(root)
            self.register_row(root, "candidates", "Solution", claimant="Pending coauthor")
            self.register_row(root, "awards", "Solution", claimant="Confirmed coauthor")
            self.assertEqual(pilot.claim_states(root, self.manifest)["JSP-000001"], {
                "Solution": "Awarded", "Lean": "", "Exposition": ""})

    def test_missing_header_separator_cannot_merge_solver_and_lean_columns(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.copy_fixture(root)
            index = root / "problems/README.md"
            index.write_text(index.read_text(encoding="utf-8").replace(
                "| Solver claim status | Lean claim status |",
                "| Solver claim status Lean claim status |", 1), encoding="utf-8")
            with self.assertRaises(pilot.InvalidPilot):
                pilot.synchronize(root)


if __name__ == "__main__":
    unittest.main()
