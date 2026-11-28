"""Offline four-package verification and negative controls for complete-source."""
from __future__ import annotations

import hashlib
import importlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

BASE = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(BASE / f"source/packages/{p}/src") for p in ("semia-core", "semia-cli")]
import complete_source as adapter

OUT = BASE / "analysis/full-source-preflight"


def fingerprint():
    manifest = json.loads((BASE / "source-manifest.json").read_text("utf-8"))
    actual = {x["path"]: hashlib.sha256((BASE / "source" / x["path"]).read_bytes()).hexdigest()
              for x in manifest["files"]}
    expected = {x["path"]: x["sha256"] for x in manifest["files"]}
    if actual != expected:
        raise AssertionError("Official source changed")
    return actual


class CompleteSourceChecks(unittest.TestCase):
    def test_all_four_cases_final_prompt_and_source_line_identity(self):
        cases = json.loads((BASE / "input-manifest.json").read_text("utf-8"))["cases"]
        for case in cases:
            with self.subTest(case=case["case_id"]):
                receipt = adapter.verify_prepared(BASE / case["path"], OUT / "prepared" / case["case_id"], case["case_id"])
                self.assertEqual(receipt["file_count"], len(case["files"]))
                self.assertTrue(receipt["complete_body_in_final_prompt"])

    def test_ga4_adds_exact_two_metadata_files(self):
        full = json.loads((OUT / "prepared/ga4/complete-source-receipt.json").read_text("utf-8"))
        self.assertEqual(full["default_skip_names_removed"], ["package-lock.json", "package.json"])
        old = json.loads((BASE / "prepared/ga4/prepare_metadata.json").read_text("utf-8"))
        old_names = set(old["source"]["files"])
        self.assertEqual({x["path"] for x in full["files"]} - old_names,
                         {"scripts/package.json", "scripts/package-lock.json"})
        self.assertEqual(full["file_count"], 16)

    def test_unchanged_small_case_rendering_matches_upstream(self):
        for case in ("001", "010", "013"):
            with self.subTest(case=case):
                self.assertEqual((BASE / f"prepared/{case}/prepared_skill.md").read_bytes(),
                                 (OUT / f"prepared/{case}/prepared_skill.md").read_bytes())

    def test_extra_input_file_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=OUT) as td:
            root = Path(td) / "input"
            shutil.copytree(BASE / "inputs/001", root)
            (root / "unexpected.txt").write_text("extra evidence")
            with self.assertRaisesRegex(ValueError, "inventory mismatch"):
                adapter.verify_input(root, "001")

    def test_changed_input_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=OUT) as td:
            root = Path(td) / "input"
            shutil.copytree(BASE / "inputs/001", root)
            with (root / "SKILL.md").open("ab") as stream:
                stream.write(b"\nchanged")
            with self.assertRaisesRegex(ValueError, "integrity mismatch"):
                adapter.verify_input(root, "001")

    def test_truncated_prepared_body_rejected_even_with_rehashed_metadata(self):
        with tempfile.TemporaryDirectory(dir=OUT) as td:
            root = Path(td) / "artifacts"
            shutil.copytree(OUT / "prepared/001", root)
            prepared = root / "prepared_skill.md"
            data = prepared.read_bytes().replace(b"events.json", b"eventx.json", 1)
            prepared.write_bytes(data)
            meta = json.loads((root / "prepare_metadata.json").read_text("utf-8"))
            meta["prepared_skill_sha256"] = hashlib.sha256(data).hexdigest()
            (root / "prepare_metadata.json").write_text(json.dumps(meta), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Source line loss or rewriting"):
                adapter.verify_prepared(BASE / "inputs/001", root, "001")

    def test_final_prompt_omission_rejected(self):
        loop = importlib.import_module("semia_cli.synthesis_loop")
        with patch.object(loop, "_prompt", return_value="missing source"):
            with self.assertRaisesRegex(ValueError, "absent from final synthesis prompt"):
                adapter.verify_prepared(BASE / "inputs/001", OUT / "prepared/001", "001")

    def test_skip_policy_restored_on_failure(self):
        prepare = importlib.import_module("semia_core.prepare")
        original = prepare._SKIP_FILES_ALWAYS
        with self.assertRaisesRegex(RuntimeError, "test failure"):
            with adapter.complete_source_policy("ga4", BASE / "inputs/ga4"):
                self.assertNotIn("package.json", prepare._SKIP_FILES_ALWAYS)
                raise RuntimeError("test failure")
        self.assertIs(prepare._SKIP_FILES_ALWAYS, original)

    def test_existing_artifacts_are_not_overwritten(self):
        with self.assertRaisesRegex(ValueError, "Refusing to overwrite"):
            adapter.prepare_complete_source(BASE / "inputs/001", OUT / "prepared/001", "001")

    def test_official_source_files_unchanged(self):
        self.assertEqual(fingerprint(), BEFORE)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    BEFORE = fingerprint()
    cases = json.loads((BASE / "input-manifest.json").read_text("utf-8"))["cases"]
    for case in cases:
        target = OUT / "prepared" / case["case_id"]
        adapter.prepare_complete_source(BASE / case["path"], target, case["case_id"])
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(CompleteSourceChecks)
    with (OUT / "validation.txt").open("w", encoding="utf-8") as log:
        result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
    receipts = [json.loads((OUT / "prepared" / case["case_id"] / "complete-source-receipt.json").read_text("utf-8")) for case in cases]
    report = {
        "variant": adapter.VARIANT, "validation": {"tests": result.testsRun,
        "failures": len(result.failures), "errors": len(result.errors), "skipped": len(result.skipped)},
        "cases": [{k: r[k] for k in ("case_id", "file_count", "prepared_bytes", "synthesis_prompt_bytes", "semantic_unit_count", "default_skip_names_removed", "complete_body_in_final_prompt")} for r in receipts],
        "source_files_verified_unchanged": len(fingerprint()), "model_calls": 0, "skill_executions": 0,
        "adapter_sha256": hashlib.sha256((BASE / "adapters/complete_source.py").read_bytes()).hexdigest(),
    }
    (OUT / "manifest.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    raise SystemExit(0 if result.wasSuccessful() else 1)
