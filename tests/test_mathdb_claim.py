"""Exercise category/link consistency using GitHub Issue Form body formatting."""

import importlib.util
from itertools import combinations
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/check_mathdb_claim.py"
SPEC = importlib.util.spec_from_file_location("check_mathdb_claim", SCRIPT)
claim = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(claim)


class MathDBClaimTests(unittest.TestCase):
    def body(self, selected=("Solution",), overrides=None, legacy=False):
        choices = (
            ("Solution", "Solution — mathematical solution author"),
            ("Lean", "Lean — Lean formalization author"),
            ("Exposition", "Exposition — explanatory article, video or other material author"),
        )
        roles = "\n".join(f"- [{'x' if category in selected else ' '}] {label}"
                          for category, label in choices)
        fields = {
            "JSP identifier": "JSP-000001",
            "Catalog link": "https://github.com/TheJustinSunPrize/awards/blob/main/"
                            "problems/catalog-0001-0100.md#JSP-000001",
            "MathDB problem link": "https://mathdb.com/p/315854/riemann-hypothesis",
            "Contributor": "Alice; MathDB user 123; solution author",
            "Contribution roles": roles,
            "Solution material links": "_No response_",
            "Lean material links": "_No response_",
            "Exposition material links": "_No response_",
            "Review record links": "[Shared review](https://mathdb.com/reviews/123)",
            "Related claims or disputes (if any)": "_No response_",
        }
        for category in selected:
            if category in claim.CATEGORY_FIELDS:
                fields[claim.CATEGORY_FIELDS[category]] = "https://example.org/material"
        if "Lean" in selected:
            fields["Lean material links"] = "Repository: https://github.com/alice/proof\nCommit: " + "a"*40
        if legacy:
            fields["Categories claimed"] = ", ".join(selected)
            del fields["Contribution roles"]
        fields.update(overrides or {})
        return "\n\n".join(f"### {label}\n\n{value}" for label, value in fields.items())

    def test_all_seven_category_combinations(self):
        for count in (1, 2, 3):
            for selected in combinations(claim.CATEGORY_FIELDS, count):
                with self.subTest(selected=selected):
                    self.assertEqual(claim.validate_body(self.body(selected)), [])

    def test_selected_material_is_required_even_when_other_material_is_present(self):
        for category, label in claim.CATEGORY_FIELDS.items():
            for missing in ("", "_No response_", "N/A", "None", "See the proof", "https://..."):
                with self.subTest(category=category, missing=missing):
                    errors = claim.validate_body(self.body(
                        tuple(claim.CATEGORY_FIELDS), {label: missing}))
                    self.assertTrue(any(f"{category} is selected" in error for error in errors))

    def test_unselected_material_must_be_added_to_selection_or_cleared(self):
        errors = claim.validate_body(self.body(overrides={
            "Lean material links": "https://github.com/author/proof"}))
        self.assertTrue(any("select Lean or clear this field" in error for error in errors))

    def test_lean_repository_and_full_commit_are_sufficient(self):
        self.assertEqual(claim.validate_body(self.body(("Lean",))), [])

    def test_lean_commit_cannot_be_omitted_or_abbreviated(self):
        for commit in ("", "main", "a"*7, "a"*39, "a"*41, "g"*40):
            with self.subTest(commit=commit):
                body = self.body(("Lean",), {"Lean material links":
                    "Repository: https://github.com/alice/proof\nCommit: " + commit})
                self.assertIn("Lean is selected: provide the full commit SHA.",
                              claim.validate_body(body))

    def test_lean_commit_without_repository_does_not_pass(self):
        body = self.body(("Lean",), {"Lean material links": "Commit: " + "a"*40})
        self.assertTrue(any("provide a material link" in error for error in claim.validate_body(body)))

    def test_pinned_lean_links_remain_accepted(self):
        body = self.body(("Lean",), {"Lean material links":
            "https://github.com/alice/proof/blob/" + "a"*40 + "/Proof.lean"})
        self.assertEqual(claim.validate_body(body), [])

    def test_empty_unknown_and_repeated_categories_fail(self):
        for selected in ((), ("Both",), ("Solution", "Solution")):
            with self.subTest(selected=selected):
                self.assertTrue(claim.validate_body(self.body(selected, legacy=True)))

    def test_unchecked_role_boxes_cannot_satisfy_selection(self):
        self.assertIn("Select at least one contribution role.", claim.validate_body(self.body(())))

    def test_unknown_and_duplicate_checkboxes_fail(self):
        for roles in ("- [x] Other", "- [x] Solution — mathematical solution author\n"
                      "- [X] Solution — mathematical solution author", "Solution"):
            with self.subTest(roles=roles):
                self.assertTrue(claim.validate_body(self.body(overrides={"Contribution roles": roles})))

    def test_legacy_dropdown_claims_and_checkbox_claims_are_supported(self):
        for legacy in (False, True):
            with self.subTest(legacy=legacy):
                self.assertEqual(claim.validate_body(self.body(tuple(claim.CATEGORY_FIELDS),
                                 legacy=legacy)), [])

    def test_two_role_sections_are_ambiguous(self):
        self.assertIn("Use only one contribution-role section.", claim.validate_body(
            self.body() + "\n\n### Categories claimed\n\nSolution"))

    def test_required_fields_cannot_be_removed_on_edit(self):
        for label in claim.REQUIRED_FIELDS:
            with self.subTest(label=label):
                body = self.body(overrides={label: ""})
                self.assertIn(f"Missing required field: {label}.", claim.validate_body(body))
        body = self.body().replace("### Contributor", "### Deleted contributor heading")
        self.assertIn("Missing required field: Contributor.", claim.validate_body(body))

    def test_review_can_be_blank_or_omitted(self):
        for review in ("", "_No response_", "N/A"):
            with self.subTest(review=review):
                self.assertEqual(claim.validate_body(self.body(tuple(claim.CATEGORY_FIELDS),
                                 {"Review record links": review})), [])
        body = self.body().replace("### Review record links", "### Other information")
        self.assertEqual(claim.validate_body(body), [])

    def test_review_requires_a_link_and_shared_review_only_needs_one(self):
        self.assertEqual(claim.validate_body(self.body(tuple(claim.CATEGORY_FIELDS))), [])
        errors = claim.validate_body(self.body(overrides={"Review record links": "Passed"}))
        self.assertIn("Provide a valid HTTP(S) link in Review record links.", errors)

    def test_duplicate_sections_are_rejected(self):
        for label in ("Solution material links", "Review record links"):
            with self.subTest(label=label):
                body = self.body() + f"\n\n### {label}\n\nhttps://example.org/other"
                self.assertIn(f"Duplicate section: {label}.", claim.validate_body(body))

    def test_crlf_and_empty_final_heading(self):
        self.assertEqual(claim.validate_body(self.body().replace("\n", "\r\n")), [])
        body = self.body() + "\n\n### Exposition material links"
        self.assertIn("Duplicate section: Exposition material links.", claim.validate_body(body))

    def test_html_comments_do_not_supply_missing_links(self):
        body = self.body(overrides={"Solution material links": "<!-- https://example.org -->"})
        self.assertTrue(claim.validate_body(body))

    def test_edited_title_does_not_bypass_web_form_check(self):
        event = {"issue": {"title": "Renamed issue", "body": self.body(overrides={
            "Solution material links": "_No response_"})}}
        self.assertTrue(claim.check_event(event))

    def write_registers(self, root, occupied=None):
        for location, heading, count in (("candidates", "MathDB pilot candidates", 10),
                                          ("awards", "MathDB pilot awards", 9)):
            directory = root / location
            directory.mkdir(exist_ok=True)
            content = f"### {heading}\n\n"
            for record_location, jsp, category, issue_url in occupied or []:
                if record_location == location:
                    cells = [f"[{jsp}](../problems/catalog.md#{jsp})", category,
                             "Public contributor", "mathdb", "https://mathdb.com/p/123",
                             f"[Claim]({issue_url})"] + ["evidence"]*(count-6)
                    content += "| " + " | ".join(cells) + " |\n"
            (directory / "README.md").write_text(content)

    def test_published_roles_reject_new_claims_but_not_other_roles_or_problems(self):
        for location in ("candidates", "awards"):
            with self.subTest(location=location), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.write_registers(root, [(location, "JSP-000001", "Solution",
                                            "https://github.com/TheJustinSunPrize/awards/issues/123")])
                event = {"issue": {"body": self.body()}}
                self.assertTrue(any("Solution is already published" in error
                                    for error in claim.check_event(event, root)))
                event["issue"]["body"] = self.body(("Lean",))
                self.assertEqual(claim.check_event(event, root), [])
                event["issue"]["body"] = self.body(overrides={"JSP identifier": "JSP-000002"})
                self.assertEqual(claim.check_event(event, root), [])

    def test_registered_claim_can_be_updated_without_blocking_its_own_role(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            url = "https://github.com/TheJustinSunPrize/awards/issues/123"
            self.write_registers(root, [("candidates", "JSP-000001", "Solution", url),
                                       ("candidates", "JSP-000001", "Solution", url + "4")])
            event = {"issue": {"body": self.body(), "html_url": url}}
            self.assertEqual(claim.check_event(event, root), [])
            # Mentioning the original claim in submitted text cannot bypass the check.
            event["issue"] = {"body": self.body(overrides={
                "Related claims or disputes (if any)": url}), "html_url": url + "5"}
            self.assertTrue(claim.check_event(event, root))

    def test_legacy_public_records_also_reserve_roles(self):
        for location, cells in (("candidates", ["2026-10-01", "Author", "", ""]),
                                ("awards", ["Mathematical solution", "Author", "start", "end"])):
            with self.subTest(location=location), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.write_registers(root)
                path = root / location / "README.md"
                row = "| " + " | ".join(["[JSP-000001](../problems/catalog.md#JSP-000001)"]
                                         + cells) + " |\n\n"
                path.write_text(row + path.read_text())
                event = {"issue": {"body": self.body()}}
                self.assertTrue(any("Solution is already published" in error
                                    for error in claim.check_event(event, root)))
                event["issue"]["body"] = self.body(("Lean",))
                self.assertEqual(claim.check_event(event, root), [])

    def test_missing_or_invalid_registers_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            event = {"issue": {"body": self.body()}}
            self.assertTrue(any("Cannot check role availability" in error
                                for error in claim.check_event(event, root)))
            self.write_registers(root)
            (root / "awards/README.md").write_text("### MathDB pilot awards\n\n| invalid | row |\n")
            self.assertTrue(any("Cannot check role availability" in error
                                for error in claim.check_event(event, root)))

    def test_correction_and_dispute_templates_do_not_reserve_or_claim_roles(self):
        for title, headings in (("[Correction] JSP-000001", ("Record or document",
                                 "Current text and proposed correction")),
                                ("[Dispute] JSP-000001", ("Disputed claim",
                                 "Evidence and requested resolution"))):
            with self.subTest(title=title):
                body = self.body() + "\n\n" + "\n\n".join(
                    f"### {label}\n\nExisting record" for label in headings)
                self.assertIsNone(claim.check_event({"issue": {"title": title, "body": body}}))

    def test_legacy_api_and_unrelated_bodies_are_outside_web_form_scope(self):
        api_body = (ROOT / "docs/templates/mathdb-claim-reward.md").read_text()
        for body in (None, "A regular issue", api_body):
            with self.subTest(body=body):
                self.assertIsNone(claim.check_event({"issue": {"body": body}}))
        self.assertIsNone(claim.check_event({"issue": {
            "title": "[Claim Reward] JSP-000001 — Alice", "body": api_body}}))

    def test_removing_entire_claim_body_does_not_pass(self):
        for body in (None, "", "Please award my proof"):
            with self.subTest(body=body):
                self.assertTrue(claim.check_event({"issue": {
                    "title": "[Claim Reward] JSP-000001 — Alice", "body": body}}))

    def test_jsp_format_and_link_syntax(self):
        self.assertTrue(claim.validate_body(self.body(overrides={"JSP identifier": "JSP-XXXXXX"})))
        for candidate in ("javascript:alert(1)", "https://...", "http://[broken", "No URL"):
            with self.subTest(candidate=candidate):
                self.assertFalse(claim.has_link(candidate))

    def test_cli_exit_status_and_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            event_path = Path(directory) / "event.json"
            summary_path = Path(directory) / "summary.md"
            env = dict(os.environ, GITHUB_STEP_SUMMARY=str(summary_path))
            for expected, overrides in ((0, {}), (1, {"Solution material links": ""})):
                with self.subTest(expected=expected):
                    event_path.write_text(json.dumps({"issue": {"body": self.body(overrides=overrides)}}))
                    result = subprocess.run([sys.executable, str(SCRIPT), "--event", str(event_path)],
                                            env=env, capture_output=True, text=True)
                    self.assertEqual(result.returncode, expected, result.stderr)
                    self.assertIn("MathDB claim", summary_path.read_text())


if __name__ == "__main__":
    unittest.main()
