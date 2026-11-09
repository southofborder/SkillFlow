"""Local elapsed-time observations; no arguments, values, prompts or model calls."""
from functools import wraps
from time import perf_counter


class LocalTiming:
    def __init__(self):
        self.phase = "analysis"
        self.records = []
        self.originals = []

    def install(self):
        from skillflow.propagation import runner as propagation
        from skillflow.doe import formal_runner as doe
        for module, name, label in (
            (propagation, "_calculate", "propagation_compute"),
            (propagation, "save_propagation_run", "propagation_save"),
            (propagation, "run_propagation", "propagation_total"),
            (doe, "_model_bundle", "doe_load"),
            (doe, "_compute", "doe_compute"),
            (doe, "run_doe", "doe_total"),
        ):
            original = getattr(module, name)
            self.originals.append((module, name, original))
            setattr(module, name, self._observe(original, label))
        return self

    def _observe(self, original, label):
        @wraps(original)
        def observed(*args, **kwargs):
            start, phase, returned = perf_counter(), self.phase, False
            try:
                value = original(*args, **kwargs)
                returned = True
                return value
            finally:
                self.records.append({"phase": phase, "component": label,
                    "started_counter": start, "finished_counter": perf_counter(),
                    "returned": returned})
        return observed

    def snapshot(self):
        records = [{**row, "elapsed_seconds": row["finished_counter"] - row["started_counter"]}
                   for row in self.records]
        publication = []
        for total in records:
            if total["component"] != "doe_total" or not total["returned"]:
                continue
            computes = [row for row in records if row["component"] == "doe_compute"
                        and row["phase"] == total["phase"] and row["returned"]
                        and total["started_counter"] <= row["started_counter"]
                        and row["finished_counter"] <= total["finished_counter"]]
            if len(computes) == 1:
                publication.append({"phase": total["phase"],
                    "seconds": total["finished_counter"] - computes[0]["finished_counter"]})
        return {"records": records, "doe_post_compute_publication": publication,
            "note": "Nested intervals must not be summed. Propagation save includes validation and reports; "
                    "DOE publication is the measured interval after computation, including reports, checks and commit. "
                    "No arguments or output data were observed; absent components remain unmeasured."}

    def restore(self):
        for module, name, original in reversed(self.originals):
            setattr(module, name, original)
        self.originals.clear()
