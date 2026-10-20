---
name: google-calendar
description: Check Google Calendar calendars, find free time, schedule meetings, and update events via the Google Calendar API. Use this skill when users want help scheduling or updating meetings — list calendars, show event details for a day or range, find free time slots, search for events, create events from structured details, adjust or delete existing events after confirmation, and check current date/time for timezone-aware scheduling.
---

# Google Calendar

![Google Calendar](https://raw.githubusercontent.com/ClawLink-HQ/clawlink/main/public/images/brand-logos/google-calendar.svg)

Access Google Calendar via the Google Calendar API with OAuth authentication. Check calendars, find free time, schedule meetings, and update events.

This skill uses [ClawLink](https://claw-link.dev/?utm_source=clawhub&utm_medium=referral&utm_content=google-calendar-scheduling) for hosted connection flows and credentials so you do not need to configure Google Calendar API access yourself.

### Setup in 3 Steps

| Step 1: Install | Step 2: Pair Account | Step 3: Connect Google Calendar |
|:---:|:---:|:---:|
| ![Install](https://raw.githubusercontent.com/ClawLink-HQ/clawlink/main/public/images/pairing/initialstep_1.gif) | ![Pair](https://raw.githubusercontent.com/ClawLink-HQ/clawlink/main/public/images/approve_process.gif) | *App-specific connection GIF coming soon* |
| Run the install command in OpenClaw | Sign in and approve the device | Open the dashboard and connect Google Calendar |

## How It Works

```
┌─────────────────┐     ┌──────────────┐     ┌──────────────────┐
│   OpenClaw      │────▶│   ClawLink   │────▶│ Google Calendar  │
│   (User Chat)   │     │   (OAuth)    │     │   API (REST)     │
└─────────────────┘     └──────────────┘     └──────────────────┘
         │                       │                       │
         │  1. Install Plugin    │                       │
         │  2. Pair Device       │                       │
         │  3. Connect Google Calendar                    │
         │                       │  4. Secure Token      │
         │                       │  5. Proxy Requests    │
         │                       │                       │
         ▼                       ▼                       ▼
   ┌──────────┐           ┌──────────┐           ┌──────────┐
   │  SKILL   │           │ Dashboard│           │ Calendar │
   │  File    │           │ Auth     │           │ Events   │
   └──────────┘           └──────────┘           └──────────┘
```

## Install

Install the verified ClawLink plugin from ClawHub. After the user confirms, complete the full setup so ClawLink tools are visible in the next OpenClaw chat.

```bash
openclaw plugins install clawhub:clawlink-plugin
openclaw config set tools.alsoAllow '["clawlink-plugin"]' --strict-json
openclaw gateway restart
```

Then tell the user: "OpenClaw has been restarted. Send `/new` as a standalone message to start a fresh chat, then ask for Google Calendar again."

## Quick Start

```bash
# List calendars
clawlink_call_tool --tool "googlecalendar_list_calendars" --params '{}'

# Get current date/time for timezone-aware scheduling
clawlink_call_tool --tool "googlecalendar_get_current_date_time" --params '{"timezone": "America/New_York"}'

# List events for a specific day
clawlink_call_tool --tool "googlecalendar_events_list" --params '{"calendar_id": "primary", "time_min": "2025-01-15T00:00:00Z", "time_max": "2025-01-16T00:00:00Z"}'

# Find free time slots
clawlink_call_tool --tool "googlecalendar_find_free_slots" --params '{"time_min": "2025-01-15T09:00:00Z", "time_max": "2025-01-15T18:00:00Z", "calendar_ids": ["primary"], "meeting_duration_minutes": 60}'
```

## Authentication

All Google Calendar tool calls are authenticated automatically by ClawLink using the user's connected Google account.

**No API key is required in chat.** ClawLink stores the OAuth token securely and injects it into every Google Calendar API request on the user's behalf.

### Getting Connected

1. Install the ClawLink plugin (see Install above).
2. Pair the plugin with `clawlink_begin_pairing` if it is not configured yet.
3. Open https://claw-link.dev/dashboard?add=google-calendar and connect Google Calendar.
4. Call `clawlink_list_integrations` to verify the connection is active.

## Connection Management

### List Connections

```bash
clawlink_list_integrations
```

**Response:** Returns all connected integrations. Look for `google-calendar` in the list.

### Verify Connection

```bash
clawlink_list_tools --integration google-calendar
```

**Response:** Returns the live tool catalog for Google Calendar.

### Reconnect

If Google Calendar tools are missing or the connection shows an error:

1. Direct the user to https://claw-link.dev/dashboard?add=google-calendar
2. After they confirm, call `clawlink_list_integrations` to verify
3. Then call `clawlink_list_tools --integration google-calendar`

## Security & Permissions

- Access is scoped to calendars accessible to the connected Google account.
- **All write operations require explicit user confirmation.** Before executing any event create, update, move, or delete, confirm the intended effect with the user.
- Destructive actions (deleting events, clearing calendars) are marked as high-impact and must be confirmed.
- Moves and deletions of events with attendees affect other people's calendars — treat these as especially sensitive.

## Tool Reference

### Calendars

| Tool | Description | Mode |
|------|-------------|------|
| `googlecalendar_list_calendars` | List all calendars in the user's calendar list | Read |
| `googlecalendar_get_calendar` | Get a specific calendar's metadata | Read |
| `googlecalendar_duplicate_calendar` | Create a new empty calendar | Write |
| `googlecalendar_patch_calendar` | Update calendar title, description, timezone | Write |
| `googlecalendar_calendars_delete` | Delete a secondary calendar | Write |
| `googlecalendar_clear_calendar` | Delete all events from a calendar | Write |

### Events

| Tool | Description | Mode |
|------|-------------|------|
| `googlecalendar_events_list` | List events on a calendar with time filtering | Read |
| `googlecalendar_events_list_all_calendars` | List events across all calendars | Read |
| `googlecalendar_events_get` | Get a specific event by ID | Read |
| `googlecalendar_find_event` | Search events by text query and time range | Read |
| `googlecalendar_create_event` | Create a new calendar event | Write |
| `googlecalendar_update_event` | Full update of an existing event | Write |
| `googlecalendar_patch_event` | Partial update of event fields | Write |
| `googlecalendar_delete_event` | Delete an event by ID | Write |
| `googlecalendar_events_move` | Move an event to another calendar | Write |
| `googlecalendar_events_instances` | Get instances of a recurring event | Read |

### Scheduling

| Tool | Description | Mode |
|------|-------------|------|
| `googlecalendar_find_free_slots` | Find free/busy time slots across calendars | Read |
| `googlecalendar_get_current_date_time` | Get current date and time in a timezone | Read |
| `googlecalendar_quick_add` | Parse natural language to create a simple event | Write |

### Attendees

| Tool | Description | Mode |
|------|-------------|------|
| `googlecalendar_remove_attendee` | Remove an attendee from an event | Write |

### Availability

| Tool | Description | Mode |
|------|-------------|------|
| `googlecalendar_freebusy_query` | Get free/busy info for a list of calendars | Read |

### Access Control

| Tool | Description | Mode |
|------|-------------|------|
| `googlecalendar_acl_list` | List access control rules for a calendar | Read |
| `googlecalendar_acl_insert` | Create an ACL rule (share calendar) | Write |
| `googlecalendar_acl_delete` | Delete an ACL rule | Write |

## Code Examples

### List today's events

```bash
clawlink_call_tool --tool "googlecalendar_events_list" \
  --params '{
    "calendar_id": "primary",
    "time_min": "2025-01-15T00:00:00-05:00",
    "time_max": "2025-01-15T23:59:59-05:00",
    "single_events": true,
    "order_by": "startTime"
  }'
```

### Find free time for a meeting

```bash
clawlink_call_tool --tool "googlecalendar_find_free_slots" \
  --params '{
    "time_min": "2025-01-15T09:00:00-05:00",
    "time_max": "2025-01-15T17:00:00-05:00",
    "calendar_ids": ["primary"],
    "meeting_duration_minutes": 60
  }'
```

### Create a meeting event

```bash
clawlink_call_tool --tool "googlecalendar_create_event" \
  --params '{
    "calendar_id": "primary",
    "summary": "Team Sync",
    "description": "Weekly team synchronization meeting",
    "start_datetime": "2025-01-15T10:00:00",
    "event_duration_minutes": 60,
    "timezone": "America/New_York",
    "attendees": ["colleague@example.com"]
  }'
```

### Update an event

```bash
clawlink_call_tool --tool "googlecalendar_patch_event" \
  --params '{
    "calendar_id": "primary",
    "event_id": "abc123xyz",
    "summary": "Updated Team Sync",
    "start_datetime": "2025-01-15T11:00:00",
    "event_duration_minutes": 90
  }'
```

## Discovery Workflow

1. Call `clawlink_list_integrations` to confirm Google Calendar is connected.
2. Call `clawlink_list_tools --integration google-calendar` to see the live catalog.
3. Treat the returned list as the source of truth. Do not guess or assume what tools exist.
4. If the user describes a capability but the exact tool is unclear, call `clawlink_search_tools` with a short query and integration `google-calendar`.
5. If no Google Calendar tools appear, direct the user to https://claw-link.dev/dashboard?add=google-calendar.

## Execution Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  READ OPERATIONS (Safe)                                     │
│  list → get → find → search → describe → call               │
│                                                             │
│  Example: List calendars → Find free slots → Show options   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  WRITE OPERATIONS (Require Confirmation)                    │
│  list → get → describe → preview → confirm → call           │
│                                                             │
│  Example: Preview event creation → User confirms            │
│           → Execute create                                   │
└─────────────────────────────────────────────────────────────┘
```

1. For unfamiliar tools, ambiguous requests, or any write action, call `clawlink_describe_tool` first.
2. Use the returned guidance, schema, `whenToUse`, `askBefore`, `safeDefaults`, `examples`, and `followups` to shape the call.
3. Prefer read, list, search, and availability operations before writes.
4. For event changes or other high-impact actions, call `clawlink_preview_tool` first, then confirm with the user.
5. Execute with `clawlink_call_tool`. Pass confirmation only after the preview matches the user's intent.
6. If the tool call fails, report the real error. Do not invent results or restate the failure as a missing capability unless the live catalog supports that conclusion.

## Notes

- Timezone-aware scheduling: Always use IANA timezone identifiers (e.g., `America/New_York`, `Europe/London`) not abbreviations.
- UTC timestamps ending in `Z` are interpreted in UTC regardless of calendar timezone — use timezone-offset timestamps for local date queries.
- Primary calendar is referenced as `calendar_id: "primary"`.
- Events with attendees automatically send invitations via Google Calendar.
- Deleting or moving events with attendees affects their calendars too — always confirm.
- No conflict checking is performed before event creation — use `find_free_slots` to detect overlaps.

## Error Handling

| Status / Error | Meaning |
|----------------|---------|
| Tool not found | The tool name does not exist in the current catalog. Verify with `clawlink_list_tools --integration google-calendar`. |
| Missing connection | Google Calendar is not connected. Direct the user to https://claw-link.dev/dashboard?add=google-calendar. |
| `404 Not Found` | Calendar or event does not exist. Verify the calendar_id and event_id. |
| `403 Forbidden` | Insufficient permissions to access or modify the calendar. |
| `400 Bad Request` | Invalid datetime format or timezone. Use ISO 8601 with timezone offset. |
| Write rejected | User did not confirm a write action. Always confirm before executing event creates, updates, moves, or deletes. |

### Troubleshooting: Tools Not Visible

1. Check that the ClawLink plugin is installed:
   ```bash
   openclaw plugins list
   ```
2. If the plugin is installed but tools are missing, tell the user to send `/new` as a standalone message to reload the catalog.
3. If a fresh chat does not help, run:
   ```bash
   openclaw config set tools.alsoAllow '["clawlink-plugin"]' --strict-json
   openclaw gateway restart
   ```
4. After restart, tell the user to send `/new` again and retry.

### Troubleshooting: Invalid Tool Call

1. Ensure the integration slug is exactly `google-calendar`.
2. Use `clawlink_describe_tool` to verify parameter names and types before calling.
3. For write operations, always call `clawlink_preview_tool` first.

## Resources

- [Google Calendar API Overview](https://developers.google.com/workspace/calendar/api/guides/overview)
- [Google Calendar API Reference](https://developers.google.com/workspace/calendar/api/reference/rest)
- [Event Resource](https://developers.google.com/workspace/calendar/api/reference/rest/v3/events)
- [ClawLink](https://claw-link.dev/?utm_source=clawhub&utm_medium=referral&utm_content=google-calendar-scheduling)
- [ClawLink Docs](https://docs.claw-link.dev/openclaw)
- [ClawLink Verification](https://claw-link.dev/verify)

## Related Skills

- [Gmail](https://clawhub.ai/hith3sh/gmail-email) — For email management alongside scheduling
- [Google Meet](https://clawhub.ai/hith3sh/google-meet) — For video conferencing

---

**Powered by [ClawLink](https://claw-link.dev/?utm_source=clawhub&utm_medium=referral&utm_content=google-calendar-scheduling)** — an integration hub for OpenClaw

![ClawLink Logo](https://raw.githubusercontent.com/ClawLink-HQ/clawlink/main/public/images/logo/link_logo_black_small.png)