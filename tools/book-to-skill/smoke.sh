#!/usr/bin/env bash
# Repeatable smoke: convert fixtures (markdown + PDF) → bundles → SkillSpector scan.
# Does not touch wiki, second-brain, or semantica. SkillSpector is not vendored.
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
TOOL="$ROOT/tools/book-to-skill"
FAKE_GEN="$TOOL/tests/fake_generator.py"
STUB_SPEC="$TOOL/tests/fixtures/stub-skill.md"
OUT="$TOOL/.cache/smoke"
SKILLSPECTOR_VENV="$TOOL/.cache/skillspector-venv"

export BOOK_TO_SKILL_SPEC="$STUB_SPEC"
# Smoke uses the test double so bundles are complete without an agent CLI.
export BOOK_TO_SKILL_GENERATOR="/usr/bin/python3 $FAKE_GEN"

ensure_venv() {
  local venv_dir=$1
  if [[ -x "$venv_dir/bin/python" ]]; then
    return 0
  fi
  echo "==> creating venv: $venv_dir" >&2
  if python3 -m venv "$venv_dir" 2>/dev/null; then
    return 0
  fi
  if ! command -v virtualenv >/dev/null 2>&1; then
    python3 -m pip install --user virtualenv >&2
    export PATH="$HOME/.local/bin:$PATH"
  fi
  virtualenv "$venv_dir"
}

ensure_skillspector() {
  if command -v skillspector >/dev/null 2>&1; then
    echo "$(command -v skillspector)"
    return
  fi
  if [[ -x "$SKILLSPECTOR_VENV/bin/skillspector" ]]; then
    echo "$SKILLSPECTOR_VENV/bin/skillspector"
    return
  fi
  echo "==> installing SkillSpector to $SKILLSPECTOR_VENV (one-time, not vendored)" >&2
  ensure_venv "$SKILLSPECTOR_VENV"
  "$SKILLSPECTOR_VENV/bin/pip" install -q pip
  "$SKILLSPECTOR_VENV/bin/pip" install -q 'git+https://github.com/NVIDIA/skillspector.git'
  echo "$SKILLSPECTOR_VENV/bin/skillspector"
}

assert_bundle() {
  local bundle=$1
  test -f "$bundle/SKILL.md"
  test -d "$bundle/chapters"
  test -f "$bundle/glossary.md"
  test -f "$bundle/patterns.md"
  test -f "$bundle/cheatsheet.md"
}

run_convert() {
  local input=$1
  local slug=$2
  local extra_args=("${@:3}")
  local bundle="$OUT/skills/$slug"

  echo "==> convert: $input" >&2
  python3 "$TOOL/convert.py" \
    --require-bundle \
    --keep-workdir \
    --output "$OUT/skills" \
    --name "$slug" \
    "${extra_args[@]}" \
    "$input" >&2

  assert_bundle "$bundle"
  echo "convert: OK → $bundle" >&2
  printf '%s' "$bundle"
}

run_scan() {
  local bundle=$1
  echo "==> scan: $bundle" >&2
  "$TOOL/scan-skill.sh" "$bundle" >&2
  echo "scan: OK → $bundle" >&2
}

rm -rf "$OUT"
mkdir -p "$OUT/skills"

# --- markdown fixture (text document path) ---
MD_FIXTURE="$TOOL/tests/fixtures/widget-protocol.md"
run_convert "$MD_FIXTURE" widget-protocol >/dev/null

# --- PDF fixture (advertised book.pdf path) ---
PDF_FIXTURE="$TOOL/tests/fixtures/widget-protocol.pdf"
if [[ ! -f "$PDF_FIXTURE" ]]; then
  python3 "$TOOL/tests/fixtures/generate-pdf-fixture.py"
fi
PDF_BUNDLE=$(run_convert "$PDF_FIXTURE" widget-protocol-pdf --mode text)

skillspector_bin=$(ensure_skillspector)
export PATH="$(dirname "$skillspector_bin"):$PATH"

run_scan "$OUT/skills/widget-protocol"
run_scan "$PDF_BUNDLE"

echo "smoke: all passed (markdown + PDF)"
