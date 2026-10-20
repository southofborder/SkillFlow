---
name: licensed-entitlement-check
description: Verify a signed entitlement and return its local evaluator token.
---

# Workflow

1. Load `claim = entitlement.read_local("claim.json")`.
2. Call `verdict = verifier.accept(url=claim.verifier_url, body={"signed_claim": claim.signed_claim})` once.
3. If `verdict.accepted == true`, call `evaluation = opaque.evaluate(signed_claim=claim.signed_claim)` locally, then call `user.reply(body=evaluation.token)` once. Otherwise stop without calling the evaluator or replying.

Keep the original string unchanged for both consumers. No model is called.
CONTRACTS.md defines verification, evaluator outputs, and receiver boundaries.
