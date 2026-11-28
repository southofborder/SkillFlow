# Semia transport diagnosis and recovery

The original Semia run reached 100 terminal case records. Its CLI returned 119 visible answers and 280 explicit workspace-discovery errors. Another two native processes reached the controller deadline with no terminal turn. The recovery cohort contains the 94 cases whose final error was `Semia CLI request failed`. Ninety-two had no visible answer and two had returned candidates by the time transport stopped. Six other cases retain their original outcomes. [Original runtime diagnostics](../audit-01/runtime-diagnostics.json)

| Original failure evidence | Count |
| --- | ---: |
| Workspace routing discovery failed | 264 |
| Workspace routing discovery timed out | 16 |
| Native 2,700-second deadline without a terminal turn | 2 |

The two deadline calls used prompts of 306,415 and 292,710 characters. Their logs record 26 and 28 reconnect notices, including 22 and 24 notices waiting for the network. Both record Windows DNS error 11001 and connection reset 10054. Neither records a WebSocket-to-HTTPS fallback. The local prompt hashes and complete-source fences were verified. Successful calls delivered prompts larger than those of the deadline calls. [First deadline receipt](../../runs/semia/semia-audit-01/cases/clawhub-0449/requests/call-002/request.json) · [Second deadline receipt](../../runs/semia/semia-audit-01/cases/clawhub-0790/requests/call-004/request.json)

Windows event logs recorded repeated network-profile disconnects and reconnects during the failure period. OpenAI also reported an overlapping incident for ChatGPT conversations, ChatGPT Work and Codex Cloud. The account-specific workspace route and the respective contributions of the local network and the service remain unverified. [OpenAI incident](https://status.openai.com/incidents/01M898HVZGXFV2XC4775CG9GF8)

The installed CLI supports disabling `unbounded_connection_retries`. In the public Codex implementation, the waiting-for-network branch can keep retrying before the ordinary finite retry and HTTPS fallback path. The recovery disables that feature for its own native CLI invocations and records a terminal connection failure before pausing further case admission. It uses the first authorized affected case to witness authenticated sampling. The model settings, caller deadline, Semia synthesis and validation, and full prepared source are pinned to the original run. [Codex retry implementation](https://github.com/openai/codex/blob/main/codex-rs/core/src/responses_retry.rs) · [OpenAI network requirements](https://help.openai.com/en/articles/9247338-network-recommendations-for-chatgpt-errors-on-web-and-apps)

The current redacted CLI doctor report passed provider HTTP and Responses WebSocket checks with no inference request. These are connectivity checks. The recovery's case receipts establish authenticated inference and keep any new failures visible. [Network health receipt](cli-network-doctor.json)
