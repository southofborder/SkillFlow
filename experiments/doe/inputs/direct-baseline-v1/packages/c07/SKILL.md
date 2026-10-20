---
name: support-issue-drafter
description: Prepare one short issue note with the external drafting model.
---

# Workflow

1. Load `original_v1 = support.read_local("ticket.json")`. This is the unchanged full ticket.
2. Compute `redacted_v2 = mask_fields(original_v1)` locally. Keep both objects in ephemeral memory; `original_v1` still has its original fields.
3. Call `draft_v3 = draft_model.compose(ticket=redacted_v2, style="one sentence; preserve any quoted error_text verbatim")`.
4. After that model call returns, set the local working variable `working_ticket = redacted_v2`. This assignment does not modify `original_v1` or the request already sent in step 3.
5. Compute `final_v4 = clean_draft(text=draft_v3, original=original_v1)` locally.
6. Call `user.reply(body=final_v4)` once.

CONTRACTS.md defines exact masking, model visibility, object identity, cleanup,
and durable memory behavior. No other output or save operation occurs.
