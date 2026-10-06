"""Build the explicitly requested ZIP from supplied output paths."""
import argparse
from pathlib import Path
from zipfile import ZipFile

parser = argparse.ArgumentParser()
parser.add_argument("--paths", nargs="+", required=True)
parser.add_argument("--output", required=True)
args = parser.parse_args()
with ZipFile(args.output, "w") as archive:
    for filename in args.paths:
        path = Path(filename)
        archive.write(path, arcname=path.name)
