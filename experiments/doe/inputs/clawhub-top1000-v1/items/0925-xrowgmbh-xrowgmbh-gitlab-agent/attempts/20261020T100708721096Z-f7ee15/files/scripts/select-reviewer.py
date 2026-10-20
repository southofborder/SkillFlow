#!/usr/bin/env python3
"""Select and optionally apply the deterministic reviewer for an assigned MR."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import NoReturn
from urllib.parse import quote, urlencode


PER_PAGE = 100
CONFIG_PATH_ENV = "OPENCLAW_CONFIG_PATH"


def fail(message: str) -> NoReturn:
    print(f"[reviewer-selection] {message}", file=sys.stderr)
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


def integer(record: dict[str, object], key: str) -> int | None:
    value = record.get(key)
    return value if type(value) is int else None


def username(record: dict[str, object]) -> str | None:
    value = record.get("username")
    return value if isinstance(value, str) and value else None


def user_id(record: object) -> int | None:
    return integer(record, "id") if isinstance(record, dict) else None


def valid_member(member: dict[str, object]) -> bool:
    return (
        integer(member, "id") is not None
        and username(member) is not None
        and integer(member, "access_level") is not None
        and isinstance(member.get("state"), str)
        and type(member.get("locked")) is bool
    )


def human_user(user: dict[str, object], expected_id: int) -> bool:
    if integer(user, "id") != expected_id or type(user.get("bot")) is not bool:
        fail("reviewer identity data is incomplete")
    return user["bot"] is False


def mr_signature(mr: dict[str, object]) -> dict[str, object]:
    author = mr.get("author")
    assignees = mr.get("assignees")
    reviewers = mr.get("reviewers")
    return {
        "state": mr.get("state"),
        "sha": mr.get("sha"),
        "author": user_id(author),
        "assignees": sorted(
            value
            for value in (user_id(item) for item in assignees or [])
            if value is not None
        ),
        "reviewers": sorted(
            value
            for value in (user_id(item) for item in reviewers or [])
            if value is not None
        ),
    }


def configured_reviewers(agents_markdown: str) -> list[str]:
    reviewers: list[str] = []
    for line in agents_markdown.splitlines():
        columns = line.split("|")
        if len(columns) < 4 or columns[1].strip().lower() != "reviewers":
            continue
        for candidate in re.findall(r"\[([A-Za-z0-9_.-]+)\]", columns[2]):
            if candidate not in reviewers:
                reviewers.append(candidate)
    return reviewers


def ignored_reviewers() -> set[str]:
    """Read the reviewer exclusion list from the active OpenClaw configuration."""
    configured_path = os.environ.get(CONFIG_PATH_ENV)
    config_path = (
        Path(configured_path).expanduser()
        if configured_path
        else Path.home() / ".openclaw" / "openclaw.json"
    )
    if not config_path.exists():
        return set()
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        fail("unable to read OpenClaw configuration")
    if not isinstance(payload, dict):
        fail("OpenClaw configuration is incomplete")
    skills = payload.get("skills", {})
    if not isinstance(skills, dict):
        fail("OpenClaw skills configuration is incomplete")
    entries = skills.get("entries", {})
    if not isinstance(entries, dict):
        fail("OpenClaw skill entries configuration is incomplete")
    agent = entries.get("gitlab-agent", {})
    if not isinstance(agent, dict):
        fail("gitlab-agent configuration is incomplete")

    # OpenClaw requires custom skill settings below `config`. Accept the issue's
    # direct spelling as well for installations that already use it.
    reviewer = agent.get("reviewer")
    if reviewer is None:
        skill_config = agent.get("config", {})
        if not isinstance(skill_config, dict):
            fail("gitlab-agent config is incomplete")
        reviewer = skill_config.get("reviewer", {})
    if not isinstance(reviewer, dict):
        fail("gitlab-agent reviewer configuration is incomplete")
    ignored = reviewer.get("ignore", [])
    if not isinstance(ignored, list) or any(
        not isinstance(value, str) or not value.strip() for value in ignored
    ):
        fail("gitlab-agent reviewer.ignore must be a list of usernames")
    return {value.strip().casefold() for value in ignored}


def optional_approval(endpoint: str) -> bool:
    """Require both MR approval APIs to prove that no approval rule is required."""
    try:
        approvals = json.loads(api_text(f"{endpoint}/approvals"))
        state = json.loads(api_text(f"{endpoint}/approval_state"))
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
        return False
    if not isinstance(approvals, dict) or not isinstance(state, dict):
        return False
    rules = state.get("rules")
    return (
        approvals.get("user_can_approve") is True
        and integer(approvals, "approvals_required") == 0
        and integer(approvals, "approvals_left") == 0
        and isinstance(rules, list)
        and all(
            isinstance(rule, dict)
            and integer(rule, "approvals_required") == 0
            for rule in rules
        )
    )


def merge_allowed(
    encoded_project: str,
    mr: dict[str, object],
    agent_id: int,
    members: list[dict[str, object]],
) -> bool:
    """Prove merge access on the target branch; unknown permissions use human review."""
    target = mr.get("target_branch")
    member = next(
        (item for item in members if integer(item, "id") == agent_id), None
    )
    level = integer(member, "access_level") if member else None
    if not isinstance(target, str) or not target or level is None:
        return False
    branch_endpoint = (
        f"projects/{encoded_project}/repository/branches/{quote(target, safe='')}"
    )
    try:
        branch = json.loads(api_text(branch_endpoint))
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
        return False
    if not isinstance(branch, dict) or branch.get("name") != target:
        return False
    if branch.get("protected") is False:
        return level >= 30
    if branch.get("protected") is not True:
        return False
    try:
        protection = json.loads(api_text(
            f"projects/{encoded_project}/protected_branches/{quote(target, safe='')}"
        ))
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
        return False
    if not isinstance(protection, dict) or protection.get("name") != target:
        return False
    merge_levels = protection.get("merge_access_levels")
    return isinstance(merge_levels, list) and any(
        isinstance(item, dict)
        and (
            integer(item, "user_id") == agent_id
            or (
                integer(item, "access_level") in (30, 40, 50)
                and level >= integer(item, "access_level")
            )
        )
        for item in merge_levels
    )


def merge_ready(mr: dict[str, object]) -> bool:
    """Require a successful pipeline and a mergeable, discussion-clean non-draft MR."""
    pipeline = mr.get("head_pipeline")
    return (
        mr.get("state") == "opened"
        and mr.get("draft") is False
        and mr.get("merge_status") == "can_be_merged"
        and mr.get("detailed_merge_status") == "mergeable"
        and mr.get("blocking_discussions_resolved") is True
        and isinstance(pipeline, dict)
        and pipeline.get("status") == "success"
        and pipeline.get("sha") == mr.get("sha")
    )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [--apply] <project-path> <merge-request-iid>"
    )
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("project_path")
    parser.add_argument("mr_iid", type=int)
    args = parser.parse_args(argv)
    if args.mr_iid < 0:
        parser.error("merge-request-iid must be non-negative")
    if shutil.which("glab") is None:
        fail("glab is required")

    encoded_project = quote(args.project_path, safe="")
    me = api_object("user", "current user")
    project = api_object(f"projects/{encoded_project}", "project")
    endpoint = f"projects/{encoded_project}/merge_requests/{args.mr_iid}"
    mr = api_object(endpoint, "merge request")
    members = api_pages(
        f"projects/{encoded_project}/members/all", "project memberships"
    )
    linked = api_pages(f"{endpoint}/closes_issues", "linked work items")

    agent_id = integer(me, "id")
    default_branch = project.get("default_branch")
    assignees = mr.get("assignees")
    if (
        agent_id is None
        or not isinstance(default_branch, str)
        or not default_branch
        or integer(mr, "iid") != args.mr_iid
        or mr.get("state") != "opened"
        or not isinstance(mr.get("sha"), str)
        or not mr.get("sha")
        or not isinstance(assignees, list)
        or agent_id not in (user_id(item) for item in assignees)
    ):
        fail("merge request is not open and assigned to the current user")
    if not all(valid_member(member) for member in members):
        fail("project memberships are incomplete")
    if not all(
        integer(item, "iid") is not None
        and isinstance(item.get("author"), dict)
        and user_id(item["author"]) is not None
        and username(item["author"]) is not None
        for item in linked
    ):
        fail("linked work items are incomplete")

    ignored = ignored_reviewers()
    configured: list[str] = []
    tree = api_pages(
        f"projects/{encoded_project}/repository/tree?ref={quote(default_branch, safe='')}",
        "default-branch tree",
    )
    if any(item.get("path") == "AGENTS.md" for item in tree):
        try:
            configured = configured_reviewers(
                api_text(
                    "projects/"
                    f"{encoded_project}/repository/files/AGENTS.md/raw"
                    f"?ref={quote(default_branch, safe='')}"
                )
            )
        except (OSError, subprocess.SubprocessError):
            fail("unable to read default-branch AGENTS.md")

    excluded = {
        agent_id,
        user_id(mr.get("author")),
        *(user_id(item) for item in assignees),
    }
    eligible_members = [
        member
        for member in members
        if member.get("state") == "active"
        and member.get("locked") is False
        and integer(member, "access_level") in (40, 50)
        and integer(member, "id") not in excluded
        and (username(member) or "").casefold() not in ignored
    ]
    eligible = [
        member
        for member in eligible_members
        if human_user(
            api_object(f"users/{integer(member, 'id')}", "reviewer identity"),
            integer(member, "id") or 0,
        )
    ]
    eligible_by_id = {integer(member, "id"): member for member in eligible}
    linked_candidates = {
        user_id(item["author"]): eligible_by_id[user_id(item["author"])]
        for item in linked
        if user_id(item["author"]) in eligible_by_id
    }

    if len(linked_candidates) > 1:
        fail("linked work items have different eligible authors")

    self_review = (
        mr.get("reviewers") == []
        and merge_ready(mr)
        and optional_approval(endpoint)
        and merge_allowed(encoded_project, mr, agent_id, members)
        and any(
            integer(member, "id") == agent_id
            and member.get("state") == "active"
            and member.get("locked") is False
            and (integer(member, "access_level") or 0) >= 30
            for member in members
        )
    )
    reviewer: dict[str, object]
    if self_review:
        rule = "optional-approval-self-merge"
        reviewer = next(
            member for member in members if integer(member, "id") == agent_id
        )
    elif len(linked_candidates) == 1:
        rule = "linked-work-item-author"
        reviewer = next(iter(linked_candidates.values()))
    else:
        eligible_by_name = {username(member): member for member in eligible}
        configured_candidates = [
            eligible_by_name[name] for name in configured if name in eligible_by_name
        ]
        if configured_candidates:
            rule = "configured-reviewer"
            reviewer = configured_candidates[0]
        else:
            if not eligible:
                fail("no eligible reviewer")
            reviewer = sorted(
                eligible,
                key=lambda member: (
                    integer(member, "access_level") or 0,
                    username(member) or "",
                    integer(member, "id") or 0,
                ),
            )[0]
            rule = (
                "maintainer-fallback"
                if integer(reviewer, "access_level") == 40
                else "owner-fallback"
            )

    reviewer_id = integer(reviewer, "id")
    result = {
        "project": args.project_path,
        "merge_request_iid": args.mr_iid,
        "reviewer": {
            "id": reviewer_id,
            "username": username(reviewer),
            "access_level": integer(reviewer, "access_level"),
        },
        "rule": rule,
        "linked_work_item_iids": [integer(item, "iid") for item in linked],
        "ignored_reviewers": sorted(ignored),
        "dry_run": not args.apply,
        "applied": False,
        "self_merge": self_review,
        "merged": False,
    }

    if args.apply:
        if ignored_reviewers() != ignored:
            fail("reviewer exclusions changed; reviewers were not modified")
        fresh_member = api_object(
            f"projects/{encoded_project}/members/all/{reviewer_id}",
            "reviewer membership",
        )
        if not (
            integer(fresh_member, "id") == reviewer_id
            and fresh_member.get("state") == "active"
            and fresh_member.get("locked") is False
            and (
                (integer(fresh_member, "access_level") or 0) >= 30
                if self_review
                else integer(fresh_member, "access_level") in (40, 50)
            )
        ):
            fail("reviewer is no longer eligible")
        if not self_review and not human_user(
            api_object(f"users/{reviewer_id}", "reviewer identity revalidation"),
            reviewer_id or 0,
        ):
            fail("reviewer is no longer eligible")
        fresh_mr = api_object(endpoint, "merge request revalidation")
        if mr_signature(mr) != mr_signature(fresh_mr):
            fail("merge request changed; reviewers were not modified")
        if self_review and not (
            merge_ready(fresh_mr)
            and optional_approval(endpoint)
            and merge_allowed(encoded_project, fresh_mr, agent_id, members)
        ):
            fail(
                "optional approval or merge readiness changed; "
                "reviewers were not modified"
            )
        fresh_reviewers = fresh_mr.get("reviewers")
        reviewer_ids = sorted(
            {
                reviewer_id,
                *(
                    user_id(item)
                    for item in fresh_reviewers or []
                    if user_id(item) is not None
                ),
            }
        )
        try:
            subprocess.run(
                [
                    "glab",
                    "api",
                    "-X",
                    "PUT",
                    endpoint,
                    "--header",
                    "Content-Type: application/json",
                    "--input",
                    "-",
                ],
                input=json.dumps({"reviewer_ids": reviewer_ids}),
                check=True,
                text=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except (OSError, subprocess.SubprocessError):
            fail("unable to add reviewer")
        result["dry_run"] = False
        result["applied"] = True
        if self_review:
            try:
                subprocess.run(
                    [
                        "glab", "api", "-X", "POST", f"{endpoint}/approve",
                        "-f", f"sha={mr['sha']}",
                    ],
                    check=True,
                    text=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except (OSError, subprocess.SubprocessError):
                fail(
                    "unable to approve optional-approval merge request; "
                    "merge was not attempted"
                )
            fresh_mr = api_object(endpoint, "merge request before merge")
            if fresh_mr.get("sha") != mr["sha"] or not merge_ready(fresh_mr):
                fail("merge request changed after approval; merge was not attempted")
            try:
                merged = subprocess.run(
                    [
                        "glab", "api", "-X", "PUT", f"{endpoint}/merge",
                        "-f", f"sha={mr['sha']}",
                    ],
                    check=True,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                )
                response = json.loads(merged.stdout)
            except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
                fail("unable to merge optional-approval merge request")
            if not isinstance(response, dict) or response.get("state") != "merged":
                fail("merge API did not confirm merged state")
            result["merged"] = True

    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
