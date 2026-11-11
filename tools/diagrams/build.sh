#!/bin/bash
# Regenerate workshop diagrams from their generator scripts.
#   build.sh [name ...]          write the draft, check the layout, export SVG + PNG (2x) into docs/images
#   build.sh --check [name ...]  only regenerate into a temp dir and report whether each matches the committed draft
# With no names, every diagram is processed. Names: see the table below or README.md.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../.." && pwd)
SKILL=${SKILL_DIR:-$HOME/.claude/skills/skill-aws-arch-diagram}/scripts

# name | generator | draft path (relative to docs/images)
TABLE="architecture|architecture.py|architecture.draft.svg
concept-snat-dnat|concept_snat_dnat.py|diagrams/concept-snat-dnat.draft.svg
concept-snat-dnat-steps|concept_snat_dnat.py|diagrams/concept-snat-dnat-steps.draft.svg
lab1-dx-build|lab1_dx_build.py|diagrams/lab1-dx-build.draft.svg
lab2-overlap-problem|lab2_overlap.py|diagrams/lab2-overlap-problem.draft.svg
lab2-packet-walk|lab2_packet_walk.py|diagrams/lab2-packet-walk.draft.svg
extra-a|extra_a.py|diagrams/extra-a-vpcb-and-original-route.draft.svg
extra-b|extra_b.py|diagrams/extra-b-nat-system-routes.draft.svg
extra-c|extra_c.py|diagrams/extra-c-observability.draft.svg
router-config-map|router_config_map.py|diagrams/router-config-map.draft.svg"

CHECK=0
if [[ ${1:-} == --check ]]; then CHECK=1; shift; fi
WANT=" $* "

gen() {  # gen <script> <out> [name]
  case ${3:-}:$1 in
    concept-snat-dnat-steps:*) python3 "$HERE/$1" "$2" --steps ;;
    *:lab2_packet_walk.py) python3 "$HERE/$1" 20 17 "$2" ;;
    *:router_config_map.py) python3 "$HERE/$1" > "$2" ;;
    *) python3 "$HERE/$1" "$2" ;;
  esac
}

TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
rc=0
while IFS='|' read -r name script draft; do
  [[ $# -gt 0 && $WANT != *" $name "* ]] && continue
  dest="$ROOT/docs/images/$draft"
  if (( CHECK )); then
    gen "$script" "$TMP/$name.svg" "$name" >/dev/null 2>&1
    if cmp -s "$TMP/$name.svg" "$dest"; then echo "same     $name"; else echo "differs  $name"; rc=1; fi
    continue
  fi
  echo "== $name"
  gen "$script" "$dest" "$name"
  python3 "$SKILL/check_layout.py" "$dest" || echo "!! check_layout reported the problems above (route-table cells are known false positives)"
  w=$(grep -o 'viewBox="0 0 [0-9.]*' "$dest" | awk '{print $3}')
  w=$(python3 -c "print(round(float('$w') * 2))")
  uv run -q --with python-pptx --with cairosvg python "$SKILL/export.py" "$dest" --svg --png \
    --png-width "$w" --out-dir "$(dirname "$dest")" >/dev/null
  echo "exported $(dirname "$draft")/$(basename "$draft" .draft.svg).{svg,png}"
done <<< "$TABLE"
exit $rc
