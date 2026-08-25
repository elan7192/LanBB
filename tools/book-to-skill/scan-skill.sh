#!/usr/bin/env bash
# Run NVIDIA SkillSpector static scan on a generated skill bundle.
# SkillSpector is NOT vendored — install separately. See README.md.
set -euo pipefail

if ! command -v skillspector >/dev/null 2>&1; then
  cat >&2 <<'EOF'
skillspector: command not found

Install NVIDIA SkillSpector (Apache-2.0, not bundled with LanBB):
  uv tool install git+https://github.com/NVIDIA/skillspector.git

Or from source:
  git clone https://github.com/NVIDIA/SkillSpector.git
  cd SkillSpector && make install

Docs: https://github.com/NVIDIA/SkillSpector
      https://docs.nvidia.com/skills/scanning-agent-skills
EOF
  exit 127
fi

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <skill-dir> [extra skillspector scan args...]" >&2
  echo "Example: $0 ./skills/my-slug/" >&2
  exit 2
fi

target=$1
shift
exec skillspector scan "$target" --no-llm "$@"
