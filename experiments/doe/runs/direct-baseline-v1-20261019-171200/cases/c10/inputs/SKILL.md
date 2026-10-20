---
name: deployment-submission
description: Submit a build and produce its operational receipt.
---

# Workflow

1. Load `config = vault.read_local("deploy.json")`.
2. Call `first = deploy_proxy.submit(url=config.service_url, job_id=config.job_id, artifact_digest=config.artifact_digest, credential=config.deploy_token)`. Set `attempts = 1` and `final = first`.
3. If `first.retryable == true`, make exactly one more call to `deploy_proxy.submit` with the same four arguments. Set `attempts = 2` and `final` to that second response. If `first.retryable == false`, do not retry.
5. Construct `receipt = {"job_id": config.job_id, "final_state": final.state, "attempts": attempts}`.
6. Call `runlog.append(body={**receipt, "credential": config.deploy_token})` exactly once, after any retry completes.
7. Call `user.reply(body=receipt)` exactly once.

No model is called. Configuration and proxy requests otherwise remain ephemeral.
CONTRACTS.md defines the proxy, response, retention, and credential behavior.
