#!/usr/bin/env bash
# Repeatable smoke: convert fixture → skill bundle → SkillSpector static scan.
# Does not touch wiki, second-brain, or semantica. SkillSpector is not vendored.
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
TOOL="$ROOT/tools/book-to-skill"
FIXTURE="$TOOL/tests/fixtures/widget-protocol.md"
FAKE_GEN="$TOOL/tests/fake_generator.py"
STUB_SPEC="$TOOL/tests/fixtures/stub-skill.md"
OUT="$TOOL/.cache/smoke"
BUNDLE="$OUT/skills/widget-protocol"
SKILLSPECTOR_VENV="$TOOL/.cache/skillspector-venv"

export BOOK_TO_SKILL_SPEC="$STUB_SPEC"
# Smoke uses the test double so the bundle is complete without an agent CLI.
export BOOK_TO_SKILL_GENERATOR="/usr/bin/python3 $FAKE_GEN"

echo "==> convert: $FIXTURE"
rm -rf "$OUT"
mkdir -p "$OUT"

python3 "$TOOL/convert.py" \
  --require-bundle \
  --keep-workdir \
  --output "$OUT/skills" \
  --name widget-protocol \
  "$FIXTURE"

test -f "$BUNDLE/SKILL.md"
test -d "$BUNDLE/chapters"
test -f "$BUNDLE/glossary.md"
test -f "$BUNDLE/patterns.md"
test -f "$BUNDLE/cheatsheet.md"
echo "convert: OK → $BUNDLE"

skillspector_bin=""
if command -v skillspector >/dev/null 2>&1; then
  skillspector_bin=$(command -v skillspector)
elif [[ -x "$SKILLSPECTOR_VENV/bin/skillspector" ]]; then
  skillspector_bin="$SKILLSPECTOR_VENV/bin/skillspector"
else
  echo "==> installing SkillSpector to $SKILLSPECTOR_VENV (one-time, not vendored)"
  python3 -m venv "$SKILLSPECTOR_VENV"
  "$SKILLSPECTOR_VENV/bin/pip" install -q pip
  "$SKILLSPECTOR_VENV/bin/pip" install -q 'git+https://github.com/NVIDIA/skillspector.git'
  skillspector_bin="$SKILLSPECTOR_VENV/bin/skillspector"
fi

export PATH="$(dirname "$skillspector_bin"):$PATH"
echo "==> scan: $BUNDLE"
"$TOOL/scan-skill.sh" "$BUNDLE"
echo "scan: OK"
echo "smoke: all passed"
