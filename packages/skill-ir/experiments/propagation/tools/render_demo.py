"""Reproduce the authored example through the shared propagation save path."""
from __future__ import annotations
import argparse
import importlib.util
from pathlib import Path
import sys

HERE = Path(__file__).resolve()
PACKAGE = HERE.parents[3]
REPOSITORY = PACKAGE.parents[1]
sys.path.insert(0, str(PACKAGE / 'src'))
EXAMPLE = PACKAGE / 'examples/propagation_demo.py'
DEFAULT_OUTPUT = PACKAGE / 'experiments/propagation/runs/offline-demo-v3'


def generate(output: Path = DEFAULT_OUTPUT):
    output = Path(output).resolve()
    if any(output == root or output.is_relative_to(root) for root in
           (REPOSITORY / 'dataset', REPOSITORY / 'result', PACKAGE / 'src', PACKAGE / 'examples')):
        raise ValueError('demo outputs cannot overlap protected inputs or source code')
    loader = importlib.util.spec_from_file_location('skillflow_offline_propagation_demo', EXAMPLE)
    module = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(module)
    return module.save_demo(output)


def main(argv=None):
    parser = argparse.ArgumentParser(description='用统一传播保存入口生成手工规格示例，不调用模型')
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    result = generate(args.output)
    print(f"{result['status']}: {args.output.resolve() / 'report.html'}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
