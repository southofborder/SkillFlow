#!/usr/bin/env python3
"""Select a protected target branch and create a GitLab merge request."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from collections.abc import Iterable
from typing import NoReturn
from urllib.parse import quote, urlencode

try:
    import yaml
except ImportError:  # pragma: no cover - depends on the runtime image
    yaml = None


PER_PAGE = 100
WORKFLOW_NAMES = ("workflow-gitflow", "workflow-trunkbased")
VALID_PREFIXES = ("feat/", "fix/", "chore/", "hotfix/")


class SelectionError(Exception):
    """A workflow hint could not select a usable target branch."""


def selection_fail(message: str) -> NoReturn:
    raise SelectionError(message)


def fail(message: str) -> NoReturn:
    print(f"[target-branch-selection] {message}", file=sys.stderr)
    raise SystemExit(78)


def api_text(endpoint: str) -> str:
    result = subprocess.run(
        ["glab", "api", endpoint],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    return result.stdout


def create_merge_request(
    project_path: str,
    source_branch: str,
    target_branch: str,
    *,
    title: str | None,
    description: str | None,
    related_issue: int | None,
    draft: bool,
) -> str:
    command = [
        "glab",
        "mr",
        "create",
        "--repo",
        project_path,
        "--source-branch",
        source_branch,
        "--target-branch",
        target_branch,
        "--assignee",
        "@me",
        "--yes",
    ]
    if title is None and description is None:
        command.append("--fill")
    else:
        assert title is not None and description is not None
        command.extend(["--title", title, "--description", description])
    if related_issue is not None:
        command.extend(["--related-issue", str(related_issue)])
    if draft:
        command.append("--draft")

    try:
        result = subprocess.run(
            command,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.SubprocessError):
        fail("glab could not create the merge request")
    output = result.stdout.strip()
    if not output:
        fail("glab returned no merge request reference")
    return output.splitlines()[-1]


def api_object(endpoint: str, description: str) -> dict[str, object]:
    try:
        payload = json.loads(api_text(endpoint))
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
        fail(f"unable to read {description}")
    if not isinstance(payload, dict):
        fail(f"{description} is incomplete")
    return payload


def api_pages(endpoint: str, description: str) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    page = 1
    while True:
        separator = "&" if "?" in endpoint else "?"
        paged_endpoint = (
            f"{endpoint}{separator}{urlencode({'per_page': PER_PAGE, 'page': page})}"
        )
        try:
            payload = json.loads(api_text(paged_endpoint))
        except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
            fail(f"unable to read {description}")
        if not isinstance(payload, list) or not all(
            isinstance(item, dict) for item in payload
        ):
            fail(f"{description} is incomplete")
        records.extend(payload)
        if len(payload) < PER_PAGE:
            return records
        page += 1


def yaml_documents(text: str, description: str) -> list[dict[str, object]]:
    if yaml is None:
        selection_fail("PyYAML is required")
    try:
        documents = list(yaml.safe_load_all(text))
    except yaml.YAMLError:
        selection_fail(f"unable to parse {description}")
    return [document for document in documents if isinstance(document, dict)]


def include_entries(documents: Iterable[dict[str, object]]) -> Iterable[object]:
    for document in documents:
        includes = document.get("include", [])
        if not isinstance(includes, list):
            includes = [includes]
        yield from includes


def raw_file(project_path: str, ref: str, file_path: str) -> str:
    encoded_project = quote(project_path, safe="")
    encoded_file = quote(file_path.lstrip("/"), safe="")
    try:
        return api_text(
            f"projects/{encoded_project}/repository/files/{encoded_file}/raw"
            f"?ref={quote(ref, safe='')}"
        )
    except (OSError, subprocess.SubprocessError):
        selection_fail(f"unable to read {project_path}:{ref}:{file_path}")


def project_default_branch(project_path: str) -> str:
    try:
        project = json.loads(api_text(f"projects/{quote(project_path, safe='')}"))
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
        selection_fail(f"unable to read project {project_path}")
    if not isinstance(project, dict):
        selection_fail(f"project {project_path} is incomplete")
    default_branch = project.get("default_branch")
    if not isinstance(default_branch, str) or not default_branch:
        selection_fail(f"project {project_path} has no default branch")
    return default_branch


def workflow_components(
    project_path: str,
    ref: str,
    file_path: str = ".gitlab-ci.yml",
    visited: set[tuple[str, str, str]] | None = None,
) -> list[dict[str, object]]:
    visited = set() if visited is None else visited
    key = (project_path, ref, file_path.lstrip("/"))
    if key in visited:
        return []
    visited.add(key)

    documents = yaml_documents(
        raw_file(project_path, ref, file_path),
        f"{project_path}:{ref}:{file_path}",
    )
    workflows: list[dict[str, object]] = []
    for entry in include_entries(documents):
        if isinstance(entry, str):
            if entry.startswith(("http://", "https://")):
                selection_fail("remote CI includes cannot be inspected safely")
            workflows.extend(
                workflow_components(project_path, ref, entry, visited)
            )
            continue
        if not isinstance(entry, dict):
            selection_fail("CI include configuration is incomplete")

        component = entry.get("component")
        if isinstance(component, str):
            matches = [name for name in WORKFLOW_NAMES if f"/{name}@" in component]
            if matches:
                inputs = entry.get("inputs", {})
                if not isinstance(inputs, dict):
                    selection_fail(f"{matches[0]} inputs are incomplete")
                workflows.append(
                    {"name": matches[0], "component": component, "inputs": inputs}
                )
            continue

        local = entry.get("local")
        if isinstance(local, str):
            workflows.extend(
                workflow_components(project_path, ref, local, visited)
            )
            continue

        included_project = entry.get("project")
        included_files = entry.get("file")
        if isinstance(included_project, str) and included_files is not None:
            included_ref = entry.get("ref")
            if included_ref is None:
                included_ref = project_default_branch(included_project)
            if not isinstance(included_ref, str) or "$" in included_ref:
                selection_fail("project CI include ref is unresolved")
            if not isinstance(included_files, list):
                included_files = [included_files]
            if not all(isinstance(value, str) for value in included_files):
                selection_fail("project CI include file list is incomplete")
            for included_file in included_files:
                workflows.extend(
                    workflow_components(
                        included_project, included_ref, included_file, visited
                    )
                )
            continue

        if "remote" in entry or "template" in entry:
            selection_fail("remote or template CI includes cannot be inspected safely")
    return workflows


def configured_merge_level(inputs: dict[str, object], target: str) -> int | None:
    rules = inputs.get("branch-rules", [])
    if not isinstance(rules, list):
        selection_fail("workflow branch-rules are incomplete")
    for rule in rules:
        if not isinstance(rule, dict) or rule.get("name") != target:
            continue
        level = rule.get("allowed-to-merge")
        if type(level) is int:
            return level
        selection_fail(f"workflow merge access for {target} is incomplete")
    return None


def select_target(
    default_branch: str,
    source_branch: str,
    protected_branches: list[dict[str, object]],
    workflows: list[dict[str, object]],
    explicit_target: str | None,
    target_source: str | None,
) -> tuple[str, str, int | None]:
    if not source_branch.startswith(VALID_PREFIXES):
        fail("source branch must use feat/, fix/, chore/, or hotfix/")
    if explicit_target and target_source:
        return explicit_target, f"explicit-{target_source}", None

    if not protected_branches:
        fail("project has no protected branches")
    if len(protected_branches) == 1:
        target = protected_branches[0].get("name")
        if not isinstance(target, str) or not target:
            fail("protected branch data is incomplete")
        return target, "single-protected-branch", None

    if len(workflows) > 1:
        selection_fail("multiple GitLab workflow components are configured")
    if not workflows:
        selection_fail("no GitLab workflow component selects a target")

    workflow = workflows[0]
    name = workflow["name"]
    inputs = workflow["inputs"]
    if not isinstance(name, str) or not isinstance(inputs, dict):
        selection_fail("GitLab workflow component is incomplete")
    if name == "workflow-trunkbased":
        target = default_branch
        rule = "workflow-trunkbased"
    elif source_branch.startswith("hotfix/"):
        target = default_branch
        rule = "workflow-gitflow-hotfix"
    elif source_branch.startswith(("feat/", "fix/")):
        development_branch = inputs.get("development-branch", "develop")
        if not isinstance(development_branch, str) or not development_branch:
            selection_fail("workflow-gitflow development-branch is incomplete")
        target = development_branch
        rule = "workflow-gitflow-development"
    else:
        selection_fail("workflow-gitflow does not define a target for chore/ branches")
    return target, rule, configured_merge_level(inputs, target)


def validate_protection(
    target: str,
    protected_branches: list[dict[str, object]],
    expected_level: int | None,
) -> list[dict[str, object]]:
    matches = [branch for branch in protected_branches if branch.get("name") == target]
    if len(matches) != 1:
        selection_fail(f"target branch {target} is not uniquely protected")
    levels = matches[0].get("merge_access_levels")
    if not isinstance(levels, list) or not levels:
        selection_fail(f"target branch {target} has no merge access rule")
    valid_levels = [
        level
        for level in levels
        if isinstance(level, dict)
        and (
            type(level.get("access_level")) is int
            or type(level.get("user_id")) is int
            or type(level.get("group_id")) is int
        )
    ]
    if len(valid_levels) != len(levels):
        selection_fail(f"target branch {target} merge access data is incomplete")
    if expected_level is not None and not any(
        level.get("access_level") == expected_level for level in valid_levels
    ):
        selection_fail(
            f"target branch {target} does not allow the workflow merge role "
            f"{expected_level}"
        )
    return valid_levels


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        usage=(
            "%(prog)s [--target BRANCH --target-source {item,owner-note,agents}] "
            "[--title TITLE --description DESCRIPTION] [--related-issue IID] "
            "[--draft] <project-path> <source-branch>"
        )
    )
    parser.add_argument("--target")
    parser.add_argument(
        "--target-source", choices=("item", "owner-note", "agents")
    )
    parser.add_argument("--title")
    parser.add_argument("--description")
    parser.add_argument("--related-issue", type=int)
    parser.add_argument("--draft", action="store_true")
    parser.add_argument("project_path")
    parser.add_argument("source_branch")
    args = parser.parse_args(argv)
    if bool(args.target) != bool(args.target_source):
        parser.error("--target and --target-source must be used together")
    if bool(args.title) != bool(args.description):
        parser.error("--title and --description must be used together")
    if not args.source_branch.startswith(VALID_PREFIXES):
        fail("source branch must use feat/, fix/, chore/, or hotfix/")
    if shutil.which("glab") is None:
        fail("glab is required")

    encoded_project = quote(args.project_path, safe="")
    project = api_object(f"projects/{encoded_project}", "project")
    default_branch = project.get("default_branch")
    if not isinstance(default_branch, str) or not default_branch:
        fail("project default branch is incomplete")

    protected = api_pages(
        f"projects/{encoded_project}/protected_branches", "protected branches"
    )
    workflows = []
    fallback_reason = None
    try:
        if not args.target and len(protected) != 1:
            workflows = workflow_components(args.project_path, default_branch)
        target, rule, expected_level = select_target(
            default_branch,
            args.source_branch,
            protected,
            workflows,
            args.target,
            args.target_source,
        )
    except SelectionError as error:
        if args.target or not protected:
            fail(str(error))
        fallback_reason = str(error)
        target, rule, expected_level = default_branch, "default-branch-fallback", None
    try:
        merge_access = validate_protection(target, protected, expected_level)
    except SelectionError as error:
        if args.target or target == default_branch:
            fail(str(error))
        fallback_reason = str(error)
        target, rule, expected_level = default_branch, "default-branch-fallback", None
        try:
            merge_access = validate_protection(target, protected, expected_level)
        except SelectionError as fallback_error:
            fail(str(fallback_error))
    branch = api_object(
        f"projects/{encoded_project}/repository/branches/{quote(target, safe='')}",
        f"target branch {target}",
    )
    if branch.get("name") != target or branch.get("protected") is not True:
        fail(f"target branch {target} does not exist as a protected branch")

    merge_request = create_merge_request(
        args.project_path,
        args.source_branch,
        target,
        title=args.title,
        description=args.description,
        related_issue=args.related_issue,
        draft=args.draft,
    )

    result = {
        "project": args.project_path,
        "source_branch": args.source_branch,
        "default_branch": default_branch,
        "workflow": (
            workflows[0]["name"] if len(workflows) == 1 and not fallback_reason else None
        ),
        "target_branch": target,
        "rule": rule,
        "fallback_reason": fallback_reason,
        "expected_merge_access_level": expected_level,
        "merge_access_levels": merge_access,
        "merge_request": merge_request,
        "created": True,
        "validated": True,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
