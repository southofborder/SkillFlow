#!/usr/bin/env python3
"""List assigned work, collaborator submissions, and adopt unassigned incidents."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote, unquote, urlencode, urlsplit


PER_PAGE = 100
PRIORITY_ORDER = {
    "priority::blocker": 0,
    "priority::high": 1,
    "priority::medium": 2,
    "priority::low": 3,
}
CONFIG_PATH_ENV = "OPENCLAW_CONFIG_PATH"
INCIDENT_PRIORITY = {
    "CRITICAL": "priority::blocker",
    "HIGH": "priority::high",
    "MEDIUM": "priority::medium",
    "LOW": "priority::low",
}


def api_json(endpoint: str) -> object:
    result = subprocess.run(
        ["glab", "api", endpoint],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    return json.loads(result.stdout)


def paginated(endpoint: str) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    page = 1
    while True:
        separator = "&" if "?" in endpoint else "?"
        payload = api_json(
            f"{endpoint}{separator}{urlencode({'per_page': PER_PAGE, 'page': page})}"
        )
        if not isinstance(payload, list):
            raise ValueError(f"GitLab returned a non-list page for {endpoint}")
        for item in payload:
            if not isinstance(item, dict):
                raise ValueError(f"GitLab returned an invalid item for {endpoint}")
            records.append(item)
        if len(payload) < PER_PAGE:
            break
        page += 1
    return records


def configured_owner() -> str:
    """Use the explicit owner, or the active workspace's USER.md identity."""
    owner = os.environ.get("GITLAB_AGENT_OWNER", "").strip()
    if owner:
        return owner
    user_file = Path(__file__).resolve().parents[3] / "USER.md"
    for line in user_file.read_text(encoding="utf-8").splitlines():
        prefix = "- **GitLab Username:**"
        if line.strip().startswith(prefix):
            owner = line.strip()[len(prefix):].strip()
            if owner:
                return owner
    raise ValueError("GitLab agent owner is not configured")


def object_endpoint(item: dict[str, object], kind: str) -> tuple[str, str]:
    """Resolve project identity only from the GitLab item URL."""
    url = item.get("web_url")
    iid = item.get("iid")
    if not isinstance(url, str) or not url or type(iid) is not int or iid <= 0:
        raise ValueError("GitLab item identity is incomplete")
    path = urlsplit(url).path
    project, separator, tail = path.partition("/-/")
    collection = "merge_requests" if kind == "merge_request" else "issues"
    valid_routes = ("merge_requests",) if kind == "merge_request" else ("issues", "work_items")
    if not separator or not any(tail == f"{route}/{iid}" for route in valid_routes):
        raise ValueError("GitLab item URL does not match its identity")
    project_path = unquote(project.strip("/"))
    if not project_path or any(part in ("", ".", "..") for part in project_path.split("/")):
        raise ValueError("GitLab project path is invalid")
    return project_path, f"projects/{quote(project_path, safe='')}/{collection}/{iid}"


def owner_created_membership(
    project_path: str, agent_id: int, agent_username: str, owner: str
) -> bool:
    try:
        membership = api_json(
            f"projects/{quote(project_path, safe='')}/members/all/{agent_id}"
        )
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
        return False
    return (
        isinstance(membership, dict)
        and membership.get("username") == agent_username
        and membership.get("membership_state") == "active"
        and type(membership.get("access_level")) is int
        and membership["access_level"] >= 10
        and isinstance(membership.get("created_by"), dict)
        and membership["created_by"].get("username") == owner
    )


def synchronize_forbidden(endpoint: str, *, allowed: bool) -> list[str]:
    """Read current labels, then send only the required delta."""
    payload = api_json(endpoint)
    labels = payload.get("labels") if isinstance(payload, dict) else None
    if not isinstance(labels, list) or any(not isinstance(label, str) for label in labels):
        raise ValueError("GitLab object labels are missing or invalid")
    current = set(labels)
    forbidden = "workflow::forbidden"
    additions = [] if allowed or forbidden in current else [forbidden]
    removals = sorted(
        label for label in current
        if (label == forbidden if allowed else label.startswith("workflow::") and label != forbidden)
    )
    if additions or removals:
        command = ["glab", "api", "-X", "PUT", endpoint]
        if additions:
            command.extend(("-f", "add_labels=" + ",".join(additions)))
        if removals:
            command.extend(("-f", "remove_labels=" + ",".join(removals)))
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return sorted((current | set(additions)) - set(removals))


def permitted_items(
    items: list[tuple[dict[str, object], str]],
    agent_id: int,
    agent_username: str,
    owner: str,
) -> list[dict[str, object]]:
    """Fail each item closed and quietly omit denied items after label hygiene."""
    access: dict[str, bool] = {}
    result: list[dict[str, object]] = []
    for item, kind in items:
        try:
            project_path, endpoint = object_endpoint(item, kind)
            if project_path not in access:
                access[project_path] = (
                    agent_username == owner
                    or owner_created_membership(project_path, agent_id, agent_username, owner)
                )
            allowed = access[project_path]
            labels = synchronize_forbidden(endpoint, allowed=allowed)
            if allowed:
                safe_item = dict(item)
                safe_item["labels"] = labels
                result.append(normalized(safe_item, kind))
        except (OSError, subprocess.SubprocessError, json.JSONDecodeError, ValueError):
            continue
    return result


def configured_accept_entries() -> list[str]:
    """Read collaborator selectors from the active OpenClaw configuration."""
    configured_path = os.environ.get(CONFIG_PATH_ENV)
    config_path = (
        Path(configured_path).expanduser()
        if configured_path
        else Path.home() / ".openclaw" / "openclaw.json"
    )
    if not config_path.exists():
        return []
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("OpenClaw configuration is not an object")
    skills = payload.get("skills", {})
    if not isinstance(skills, dict):
        raise ValueError("OpenClaw skills configuration is not an object")
    entries = skills.get("entries", {})
    if not isinstance(entries, dict):
        raise ValueError("OpenClaw skill entries configuration is not an object")
    agent = entries.get("gitlab-agent", {})
    if not isinstance(agent, dict):
        raise ValueError("gitlab-agent configuration is not an object")

    # OpenClaw currently reserves arbitrary skill settings below `config`, while
    # accepting the issue-requested direct spelling for forward compatibility.
    collaborators = agent.get("collaborators")
    if collaborators is None:
        skill_config = agent.get("config", {})
        if not isinstance(skill_config, dict):
            raise ValueError("gitlab-agent config is not an object")
        collaborators = skill_config.get("collaborators", {})
    if not isinstance(collaborators, dict):
        raise ValueError("gitlab-agent collaborators configuration is not an object")
    accept = collaborators.get("accept", [])
    if not isinstance(accept, list) or any(
        not isinstance(entry, str) or not entry.strip() for entry in accept
    ):
        raise ValueError("gitlab-agent collaborators.accept must be a list of strings")
    return [entry.strip() for entry in accept]


def user_matches_domain(user: dict[str, object], domain: str) -> bool:
    suffix = f"@{domain.lower()}"
    return any(
        isinstance(user.get(field), str)
        and str(user[field]).lower().endswith(suffix)
        for field in ("email", "public_email", "commit_email")
    )


def accepted_usernames(selectors: list[str]) -> set[str]:
    """Resolve username, group, and public-email-domain selectors."""
    usernames: set[str] = set()
    for selector in selectors:
        if selector.startswith("@"):
            domain = selector[1:].lower()
            if not domain or "." not in domain:
                raise ValueError(f"invalid collaborator email domain: {selector}")
            for user in paginated(f"users?{urlencode({'search': domain})}"):
                username = user.get("username")
                if isinstance(username, str) and user_matches_domain(user, domain):
                    usernames.add(username)
            continue

        matching_users = [
            user
            for user in paginated(f"users?{urlencode({'username': selector})}")
            if user.get("username") == selector
        ]
        usernames.update(
            user["username"]
            for user in matching_users
            if isinstance(user.get("username"), str)
        )

        groups = [
            group
            for group in paginated(f"groups?{urlencode({'search': selector})}")
            if group.get("full_path") == selector or group.get("path") == selector
        ]
        for group in groups:
            group_id = group.get("id")
            if not isinstance(group_id, int) or isinstance(group_id, bool):
                raise ValueError(f"GitLab group identity is incomplete: {selector}")
            for member in paginated(f"groups/{group_id}/members/all"):
                username = member.get("username")
                if isinstance(username, str):
                    usernames.add(username)

        if not matching_users and not groups:
            raise ValueError(f"unknown collaborator username or group: {selector}")
    return usernames


def unassigned_items_by(usernames: set[str]) -> list[dict[str, object]]:
    items: dict[tuple[object, object], dict[str, object]] = {}
    for username in sorted(usernames):
        endpoint = "issues?" + urlencode(
            {
                "state": "opened",
                "scope": "all",
                "assignee_id": "None",
                "author_username": username,
            }
        )
        for item in paginated(endpoint):
            author = item.get("author")
            if not isinstance(author, dict) or author.get("username") not in usernames:
                raise ValueError("GitLab collaborator item author is incomplete")
            items[(item.get("project_id"), item.get("iid"))] = item
    return list(items.values())


def project_is_active(project_id: object, cache: dict[int, bool]) -> bool:
    """Exclude archived, deleting, and forked projects before fetching work."""
    if type(project_id) is not int or project_id <= 0:
        raise ValueError("GitLab project identity is incomplete")
    if project_id not in cache:
        project = api_json(f"projects/{project_id}")
        if (
            not isinstance(project, dict)
            or project.get("id") != project_id
            or type(project.get("archived")) is not bool
        ):
            raise ValueError(f"GitLab project metadata is incomplete: {project_id}")
        cache[project_id] = not (
            project["archived"]
            or project.get("marked_for_deletion_at")
            or project.get("pending_delete")
            or project.get("forked_from_project")
        )
    return cache[project_id]


def unassigned_incidents(project_cache: dict[int, bool]) -> list[dict[str, object]]:
    """Enumerate incidents only in active non-fork member projects."""
    incidents: list[dict[str, object]] = []
    for project in paginated("projects?membership=true&simple=true"):
        project_id = project.get("id")
        if not project_is_active(project_id, project_cache):
            continue
        for item in paginated(
            f"projects/{project_id}/issues?state=opened&issue_type=incident&assignee_id=None"
        ):
            if item.get("issue_type") != "incident":
                raise ValueError("GitLab incident query returned another issue type")
            if item.get("assignees") != []:
                raise ValueError("GitLab unassigned incident query returned an assignee")
            incidents.append(item)
    return incidents


def adopt_incident(
    item: dict[str, object], username: str, user_id: int, owner: str
) -> dict[str, object] | None:
    """Gate, assign, and label an unassigned incident before adding it to the queue."""
    try:
        project_path, endpoint = object_endpoint(item, "incident")
        allowed = username == owner or owner_created_membership(
            project_path, user_id, username, owner
        )
        synchronize_forbidden(endpoint, allowed=allowed)
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError, ValueError):
        return None
    if not allowed:
        return None
    current = api_json(endpoint)
    if not isinstance(current, dict) or current.get("issue_type") != "incident":
        raise ValueError("GitLab incident changed during adoption")
    if current.get("assignees") != [] or current.get("state") != "opened":
        return None
    labels = current.get("labels")
    if not isinstance(labels, list) or any(not isinstance(label, str) for label in labels):
        raise ValueError("GitLab incident labels are incomplete")
    severity = current.get("severity")
    if not isinstance(severity, str):
        raise ValueError("GitLab incident severity is incomplete")
    desired = {"type::support", "workflow::in-progress"}
    # UNKNOWN is not a priority; retain any existing priority until severity is set.
    priority = INCIDENT_PRIORITY.get(severity.upper())
    if priority:
        desired.add(priority)
    existing = set(labels)
    removals = {
        label for label in existing
        if (label.startswith("workflow::") and label != "workflow::in-progress")
        or (label.startswith("type::") and label != "type::support")
    }
    if priority:
        removals.update(
            label for label in existing
            if label.startswith("priority::") and label != priority
        )
    additions = desired - existing
    command = ["glab", "api", "-X", "PUT", "-f", f"assignee_ids={user_id}"]
    if additions:
        command += ["-f", "add_labels=" + ",".join(sorted(additions))]
    if removals:
        command += ["-f", "remove_labels=" + ",".join(sorted(removals))]
    command.append(endpoint)
    result = subprocess.run(command, check=True, text=True, stdout=subprocess.PIPE)
    adopted = json.loads(result.stdout)
    if not isinstance(adopted, dict) or username not in [
        assignee.get("username") for assignee in adopted.get("assignees", [])
        if isinstance(assignee, dict)
    ]:
        raise ValueError("GitLab did not assign the incident to the agent")
    return adopted


def normalized(item: dict[str, object], kind: str) -> dict[str, object]:
    assignees = item.get("assignees")
    if not isinstance(assignees, list):
        assignees = []
    labels = item.get("labels")
    if not isinstance(labels, list):
        labels = []
    updated_at = item.get("updated_at")
    user_notes_count = item.get("user_notes_count")
    if not isinstance(updated_at, str) or not updated_at:
        raise ValueError("GitLab item activity is missing updated_at")
    if (
        not isinstance(user_notes_count, int)
        or isinstance(user_notes_count, bool)
        or user_notes_count < 0
    ):
        raise ValueError("GitLab item activity has an invalid user_notes_count")
    return {
        "kind": kind,
        "project_id": item.get("project_id"),
        "iid": item.get("iid"),
        "title": item.get("title"),
        "web_url": item.get("web_url"),
        "labels": labels,
        "assignees": [
            assignee.get("username")
            for assignee in assignees
            if isinstance(assignee, dict)
        ],
        "activity_cursor": {
            "updated_at": updated_at,
            "user_notes_count": user_notes_count,
        },
    }


def issue_kind(item: dict[str, object]) -> str:
    """Keep incidents visible as incidents while treating other work items as issues."""
    return "incident" if item.get("issue_type") == "incident" else "issue"


def is_root_cause(item: dict[str, object]) -> bool:
    """Return whether an issue blocks at least one other open work item."""
    project_id = item.get("project_id")
    iid = item.get("iid")
    if (
        not isinstance(project_id, int)
        or isinstance(project_id, bool)
        or project_id <= 0
        or not isinstance(iid, int)
        or isinstance(iid, bool)
        or iid <= 0
    ):
        raise ValueError("GitLab issue identity is incomplete")
    links = paginated(f"projects/{project_id}/issues/{iid}/links")
    return any(
        link.get("link_type") == "blocks" and link.get("state") == "opened"
        for link in links
    )


def priority_rank(labels: object) -> int:
    if not isinstance(labels, list):
        raise ValueError("GitLab item labels are incomplete")
    return min(
        (PRIORITY_ORDER[label] for label in labels if label in PRIORITY_ORDER),
        default=len(PRIORITY_ORDER),
    )


def main() -> int:
    if shutil.which("glab") is None:
        print("glab is required", file=sys.stderr)
        return 69
    try:
        user = api_json("user")
        if not isinstance(user, dict) or not isinstance(user.get("username"), str):
            raise ValueError("GitLab user response is incomplete")
        username = user["username"]
        agent_id = user.get("id")
        if type(agent_id) is not int:
            raise ValueError("GitLab user id is missing")
        owner = configured_owner()
        project_cache: dict[int, bool] = {}
        adopted_incidents = [
            adopted for incident in unassigned_incidents(project_cache)
            if (adopted := adopt_incident(incident, username, agent_id, owner))
            is not None
        ]
        collaborators = accepted_usernames(configured_accept_entries())
        assigned_issues = [
            item for item in paginated("issues?state=opened&scope=assigned_to_me")
            if project_is_active(item.get("project_id"), project_cache)
        ]
        collaborator_issues = [
            item for item in unassigned_items_by(collaborators)
            if project_is_active(item.get("project_id"), project_cache)
        ]
        collaborator_item_ids = {
            (item.get("project_id"), item.get("iid"))
            for item in collaborator_issues
        }
        issue_items = {
            (item.get("project_id"), item.get("iid")): item
            for item in [*assigned_issues, *collaborator_issues, *adopted_incidents]
        }.values()
        raw_items = [
            *((item, issue_kind(item)) for item in issue_items),
            *((item, "merge_request") for item in paginated(
                "merge_requests?state=opened&scope=assigned_to_me"
            ) if project_is_active(item.get("project_id"), project_cache)),
        ]
        eligible = [
            (item, kind) for item, kind in raw_items
            if (
                any(
                    isinstance(assignee, dict) and assignee.get("username") == username
                    for assignee in (
                        item.get("assignees") if isinstance(item.get("assignees"), list) else []
                    )
                )
                or (
                    item.get("assignees") == []
                    and (item.get("project_id"), item.get("iid")) in collaborator_item_ids
                )
            )
        ]
        active = permitted_items(eligible, agent_id, username, owner)
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError, ValueError) as error:
        print(f"unable to list active GitLab items: {error}", file=sys.stderr)
        return 69

    try:
        root_causes = {
            (item["project_id"], item["iid"])
            for item in active
            if item["kind"] != "merge_request" and is_root_cause(item)
        }
        active.sort(
            key=lambda item: (
                priority_rank(item["labels"]),
                0 if (item["project_id"], item["iid"]) in root_causes else 1,
                str(item.get("web_url") or ""),
            )
        )
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError, ValueError) as error:
        print(f"unable to order active GitLab items: {error}", file=sys.stderr)
        return 69
    json.dump(active, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
