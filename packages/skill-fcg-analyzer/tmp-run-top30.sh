#!/usr/bin/env bash
# Temp batch runner: FCG (with LLM) over the first 30 skills, serial.
# src/index.js main() does NOT auto-load .env, so we export it here.
# Serial on purpose: 00001/00004 are heavyweight (10k-20k+ label flows).
set -u

PKG=d:/projects/SkillFlow/packages/skill-fcg-analyzer
ZIPS=d:/projects/SkillFlow/results/clawhub-top-k10000/zips
OUT=d:/projects/SkillFlow/results/clawhub-top-k10000/fcg/skills
LOGDIR=d:/projects/SkillFlow/results/clawhub-top-k10000/fcg/run-logs
PROGRESS="$LOGDIR/progress.txt"

mkdir -p "$OUT" "$LOGDIR"
: > "$PROGRESS"

set -a
. d:/projects/SkillFlow/.env
set +a
export FCG_DISABLE_LLM=0

cd "$PKG" || exit 1

# First 30 zips in numeric order (00001..00030).
mapfile -t FILES < <(ls "$ZIPS"/000[0-2][0-9]_*.zip "$ZIPS"/00030_*.zip 2>/dev/null | sort | head -30)

echo "Found ${#FILES[@]} skill zips to run" | tee -a "$PROGRESS"

i=0
for f in "${FILES[@]}"; do
  i=$((i+1))
  base=$(basename "$f" .zip)          # e.g. 00009_weather_1.0.0
  idx=${base%%_*}                      # 00009
  outjson="$OUT/skill_${idx}-${base}-fcg.json"
  log="$LOGDIR/${base}.log"
  start=$(date +%s)
  echo "[$i/30] START $base" | tee -a "$PROGRESS"
  node src/index.js analyze "$f" \
    --output "$outjson" \
    --mode full --label-llm-assist > "$log" 2>&1
  rc=$?
  end=$(date +%s)
  dur=$((end-start))
  if [ $rc -eq 0 ] && [ -f "$outjson" ]; then
    echo "[$i/30] OK    $base  (${dur}s)" | tee -a "$PROGRESS"
  else
    echo "[$i/30] FAIL  $base  rc=$rc (${dur}s) -- see $log" | tee -a "$PROGRESS"
  fi
done

echo "DONE. See $PROGRESS and per-skill logs in $LOGDIR" | tee -a "$PROGRESS"
