"""Convert one UTF-8 text document and print the output path."""
from pathlib import Path
import sys

source = Path(sys.argv[1])
output_dir = Path(sys.argv[2])
output_dir.mkdir(parents=True, exist_ok=True)
output = output_dir / (source.stem + ".txt")
output.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
print(output)
