"""One downstream-only online audit with an offline-validated original response."""
from datetime import datetime
import json
from pathlib import Path
import sys

from skillflow.document_guided.runner import prepare_from_revalidated_graph, run
from tools.doe.document_guided_client import Client
from tools.doe.document_guided_metrics import transport_metrics


def read(file):
    return json.loads(file.read_bytes())


def main():
    root = Path(__file__).resolve().parent
    prior = read(root / "dispatch.json")
    parent = Path(prior["run"])
    now = datetime.now().astimezone()
    child = parent.parent / ("document-guided-google-search-downstream-high-" + now.strftime("%Y%m%d-%H%M%S"))
    allowed = {"processing", "task-correspondence", "sensitivity", "review",
               "revision-processing", "revision-task-correspondence", "revision-sensitivity", "revision/review"}
    if (root / "downstream-dispatch.json").exists():
        raise ValueError("The downstream audit has already been dispatched")
    prepare_from_revalidated_graph(parent, run_dir=child, config=prior["config"])
    verified = read(root / "recompiled-online-cfg.json")
    assert read(child / "graph/initial.json") == {"cfg": verified}
    with (root / "downstream-dispatch.json").open("x", encoding="utf-8") as file:
        json.dump({"time": now.isoformat(), "run": str(child), "parent": str(parent),
            "original_graph": str(parent / "steps/graph/calls/a001/response.json"),
            "allowed_online_stages": sorted(allowed), "config": prior["config"],
            "timeout": prior["timeout"], "network_retries": prior["network_retries"]}, file, indent=2)
    def client(name, owner):
        if name not in allowed:
            raise ValueError(f"{name} is outside the downstream dispatch")
        return Client(child / "transport" / name, owner=owner, executable=Path(prior["executable"]),
                      timeout=prior["timeout"], retries=prior["network_retries"], config=prior["config"])
    print(child, flush=True)
    with (root / "downstream.log").open("w", encoding="utf-8", buffering=1) as log:
        result = run(child, client_factory=client, progress=lambda r: print(
            r["stage"], r["stages"].get(r["stage"]), file=log, flush=True))
    (child / "metrics.json").write_text(json.dumps(transport_metrics(child), ensure_ascii=False, indent=2) + "\n",
                                       encoding="utf-8")
    print(result["status"], result["stage"], result.get("reason"), flush=True)
    return 0 if result["status"] in ("partial", "complete", "diagnostic_complete") else 1


if __name__ == "__main__":
    sys.exit(main())
