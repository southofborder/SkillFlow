---
name: source-fetch-with-fallback
description: Fetch one source using a credential-gated preferred tool and a bounded archive fallback.
---

# Source Fetch With Fallback

1. Read source_id from the user's request and read FAST_KEY from the environment.
2. If FAST_KEY is present, try fast.fetch first with source_id and FAST_KEY; if it is absent, go directly to archive.fetch without calling fast.fetch.
3. Retry fast.fetch exactly once only when its first attempt fails with a transient error; do not retry a non-transient first failure.
4. After a non-transient first failure or any failed retry of fast.fetch, call archive.fetch with source_id.
5. Call archive.fetch at most once and pass source_id as its only argument.
6. On either tool's success, return that successful response's summary value unchanged and make no further fetch calls.
7. If archive.fetch fails, stop and return its error; do not retry archive.fetch.
8. Never pass FAST_KEY to archive.fetch or diagnostic output anywhere in this workflow.
9. Before returning from every success or failure path, append the final status to local status.txt.
