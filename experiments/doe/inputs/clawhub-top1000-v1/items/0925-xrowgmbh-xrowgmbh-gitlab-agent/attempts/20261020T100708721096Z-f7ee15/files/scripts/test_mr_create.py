#!/usr/bin/env python3
"""Regression tests for guarded GitLab merge-request creation."""

from __future__ import annotations

import importlib.util
import io
import json
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parent / "mr-create.py"
SPEC = importlib.util.spec_from_file_location("mr_create", SCRIPT)
assert SPEC and SPEC.loader
selector = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(selector)


PROJECT = {"id": 1, "default_branch": "main"}
PROTECTED = [
    {
        "name": "main",
        "merge_access_levels": [
            {"access_level": 40, "user_id": None, "group_id": None}
        ],
    },
    {
        "name": "dev",
        "merge_access_levels": [
            {"access_level": 40, "user_id": None, "group_id": None}
        ],
    },
]
GITFLOW = """\
include:
  - component: $CI_SERVER_FQDN/xrow-public/ci-tools/workflow-gitflow@stable
    inputs:
      development-branch: dev
      branch-rules:
        - name: dev
          allowed-to-merge: 40
        - name: main
          allowed-to-merge: 40
"""
TRUNK = """\
include:
  - component: $CI_SERVER_FQDN/xrow-public/ci-tools/workflow-trunkbased@stable
"""


class MergeRequestCreationTests(unittest.TestCase):
    def run_selection(
        self, source="feat/19-example", ci=GITFLOW, arguments=None, protected=None
    ):
        arguments = [] if arguments is None else arguments
        protected = PROTECTED if protected is None else protected

        def api_object(endpoint, _description):
            if endpoint == "projects/example%2Fproject":
                return PROJECT
            for branch in protected:
                if endpoint.endswith(f"/repository/branches/{branch['name']}"):
                    return {"name": branch["name"], "protected": True}
            raise AssertionError(endpoint)

        stdout = io.StringIO()
        with (
            patch.object(selector.shutil, "which", return_value="/usr/bin/glab"),
            patch.object(selector, "api_object", side_effect=api_object),
            patch.object(selector, "api_pages", return_value=protected),
            patch.object(selector, "raw_file", return_value=ci),
            patch.object(
                selector,
                "create_merge_request",
                return_value="https://gitlab.example/example/project/-/merge_requests/1",
            ) as create_merge_request,
            redirect_stdout(stdout),
        ):
            selector.main([*arguments, "example/project", source])
        return json.loads(stdout.getvalue()), create_merge_request

    def test_gitflow_feature_and_fix_target_development_branch(self):
        for source in ("feat/19-example", "fix/19-example"):
            with self.subTest(source=source):
                result, _ = self.run_selection(source=source)
                self.assertEqual(result["target_branch"], "dev")
                self.assertEqual(result["rule"], "workflow-gitflow-development")
                self.assertTrue(result["validated"])

    def test_gitflow_hotfix_targets_default_branch(self):
        result, _ = self.run_selection(source="hotfix/19-example")
        self.assertEqual(result["target_branch"], "main")
        self.assertEqual(result["rule"], "workflow-gitflow-hotfix")

    def test_gitflow_defaults_to_develop(self):
        ci = GITFLOW.replace("      development-branch: dev\n", "")
        protected = [
            PROTECTED[0],
            {**PROTECTED[1], "name": "develop"},
        ]
        result, _ = self.run_selection(ci=ci, protected=protected)
        self.assertEqual(result["target_branch"], "develop")

    def test_trunkbased_targets_default_branch(self):
        for source in ("feat/19-example", "fix/19-example", "chore/example"):
            with self.subTest(source=source):
                result, _ = self.run_selection(source=source, ci=TRUNK)
                self.assertEqual(result["target_branch"], "main")

    def test_no_workflow_uses_single_protected_branch(self):
        result, _ = self.run_selection(
            ci="include: []\n", protected=[PROTECTED[0]]
        )
        self.assertEqual(result["target_branch"], "main")
        self.assertEqual(result["rule"], "single-protected-branch")

    def test_no_workflow_with_multiple_protected_branches_uses_default(self):
        protected = [
            PROTECTED[0],
            {**PROTECTED[1], "name": "3.0"},
            {**PROTECTED[1], "name": "stable"},
        ]
        fallback, _ = self.run_selection(ci="include: []\n", protected=protected)
        self.assertEqual(fallback["target_branch"], "main")
        self.assertEqual(fallback["rule"], "default-branch-fallback")
        self.assertIn("no GitLab workflow", fallback["fallback_reason"])
        result, _ = self.run_selection(
            ci="include: []\n",
            arguments=["--target", "dev", "--target-source", "owner-note"],
        )
        self.assertEqual(result["target_branch"], "dev")
        self.assertEqual(result["rule"], "explicit-owner-note")

    def test_creates_mr_with_validated_target_and_requested_metadata(self):
        result, create_merge_request = self.run_selection(
            arguments=[
                "--title",
                "Add guarded MR creation",
                "--description",
                "Plan and acceptance criteria",
                "--related-issue",
                "19",
                "--draft",
            ]
        )
        create_merge_request.assert_called_once_with(
            "example/project",
            "feat/19-example",
            "dev",
            title="Add guarded MR creation",
            description="Plan and acceptance criteria",
            related_issue=19,
            draft=True,
        )
        self.assertTrue(result["created"])
        self.assertEqual(
            result["merge_request"],
            "https://gitlab.example/example/project/-/merge_requests/1",
        )

    def test_create_merge_request_calls_glab(self):
        with patch.object(selector.subprocess, "run") as run:
            run.return_value.stdout = (
                "Creating merge request\n"
                "https://gitlab.example/example/project/-/merge_requests/1\n"
            )
            result = selector.create_merge_request(
                "example/project",
                "feat/19-example",
                "dev",
                title=None,
                description=None,
                related_issue=19,
                draft=False,
            )

        command = run.call_args.args[0]
        self.assertEqual(command[:3], ["glab", "mr", "create"])
        self.assertIn("--fill", command)
        self.assertEqual(
            command[command.index("--target-branch") + 1], "dev"
        )
        self.assertEqual(
            result, "https://gitlab.example/example/project/-/merge_requests/1"
        )

    def test_ambiguous_or_invalid_workflow_target_uses_default(self):
        both = GITFLOW + "\n---\n" + TRUNK
        ambiguous, _ = self.run_selection(ci=both)
        self.assertEqual(ambiguous["target_branch"], "main")
        self.assertIn("multiple", ambiguous["fallback_reason"])
        protected_without_dev = [
            PROTECTED[0],
            {**PROTECTED[1], "name": "release"},
        ]
        invalid, _ = self.run_selection(protected=protected_without_dev)
        self.assertEqual(invalid["target_branch"], "main")
        self.assertIn("not uniquely protected", invalid["fallback_reason"])

    def test_workflow_inspection_failure_uses_default(self):
        with patch.object(
            selector,
            "workflow_components",
            side_effect=selector.SelectionError("unable to read workflow"),
        ):
            result, _ = self.run_selection()
        self.assertEqual(result["target_branch"], "main")
        self.assertEqual(result["fallback_reason"], "unable to read workflow")

    def test_missing_yaml_dependency_uses_default(self):
        with patch.object(selector, "yaml", None):
            result, _ = self.run_selection()
        self.assertEqual(result["target_branch"], "main")
        self.assertEqual(result["fallback_reason"], "PyYAML is required")

    def test_invalid_explicit_target_and_unprotected_default_still_fail(self):
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            self.run_selection(
                arguments=["--target", "missing", "--target-source", "owner-note"]
            )
        without_default = [
            {**PROTECTED[0], "name": "3.0"},
            {**PROTECTED[1], "name": "stable"},
        ]
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            self.run_selection(ci="include: []\n", protected=without_default)

    def test_default_workflow_merge_role_mismatch_does_not_bypass_role_check(self):
        restricted_default = [
            {
                **PROTECTED[0],
                "merge_access_levels": [{"access_level": 30}],
            },
            PROTECTED[1],
        ]
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            self.run_selection(source="hotfix/19-example", protected=restricted_default)

    def test_invalid_source_prefix_cannot_bypass_validation_with_fallback(self):
        with patch.object(
            selector,
            "workflow_components",
            side_effect=selector.SelectionError("unable to read workflow"),
        ):
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                self.run_selection(source="unrecognized/example")

    def test_follows_local_and_project_includes(self):
        files = {
            ("example/project", "main", ".gitlab-ci.yml"): (
                "include:\n  - local: ci/local.yml\n"
            ),
            ("example/project", "main", "ci/local.yml"): (
                "include:\n  - project: shared/pipelines\n"
                "    ref: stable\n    file: workflow.yml\n"
            ),
            ("shared/pipelines", "stable", "workflow.yml"): TRUNK,
        }
        with patch.object(
            selector,
            "raw_file",
            side_effect=lambda project, ref, path: files[(project, ref, path)],
        ):
            workflows = selector.workflow_components("example/project", "main")
        self.assertEqual([item["name"] for item in workflows], ["workflow-trunkbased"])

    def test_pagination_loops_until_a_short_page(self):
        first_page = [{"name": str(value)} for value in range(100)]
        with patch.object(
            selector, "api_text", side_effect=[json.dumps(first_page), '[{"name":"x"}]']
        ) as api_text:
            records = selector.api_pages(
                "projects/example/protected_branches", "branches"
            )
        self.assertEqual(len(records), 101)
        self.assertIn("page=1", api_text.call_args_list[0].args[0])
        self.assertIn("page=2", api_text.call_args_list[1].args[0])


if __name__ == "__main__":
    unittest.main()
