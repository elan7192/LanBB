#!/usr/bin/python3
"""Passive in-scope subdomain recon for LanBB CASE.

Optional CLI: subfaster (https://github.com/melvinsh/subfaster, homepage crt.name).
Not vendored. Not run on out-of-scope domains. Local labs skip public CT lookup.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import List, Optional

from scope import (
    ScopeError,
    ProgramScope,
    is_loopback,
    load_scope,
    public_in_scope_domains,
    require_in_scope,
    require_scope_file,
)


class ReconError(ScopeError):
    """Recon refused or failed closed."""


def subfaster_bin() -> Optional[str]:
    return shutil.which("subfaster")


def should_skip_public_lookup(scope: ProgramScope) -> bool:
    if scope.is_lab:
        return not public_in_scope_domains(scope)
    return not public_in_scope_domains(scope)


def recon_output_dir(scope: ProgramScope) -> Path:
    dest = scope.path.parent / "recon" / "subdomains"
    dest.mkdir(parents=True, exist_ok=True)
    return dest


def run_passive_recon(
    slug: str,
    domain: Optional[str] = None,
    root: Optional[Path] = None,
    run_subfaster: bool = False,
) -> dict:
    """Fail-closed recon. Never runs against OOS or missing scope."""
    scope = require_scope_file(slug, root)
    if domain:
        require_in_scope(slug, domain, root)
        targets = [domain]
        if is_loopback(domain):
            run_subfaster = False
    else:
        public = public_in_scope_domains(scope)
        if not public:
            dest = recon_output_dir(scope)
            note = dest / "skipped.txt"
            note.write_text(
                "Local/lab in-scope only (loopback or .local). "
                "Skipped optional subfaster/crt.name public lookup.\n",
                encoding="utf-8",
            )
            return {
                "ok": True,
                "skipped": True,
                "reason": "lab-or-loopback-only",
                "program": scope.slug,
                "wrote": str(note),
            }
        targets = public

    for target in targets:
        require_in_scope(slug, target, root)

    dest = recon_output_dir(scope)
    summary: List[str] = []
    ran = False
    binary = subfaster_bin() if run_subfaster else None
    if run_subfaster and not binary:
        summary.append(
            "subfaster not installed; documented only "
            "(https://github.com/melvinsh/subfaster, homepage https://crt.name). "
            "Install: go install -v github.com/melvinsh/subfaster/v2/cmd/subfaster@latest"
        )
    elif binary:
        for target in targets:
            out_file = dest / f"{target.replace(':', '_')}.txt"
            cmd = [binary, "-d", target, "-o", str(out_file)]
            try:
                subprocess.run(cmd, check=True, capture_output=True, text=True)
                ran = True
                summary.append(f"subfaster wrote {out_file}")
            except (OSError, subprocess.CalledProcessError) as exc:
                raise ReconError(f"subfaster failed for in-scope {target}: {exc}") from exc
    else:
        listed = dest / "in-scope.txt"
        listed.write_text("\n".join(targets) + "\n", encoding="utf-8")
        summary.append(
            "Listed in-scope hosts only. Optional subfaster not invoked "
            "(pass --run-subfaster when the binary is installed)."
        )
        ran = False

    return {
        "ok": True,
        "skipped": False,
        "ran_subfaster": ran,
        "program": scope.slug,
        "targets": targets,
        "notes": summary,
        "dir": str(dest),
    }
