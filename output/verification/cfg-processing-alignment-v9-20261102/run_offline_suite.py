"""Focused offline suites; injected clients only, no real target execution."""
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
kind = sys.argv[1]
if kind == "guided":
    files = ["tests/document_guided"]
elif kind == "backend":
    needles = ("demand", "sensitivity", "endpoint", "sink", "case", "map_collection", "loop", "member", "verified_material")
    files = [p.as_posix() for p in Path("tests/doe").glob("test_*.py")
             if any(word in p.name for word in needles) and "comparison" not in p.name]
    files += ["tests/propagation/data", "tests/propagation/test_explicit_loops.py",
              "tests/propagation/test_filtered_empty_guard.py", "tests/propagation/test_map_collection.py",
              "tests/propagation/test_collection_scopes.py", "tests/propagation/test_conditional_flow.py",
              "tests/propagation/test_source_boundaries.py"]
else:
    raise ValueError("Unknown offline suite")
command = [sys.executable, "-m", "pytest", *files, "-q", "--junitxml=" + str(BASE / (kind + "-integration.xml"))]
(BASE / (kind + "-integration-command.json")).write_text(json.dumps(command,indent=2)+"\n",encoding="utf-8")
with (BASE / (kind + "-integration.log")).open("xb") as output:
    result = subprocess.run(command, cwd=ROOT, stdout=output, stderr=subprocess.STDOUT)
print(json.dumps({"suite":kind,"returncode":result.returncode,"log":str(BASE / (kind + "-integration.log"))}))
raise SystemExit(result.returncode)
