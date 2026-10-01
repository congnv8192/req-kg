"""
Bang metrics DAY DU cho nhieu repo (moi repo/muc: Coverage, Precision,
Consistency, FR-cov, NFR/constraint-cov, Implicit-gap) + pass@k neu co.

Dung: python general_metrics.py <repo1>:<prefix1> <repo2>:<prefix2> ...
  vd: python general_metrics.py TaskManagement:req UserManagement:um_req Customization:cust_req
"""
import sys
import json
from pathlib import Path
import importlib.util


def load(mod, path):
    s = importlib.util.spec_from_file_location(mod, path)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


GS = load("gs", "scripts/general_score.py")
MF = load("mf", "scripts/metrics_full.py")

# category -> nhom lon
FR_CATS = {"FR-endpoint", "FR-validation"}
NFR_CATS = {"enum", "threshold", "NFR-struct"}  # constraint + NFR


def greq_path(prefix, n):
    for c in (f"{prefix}{n}", f"{prefix}_L{n}", f"{prefix.replace('_req','')}_req{n}"):
        p = Path(f"llm-answers/{c}.json")
        if p.exists():
            return p
    return None


def repo_rows(repo, prefix):
    goldmap = json.load(open(f"output/gold_{repo}.json", encoding="utf-8"))
    gold = set(goldmap)
    FR = {u for u, c in goldmap.items() if c in FR_CATS}
    NFR = {u for u, c in goldmap.items() if c in NFR_CATS}
    passk = {}
    pf = Path(f"output/repo_{repo}.json")
    if pf.exists():
        passk = json.load(open(pf, encoding="utf-8")).get("passk", {})
    rows = []
    for n, L in (("1", "L1"), ("2", "L2"), ("3", "L3")):
        p = greq_path(prefix, n)
        if not p:
            continue
        g = json.loads(p.read_text(encoding="utf-8"))
        a = GS.align(g, gold)
        inter = a & gold
        cov = len(inter) / len(gold) if gold else 0
        prec = len(inter) / len(a) if a else 0
        # strict precision: /tong assertion
        tot = sum(len(g.get(k, []) or []) for k in
                  ("operations", "attributes", "nfr", "thresholds",
                   "relations", "entities"))
        prec_s = len(inter) / tot if tot else 0
        cons = MF.consistency(g)
        frc = len(inter & FR) / len(FR) if FR else 0
        nfrc = len(inter & NFR) / len(NFR) if NFR else 0
        gap = len(gold - inter)
        pk = ""
        if L in passk and passk[L].get("total"):
            pk = f"{passk[L]['passed']}/{passk[L]['total']}"
        rows.append({"repo": repo, "L": L, "cov": cov, "prec": prec,
                     "prec_s": prec_s, "cons": "PASS" if not cons else f"{len(cons)}v",
                     "frc": frc, "nfrc": nfrc, "gap": gap, "gold": len(gold),
                     "passk": pk})
    return rows


def main():
    all_rows = []
    for arg in sys.argv[1:]:
        repo, prefix = arg.split(":")
        all_rows += repo_rows(repo, prefix)

    hdr = (f"{'Repo':<16}{'L':<4}{'Cov':>6}{'Prec':>6}{'Prec_s':>7}"
           f"{'Consis':>7}{'FR-cov':>7}{'NFRcov':>7}{'Gap':>5}{'pass@k':>9}")
    print(hdr)
    print("-" * len(hdr))
    cur = None
    for r in all_rows:
        if r["repo"] != cur:
            cur = r["repo"]
        print(f"{r['repo'][:15]:<16}{r['L']:<4}{r['cov']:>6.2f}{r['prec']:>6.2f}"
              f"{r['prec_s']:>7.2f}{r['cons']:>7}{r['frc']:>7.2f}{r['nfrc']:>7.2f}"
              f"{r['gap']:>5}{r['passk']:>9}")
    Path("output/metrics_table.json").write_text(
        json.dumps(all_rows, indent=2), encoding="utf-8")
    print("\nSAVED output/metrics_table.json")
    print("Cot: Cov=Coverage · Prec=Precision(/align) · Prec_s=Precision(/tong "
          "assertion) · Consis=Consistency SHACL-lite · FR-cov/NFRcov=tach "
          "chuc-nang/phi-chuc-nang · Gap=so unit luat ngam bi bo · pass@k=fair")


if __name__ == "__main__":
    main()
