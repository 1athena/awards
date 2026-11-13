"""Regression fixtures are authored here; no downloaded proofs are executed."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit.py"
spec = importlib.util.spec_from_file_location("lean_audit", SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def manifest(root, targets=None, sha="a" * 40, toolchain="leanprover/lean4:v4.32.0"):
    targets = targets or [{"id": "main", "problem": "fixture", "role": "theorem",
                           "module": "Fixture", "source": "Fixture.lean", "declaration": "Fixture.good"}]
    return {"schema_version": 1,
            "project": {"root": str(root), "repository": "local-fixture", "commit": sha, "toolchain": toolchain},
            "problems": [{"id": "fixture", "source": "test fixture, not an Erdos problem",
                          "requirements": [{"id": "main", "description": "regression target set",
                                            "targets": [t["id"] for t in targets], "coverage": "pending"}]}],
            "targets": targets}


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="lean-audit-unit-")
        self.root = Path(self.tmp.name) / "project"
        self.root.mkdir()
        self.file = Path(self.tmp.name) / "targets.json"

    def tearDown(self):
        self.tmp.cleanup()

    def load(self, data):
        self.file.write_text(json.dumps(data))
        return audit.load_manifest(self.file)

    def test_requirement_without_proof_is_preserved(self):
        data = manifest(self.root)
        data["problems"][0]["requirements"].append({"id": "remaining", "description": "unproved second direction",
                                                   "targets": [], "coverage": "uncovered", "evidence": "no candidate proof"})
        loaded, _ = self.load(data)
        self.assertEqual(len(loaded["problems"][0]["requirements"]), 2)
        data["problems"][0]["requirements"][-1]["coverage"] = "full"
        with self.assertRaises(ValueError):
            self.load(data)

    def test_malformed_json_is_input_error_not_proof_gap(self):
        for index, value in enumerate([[], {"schema_version": 1, "project": []}]):
            self.file.write_text(json.dumps(value))
            self.assertEqual(audit.main(["prepare", str(self.file), "--out",
                                         str(Path(self.tmp.name) / f"invalid-{index}")]), 2)

    def test_changed_inputs_cannot_attribute_sorry_to_original_commit(self):
        data = manifest(self.root)
        before = {"ready_for_target_checks": True, "file_sha256": {"Fixture.lean": "a"}, "head": "a" * 40}
        after = dict(before, file_sha256={"Fixture.lean": "changed"})
        def fake_capture(argv, cwd, log, timeout):
            if "--version" in argv:
                log.write_text("Lean (version 4.32.0, test fixture)\n")
            else:
                log.write_text("'Fixture.good' depends on axioms: [sorryAx]\n")
            return {"status": "ok", "exit_code": 0, "log": str(log)}
        out = Path(self.tmp.name) / "changed"
        out.mkdir()
        with patch.object(audit, "preflight", side_effect=[before, after]), patch.object(audit, "capture", side_effect=fake_capture):
            result, code = audit.execute(data, self.root, out, "/trusted/lake", 1)
        self.assertEqual(result["targets"][0]["status"], "proof_gap")
        self.assertEqual(result["mechanical_status"], "incomplete")
        self.assertEqual(code, 2)

    def test_wrong_lean_version_prevents_target_checks(self):
        def fake_capture(argv, cwd, log, timeout):
            log.write_text("Lean (version 4.31.0, wrong toolchain)\n")
            return {"status": "ok", "exit_code": 0, "log": str(log)}
        out = Path(self.tmp.name) / "wrong-version"
        out.mkdir()
        with patch.object(audit, "preflight", return_value={"ready_for_target_checks": True}), patch.object(audit, "capture", side_effect=fake_capture):
            result, code = audit.execute(manifest(self.root), self.root, out, "/trusted/lake", 1)
        self.assertEqual(result["targets"], [])
        self.assertEqual(code, 2)

    def test_missing_and_duplicate_targets_are_rejected(self):
        original = manifest(self.root)
        cases = []
        data = copy.deepcopy(original)
        data["problems"][0]["requirements"][0]["targets"] = ["not-listed"]
        cases.append(data)
        data = copy.deepcopy(original)
        data["targets"].append(dict(data["targets"][0]))
        cases.append(data)
        data = copy.deepcopy(original)
        data["targets"].append(dict(data["targets"][0], id="extra", declaration="Fixture.other"))
        cases.append(data)
        for data in cases:
            with self.subTest(data=data), self.assertRaises(ValueError):
                self.load(data)

    def test_identifiers_and_paths_cannot_inject_code(self):
        for field, value in [("module", "Fixture\n#eval IO.println 1"),
                             ("declaration", "good; echo injected"),
                             ("source", "../Outside.lean"), ("source", "/tmp/Outside.lean")]:
            data = manifest(self.root)
            data["targets"][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.load(data)
        (self.root / "Escape.lean").symlink_to(Path(self.tmp.name) / "outside.lean")
        data = manifest(self.root)
        data["targets"][0]["source"] = "Escape.lean"
        with self.assertRaises(ValueError):
            self.load(data)

    def test_missing_duplicate_truncated_and_wrong_name_output_fail(self):
        good = "'Fixture.good' does not depend on any axioms\n"
        for output in ["", good * 2, "'Fixture.good' depends on axioms: [sorryAx",
                       good.replace("Fixture.good", "Other.good")]:
            with self.subTest(output=output), self.assertRaises(ValueError):
                audit.parse_axioms(output, "Fixture.good")

    def test_transitive_sorry_and_extra_trust_have_different_outcomes(self):
        axioms = audit.parse_axioms("'Fixture.good' depends on axioms: [propext,\n sorryAx]\n", "Fixture.good")
        self.assertEqual(audit.classify(axioms), "proof_gap")
        self.assertEqual(audit.classify(["Custom.assumption"]), "trust_review_required")
        self.assertEqual(audit.classify(["Lean.ofReduceBool"]), "trust_review_required")
        self.assertEqual(audit.classify([]), "standard_axioms_only")

    def test_nonzero_exit_cannot_be_hidden_by_success_text(self):
        log = Path(self.tmp.name) / "failure.log"
        row = audit.capture([sys.executable, "-c", "print('success'); raise SystemExit(7)"], self.root, log, 3)
        self.assertEqual(row["exit_code"], 7)
        self.assertEqual(row["status"], "command_failed")
        self.assertIn("success", log.read_text())

    def test_timeout_and_missing_binary_are_incomplete(self):
        row = audit.capture([sys.executable, "-c", "import time; time.sleep(10)"], self.root,
                            Path(self.tmp.name) / "timeout.log", 0.05)
        self.assertEqual(row["status"], "timeout")
        row = audit.capture(["/nonexistent/lean-audit-test-binary"], self.root,
                            Path(self.tmp.name) / "missing.log", 1)
        self.assertEqual(row["status"], "launch_failed")

    def test_no_overwriting_existing_outputs(self):
        self.load(manifest(self.root))
        output = Path(self.tmp.name) / "old-result"
        output.mkdir()
        marker = output / "result.json"
        marker.write_text("old evidence")
        self.assertEqual(audit.main(["prepare", str(self.file), "--out", str(output)]), 2)
        self.assertEqual(marker.read_text(), "old evidence")

    def test_preflight_does_not_execute_lake_config(self):
        (self.root / "lakefile.lean").write_text("this is deliberately invalid Lean")
        result = audit.preflight(manifest(self.root), self.root)
        self.assertFalse(result["ready_for_target_checks"])
        self.assertIn("dependency_lock_missing", result["issues"])


@unittest.skipUnless(os.environ.get("LEAN_AUDIT_TEST_LAKE"), "set LEAN_AUDIT_TEST_LAKE for actual Lean checks")
class LeanIntegrationTests(unittest.TestCase):
    def test_actual_lean_targets_and_failures(self):
        lake = Path(os.environ["LEAN_AUDIT_TEST_LAKE"])
        self.assertTrue(lake.is_absolute() and lake.is_file())
        lean = lake.parent / "lean"
        version = subprocess.check_output([str(lean), "--version"], text=True)
        import re
        release = re.search(r"version (\d+\.\d+\.\d+(?:-rc\d+)?)", version).group(1)
        toolchain = "leanprover/lean4:v" + release
        with tempfile.TemporaryDirectory(prefix="lean-audit-integration-") as temp:
            root = Path(temp) / "project"
            root.mkdir()
            (root / "lean-toolchain").write_text(toolchain + "\n")
            (root / ".gitignore").write_text(".lake/\n")
            (root / "lakefile.lean").write_text("import Lake\nopen Lake DSL\npackage auditFixtures\n@[default_target]\nlean_lib Fixture\nlean_lib Extra\nlean_lib Broken\n")
            (root / "Fixture.lean").write_text("""import Lean
namespace Fixture
theorem good : True := True.intro
theorem unfinished : True := by sorry
theorem indirect : True := unfinished
axiom externalFact : False
theorem extraTrust : False := externalFact
theorem circular (h : False) : False := h
end Fixture
""")
            (root / "Extra.lean").write_text("theorem extraGood : True := True.intro\n")
            (root / "Broken.lean").write_text("theorem broken : False := by exact True.intro\n")
            def command(*args):
                return subprocess.run(args, cwd=root, text=True, capture_output=True, timeout=60, check=True)
            command(str(lake), "build")  # Creates the fixture's initial lockfile; no dependencies.
            self.assertFalse((root / ".lake/build/lib/lean/Extra.olean").exists())
            command("git", "init", "-q")
            command("git", "add", ".")
            command("git", "-c", "core.hooksPath=/dev/null", "-c", "user.name=Lean Audit Fixture",
                    "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixed regression fixture")
            sha = command("git", "rev-parse", "HEAD").stdout.strip()
            # A local theorem added after the pinned commit is not that submission.
            (root / "Untracked.lean").write_text("theorem untracked : True := True.intro\n")
            untracked = [{"id": "new", "problem": "fixture", "role": "theorem", "module": "Untracked",
                          "source": "Untracked.lean", "declaration": "untracked"}]
            pf = audit.preflight(manifest(root, untracked, sha, toolchain), root)
            self.assertIn("source_not_in_commit:new", pf["issues"])
            untracked[0]["role"] = "bridge"
            self.assertTrue(audit.preflight(manifest(root, untracked, sha, toolchain), root)["ready_for_target_checks"])
            targets = []
            for name in ["good", "indirect", "extraTrust", "circular", "missing"]:
                targets.append({"id": name, "problem": "fixture", "role": "theorem", "module": "Fixture",
                                "source": "Fixture.lean", "declaration": "Fixture." + name})
            for module, name in [("Extra", "extraGood"), ("Broken", "broken")]:
                targets.append({"id": name, "problem": "fixture", "role": "theorem", "module": module,
                                "source": module + ".lean", "declaration": name})
            data = manifest(root, targets, sha, toolchain)
            manifest_path = Path(temp) / "targets.json"
            manifest_path.write_text(json.dumps(data))
            out = Path(temp) / "results"
            code = audit.main(["run", str(manifest_path), "--out", str(out), "--lake", str(lake)])
            result = json.loads((out / "result.json").read_text())
            rows = {r["id"]: r for r in result["targets"]}
            diagnostics = json.dumps(result, ensure_ascii=False, indent=2)
            diagnostics += "\n" + "\n".join(p.name + ":\n" + p.read_text() for p in out.glob("*.log"))
            self.assertEqual(code, 1, diagnostics)  # Confirmed sorry takes priority; failures remain visible.
            self.assertEqual(result["semantic_verdict"], "not_determined")
            self.assertTrue(result["inputs_stable"])
            self.assertEqual(len(rows), len(targets))
            self.assertEqual(rows["good"]["status"], "standard_axioms_only")  # Unrelated sorry does not taint it.
            self.assertEqual(rows["indirect"]["status"], "proof_gap")
            self.assertIn("sorryAx", rows["indirect"]["axioms"])
            self.assertEqual(rows["extraTrust"]["status"], "trust_review_required")
            self.assertEqual(rows["circular"]["status"], "standard_axioms_only")  # NOT a proof of False.
            self.assertEqual(rows["missing"]["status"], "incomplete")
            self.assertEqual(rows["extraGood"]["status"], "standard_axioms_only")
            self.assertTrue((root / ".lake/build/lib/lean/Extra.olean").exists())
            self.assertEqual(rows["broken"]["status"], "incomplete")
            # Wrong historical commit must prevent all Lean execution.
            data["project"]["commit"] = "0" * 40
            manifest_path.write_text(json.dumps(data))
            blocked_out = Path(temp) / "wrong-commit"
            self.assertEqual(audit.main(["run", str(manifest_path), "--out", str(blocked_out), "--lake", str(lake)]), 2)
            blocked = json.loads((blocked_out / "result.json").read_text())
            self.assertEqual(blocked["commands"], [])


if __name__ == "__main__":
    unittest.main()
