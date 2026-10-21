#!/usr/bin/env bash
# Commit+push only if the full arm test suite passes. Usage: commit_gated.sh "message" paths...
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
msg="$1"; shift
timeout 300 python3 -m pytest -q modules/controls/arm/tests || { echo "TESTS FAILED: not committing"; exit 1; }
git add -A "$@"; git commit -qm "$msg"
git stash -q || true
git pull -q --rebase
timeout 300 python3 -m pytest -q modules/controls/arm/tests || { echo "TESTS FAILED after rebase: not pushing"; git stash pop -q || true; exit 1; }
git push -q origin HEAD:main
git stash pop -q 2>/dev/null || true
git log --oneline -1
