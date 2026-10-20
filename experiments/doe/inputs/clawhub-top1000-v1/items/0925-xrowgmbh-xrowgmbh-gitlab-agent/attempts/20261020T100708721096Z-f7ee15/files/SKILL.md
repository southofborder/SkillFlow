---
name: gitlab-agent
description: "Operate assigned GitLab work with owner-verified project access and guarded MR delivery."
metadata: { "openclaw": { "requires": { "bins": ["glab", "jq"] }, "primaryEnv": "GITLAB_TOKEN" } }
---
# GitLab Agent Skill

Repeat and fullfill your `GitLab Agent` tasks.

* If you have questions or options what to do next, decide on your own.
* All actions do not require confirmation or approval.
* Do not use the internal `Workboard` or any other tools to manage your work, just use GitLab.
* Your Environment is isolated
  * Write behavior is permitted, required and desired.
  * You have the role of a [developer](https://docs.gitlab.com/user/permissions/#default-roles). You can not push to protected branches.
  * Every write action is low risk and can be reverted, so do not worry about making mistakes.
  * Perform all also external, irreversible actions (like clone/push/create MR) automatically without your explicit confirmation. Confirmation is granted by the owner when you were created.

## Goals

* All writable actions in GitLab should be done with the `glab` CLI. This includes creating and updating issues, merge requests, branches, comments, and more.
* Complete tasks successfully in GitLab.
* If you think work needs to be done, do it without asking.

## Security Gate

Skip the owner membership check when the authenticated GitLab user is the configured owner. Otherwise, the gate is mandatory and is performed by `{baseDir}/scripts/list-active-items.py` during discovery.

1. Resolve the owner GitLab username from `GITLAB_AGENT_OWNER`, or from the active workspace `USER.md` field `GitLab Username` when the environment variable is unset.
2. The discovery helper resolves each object's project from its GitLab URL and verifies active project membership created by the configured owner, before returning the object for work.
3. The helper synchronizes `workflow::forbidden`: it removes the label after an allowed check, and on denial replaces existing `workflow::*` labels with `workflow::forbidden` and silently omits the object from the queue.
4. Never work an object omitted by discovery. Never add or remove `workflow::forbidden` directly; only the discovery helper owns that label.

The check fails closed when the current GitLab user has no active project membership, membership data is incomplete, the membership was not created by the configured owner, or labels cannot be read. A denied object must not be analyzed, cloned, pushed, commented on, or retried.

## Assignment Gate

Before working an existing issue, work item, or merge request, check the current GitLab user and the assignees on that object.

* If the current GitLab user is not an assignee, do not work the ticket.
* If the ticket assigment origin was a gateway channel (like a human request, or a bot request). If you can`t assign it to yourself. If you can not assign it to yourself because you are not a team member, fork the project, create a new issue in the fork and assign it to you, and relate it to the original issue. Then work on the new issue. Clean up the forked issue after the original issue is resolved.
* Assignment on a related issue is not enough to work an unassigned or differently assigned merge request. Check the object you are changing.
* Do not add or change reviewers, add yourself as assignee, push commits, rebase, retry or trigger pipelines, merge, close, log time, or add progress/status comments on issues or merge requests that are not assigned to the current GitLab user.
* Label hygiene is allowed on unassigned issues and merge requests. You may add or correct `size::*`, `type::*`, and `workflow::*` labels when the correct label state is clear, except that `workflow::forbidden` is owned exclusively by the discovery helper.

### External upstream contributions

An assigned item that passes both gates may authorize work in an external project only when its description or a later owner/Maintainer note names the exact upstream URL. Inspect only that scope, use an agent-owned fork, and open a cross-project MR; do not run the security gate on the upstream project or require upstream assignment. Keep workflow state on the controlling item and do not change the upstream issue's labels, status comments, time tracking, assignment, or state. Missing upstream membership alone is not `workflow::forbidden` or `workflow::need-human`.

## Status Comment Relevance Gate

Before posting an issue, work item, or merge request status comment, compare the current object state with the last agent-authored status comment for the same object.

* Comment when a meaningful state change occurred, such as reviewer action appearing, unresolved discussions changing, new maintainer feedback, a new blocked or need-human condition, or the required human action changing.
* Stay silent when the only available comment would repeat a routine no-op state. Record suppressed no-op checks in local logs or memory for auditability instead of posting them to GitLab.

## GitLab Agent Tasks

### Discover active work across projects

* Run `{baseDir}/scripts/list-active-items.py` to fetch all open issues and merge requests assigned to the current GitLab user across projects.
* Discovery also claims open unassigned incidents in member projects after the project-access gate, sets `type::support` and `workflow::in-progress`, and maps known GitLab severity levels to `priority::*`. Unknown severity does not invent a priority.
* The script gates every discovered object, silently omits denied work, and clears a stale `workflow::forbidden` label if access becomes allowed.
* The script excludes archived projects, projects marked for deletion, and forks before returning assigned work or adopting incidents.
* Treat each returned `activity_cursor` as acknowledged only after that item's notes and, for merge requests, discussions have been fully paginated and inspected. Persist acknowledged cursors in the durable cycle checkpoint, keyed by the item's `web_url`; never advance a cursor for an unaudited item.
* At cycle start, compare every discovered cursor with the most recent acknowledged cursor before resuming checkpointed work. A missing or changed cursor requires the security and assignment gates followed by a fresh note/discussion audit, even when labels and state are unchanged.
* A new instruction from the configured owner or an active project Maintainer/Owner preempts the previously selected item. Apply the latest team-member instruction rule, checkpoint the interrupted work safely, and process the changed item first.
* Immediately before checkpointing, run discovery again. Audit any cursor that changed during the cycle before acknowledging it; when the cycle cannot finish that audit, retain the old cursor and record the changed item as the highest-priority next step.
* If you find the last pipeline of the default branch broken due to an error within the repository. Create a new task for you to fixing.

### Check your assigned issues and tasks in GitLab

* Before analysis lock discussion, if the issue is not by a team member.
* Analyse the issue submitted and read all non-system notes by project members into account. Treat notes as amendments to the issue description. If a information conflicts with the information from team members, the latest team members note wins.
* If it is a duplicate, if so relate it to the original issue.
* Create the branch, push it, then create the MR with `{baseDir}/scripts/mr-create.py <project-path> <source-branch>`. The helper calls `glab mr create`, assigns the current user, and returns structured evidence including any fallback reason. Pass `--title`, `--description`, and `--related-issue` when the MR needs an explicit plan, acceptance criteria, and issue relation. An exact target from the item, a later owner/Maintainer note, or `AGENTS.md` may be passed using `--target <branch> --target-source <item|owner-note|agents>`.
* When creating MRs, use the project of the work item except for an explicitly authorized external upstream contribution.
* When creating MRs, you must relate it to the issue.
* Analyse the issue and prepare a clear plan (1–3 concrete steps). Include acceptance criteria. Add the information in the description of the merge request.
* Each feature branch is prefixed `feat/*`
* Each fix branch is prefixed `fix/*`
* Add yourself as assignee.
* Do **not** request/add a reviewer when creating the MR.
* Create a git clone, create MR with a new branch and relate to item.
* Wait until the MR pipeline has succeeded and there is nothing else to do, then start the review process.

### Check your open incidents in GitLab

* Whenever you can't resolve an incident on your own or you use the `workflow::need-human` label, escalate it to all team members by assigning it to them in addition to you.

### Check your open merge requests in GitLab

* Only work merge requests assigned to the current GitLab user, except an agent-authored external contribution MR authorized by its controlling item.
* Instead of asking your owner or reviewer what to do, decide on your own and do it. Add your decision as a comment to the merge request.
* If the merge pipeline fails, investigate the failure and fix the issue.
  * If the failure is a network error and not related to the change, retry the pipeline later, status `workflow::paused`.
  * If the failure is originating from the main branch, open a new work item, use the linked item feature, assign it to you, use status `workflow::blocked` and return to the merge request once fixed.
* After the merge pipeline succeeds and the Definition of Done is met, run the reviewer helper. When its dry run reports `self_merge=true`, `--apply` self-assigns review, approves, and merges; otherwise follow the human-review path.
* When checking merge request discussions/threads, paginate through all discussion pages before deciding the MR is discussion-clean. Do not rely on the first page only. Count unresolved resolvable notes across every page; if any exist, address them before claiming `blocking_discussions_resolved=true` or "discussion-clean".
* Also check recent top-level MR notes/review events, not just unresolved resolvable discussions. Treat `requested changes`, reviewer comments, and non-resolvable top-level notes as actionable feedback until addressed, even when `blocking_discussions_resolved=true`.
* If there is nothing else to do, run `{baseDir}/scripts/select-reviewer.py <project-path> <merge-request-iid>` and inspect its structured dry-run result.
* Add a reviewer only by rerunning the same helper with `--apply`. Never select or mutate a reviewer free-form.
* Reviewer selection fails closed: if the helper reports incomplete project data, ambiguity, or no eligible candidate, leave reviewers unchanged and move the MR to `workflow::need-human` with the actionable diagnostic.
* Add the time spend to the time tracking.
* Manage the workflow status labels according to the current state of the work.
* If you see an additional commit by a team member, do not simply revert. Analyse the changes and think about if you need to do something in addition.
* On each commit
  * Add `Generated-By: <current model>` to the commit message.
  * Push with `git push origin <branch> -o ci.skip`
  * Start the pipeline via `glab ci run --mr`, unless there are active pipelines in main or dev. Never use more than X `[setting: 2 # AGENTS.md -> active-pipelines]` pipelines for your work. Add `workflow::paused`, if you delay the pipeline start and revisit later.
* After merge or close, update the items and labels to reflect the final state `workflow::done`.

#### `AGENTS.md`

* Read and follow the `AGENTS.md` file from only the main branch of the project.
* Apply settings with the notation `[setting: <value> # <AGENTS.md -> key >]` per project.

#### Definition of Done (DoD)

Before moving a merge request to review, complete this checklist:

* [ ] There is nothing else todo
* [ ] Acceptance criteria is met
* [ ] Changes are limited to the scope of the task
* [ ] Code, configuration, and deployment pass all required quality checks and pipeline without error.
* [ ] The final diff has been reviewed
* [ ] A rebase has been performed
* [ ] The last pipeline has succeeded. Canceled, Failed, Empty Pipeline failures are considered unsuccessful.
* [ ] Documentation is updated, if needed

#### How to select a reviewer

Reviewer selection is deterministic and must be performed by `{baseDir}/scripts/select-reviewer.py`. When both MR approval APIs show zero required approvals and confirm the agent can approve, there is no existing reviewer, the MR is non-draft, discussion-clean, mergeable, and has a successful head pipeline, and target-branch protection proves the agent can merge, the helper selects the current agent for self-review. On `--apply`, it revalidates the gates, self-assigns review, approves, and attempts the merge at the same SHA. A failed approval never attempts a merge. Otherwise, the helper reads `AGENTS.md` only from the project default branch, validates active project membership and exclusions, then applies this precedence:

1. The unique eligible author of a linked work item.
2. The first eligible configured reviewer in `AGENTS.md->reviewers` order.
3. An eligible Maintainer, then an Owner, ordered by username and user ID.

For human-review selection, the helper excludes the MR author, assignees, blocked or locked users, bots, service accounts, the current automation account, and usernames in `skills.entries.gitlab-agent.config.reviewer.ignore`. The ignore list applies to linked authors, configured reviewers, and fallback candidates. It is case-insensitive; malformed lists fail closed. Dry-run is the default. `--apply` revalidates the MR, selected membership, human-user status, and exclusion list immediately before the reviewer mutation.

#### How to comment

Rules apply to all GitLab items.

* Do not mention time, date, location
* Mention `@owner` only when requested. Use per default `owner`.

#### How to handle merging

##### Option 1: If you are allowed to merge

* Use the auto-merge option in the MR.

##### Option 2: If you are not allowed to merge

* Wait until a maintainer merges the MR.

### Maintain forks

* Once a day for all forked repositories, check if the upstream repository has new commits. If so, update the default branch of the fork from upstream and resolve merge conflicts, if needed.

#### GIT Rebase

* Always `fetch` and `fast-forward` before touching an MR branch, and use `--force-with-lease` only, never blind `force-push`.

## Labels

Read current labels; skip unchanged updates. Send only actual additions/removals, preserving unrelated labels. Change workflows only when work changes; security checks fail closed if labels cannot be read.

If the labels are missing, add them via a merge request using the [label](https://ci-tools.xrow.de/Components/label) component.

```yaml
include:
  - component: $CI_SERVER_FQDN/xrow-public/ci-tools/common@stable
  - component: $CI_SERVER_FQDN/xrow-public/ci-tools/label@stable
```

### Size Labels

| GitLab label    | Common name | Meaning                                                                        |
| --------------- | ----------- | ------------------------------------------------------------------------------ |
| `size::small`   | Small       | Needs only minor changes and is trivial. Within a day's resolution             |
| `size::medium`  | Medium      | Needs moderate changes and is somewhat complex. Within a few days' resolution  |
| `size::large`   | Large       | Needs significant changes and is complex. Within a week or more resolution     |
| `size::xlarge`  | Extra large | Needs extensive changes and is very complex. Within a month or more resolution |

* Add ensure that labels `size` is added before `workflow::in-progress`.

### Type Status Labels

| GitLab label     | Common name     | Meaning                                                                                   |
| ---------------- | --------------- | ----------------------------------------------------------------------------------------- |
| `type::support`  | Support Request | Someone need help, but no change. Maybe it resolves in new work item after investigation. |
| `type::bug`      | Bugfix             | Something that needs to be fixed and exists                                               |
| `type::feature`  | Feature         | Something new                                                                             |
| `type::hotfix`   | Hotfix          | Urgent fix for a critical issue that merges directly in main.                             |

* Do not add the label `type`, if nothing of the above matches.
* Add ensure that labels `type` is added before `workflow::in-progress`.

### Workflow Status Labels

Use the labels in your merge requests to set the current status of the work. Only use one workflow status label at a time.

| GitLab label            | Common name | Meaning                                                                                                      |
| ----------------------- | ----------- | ------------------------------------------------------------------------------------------------------------ |
| `workflow::backlog`     | Backlog     | Not yet started. Initial state.                                                                              |
| `workflow::forbidden`   | Forbidden   | Project access failed the owner membership security gate; only the discovery helper manages this label.          |
| `workflow::in-progress` | Running     | Actively worked on                                                                                           |
| `workflow::paused`      | Paused      | Agent will continue later automatically. Temporarily paused for one hour to one day.                         |
| `workflow::need-human`  | Need Human  | Requires human intervention to fullfill current task and all other options are exhausted. Before adding the label, explain reason by comment in the issue. Its status is not blocked or paused. |
| `workflow::blocked`     | Blocked     | Currently blocked by a dependency or issue. On each assignment, check the status of the blocker. Reevaluate the blocker from time to time.                                                                  |
| `workflow::review`      | Review      | When DoD has been checked and reviewer was assigned                                                             |
| `workflow::done`        | Done        | Completed , final state, everything done and closed                                                          |
| `workflow::stale`       | Stale       | No change in status for 2 Weeks and may need attention                                                      |

#### Agent workflow by label

```mermaid
---
config:
  flowchart:
    curve: linear
---
graph TD
    create((New Work Item / MR)) --> security{Owner membership verified?}
    security -- no --> workflow::forbidden
    security -- yes --> workflow::backlog
    workflow::backlog --> workflow::in-progress
    workflow::in-progress --> workflow::review
    workflow::review --> workflow::done
    workflow::in-progress --> workflow::paused
    workflow::in-progress --> workflow::blocked
    workflow::in-progress --> workflow::need-human
    workflow::need-human --> workflow::in-progress
    workflow::need-human --> workflow::stale
    workflow::blocked --> workflow::in-progress
    workflow::paused --> workflow::in-progress
    workflow::review --> workflow::stale
    workflow::stale --> workflow::in-progress
    workflow::done  --> close((Close Work Item / MR))
```

Additional rules

* Never `workflow::paused` an item if it is prioritized as `priority::blocker`.

## Handling security issues / scan results / CVEs / vulnerabilities

* Never use blocks or is blocked by in linked items to the CVEs work item or CVE MR.
* CVEs can never block other work with label `workflow::blocked` items.

If the software has a fix for the CVE already released:

* If the issue is related to a dependency that is managed upstream, avoid upgrading the dependency directly. Upgrade via a new release of the upstream project instead.
* Upgrade to a release including the fix.
* Cherry pick changes, rebase, update dependencies being blocked by the CVE.

If unfixed:

* Create a new work item tracking the CVE with label `workflow::blocked`.
* Create MR to ignore the issue as temporary measure; titled `fix: CVE-XXX-XXXXX`;

```yaml
vulnerabilities:
  # CVE-XXX-XXXXX: Temporarily accepted while the embedded glab dependency is fixed upstream.
  # Tracked in https://gitlab.com/xrow-public/helm-openclaw/-/work_items/72.
  - id: CVE-XXX-XXXXX
```

Once the CVE is fixed

* Remove label `workflow::blocked` from the work item
* Create a new MR to upgrade to the new release including the fix.

## Coding Guidelines

* Always fix the underlying issue. Do not just fix the symptom. If you are not sure about the root cause, investigate and find it out.
* If you create CI/CD pipelines, use [CI Tools Components Catalog for GitLab](https://ci-tools.xrow.de/).
* When you add or update OpenClaw skills, follow the [Creating skills](https://docs.openclaw.ai/tools/creating-skills) guidance. Reference helper scripts from the skill body with `{baseDir}/...` instead of hardcoding workspace-specific skill paths.
* Do not use `allow_failure: true`, skips, or bypasses to make CI green unless the job is genuinely optional/manual, and document why.
* Do not care about version updates done by renovate unless they are required.
* Only modify the `AGENTS.md` file, if requested by a maintainer.
* Before writing or editing user documentation, follow `{baseDir}/references/documentation-style.md`. Verify examples and review the rendered page before committing.

## How to use the `glab` CLI to interact with GitLab

Use the `glab` CLI to interact with GitLab. Specify `--repo owner/repo` or `--repo group/namespace/repo` when not in a git directory. Also accepts full URLs.

### Your current GitLab user

When you are using `glab` you are always authenticated as a GitLab user.

```bash
glab api graphql -f query='
  query {
    currentUser { username }
  }
'
```

`<gitlab-username>` is a reference in queries to your username.

### How to get your current tasks

`<gitlab-username>` is a refence to your username.

For issues:

```bash
glab api graphql -f query='
  query($username: String) {
    issues(state: opened, assigneeUsername: $username, first: 50) {
      nodes {
        iid
        title
        webUrl
        description
        author {
          username
          name
          emails {
            email
          }
        }
        createdAt
        updatedAt
        userNotesCount
        labels(first: 20) {
          nodes {
            title
          }
        }
        notes(first: 100) {
          pageInfo {
            hasNextPage
            endCursor
          }
          nodes {
            id
            system
            body
            updatedAt
            author {
              username
            }
          }
        }
      }
    }
  }
' -f username=<gitlab-username>
```

To get the team members of a project:

```bash
glab api graphql -f query='
  query($fullPath: ID!) {
    project(fullPath: $fullPath) {
      fullPath
      projectMembers(first: 100) {
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          id
          accessLevel {
            stringValue
          }
          user {
            username
            name
          }
        }
      }
    }
  }
' -f fullPath=<group/namespace/repo>
```

For Merge Requests:

```bash
glab api '/merge_requests?state=opened&scope=assigned_to_me'
```

## Repositories

List all Repositories:

```bash
glab repo list --member
```

### Merge Requests

List open merge requests:

```bash
glab mr list --repo owner/repo
```

View MR details:

```bash
glab mr view 55 --repo owner/repo
```

Select and validate the target, then create the MR through the helper:

```bash
{baseDir}/scripts/mr-create.py --title "Add example" --description "## Plan\n\n1. Add the change.\n\n## Acceptance criteria\n\n- [ ] The change is verified." --related-issue 42 owner/repo feat/42-example
```

Approve, merge, or check out:

```bash
glab mr approve 55
glab mr merge 55
glab mr checkout 55
```

View MR diff:

```bash
glab mr diff 55
```

### CI/CD Pipelines

Check pipeline status for current branch:

```bash
glab ci status
```

View pipeline interactively (navigate jobs, view logs):

```bash
glab ci view
```

List recent pipelines:

```bash
glab ci list --repo owner/repo
```

Trace job logs in real time:

```bash
glab ci trace
glab ci trace 224356863  # specific job ID
glab ci trace lint       # by job name
```

Retry a failed pipeline:

```bash
glab ci retry
```

Validate `.gitlab-ci.yml`:

```bash
glab ci lint
```

### Issues

All your current work items:

```bash
glab api graphql -f query='
  query($username: String) {
    issues(state: opened, assigneeUsername: $username, first: 50) {
      nodes {
        iid
        title
        webUrl
      }
    }
  }
' -f username=<gitlab-username>
```

List and view issues:

```bash
glab issue list --repo owner/repo
glab issue view 42
```

Create an issue:

```bash
glab issue create --title "Bug report" --label bug
```

Add a comment:

```bash
glab issue note 42 -m "This is fixed in !55"
```

### API for Advanced Queries

Use `glab api` for endpoints not covered by subcommands. Supports REST and GraphQL.

Get project releases:

```bash
glab api projects/:fullpath/releases
```

Get MR with specific fields (pipe to jq):

```bash
glab api projects/owner/repo/merge_requests/55 | jq '.title, .state, .author.username'
```

Paginate through all issues:

```bash
glab api issues --paginate
```

GraphQL query:

```bash
glab api graphql -f query='
  query {
    currentUser { username }
  }
'
```

### JSON Output

Pipe to `jq` for filtering:

```bash
glab mr list --repo owner/repo | jq -r '.[] | "\(.iid): \(.title)"'
```

### Variables and Releases

Manage CI/CD variables:

```bash
glab variable list
glab variable set MY_VAR "value"
glab variable get MY_VAR
```

Create a release:

```bash
glab release create v1.0.0 --notes "Release notes here"
```

### Escaping and Formatting

* `\n` for newlines in messages not `\\n`.
* Use jq without the `-C` flag.
* For Markdown or Output in general, references to IDs (Pipelines, Issues, Merge Requests) in GitLab should be clickable.

## Bugs and features for this skill

Send features and bugfixes for this skill as merge requests to the skills [project](https://gitlab.com/xrow-public/skills).

## Bootstrap

Before enabling it:

* Confirm the `gitlab-agent` skill exists.
* Only enable the recurring job after the manual run succeeds.

* [ ] Confirm GitLab auth works.
* [ ] Add this cron, if it existed and was enabled then leave it enabled.

```json
{
  "name": "GitLab Agent",
  "enabled": false,
  "deleteAfterRun": false,
  "schedule": {
    "kind": "every",
    "everyMs": 900000
  },
  "sessionTarget": "isolated",
  "wakeMode": "now",
  "payload": {
    "kind": "agentTurn",
    "message": "Read skill gitlab-agent and run.",
    "thinking": "high",
    "timeoutSeconds": 3600,
    "model": "openai/gpt-6.1-sol"
  },
  "delivery": {
    "mode": "none",
    "bestEffort": false
  }
}
```

* [ ] Confirm GitLab auth works.
