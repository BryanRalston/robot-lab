#!/bin/bash
# Job 2R driver. Mesh-check level 3, drop Ball radius to 3 mm if over 300k tets, then solve 1..3.
set -u
cd "$(dirname "$0")"
source "$HOME/fea-job2/bin/activate"
export OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 MKL_NUM_THREADS=8 NUMEXPR_NUM_THREADS=8
export PYTHONUNBUFFERED=1

run_series() {
  local tag="$1"
  export TAG="$tag" BALL_T=4 BALL_R=4
  unset STEP
  echo "MESH_CHECK $tag level 3 ball r=$BALL_R"
  MESH_ONLY=1 LEVEL=3 python fea_job2r.py
  local rc=$?
  if [ "$rc" -eq 2 ]; then
    export BALL_R=3
    echo "NEED_BALL_R=3 $tag"
    MESH_ONLY=1 LEVEL=3 python fea_job2r.py || return 1
  elif [ "$rc" -ne 0 ]; then
    echo "MESH_CHECK_FAIL $tag rc=$rc"
    return "$rc"
  fi
  local tets
  tets=$(python -c "import json;print(json.load(open('meshcheck_${tag}.json'))['tets'])")
  echo "TETS_CHECK $tag $tets ball $BALL_R"
  if [ "$tets" -gt 300000 ]; then
    echo "STILL_OVER_CAP $tag $tets"
    return 1
  fi
  local lv
  for lv in 1 2 3; do
    echo "START_LEVEL $tag $lv ball $BALL_R"
    LEVEL=$lv python fea_job2r.py || return 1
    python make_report.py || echo "REPORT_FAIL $tag $lv"
    echo "END_LEVEL $tag $lv"
  done
}

run_series a || echo "SERIES_FAIL a"
run_series b || echo "SERIES_FAIL b"
python make_report.py || echo "REPORT_FAIL"
echo ALL_CASES_DONE
