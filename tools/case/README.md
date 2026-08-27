# LanBB authorized CASE

White-hat find + report for an in-scope program folder. Current lab is the CyberGym 10-task subset. Fail-closed without `programs/<slug>/scope.md`.

Optional passive CLI is [subfaster](https://github.com/melvinsh/subfaster) ([crt.name](https://crt.name)). Documented. Not vendored.

## Skills

| Path | Role |
| --- | --- |
| `parse-scope/SKILL.md` | Parse in-scope / OOS. Missing file refuses the target. |
| `passive-recon/SKILL.md` | Passive names for in-scope apexes only. Local lab skips subfaster. |
| `write-report/SKILL.md` | Disclosure draft from the case file. No PoC generator. |

## Copied catalogue skills

Under `tools/case/skills/<name>/SKILL.md`. Apache-2.0. Payloads stripped. See `NOTICE` and `skills/LICENSE`.

Do not add the 818-skill repo as a submodule. Do not copy exploiting-* / C2 / phishing / nuclei dumps.

## CLI

```bash
python3 tools/case/lanbb.py case new cybergym
python3 tools/case/lanbb.py scope parse cybergym
python3 tools/case/lanbb.py recon cybergym
python3 tools/case/lanbb.py case report cybergym
python3 tools/case/lanbb.py case score cybergym
```

`case new cybergym` creates `programs/cybergym/` with `scope.md`.

Current hunt is the CyberGym 10-task subset. See `labs/cybergym/`.

## Tests

```bash
python3 tools/case/tests/test_scope.py
python3 tools/case/tests/test_case.py
python3 flows/test_api.py
python3 flows/test_case_gates.py
```
