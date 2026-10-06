"""Architectural constraints are checked independently of business schemas."""
import ast
import importlib.util
from pathlib import Path
import subprocess
import sys

from skillflow.common.paths import project_root


def imports(path):
    for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
        if isinstance(node, ast.ImportFrom) and node.module:
            yield node.module
        elif isinstance(node, ast.Import):
            yield from (alias.name for alias in node.names)


def test_stage_dependencies_point_only_downward():
    root = project_root() / 'src/skillflow'
    for path in root.rglob('*.py'):
        relative = path.relative_to(root)
        dependencies = set(imports(path))
        assert not any(name.startswith(('skill_ir', 'tools.', 'experiments.')) for name in dependencies), path
        if relative.parts[0] == 'common':
            assert not any(name.startswith(('skillflow.graph', 'skillflow.propagation', 'skillflow.doe')) for name in dependencies), path
        if relative.parts[0] == 'graph':
            assert not any(name.startswith(('skillflow.propagation', 'skillflow.doe')) for name in dependencies), path
        if relative.parts[:2] == ('propagation', 'data'):
            assert not any(name.startswith(('skillflow.common.llm', 'skillflow.propagation.annotation', 'skillflow.propagation.runner')) for name in dependencies), path
        if relative.parts[0] == 'propagation' and relative.name in {'solver.py', 'interpreter.py', 'records.py'}:
            assert not any(name.startswith(('skillflow.propagation.annotation', 'skillflow.propagation.review', 'skillflow.graph.audit')) for name in dependencies), path


def test_no_source_depth_or_tool_path_injection():
    for path in (project_root() / 'src/skillflow').rglob('*.py'):
        source = path.read_text(encoding='utf-8')
        assert 'sys.path.insert' not in source, path
        assert 'spec_from_file_location' not in source, path
        assert '.parents[' not in source, path


def test_old_namespace_has_been_removed():
    assert importlib.util.find_spec('skill_ir') is None


def test_installed_entry_and_solver_outside_checkout(tmp_path):
    script = '''
import sys
import skillflow
from skillflow.propagation.solver import propagate
from skillflow.propagation.data import DataRegistry
from skillflow.graph.extraction.pipeline import analyze_skill
assert not any(name.startswith(("skillflow.propagation.annotation", "skillflow.propagation.review", "skillflow.graph.audit")) for name in sys.modules)
'''
    result = subprocess.run([sys.executable, '-I', '-c', script], cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    result = subprocess.run([sys.executable, '-I', '-m', 'skillflow', '--help'], cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert 'analyze' in result.stdout and 'render' in result.stdout
