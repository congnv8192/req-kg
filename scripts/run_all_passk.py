"""Chay pass@k cho ca 3 muc code L1/L2/L3 -> output/passk_results.json."""
import json
import shutil
from pathlib import Path
import importlib.util

spec = importlib.util.spec_from_file_location("rp", "scripts/run_passk.py")
rp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rp)

ROOT = Path(".").resolve()
ORACLE_TESTS = ROOT / ("data/RepoGenesis-Verified-GoldenOracle-v1/"
                       "expert_supervised/python/TaskManagement/tests")
results = {}
for lvl in ("L1", "L2", "L3"):
    src = ROOT / f"llm-answers/code_{lvl}.py"
    d = ROOT / f"output/code_{lvl}"
    d.mkdir(parents=True, exist_ok=True)
    shutil.copy(src, d / "main.py")
    print(f"\n########## {lvl} ##########")
    r = rp.run(d, ORACLE_TESTS, 8080)
    print(f"  health={r['health_ok']} pass={r['passed']}/{r['total']} "
          f"fail={r['failed']} err={r['errors']}")
    if r.get("note"):
        print(f"  note: {r['note'][:300]}")
    results[lvl] = {"passed": r["passed"], "total": r["total"],
                    "failed": r["failed"], "errors": r["errors"],
                    "health_ok": r["health_ok"]}

out = ROOT / "output/passk_results.json"
out.write_text(json.dumps(results, indent=2), encoding="utf-8")
print(f"\nSAVED {out}")
print(json.dumps(results, indent=2))
