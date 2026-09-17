#!/usr/bin/env bash
set -euo pipefail

BANNED=$(cat <<'EOF'
26ca4b520283748bc1ef5b287a459a0d383fc46f stale pre-0.36-release lineage (force-overwritten; rebase onto current develop)
EOF
)

history=$(git rev-list HEAD)
failed=0
while read -r sha reason; do
  [ -n "$sha" ] || continue
  if grep -qx "$sha" <<< "$history"; then
    echo "::error::Banned commit $sha is in this branch's history: $reason"
    failed=1
  fi
done <<< "$BANNED"

if [ "$failed" -ne 0 ]; then
  echo "This branch contains a banned commit. Rebase it onto the current develop and drop the stale lineage."
  exit 1
fi
echo "No banned commits found in history."
