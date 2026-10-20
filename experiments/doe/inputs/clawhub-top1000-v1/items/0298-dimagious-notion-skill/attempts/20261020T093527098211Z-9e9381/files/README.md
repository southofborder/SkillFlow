# Notion Skill

Safe access to Notion pages, databases, and blocks via the official Notion API, pinned to API version `2025-09-03`.

Where most Notion skills document endpoints, this one documents guardrails: schema diffs before structural changes, append-first writes, and profile separation between personal and work workspaces.

## Quick Start

1. Create a Notion integration at <https://www.notion.so/my-integrations>
2. Copy the Internal Integration Token (starts with `ntn_`)
3. Export it: `export NOTION_API_KEY=ntn_xxx`
4. Share the target pages and databases with the integration in the Notion UI, otherwise they are invisible to the API

## Features

- Search, read, and create pages
- Append blocks to pages, with append-first as the default write mode
- Query databases (data sources) with filters, sorts, and correct pagination
- Create and update database rows
- Schema inspection with a mandatory diff-and-confirm flow before any structural change
- Personal / work profile switching via `NOTION_PROFILE`
- Error table covering the failure modes agents actually hit, including the `database_id` vs `data_source_id` trap

## Requirements

- `NOTION_API_KEY` environment variable, or a key file at `~/.config/notion/<profile>.key`
- `curl` and `jq`

No CLI to install.

## API version

Pinned to `2025-09-03`. In this version databases are addressed as **data sources** and carry two IDs: use `database_id` to create pages inside a database, and `data_source_id` to query it or read its schema.

## Version

2.0.0

Breaking change from 1.0.0: all operations are now plain `curl` calls against the Notion API. The previous version documented a `notion-cli` binary that was never distributed, so the commands could not run as written. Nothing that worked before stops working.
