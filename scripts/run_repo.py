"""
Chay TRON 1 repo (sau khi da co llm-answers): Coverage + pass@k fair + rho.
Dung: python run_repo.py <repo_dir> <prefix> <port>
Yeu cau: llm-answers/<prefix>_req{1,2,3}.json + <prefix>_code_L{1,2,3}.py
         output/gold_<repoName>.json (chay general_gold truoc)
"""
import sys
import json
import subprocess
import time
import os
import shutil
import re
from pathlib import Path
import importlib.util

repo_dir = Path(sys.argv[1]).resolve()
prefix = sys.argv[2]
port = int(sys.argv[3])
name = repo_dir.name
BASE = Path(".").resolve()
RUN = str(BASE / ".venv-run" / "Scripts" / "python.exe")


def spearman(x, y):
    def rank(v):
        s = sorted(range(len(v)), key=lambda i: v[i]); r = [0]*len(v)
        for pos, i in enumerate(s): r[i] = pos+1
        return r
    rx, ry = rank(x), rank(y); n = len(x)
    return 1 - 6*sum((a-b)**2 for a, b in zip(rx, ry))/(n*(n*n-1))


# --- 1. Coverage (general_score) ---
gs = importlib.util.spec_from_file_location("gs", "scripts/general_score.py")
gsm = importlib.util.module_from_spec(gs); gs.loader.exec_module(gsm)
gold = set(json.load(open(f"output/gold_{name}.json", encoding="utf-8")))
covs = {}
for L, n3 in (("L1", "1"), ("L2", "2"), ("L3", "3")):
    p = Path(f"llm-answers/{prefix}_req{n3}.json")
    g = json.loads(p.read_text(encoding="utf-8"))
    covs[L] = len(gsm.align(g, gold) & gold) / len(gold)

# --- 2. patch tests ---
subprocess.run([str(BASE/".venv/Scripts/python.exe"), "scripts/patch_tests.py",
                str(repo_dir)], capture_output=True)
tests = str(BASE / "output" / f"tests_patched_{name}")

# --- 3. pass@k fair moi muc ---
import requests
passk = {}
for L in ("L1", "L2", "L3"):
    d = BASE / "output" / f"{prefix}_code_{L}"
    d.mkdir(exist_ok=True)
    shutil.copy(f"llm-answers/{prefix}_code_{L}.py", d / "main.py")
    proc = subprocess.Popen(
        [RUN, "-m", "uvicorn", "main:app", "--host", "::", "--port", str(port),
         "--log-level", "warning"], cwd=str(d), stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
    try:
        time.sleep(4)
        r = subprocess.run([RUN, "-m", "pytest", tests, "-q", "--tb=no",
                            "-p", "no:cacheprovider"], cwd=str(d),
                           capture_output=True, text=True, timeout=180)
        out = r.stdout + r.stderr
        g = lambda pat: (int(re.search(pat, out).group(1)) if re.search(pat, out) else 0)
        p, f, e, s = g(r"(\d+) passed"), g(r"(\d+) failed"), g(r"(\d+) error"), g(r"(\d+) skipped")
        passk[L] = {"passed": p, "total": p+f+e+s}
    finally:
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                       capture_output=True)

# --- 4. tong hop ---
covl = [covs["L1"], covs["L2"], covs["L3"]]
rate = [passk[L]["passed"]/passk[L]["total"] if passk[L]["total"] else 0
        for L in ("L1", "L2", "L3")]
rho = spearman(covl, rate)
print(f"\n===== {name} (prefix={prefix}, port={port}) =====")
print(f"{'Muc':<4}{'Coverage':>10}{'pass@k':>10}{'pass/total':>12}")
for i, L in enumerate(("L1", "L2", "L3")):
    print(f"{L:<4}{covl[i]:>10.2f}{rate[i]:>10.2f}"
          f"{str(passk[L]['passed'])+'/'+str(passk[L]['total']):>12}")
print(f"Spearman rho (within-repo) = {rho:.3f}")
res = {"repo": name, "coverage": covs, "passk": passk, "rate": rate, "rho": rho}
Path(f"output/repo_{name}.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
print(f"SAVED output/repo_{name}.json")


if __name__ == "__main__":
    pass
