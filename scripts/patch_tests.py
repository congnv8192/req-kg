"""Tao ban TEST DA VA (chan doan) cho 1 repo: go 2 artifact harness cascade:
  1. cleanup fixture .json().get('<res>', []) tren LIST tran -> AttributeError
     cascade toan bo. Va: robust (xu ly ca list lan dict).
  2. health-gate pytest.skip(...) + max_retries lon -> treo/skip het khi thieu
     /health. Va: skip->return, max_retries->2.
Ket qua = fair pass@k (khong cascade zero oan). Dung: python patch_tests.py <repo_dir>
"""
import sys
import re
import shutil
from pathlib import Path

repo = Path(sys.argv[1]).resolve()
src = repo / "tests"
dst = Path("output") / f"tests_patched_{repo.name}"
if dst.exists():
    shutil.rmtree(dst)
shutil.copytree(src, dst)

n = 0
for f in list(dst.glob("*.py")) + list(dst.glob("**/*.py")):
    t = f.read_text(encoding="utf-8")
    o = t
    # 1. robust cleanup: .json().get('X', []) -> xu ly list
    t = re.sub(r"response\.json\(\)\.get\((['\"])(\w+)\1,\s*\[\]\)",
               r"(response.json().get(\1\2\1, []) if isinstance(response.json(), dict) else response.json())",
               t)
    # 2a. health-gate: skip -> return
    t = re.sub(r"pytest\.skip\((['\"]).*?server.*?\1\)", "return", t)
    # 2b. giam retry
    t = t.replace("max_retries = 30", "max_retries = 2")
    if t != o:
        f.write_text(t, encoding="utf-8")
        n += 1
        print("patched", f.relative_to(dst))
print(f"DONE -> {dst}  ({n} files patched)")
