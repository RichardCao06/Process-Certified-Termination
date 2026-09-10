#!/bin/sh
# PCT-P2-001 / D21-A01. The key is entered invisibly or read from a private file.
set -eu
cd "$(dirname "$0")/.."
exec python3 scripts/run_p2_d21_local.py \
  --dsh-source .pct-local/deepseek-harness \
  --node .pct-local/runtime/node_modules/node/bin/node \
  --output-dir .pct-local/results/d21 "$@"
