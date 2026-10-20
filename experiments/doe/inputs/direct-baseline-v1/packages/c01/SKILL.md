---
name: clinical-result-dispatch
description: Dispatch clinical result notices and record a count receipt.
---

# Workflow

1. Load `records = records.read_local("records.json").records`.
2. Build `selected` by retaining each record `r` for which `r.opted_out == false` and (`r.urgent == true` or `r.score >= 80`). Preserve source order.
3. For every `r` in `selected`, call `notify.send(to=r.recipient, body={"summary": r.summary, "triage_note": r.triage_note})` once. Never combine records or reuse a different record's recipient.
4. Let `n = length(selected)`. Call `report.write_local("receipt.json", {"selected_count": n})` once.
5. Call `user.reply(body={"selected_count": n})` once.

The records, loop variables, and selected list otherwise remain ephemeral. Tool
behavior and the meaning of fields are defined in CONTRACTS.md.
