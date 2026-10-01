"""
Scorer TONG QUAT (moi repo) — cham G_req vs general_gold.
Aligner map G_req (requirement-space) -> gold units (code-space) bang QUY TAC
tong quat, khong hard-code ten repo:
  - operation.action  -> FR-endpoint node chua verb tuong ung
  - attribute co constraint -> validate_<field> (tri thuc constraint bieu dien
                               qua ham validation, chung cho moi style code)
  - nfr.category      -> nfr:<category>
  - threshold/enum    -> const:/enum: neu ton tai

Dung: python general_score.py <repo_name> <greq_prefix>
  vd: python general_score.py TaskManagement req
      python general_score.py UserManagement um_req
"""
import sys
import json
from pathlib import Path

VERB = {"create": "create", "delete": "delete", "update": "update",
        "login": "login", "health": "health", "reset_password": "reset",
        "list": "list", "retrieve": "get", "register": "register"}
NFRCAT = {"validation": "validation", "error_handling": "error-handling",
          "logging": "logging", "health_check": "health-check",
          "deployment": "config", "configuration": "config",
          "containerization": "containerization", "auth": "auth",
          "migration": "migration"}


def align(greq, gold):
    gl = list(gold)
    endpoints = [u for u in gl if u.startswith("node:") and "validate" not in u]
    validations = [u for u in gl if "validate" in u]
    matched = set()

    # operations -> endpoint theo verb
    for op in greq.get("operations", []) or []:
        act = (op.get("action") or "").lower()
        v = VERB.get(act)
        if not v:
            continue
        # 'list' va 'retrieve' deu map ve get* -> phan biet: list->plural
        cands = [e for e in endpoints if v in e.lower()]
        if not cands and act in ("list", "retrieve"):
            cands = [e for e in endpoints if "get" in e.lower()]
        if cands:
            # list uu tien ten so nhieu (users), retrieve so it (user)
            if act == "list":
                cands.sort(key=lambda e: (not e.rstrip("s").endswith("s"), e))
            matched.add(sorted(cands, key=len)[0] if act == "retrieve"
                        else cands[0])

    # attributes co constraint -> validate_<field>
    for at in greq.get("attributes", []) or []:
        nm = (at.get("name") or "").lower()
        has_c = (at.get("enum") or at.get("max_length") or at.get("min_length")
                 or at.get("required") is not None or at.get("type")
                 or at.get("unique"))
        if not (nm and has_c):
            continue
        for val in validations:
            if nm in val.lower():
                matched.add(val)
                break

    # nfr -> nfr:category
    for nf in greq.get("nfr", []) or []:
        cat = NFRCAT.get((nf.get("category") or "").lower())
        if not cat:
            continue
        for u in gl:
            if u.startswith("nfr:") and cat in u:
                matched.add(u)
                break

    # thresholds/enum -> const:/enum: neu co
    for th in (greq.get("thresholds", []) or []):
        nm = (th.get("name") or "").lower()
        toks = [t for t in nm.replace("-", "_").split("_") if len(t) > 2]
        for u in gl:
            if u.startswith(("const:", "enum:")) and any(t in u.lower()
                                                          for t in toks):
                matched.add(u)
                break
    for at in greq.get("attributes", []) or []:
        if at.get("enum"):
            nm = (at.get("name") or "").lower()
            for u in gl:
                if u.startswith("enum:") and nm in u.lower():
                    matched.add(u)
                    break
    return matched


def main():
    repo, prefix = sys.argv[1], sys.argv[2]
    gold = set(json.load(open(f"output/gold_{repo}.json", encoding="utf-8")))
    print(f"REPO {repo} | gold = {len(gold)} unit")
    # map so thu tu file: L1->{prefix}1, L2->2, L3->3 (hoac _L1)
    cand = {"L1": [f"{prefix}1", f"{prefix}_L1"],
            "L2": [f"{prefix}2", f"{prefix}_L2"],
            "L3": [f"{prefix}3", f"{prefix}_L3"]}
    print(f"{'Muc':<4}{'Coverage':>10}{'Precision':>11}{'khop':>6}{'gold':>6}")
    out = {}
    for L in ("L1", "L2", "L3"):
        g = None
        for c in cand[L]:
            p = Path(f"llm-answers/{c}.json")
            if p.exists():
                g = json.loads(p.read_text(encoding="utf-8"))
                break
        if g is None:
            print(f"{L}: thieu file")
            continue
        a = align(g, gold)
        inter = a & gold
        cov = len(inter) / len(gold) if gold else 0
        nassert = (len(g.get("operations", []) or []) + len(g.get("attributes", []) or [])
                   + len(g.get("nfr", []) or []) + len(g.get("thresholds", []) or []))
        prec = len(inter) / len(a) if a else 0
        out[L] = {"coverage": round(cov, 3), "matched": len(inter),
                  "gold": len(gold)}
        print(f"{L:<4}{cov:>10.2f}{prec:>11.2f}{len(inter):>6}{len(gold):>6}")
    Path(f"output/score_{repo}.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8")
    print(f"SAVED output/score_{repo}.json")


if __name__ == "__main__":
    main()
