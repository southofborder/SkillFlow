---
name: gmail
description: Read, search, draft, reply to, and organize Gmail from chat via the Gmail API. Use this skill when users want an inbox copilot — search and fetch messages, read by thread, list labels, create and send drafts, reply to threads, forward messages, manage labels, archive or trash messages, and retrieve attachment content.
---

# Gmail

![Gmail](https://raw.githubusercontent.com/ClawLink-HQ/clawlink/main/public/images/brand-logos/gmail.svg)

Access Gmail via the Gmail API with OAuth authentication. Read, search, draft, reply to, and organize Gmail from chat.

This skill uses [ClawLink](https://claw-link.dev/?utm_source=clawhub&utm_medium=referral&utm_content=gmail-email) for hosted connection flows and credentials so you do not need to configure Gmail API access yourself.

### Setup in 3 Steps

| Step 1: Install | Step 2: Pair Account | Step 3: Connect Gmail |
|:---:|:---:|:---:|
| ![Install](https://raw.githubusercontent.com/ClawLink-HQ/clawlink/main/public/images/pairing/initialstep_1.gif) | ![Pair](https://raw.githubusercontent.com/ClawLink-HQ/clawlink/main/public/images/approve_process.gif) | *App-specific connection GIF coming soon* |
| Run the install command in OpenClaw | Sign in and approve the device | Open the dashboard and connect Gmail |

## How It Works

```
┌─────────────────┐     ┌──────────────┐     ┌──────────────────┐
│   OpenClaw      │────▶│   ClawLink   │────▶│   Gmail API      │
│   (User Chat)   │     │   (OAuth)    │     │   (REST)         │
└─────────────────┘     └──────────────┘     └──────────────────┘
         │                       │                       │
         │  1. Install Plugin    │                       │
         │  2. Pair Device       │                       │
         │  3. Connect Gmail     │                       │
         │                       │  4. Secure Token      │
         │                       │  5. Proxy Requests    │
         │                       │                       │
         ▼                       ▼                       ▼
   ┌──────────┐           ┌──────────┐           ┌──────────┐
   │  SKILL   │           │ Dashboard│           │ Gmail    │
   │  File    │           │ Auth     │           │ Inbox    │
   └──────────┘           └──────────┘           └──────────┘
```

## Install

Install the verified ClawLink plugin from ClawHub. After the user confirms, complete the full setup so ClawLink tools are visible in the next OpenClaw chat.

```bash
openclaw plugins install clawhub:clawlink-plugin
openclaw config set tools.alsoAllow '["clawlink-plugin"]' --strict-json
openclaw gateway restart
```

Then tell the user: "OpenClaw has been restarted. Send `/new` as a standalone message to start a fresh chat, then ask for Gmail again."

## Quick Start

```bash
# Get Gmail profile (confirms connection and shows email)
clawlink_call_tool --tool "gmail_get_profile" --params '{}'

# List recent emails
clawlink_call_tool --tool "gmail_fetch_emails" --params '{"max_results": 10}'

# Search emails
clawlink_call_tool --tool "gmail_fetch_emails" --params '{"query": "from:boss@example.com subject:report"}'
```

## Authentication

All Gmail tool calls are authenticated automatically by ClawLink using the user's connected Google account.

**No API key is required in chat.** ClawLink stores the OAuth token securely and injects it into every Gmail API request on the user's behalf.

### Getting Connected

1. Install the ClawLink plugin (see Install above).
2. Pair the plugin with `clawlink_begin_pairing` if it is not configured yet.
3. Open https://claw-link.dev/dashboard?add=gmail and connect Gmail.
4. Call `clawlink_list_integrations` to verify the connection is active.

## Connection Management

### List Connections

```bash
clawlink_list_integrations
```

**Response:** Returns all connected integrations. Look for `gmail` in the list.

### Verify Connection

```bash
clawlink_list_tools --integration gmail
```

**Response:** Returns the live tool catalog for Gmail.

### Reconnect

If Gmail tools are missing or the connection shows an error:

1. Direct the user to https://claw-link.dev/dashboard?add=gmail
2. After they confirm, call `clawlink_list_integrations` to verify
3. Then call `clawlink_list_tools --integration gmail`

## Security & Permissions

- The connection is an OAuth grant approved on Google's own consent screen. It covers full mailbox access (Google's `https://www.googleapis.com/auth/mail.google.com` scope), which is what read, search, draft, send, forward, and label operations require. The user can revoke it at any time at https://myaccount.google.com/permissions.
- No password or app password is stored anywhere. Nothing durable lives on the user's machine.
- Nothing runs on a timer. Gmail is touched only when the user asks.
- **All write operations require explicit user confirmation.** Before executing any send, reply, forward, draft, label change, archive, or delete call, confirm the intended action with the user.
- Destructive actions (permanent delete, trash) are marked as high-impact and must be confirmed.
- Always confirm recipients, subject, and body before sending email.

## Tool Reference

### Email Retrieval

| Tool | Description | Mode |
|------|-------------|------|
| `gmail_fetch_emails` | Search and fetch emails with filtering and pagination | Read |
| `gmail_fetch_message_by_message_id` | Get a specific email by message ID | Read |
| `gmail_fetch_message_by_thread_id` | Get all messages in a thread | Read |
| `gmail_get_attachment` | Download an email attachment | Read |

### Sending & Drafts

| Tool | Description | Mode |
|------|-------------|------|
| `gmail_send_email` | Send an email immediately | Write |
| `gmail_reply_to_thread` | Reply to an existing email thread | Write |
| `gmail_forward_message` | Forward an email to specified recipients | Write |
| `gmail_create_email_draft` | Create a draft email | Write |
| `gmail_update_draft` | Update an existing draft | Write |
| `gmail_send_draft` | Send an existing draft | Write |

### Labels

| Tool | Description | Mode |
|------|-------------|------|
| `gmail_list_labels` | List all labels (system and custom) | Read |
| `gmail_get_label` | Get details for a specific label | Read |
| `gmail_create_label` | Create a new custom label | Write |
| `gmail_update_label` | Update label name or color | Write |
| `gmail_delete_label` | Delete a custom label | Write |
| `gmail_add_label_to_email` | Add or remove labels from a message | Write |

### Thread & Message Management

| Tool | Description | Mode |
|------|-------------|------|
| `gmail_list_threads` | List email threads | Read |
| `gmail_modify_thread_labels` | Add or remove labels from a thread | Write |
| `gmail_move_thread_to_trash` | Move a thread to trash | Write |
| `gmail_move_to_trash` | Move a single message to trash | Write |
| `gmail_untrash_message` | Restore a message from trash | Write |
| `gmail_untrash_thread` | Restore a thread from trash | Write |

### Bulk Operations

| Tool | Description | Mode |
|------|-------------|------|
| `gmail_batch_modify_messages` | Modify labels on up to 1,000 messages | Write |
| `gmail_batch_delete_messages` | Permanently delete multiple messages | Write |

### Settings & Profile

| Tool | Description | Mode |
|------|-------------|------|
| `gmail_get_profile` | Get Gmail profile (email, message/thread counts) | Read |
| `gmail_list_send_as` | List send-as aliases | Read |
| `gmail_list_drafts` | List all drafts | Read |

### Filters

| Tool | Description | Mode |
|------|-------------|------|
| `gmail_list_filters` | List all email filters | Read |
| `gmail_create_filter` | Create a new filter rule | Write |

### Contacts

| Tool | Description | Mode |
|------|-------------|------|
| `gmail_get_contacts` | List contacts | Read |
| `gmail_search_people` | Search contacts by name, email, phone | Read |

## Code Examples

### Search emails from a specific sender

```bash
clawlink_call_tool --tool "gmail_fetch_emails" \
  --params '{
    "query": "from:boss@example.com",
    "max_results": 20
  }'
```

### Send a new email

```bash
clawlink_call_tool --tool "gmail_send_email" \
  --params '{
    "to": ["recipient@example.com"],
    "subject": "Weekly Report",
    "body": "Please find the weekly report attached.",
    "is_html": false
  }'
```

### Reply to a thread

```bash
clawlink_call_tool --tool "gmail_reply_to_thread" \
  --params '{
    "thread_id": "thread-id-here",
    "body": "Thank you for the update. I will review and get back to you shortly.",
    "incoming": false
  }'
```

### Create a draft

```bash
clawlink_call_tool --tool "gmail_create_email_draft" \
  --params '{
    "to": ["team@example.com"],
    "subject": "Meeting Notes",
    "body": "Here are the notes from todays meeting...",
    "is_html": false
  }'
```

### Add label to email

```bash
clawlink_call_tool --tool "gmail_add_label_to_email" \
  --params '{
    "message_id": "message-id-here",
    "label_ids": ["Label_123"]
  }'
```

## Discovery Workflow

1. Call `clawlink_list_integrations` to confirm Gmail is connected.
2. Call `clawlink_list_tools --integration gmail` to see the live catalog.
3. Treat the returned list as the source of truth. Do not guess or assume what tools exist.
4. If the user describes a capability but the exact tool is unclear, call `clawlink_search_tools` with a short query and integration `gmail`.
5. If no Gmail tools appear, direct the user to https://claw-link.dev/dashboard?add=gmail.

## Execution Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  READ OPERATIONS (Safe)                                     │
│  search → fetch → get → list → call                         │
│                                                             │
│  Example: Search emails → Fetch thread → Show messages      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  WRITE OPERATIONS (Require Confirmation)                    │
│  describe → preview → confirm → send/draft/label/trash      │
│                                                             │
│  Example: Preview email → User confirms → Execute send      │
└─────────────────────────────────────────────────────────────┘
```

1. For unfamiliar tools, ambiguous requests, or any write action, call `clawlink_describe_tool` first.
2. Use the returned guidance, schema, `whenToUse`, `askBefore`, `safeDefaults`, `examples`, and `followups` to shape the call.
3. Prefer read, list, search, and get operations before writes.
4. For sends, replies, forwards, drafts, label changes, archive/delete, call `clawlink_preview_tool` first, then confirm with the user.
5. Execute with `clawlink_call_tool`. Pass confirmation only after the preview matches the user's intent.
6. If the tool call fails, report the real error. Do not invent results or restate the failure as a missing capability unless the live catalog supports that conclusion.

## Notes

- System labels (INBOX, SENT, SPAM, TRASH) are read-only and cannot be created or deleted.
- Custom label IDs (e.g., `Label_123`) are required for label operations — display names cannot be used.
- The `thread_id` is required for replies. Leave subject empty when replying to stay in the same thread.
- Message size limit is ~25 MB including attachments. Larger attachments may fail.
- **`gmail_fetch_emails` defaults `max_results` to 1.** A request like "check my unread email" returns a single message unless you set it explicitly. Always pass a real number when the user asks for more than one.
- Gmail search query syntax for the `query` argument, same as the Gmail search box: `from:`, `to:`, `subject:`, `label:`, `is:unread`, `has:attachment`, `in:inbox`, `newer_than:7d`, `older_than:1m`, `after:`, `before:`. Combine them freely (`from:stripe.com has:attachment newer_than:30d`).
- Spam and trash are excluded unless `include_spam_trash` is set. If a message the user insists exists cannot be found, check there before reporting it missing.
- `label_ids` filters on label IDs, not display names. Built-ins are uppercase (`INBOX`, `UNREAD`, `STARRED`, `SPAM`, `TRASH`); call `gmail_list_labels` first for custom ones.

## Error Handling

| Status / Error | Meaning |
|----------------|---------|
| Tool not found | The tool name does not exist in the current catalog. Verify with `clawlink_list_tools --integration gmail`. |
| Missing connection | Gmail is not connected. Direct the user to https://claw-link.dev/dashboard?add=gmail. |
| `404 Not Found` | Message or thread ID does not exist or is not accessible. |
| `403 Forbidden` | Most often a placeholder or example ID rather than a scope problem: an ID copied from documentation instead of one returned by a live search. Run a list or search call first, then retry with a real `message_id`, `thread_id`, or label ID. Otherwise it is Gmail API quota, or the connected account lacking access to the mailbox in the request. |
| Worked before, now failing on every call | The OAuth token was invalidated. Google does this when the user changes their Google account password (refresh tokens carrying Gmail scopes are revoked), when they revoke the app's access, or after six months of non-use. Direct the user to reconnect at https://claw-link.dev/dashboard?add=gmail. |
| `429 Rate Limit` | Too many requests. Apply exponential backoff. |
| Write rejected | User did not confirm a write action. Always confirm before executing sends, replies, forwards, drafts, label changes, archive, or delete. |

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

1. Ensure the integration slug is exactly `gmail`.
2. Use `clawlink_describe_tool` to verify parameter names and types before calling.
3. For send, reply, forward, draft, label, archive, and delete operations, always call `clawlink_preview_tool` first.

## Resources

- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Gmail API Reference](https://developers.google.com/gmail/api/reference/rest)
- [Gmail Query Syntax](https://support.google.com/mail/answer/7190)
- [ClawLink](https://claw-link.dev/?utm_source=clawhub&utm_medium=referral&utm_content=gmail-email)
- [ClawLink Docs](https://docs.claw-link.dev/openclaw)
- [ClawLink Verification](https://claw-link.dev/verify)

---

**Powered by [ClawLink](https://claw-link.dev/?utm_source=clawhub&utm_medium=referral&utm_content=gmail-email)** — an integration hub for OpenClaw

![ClawLink Logo](https://raw.githubusercontent.com/ClawLink-HQ/clawlink/main/public/images/logo/link_logo_black_small.png)