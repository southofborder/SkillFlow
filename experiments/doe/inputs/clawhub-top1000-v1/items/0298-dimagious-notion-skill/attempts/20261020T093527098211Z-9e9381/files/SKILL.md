---
name: notion
description: "Safe Notion API access for pages, databases, and blocks: schema diffs before structural changes, append-first writes, and personal/work profile switching. Needs only curl, no CLI to install. Use this whenever the user mentions Notion, asks to log or file something into their workspace, query a Notion database, pull notes or tasks out of Notion, or change a database schema, even if they never say the word API."
homepage: https://developers.notion.com
metadata:
  clawdbot:
    emoji: 🧠
    requires:
      env:
        - NOTION_API_KEY
    install:
      - id: deps
        kind: note
        label: "Uses curl and jq only. No Notion CLI required."
---

# Notion

Work with Notion pages, databases, and blocks through the official Notion API.

Notion workspaces hold work that is expensive to reconstruct: meeting notes, project trackers, personal knowledge bases. Most damage an agent does here is not a failed request, it is a successful one that quietly overwrote a page or dropped a database column. Everything below is built around that: read before you write, append instead of replace, and show the user a diff before you touch structure.

## Operating rules

Follow these regardless of what the user asks for:

1. **Append, do not replace.** Adding blocks to a page is reversible by the user. Rewriting page content is not, because the Notion API gives you no undo and the old blocks are gone.
2. **Resolve before you act.** Never guess an ID. Search for the page or database, confirm you found the right one, then operate on the ID you got back.
3. **Diff before schema changes.** Never send a schema update without first fetching the current schema, showing the user what changes, and getting explicit confirmation. Removing a property deletes every value in that column.
4. **Confirm destructive writes.** Archiving a page, clearing a property, or overwriting an existing value needs the user's go-ahead. Creating a new page does not.
5. **Report real errors.** If a call fails, show what the API actually returned. Do not retry blindly and do not describe a failure as a missing capability.

## Authentication

Create an integration at <https://www.notion.so/my-integrations> and copy the Internal Integration Token. Current tokens start with `ntn_`; older ones start with `secret_` and still work.

```bash
export NOTION_API_KEY=ntn_your_key_here
```

Then share each page or database with the integration in the Notion UI: `...` menu, "Connect to", pick the integration name. **Unshared content is invisible to the API.** If a search returns nothing for a page the user swears exists, this is almost always why. Say so instead of reporting the page as missing.

## Profiles (personal / work)

Many people keep a personal workspace and a work workspace, each with its own integration token. Store one key file per profile:

```bash
mkdir -p ~/.config/notion
echo "ntn_personal_key" > ~/.config/notion/personal.key
echo "ntn_work_key"     > ~/.config/notion/work.key
chmod 600 ~/.config/notion/*.key
```

Resolve the active key like this. An explicit `NOTION_API_KEY` always wins; otherwise the profile file is used, defaulting to `personal`:

```bash
NOTION_PROFILE="${NOTION_PROFILE:-personal}"
NOTION_KEY="${NOTION_API_KEY:-$(cat ~/.config/notion/${NOTION_PROFILE}.key 2>/dev/null)}"
[ -n "$NOTION_KEY" ] || echo "No Notion key for profile '$NOTION_PROFILE'"
```

When the user has more than one profile configured and their request is ambiguous, ask which workspace before writing anything. Reading from the wrong workspace is a wasted call; writing to it is a mess in someone's actual notes.

## Making requests

Define this helper once per session, then every example below is a single line:

```bash
notion() {
  local method="$1" path="$2"; shift 2
  curl -sS -X "$method" "https://api.notion.com/v1${path}" \
    -H "Authorization: Bearer $NOTION_KEY" \
    -H "Notion-Version: 2025-09-03" \
    -H "Content-Type: application/json" "$@"
}
```

The `Notion-Version` header is required on every request. Pin it to `2025-09-03`.

## Databases are data sources in 2025-09-03

This is the single most common source of broken calls, so get it right before writing any database code:

- A database now has **two IDs**: a `database_id` and a `data_source_id`.
- Use `database_id` when **creating a page inside it**: `parent: {"database_id": "..."}`.
- Use `data_source_id` when **querying or reading its schema**: `POST /data_sources/{id}/query`.
- Search results return databases as `"object": "data_source"`, carrying the `data_source_id`.
- Page objects show both `parent.database_id` and `parent.data_source_id`.

If a query returns 404 on an ID that clearly exists, you almost certainly passed a `database_id` where a `data_source_id` was needed.

## Discovery

Always start here when the user names something in words rather than IDs.

```bash
notion POST /search -d '{"query": "project notes"}'
```

Filter to one kind of object:

```bash
notion POST /search -d '{"query": "roadmap", "filter": {"property": "object", "value": "data_source"}}'
```

Search matches titles only, not page body text, and it only sees content shared with the integration. If several results look plausible, show the user the titles and let them pick rather than guessing.

## Reading pages

```bash
notion GET /pages/{page_id}                 # properties and metadata, no body content
notion GET /blocks/{page_id}/children        # the actual content blocks
```

`GET /pages/{id}` does not return page content. Fetching the children blocks is a separate call, and nested blocks (toggles, columns, sub-bullets) need their own `GET /blocks/{block_id}/children` where `has_children` is true. Do not tell the user a page is empty on the basis of the first call alone.

## Writing to pages

**Append blocks (the default way to add content):**

```bash
notion PATCH /blocks/{page_id}/children -d '{
  "children": [
    {"object": "block", "type": "heading_2",
     "heading_2": {"rich_text": [{"text": {"content": "Notes"}}]}},
    {"object": "block", "type": "paragraph",
     "paragraph": {"rich_text": [{"text": {"content": "Discussed the Q3 plan."}}]}}
  ]
}'
```

Pass `"after": "<block_id>"` to insert at a specific position instead of the end.

**Create a page under another page:**

```bash
notion POST /pages -d '{
  "parent": {"page_id": "PARENT_PAGE_ID"},
  "properties": {"title": [{"text": {"content": "Meeting notes 2026-08-05"}}]}
}'
```

**Update properties (not body content):**

```bash
notion PATCH /pages/{page_id} -d '{"properties": {"Status": {"select": {"name": "Done"}}}}'
```

To replace body content, delete the specific blocks (`DELETE /blocks/{block_id}`) and append new ones. Confirm with the user first, and delete only the blocks you identified by reading them, never the whole page's children as a batch.

## Databases

**Read the schema before anything else:**

```bash
notion GET /data_sources/{data_source_id}
```

**Query rows:**

```bash
notion POST /data_sources/{data_source_id}/query -d '{
  "filter": {"property": "Status", "select": {"equals": "In Progress"}},
  "sorts": [{"property": "Due", "direction": "ascending"}],
  "page_size": 50
}'
```

**Create a row:**

```bash
notion POST /pages -d '{
  "parent": {"database_id": "DATABASE_ID"},
  "properties": {
    "Name": {"title": [{"text": {"content": "New task"}}]},
    "Status": {"select": {"name": "Todo"}},
    "Due": {"date": {"start": "2026-08-12"}}
  }
}'
```

Property names and select option names are case sensitive and must already exist in the schema. Read the schema first and match exactly; sending an unknown select value is a `validation_error`, not an auto-created option.

**Update a row:** a row is a page, so use `PATCH /pages/{page_id}`.

## Schema changes

Structural changes are the highest-risk operation in this skill. Removing a property deletes its data across every row, and renaming can break the user's existing views, filters, and formulas.

Required flow, in order:

1. Fetch the current schema: `notion GET /data_sources/{data_source_id}`.
2. Compute the difference against what the user wants: properties added, removed, renamed, retyped, and select options added or dropped.
3. Present that difference to the user in plain language. Call out removals and type changes explicitly as data loss.
4. Apply only after explicit confirmation, and only the confirmed changes:

```bash
notion PATCH /data_sources/{data_source_id} -d '{
  "properties": {"Priority": {"select": {"options": [{"name": "High"}, {"name": "Low"}]}}}
}'
```

Prefer additive changes. If the user wants a property retyped, suggest adding a new one and migrating rather than converting in place, because a type change discards values that do not fit the new type. Setting a property to `null` removes it; never do that without confirmation.

Note that the API cannot change view-level filters or sorts. Those are UI-only. If the user asks for that, say so instead of changing the underlying schema as a substitute.

## Property formats

```
Title        {"title": [{"text": {"content": "..."}}]}
Rich text    {"rich_text": [{"text": {"content": "..."}}]}
Select       {"select": {"name": "Option"}}
Multi-select {"multi_select": [{"name": "A"}, {"name": "B"}]}
Status       {"status": {"name": "In progress"}}
Date         {"date": {"start": "2026-08-05", "end": null}}
People       {"people": [{"id": "USER_ID"}]}
Relation     {"relation": [{"id": "PAGE_ID"}]}
Checkbox     {"checkbox": true}
Number       {"number": 42}
URL          {"url": "https://..."}
Email        {"email": "a@b.com"}
Phone        {"phone_number": "+1..."}
```

`formula`, `rollup`, `created_time`, and `last_edited_by` are computed by Notion and cannot be written. Attempting to set them fails validation.

## Pagination

List and query endpoints return at most 100 items and truncate silently from the caller's point of view. Always check `has_more` and follow `next_cursor`:

```bash
notion POST /data_sources/{id}/query -d '{"page_size": 100, "start_cursor": "CURSOR"}'
```

Never summarize or count a database from a single unpaginated response. If you stop early because the result set is large, tell the user the numbers are partial.

## Rate limits and errors

Average limit is roughly 3 requests per second with short bursts allowed. On `429`, wait for the `Retry-After` header value before retrying, and back off exponentially after repeated hits. Batch block appends into one request rather than looping one block per call.

| Status | Code | What it usually means |
|---|---|---|
| 400 | `validation_error` | Wrong property name, unknown select option, or a computed property you tried to write |
| 401 | `unauthorized` | Missing or bad token, or the wrong profile is active |
| 403 | `restricted_resource` | The integration lacks the capability, for example insert-content is off |
| 404 | `object_not_found` | Not shared with the integration, or `database_id` used where `data_source_id` was needed |
| 409 | `conflict_error` | Concurrent edit; re-fetch and retry |
| 429 | `rate_limited` | Slow down, honour `Retry-After` |

A `404` here rarely means the object does not exist. Check sharing and the ID type before telling the user something is missing.

## Security

- Keep the token in the environment or the profile key files. Never print it, log it, echo it into a page, or commit it.
- Use a dedicated integration shared only with the pages needed for the task. A token can reach everything shared with it.
- IDs are opaque UUIDs. Store them explicitly; do not parse them out of Notion URLs, because the URL slug is not a reliable ID source.
