# LanBB

LanBB is the product.

**Flow Studio** is the local CASE workflow page. Open path: `flows/studio/index.html`. Serve with `python3 flows/serve.py`. See `flows/README.md`. Local only.

**semantica** is a tool/engine under LanBB. Do not rename the GitHub repository or the Python package.

- Canonical engine remote: https://github.com/semantica-agi/semantica
- Nesting: git submodule at `tools/semantica`

## How to run a case (CyberGym 10-task subset)

Lab only. Local PoC server.

```bash
python3 tools/case/lanbb.py case new cybergym
python3 tools/case/lanbb.py scope parse cybergym
python3 tools/case/lanbb.py recon cybergym
python3 tools/case/lanbb.py case score cybergym
python3 tools/case/lanbb.py case report cybergym
```

Score is what the CyberGym PoC server accepts. Quote the server fail text if it rejects. See `labs/cybergym/README.md`.

Tests:

```bash
python3 tools/case/tests/test_scope.py
python3 tools/case/tests/test_case.py
python3 flows/test_api.py
python3 flows/test_case_gates.py
```
