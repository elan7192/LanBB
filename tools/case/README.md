# LanBB authorized CASE

White-hat **find + report** for an in-scope program folder. Lab-first (OWASP Juice Shop). Fail-closed without `programs/<slug>/scope.md`.

This is not an exploits tree. Optional passive CLI is [subfaster](https://github.com/melvinsh/subfaster) ([crt.name](https://crt.name)) — documented, not vendored.

## Skills

| Path | Role |
| --- | --- |
| `parse-scope/SKILL.md` | Parse in-scope / OOS. Missing file refuses the target. |
| `passive-recon/SKILL.md` | Passive names for in-scope apexes only. Local lab skips subfaster. |
| `write-report/SKILL.md` | Disclosure draft from the case file. No PoC generator. |

## Copied catalogue skills (tiny subset)

Under `tools/case/skills/<name>/SKILL.md`. Apache-2.0. Payloads stripped. See `NOTICE` and `skills/LICENSE`.

Do not add the 818-skill repo as a submodule. Do not copy exploiting-* / C2 / phishing / nuclei dumps.


## CLI

```bash
python3 tools/case/lanbb.py case new juice-shop
python3 tools/case/lanbb.py scope parse juice-shop
python3 tools/case/lanbb.py recon juice-shop
python3 tools/case/lanbb.py case report juice-shop
python3 tools/case/lanbb.py case score juice-shop
# same commands via ./lanbb from repo root
```

`case new juice-shop` creates:

```
programs/juice-shop/
  scope.md
  recon/subdomains/
  findings/
  reports/
  notes.md
```

## Lab wall

Stock Juice Shop is `labs/juice-shop/overlays/v0-stock/`. Hardening loops add `v1-hardened`, `v2-hardened`, `v3-hardened`, `v4-hardened`, `v5-hardened`, `v6-hardened`, `v7-hardened`, … Current wall is `labs/juice-shop/versions.json` (`wall`). `hunted` is the overlay the last loop scored. Never live programs. Never porn programs.

## Tests

```bash
python3 tools/case/tests/test_scope.py
python3 tools/case/tests/test_case.py
python3 flows/test_api.py
python3 flows/test_case_gates.py
```
