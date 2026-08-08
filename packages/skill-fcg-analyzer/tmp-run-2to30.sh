#!/usr/bin/env bash
# Temp batch runner: FCG (with LLM) over skills 00002..00030, serial.
# 00001 is being finished separately by an already-running node process (it's the
# heaviest skill, moved to run "first" only because it was already in flight).
# src/index.js main() does NOT auto-load .env, so we export it here.
set -u

PKG=d:/projects/SkillFlow/packages/skill-fcg-analyzer
ZIPS=d:/projects/SkillFlow/results/clawhub-top-k10000/zips
OUT=d:/projects/SkillFlow/results/clawhub-top-k10000/fcg/skills
LOGDIR=d:/projects/SkillFlow/results/clawhub-top-k10000/fcg/run-logs
PROGRESS="$LOGDIR/progress-2to30.txt"

mkdir -p "$OUT" "$LOGDIR"
: > "$PROGRESS"

set -a
. d:/projects/SkillFlow/.env
set +a
export FCG_DISABLE_LLM=0

cd "$PKG" || exit 1

# Skills 00002..00030 in numeric order (excludes 00001, run separately).
mapfile -t FILES < <(ls "$ZIPS"/000[0-2][0-9]_*.zip "$ZIPS"/00030_*.zip 2>/dev/null | sort | grep -v '/00001_' | head -29)

echo "Found ${#FILES[@]} skill zips to run (00002..00030)" | tee -a "$PROGRESS"

i=0
for f in "${FILES[@]}"; do
  i=$((i+1))
  base=$(basename "$f" .zip)          # e.g. 00009_weather_1.0.0
  idx=${base%%_*}                      # 00009
  outjson="$OUT/skill_${idx}-${base}-fcg.json"
  log="$LOGDIR/${base}.log"
  start=$(date +%s)
  echo "[$i/29] START $base" | tee -a "$PROGRESS"
  node src/index.js analyze "$f" \
    --output "$outjson" \
    --mode full --label-llm-assist > "$log" 2>&1
  rc=$?
  end=$(date +%s)
  dur=$((end-start))
  if [ $rc -eq 0 ] && [ -f "$outjson" ]; then
    echo "[$i/29] OK    $base  (${dur}s)" | tee -a "$PROGRESS"
  else
    echo "[$i/29] FAIL  $base  rc=$rc (${dur}s) -- see $log" | tee -a "$PROGRESS"
  fi
done

echo "DONE (2..30). See $PROGRESS and per-skill logs in $LOGDIR" | tee -a "$PROGRESS"
