#!/usr/bin/env bash
# TEMP: phase-timing measurement. Splits the "silent gap" into label-assist /
# flood / postproc / serialize, on clean machine. Sequential for clean wall-clock.
set -u
PKG=d:/projects/SkillFlow/packages/skill-fcg-analyzer
ZIPS=d:/projects/SkillFlow/results/clawhub-top-k10000/zips
TMP=d:/projects/SkillFlow/results/clawhub-top-k10000/fcg/_phasetiming
mkdir -p "$TMP"

set -a
. d:/projects/SkillFlow/.env
set +a
export FCG_DISABLE_LLM=0
export FCG_PHASE_TIMING=1

cd "$PKG" || exit 1

# Fresh label cache each run so label-assist actually executes (worst-case measure).
for spec in "00005_ontology_1.0.4" "00008_skillscan_1.1.6"; do
  z="$ZIPS/${spec}.zip"
  [ -f "$z" ] || { echo "MISSING $z"; continue; }
  echo "======== PHASE-TIMING $spec ========"
  rm -f "$TMP/${spec}.labelcache.jsonl"
  node src/index.js analyze "$z" \
    --output "$TMP/${spec}-fcg.json" \
    --mode full --label-llm-assist \
    --label-llm-cache "$TMP/${spec}.labelcache.jsonl" \
    2> "$TMP/${spec}.phase.txt"
  echo "---- phase lines for $spec ----"
  grep '\[phase\]' "$TMP/${spec}.phase.txt"
  echo ""
done
echo "PHASE-TIMING DONE"
