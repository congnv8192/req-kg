"""So lieu Section 4 (ban hien tai) -> output/metrics_groups.json.

Tinh lai tu du lieu da co, KHONG chay lai LLM:
  gold   : output/gold_<repo>.json        (general_gold.py)
  G_req  : llm-answers/<prefix>{1,2,3}.json
  pass   : output/passk_fair.json (TaskManagement),
           output/passk_fair_UserManagement.json, output/repo_Customization.json

Nhom taxonomy (Sect. 3.2): F = endpoint; C = validation + enum + threshold
(Constraints & Robustness); N = NFR mechanism.
Precision = |M| / |A(G_req)|  (= cot "Prec-strict" cu).

Luu y tai lap: general_score.align() lay "khop dau tien" khi duyet mot set,
nen ket qua phu thuoc PYTHONHASHSEED (chi Customization L2/L3 lech 1 unit).
Script tu chay lai voi PYTHONHASHSEED=3 de ra dung bang da bao cao.
Chay tu thu muc experiment/:  python scripts/metrics_groups.py
"""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

SEED = "3"
if os.environ.get("PYTHONHASHSEED") != SEED:
    env = dict(os.environ, PYTHONHASHSEED=SEED)
    sys.exit(subprocess.run([sys.executable] + sys.argv, env=env).returncode)

_spec = importlib.util.spec_from_file_location("gs", "scripts/general_score.py")
GS = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(GS)
_spec = importlib.util.spec_from_file_location("mf", "scripts/metrics_full.py")
MF = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(MF)

REPOS = [("TaskManagement", "req"), ("UserManagement", "um_req"),
         ("Customization", "cust_req")]
GROUP = {"FR-endpoint": "F", "FR-validation": "C", "enum": "C",
         "threshold": "C", "NFR-struct": "N"}
KINDS = ("operations", "attributes", "nfr", "thresholds", "relations",
         "entities")


def greq_file(prefix, n):
    for c in (f"{prefix}{n}", f"{prefix}_L{n}",
              f"{prefix.replace('_req', '')}_req{n}"):
        p = Path(f"llm-answers/{c}.json")
        if p.exists():
            return p
    raise FileNotFoundError(f"G_req {prefix} L{n}")


def pass_counts(repo):
    if repo == "TaskManagement":
        d = json.load(open("output/passk_fair.json", encoding="utf-8"))
        return {L: (d[L]["passed"], 44) for L in ("L1", "L2", "L3")}
    if repo == "UserManagement":
        d = json.load(open("output/passk_fair_UserManagement.json",
                           encoding="utf-8"))
        return {L: (d[L]["passed"], d[L]["total"]) for L in ("L1", "L2", "L3")}
    d = json.load(open(f"output/repo_{repo}.json", encoding="utf-8"))["passk"]
    return {L: (d[L]["passed"], d[L]["total"]) for L in ("L1", "L2", "L3")}


def main():
    rows = []
    for repo, prefix in REPOS:
        goldmap = json.load(open(f"output/gold_{repo}.json", encoding="utf-8"))
        gold = set(goldmap)
        size = {g: sum(1 for c in goldmap.values() if GROUP[c] == g)
                for g in "FCN"}
        passed = pass_counts(repo)
        for n in "123":
            L = f"L{n}"
            g = json.loads(greq_file(prefix, n).read_text(encoding="utf-8"))
            m = GS.align(g, gold) & gold
            n_assert = sum(len(g.get(k, []) or []) for k in KINDS)
            hit = {x: sum(1 for u in m if GROUP[goldmap[u]] == x)
                   for x in "FCN"}
            rows.append({
                "repo": repo, "L": L, "R": len(gold), "M": len(m),
                "A": n_assert,
                "cov": len(m) / len(gold),
                "prec": len(m) / n_assert if n_assert else 0.0,
                "R_g": size, "M_g": hit,
                "cov_g": {x: hit[x] / size[x] if size[x] else None
                          for x in "FCN"},
                "violations": len(MF.consistency(g)),
                "gap": sorted(gold - m),
                "passed": passed[L][0], "tests": passed[L][1],
                "pass_rate": passed[L][0] / passed[L][1],
            })
    out = Path("output/metrics_groups.json")
    out.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"{'repo':<15}{'L':<3}{'Cov':>6}{'F':>6}{'C':>6}{'N':>6}"
          f"{'Prec':>6}{'viol':>5}{'Gap':>5}{'pass':>9}")
    for r in rows:
        cg = r["cov_g"]
        print(f"{r['repo'][:14]:<15}{r['L']:<3}{r['cov']:>6.2f}"
              f"{cg['F']:>6.2f}{cg['C']:>6.2f}{cg['N']:>6.2f}"
              f"{r['prec']:>6.2f}{r['violations']:>5}{len(r['gap']):>5}"
              f"{r['passed']:>5}/{r['tests']}")
    print(f"SAVED {out}")


if __name__ == "__main__":
    main()
