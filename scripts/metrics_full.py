"""
Bo metrics DAY DU (4 tieu chi khung v6) tren du lieu smoke that (TaskManagement).
Bo sung cho score_greq_llm.py (moi co Coverage+Precision).

  1. Coverage   = |align ∩ gold| / |gold|
  2. Precision  = 3 muc (chat) — align∩gold / align∩code / tong assertion
  3. Consistency= SHACL-lite tren G_req (C1 structural + C2 shape)
  4. Implicit-coverage ⭐ = Gap profile: moi LOAI luat, phu tai muc nao
                         + luat "khong xoa duoc" (sot ca 3 muc)

Input: output/greq_out_L{1,2,3}.json
"""
import json
import importlib.util
from pathlib import Path

# nap align() + GOLD tu scorer cu
spec = importlib.util.spec_from_file_location("s", "scripts/score_greq_llm.py")
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
align, GOLD = s.align, s.GOLD

# ---- phan loai gold theo category (cho Implicit-coverage) ----
CATEGORY = {
    "node:create_task": "FR-endpoint", "node:get_tasks": "FR-endpoint",
    "node:get_task": "FR-endpoint", "node:update_task": "FR-endpoint",
    "node:delete_task": "FR-endpoint", "node:health_check": "FR-endpoint",
    "node:validate_title": "FR-validation", "node:validate_description": "FR-validation",
    "node:validate_priority": "FR-validation", "node:validate_status": "FR-validation",
    "node:validate_due_date": "FR-validation",
    "threshold:PORT": "threshold", "threshold:MAX_LIMIT": "threshold",
    "threshold:DEFAULT_LIMIT": "threshold", "threshold:TITLE_MAX_LENGTH": "threshold",
    "threshold:DESCRIPTION_MAX_LENGTH": "threshold",
    "threshold:API_V1_PREFIX": "threshold", "threshold:API_VERSION": "threshold",
    "enum:VALID_PRIORITIES": "enum", "enum:VALID_STATUSES": "enum",
    "enum:_UPDATABLE_FIELDS": "enum",
    "NFR-struct:validation": "NFR-struct", "NFR-struct:error-handling": "NFR-struct",
    "NFR-struct:health-check": "NFR-struct", "NFR-struct:env-config": "NFR-struct",
    "NFR-struct:containerization": "NFR-struct", "NFR-struct:logging": "NFR-struct",
}
CATS = ["FR-endpoint", "FR-validation", "threshold", "enum", "NFR-struct"]
# nhom taxonomy Zi et al.
TAXO = {"FR-endpoint": "G1 Functional", "FR-validation": "G2 Constraints",
        "threshold": "G2 Constraints", "enum": "G2 Constraints",
        "NFR-struct": "G5 NFR"}


def consistency(greq):
    """SHACL-lite tren G_req. Tra ve (so vi pham, danh sach)."""
    viol = []
    # C1 structural: attribute phai co ten; operation action hop le
    VALID_ACT = {"create", "list", "retrieve", "update", "delete", "health",
                 "login", "reset_password", "register", "search", "other"}
    for at in greq.get("attributes", []) or []:
        if not at.get("name"):
            viol.append("C1: attribute thieu 'name'")
    for op in greq.get("operations", []) or []:
        if (op.get("action") or "") not in VALID_ACT:
            viol.append(f"C1: operation action la '{op.get('action')}' khong hop le")
    # C1: khong trung entity
    ents = [e.lower() for e in greq.get("entities", []) or []]
    if len(ents) != len(set(ents)):
        viol.append("C1: entity trung lap")
    # C2 shape: enum khong rong; max_length la so duong; required la bool/None;
    #           mot field khong vua enum vua max_length (mau thuan kieu)
    for at in greq.get("attributes", []) or []:
        nm = at.get("name")
        if at.get("enum") is not None and len(at.get("enum")) == 0:
            viol.append(f"C2: {nm} co enum rong")
        ml = at.get("max_length")
        if ml is not None and (not isinstance(ml, int) or ml <= 0):
            viol.append(f"C2: {nm} max_length khong duong: {ml}")
        rq = at.get("required")
        if rq is not None and not isinstance(rq, bool):
            viol.append(f"C2: {nm} required khong phai bool: {rq}")
        if at.get("enum") and ml:
            viol.append(f"C2: {nm} vua enum vua max_length (mau thuan kieu)")
    # C2 shape: threshold value la so (tru prefix/version dang chuoi)
    for th in greq.get("thresholds", []) or []:
        nm = (th.get("name") or "").lower()
        v = th.get("value")
        if "port" in nm or "limit" in nm or "length" in nm or "size" in nm:
            if not isinstance(v, (int, float)):
                viol.append(f"C2: threshold {nm} value khong phai so: {v}")
    return viol


def precision_strict(greq, aligned):
    """Precision 3 muc: dem TONG assertion cua G_req (khong chi cai map duoc)."""
    total = 0
    total += len(greq.get("operations", []) or [])
    total += len(greq.get("attributes", []) or [])
    total += len(greq.get("thresholds", []) or [])
    total += len(greq.get("nfr", []) or [])
    total += len(greq.get("relations", []) or [])
    total += len(greq.get("entities", []) or [])
    inter = len(aligned & GOLD)
    # muc 1: /align (nhu cu, khoan dung)
    p_align = inter / len(aligned) if aligned else 0
    # muc 2: /tong assertion (chat — moi thu G_req noi ra)
    p_total = inter / total if total else 0
    return p_align, p_total, total


def main():
    data = {}
    for lvl in ("L1", "L2", "L3"):
        p = Path(f"output/greq_out_{lvl}.json")
        if p.exists():
            data[lvl] = json.loads(p.read_text(encoding="utf-8"))

    print("=" * 66)
    print("TIEU CHI 1+2 — Coverage & Precision (chat)")
    print("=" * 66)
    print(f"{'Muc':<4}{'Cov':>7}{'Prec/align':>12}{'Prec/total':>12}"
          f"{'#assert':>9}")
    aligned_by = {}
    for lvl, g in data.items():
        a = align(g); aligned_by[lvl] = a
        cov = len(a & GOLD) / len(GOLD)
        pa, pt, tot = precision_strict(g, a)
        print(f"{lvl:<4}{cov:>7.2f}{pa:>12.2f}{pt:>12.2f}{tot:>9}")

    print("\n" + "=" * 66)
    print("TIEU CHI 3 — Consistency (SHACL-lite tren G_req)")
    print("=" * 66)
    for lvl, g in data.items():
        v = consistency(g)
        status = "PASS (0 vi pham)" if not v else f"{len(v)} vi pham"
        print(f"  {lvl}: {status}")
        for x in v:
            print(f"       - {x}")

    print("\n" + "=" * 66)
    print("TIEU CHI 4 ⭐ — Implicit-coverage: profile theo LOAI luat")
    print("=" * 66)
    print(f"{'Category':<16}{'taxonomy':<16}{'|C|':>4}{'L1':>6}{'L2':>6}{'L3':>6}")
    goldcat = {c: {k for k, v in CATEGORY.items() if v == c} for c in CATS}
    for c in CATS:
        gc = goldcat[c]
        cells = []
        for lvl in ("L1", "L2", "L3"):
            covered = len(aligned_by.get(lvl, set()) & gc)
            cells.append(f"{covered}/{len(gc)}")
        print(f"{c:<16}{TAXO[c]:<16}{len(gc):>4}"
              f"{cells[0]:>6}{cells[1]:>6}{cells[2]:>6}")

    # luat "khong xoa duoc" = sot ca 3 muc
    miss_all = GOLD.copy()
    for lvl in ("L1", "L2", "L3"):
        miss_all -= aligned_by.get(lvl, set())
    print(f"\n  Luat NGAM KHONG XOA DUOC (sot ca L1+L2+L3): {len(miss_all)}")
    for u in sorted(miss_all):
        print(f"       - {u}  [{CATEGORY[u]}]")

    # Gap phan loai o tung muc (bao nhieu luat ngam moi loai bi bo)
    print("\n  Gap = luat ngam BI BO moi muc, theo category:")
    for lvl in ("L1", "L2", "L3"):
        gap = GOLD - aligned_by.get(lvl, set())
        by = {}
        for u in gap:
            by[CATEGORY[u]] = by.get(CATEGORY[u], 0) + 1
        pretty = ", ".join(f"{k}:{by[k]}" for k in CATS if k in by)
        print(f"       {lvl}: bo {len(gap)} -> {pretty}")


if __name__ == "__main__":
    main()
