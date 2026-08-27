#!/usr/bin/env bash
# Walk through resolving-merge-conflicts/SKILL.md on a fixture merge conflict.
# Never calls git merge --abort or git rebase --abort.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIXTURE="$ROOT/fixtures/merge-conflict"
WORK="${TMPDIR:-/tmp}/lanbb-merge-conflict-dry-run-$$"

cleanup() {
  rm -rf "$WORK"
}
trap cleanup EXIT

log() {
  printf '==> %s\n' "$*"
}

setup_conflict_repo() {
  mkdir -p "$WORK"
  git -C "$WORK" init -q
  git -C "$WORK" config user.email "dry-run@lanbb.local"
  git -C "$WORK" config user.name "LanBB dry-run"

  cp "$FIXTURE/base/greeting.txt" "$WORK/greeting.txt"
  git -C "$WORK" add greeting.txt
  git -C "$WORK" commit -q -m "base: initial greeting"

  git -C "$WORK" branch -q main
  git -C "$WORK" checkout -q -b feature

  cp "$FIXTURE/feature/greeting.txt" "$WORK/greeting.txt"
  git -C "$WORK" add greeting.txt
  git -C "$WORK" commit -q -m "feature: rename greeting for branch work"

  git -C "$WORK" checkout -q main
  cp "$FIXTURE/main/greeting.txt" "$WORK/greeting.txt"
  git -C "$WORK" add greeting.txt
  git -C "$WORK" commit -q -m "main: rename greeting for trunk"

  if git -C "$WORK" merge --no-commit feature; then
    echo "fixture error: expected a merge conflict but merge succeeded" >&2
    exit 1
  fi
}

step1_see_state() {
  log "Step 1 — see current state"
  git -C "$WORK" status --short --branch
  git -C "$WORK" log --oneline --graph --left-right HEAD...MERGE_HEAD
  if ! git -C "$WORK" diff --name-only --diff-filter=U | grep -qx greeting.txt; then
    echo "fixture error: greeting.txt is not unmerged" >&2
    exit 1
  fi
}

step2_primary_sources() {
  log "Step 2 — primary sources (commit messages on each side)"
  git -C "$WORK" log -1 --format='main:   %s' main
  git -C "$WORK" log -1 --format='feature: %s' feature
}

step3_resolve_hunks() {
  log "Step 3 — resolve hunks (preserve both intents)"
  if ! grep -q '^<<<<<<< ' "$WORK/greeting.txt"; then
    echo "fixture error: conflict markers missing before resolution" >&2
    exit 1
  fi
  cp "$FIXTURE/expected/greeting.txt" "$WORK/greeting.txt"
}

step4_run_checks() {
  log "Step 4 — automated checks"
  git -C "$WORK" diff --check
  if grep -qE '^(<<<<<<<|=======|>>>>>>>)' "$WORK/greeting.txt"; then
    echo "fixture error: conflict markers remain after resolution" >&2
    exit 1
  fi
  diff -u "$FIXTURE/expected/greeting.txt" "$WORK/greeting.txt"
}

step5_finish_merge() {
  log "Step 5 — finish merge"
  git -C "$WORK" add greeting.txt
  git -C "$WORK" commit -q --no-edit
  if git -C "$WORK" status --porcelain | grep -q .; then
    echo "fixture error: working tree not clean after merge commit" >&2
    exit 1
  fi
  log "done — merge completed without --abort"
}

main() {
  setup_conflict_repo
  step1_see_state
  step2_primary_sources
  step3_resolve_hunks
  step4_run_checks
  step5_finish_merge
}

main "$@"
