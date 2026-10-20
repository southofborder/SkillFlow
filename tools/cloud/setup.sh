#!/usr/bin/env bash
# Dependency downloads are allowed here; no model or experiment is started.
set -euo pipefail

root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
while [[ ! -f "$root/pyproject.toml" ]]; do
    parent="$(dirname -- "$root")"
    if [[ "$parent" == "$root" ]]; then
        printf '%s\n' "Cannot find the SkillFlow project marker." >&2
        exit 1
    fi
    root="$parent"
done
if ! grep -Eq '^name[[:space:]]*=[[:space:]]*"skillflow"[[:space:]]*$' "$root/pyproject.toml"; then
    printf '%s\n' "The project marker does not identify SkillFlow." >&2
    exit 1
fi

python="${SKILLFLOW_PYTHON:-python3}"
"$python" -m pip install --disable-pip-version-check -e "$root" pytest
"$python" "$root/tools/cloud/preflight.py" --project "$root"
"$python" "$root/tools/cloud/materials.py" --project "$root" verify
