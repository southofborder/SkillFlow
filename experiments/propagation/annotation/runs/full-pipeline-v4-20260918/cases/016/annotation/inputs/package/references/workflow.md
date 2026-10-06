# Fetch workflow

Read source_id from the user's request and read FAST_KEY from the environment.

If FAST_KEY is present, try fast.fetch first with source_id and FAST_KEY; if it is absent, go directly to archive.fetch without calling fast.fetch.

- Preferred-tool failure handling:
  - Retry fast.fetch exactly once only when its first attempt fails with a transient error; do not retry a non-transient first failure.
  - After a non-transient first failure or any failed retry of fast.fetch, call archive.fetch with source_id.

The same retry policy is specified by [retry configuration](../retry.yaml); apply it to fast.fetch only.

Call archive.fetch at most once and pass source_id as its only argument.

On either tool's success, return that successful response's body value unchanged and make no further fetch calls.

If archive.fetch fails, stop and return its error; do not retry archive.fetch.

> Never pass FAST_KEY to archive.fetch or diagnostic output anywhere in this workflow.

Before returning from every success or failure path, append the final status to local status.txt.
