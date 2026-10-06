"""Acceptance checks using the installed package, outside the repository."""

import json
from pathlib import Path
import subprocess
import sys

from skillflow.graph.extraction.prompt import _EXAMPLES


def test_installed_module_analyzes_and_renders_outside_repository(tmp_path):
    skill = tmp_path / "input"
    skill.mkdir()
    (skill / "notes.txt").write_text("Return the normalized input", encoding="utf-8")
    candidate = tmp_path / "candidate.json"
    candidate.write_text(json.dumps(_EXAMPLES[0][1]), encoding="utf-8")
    analysis = tmp_path / "analysis.json"
    diagram = tmp_path / "graph.mmd"
    commands = [
        [
            "analyze",
            "--input",
            str(skill),
            "--candidate",
            str(candidate),
            "--output",
            str(analysis),
        ],
        ["render", "--input", str(analysis), "--output", str(diagram)],
    ]
    for command in commands:
        run = subprocess.run(
            [sys.executable, "-I", "-m", "skillflow", *command],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )
        assert run.returncode == 0, run.stdout + run.stderr
    assert json.loads(analysis.read_text())["attempts"] == 0
    assert diagram.read_text(encoding="utf-8").startswith("flowchart TD")


def test_installed_experiment_and_render_without_optional_analysis(tmp_path):
    source = tmp_path / "case"
    source.mkdir()
    (source / "notes.txt").write_text("Return ok")
    (tmp_path / "dataset.json").write_text(
        json.dumps({"cases": [{"id": "case", "input": "case"}]})
    )
    (tmp_path / "experiment.json").write_text(
        json.dumps(
            {
                "name": "check",
                "dataset": "dataset.json",
                "variants": [{"id": "configured"}],
            }
        )
    )
    (tmp_path / "settings.env").write_text(
        "LLM_API_KEY=test-only-secret\nLLM_MODEL=test-model\nLLM_REASONING_EFFORT=max\n"
    )
    script = r"""
import importlib.abc
import json
import sys
import urllib.request
from pathlib import Path
class NoAnalysis(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == 'skillflow.graph.analysis' or fullname.startswith('skillflow.graph.analysis.'):
            raise AssertionError('Optional analysis imported')
sys.meta_path.insert(0, NoAnalysis())
from skillflow.cli import main
from skillflow.graph.extraction.prompt import _EXAMPLES
class Response:
    status = 200
    headers = {}
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self):
        return json.dumps({'choices': [{'message': {'content': json.dumps(_EXAMPLES[0][1])}}]}).encode()
urllib.request.urlopen = lambda *a, **kw: Response()
assert main(['--env-file', 'settings.env', 'experiment', '--config', 'experiment.json', '--output-dir', 'out']) == 0
analysis = next(Path('out').rglob('analysis.json'))
assert main(['render', '--input', str(analysis), '--output', 'rendered.mmd']) == 0
assert Path('rendered.mmd').is_file()
"""
    run = subprocess.run(
        [sys.executable, "-I", "-c", script],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert run.returncode == 0, run.stdout + run.stderr


def test_only_unified_console_entry_is_registered():
    from importlib.metadata import distribution

    entries = {
        entry.name
        for entry in distribution("skillflow").entry_points
        if entry.group == "console_scripts"
    }
    assert entries == {"skillflow"}
