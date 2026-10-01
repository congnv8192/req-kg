"""
Cham G_req do LLM sinh (Vong 1 smoke) so voi phan-giao-gold cua TaskManagement.

Input: output/greq_out_L1.json, _L2.json, _L3.json
       (JSON LLM tra ve, schema: entities/attributes/operations/relations/
        thresholds/nfr — xem prompts/greq_L*.md)

Buoc:
  1. ALIGN: anh xa cac phan tu requirement-space (LLM output) -> unit gold
     code-space (node:/enum:/threshold:/NFR-struct:). Day la lop "phan giao
     alignment" — co chu quan, ghi codebook, se kappa sau.
  2. SCORE: Coverage = |align ∩ gold|/|gold|; Precision = |align ∩ gold|/|align|.
     align \ gold = phan tu LLM sinh KHONG khop gold = "ao/thua" (do Precision).

So sanh voi so ma-tay truoc (Precision=1.0): gio Precision that <1 neu LLM
bia/lech.
"""
import json
import sys
from pathlib import Path

# Gold units = phan giao TaskManagement (khop score_taskmgmt.py, 30 unit).
GOLD = {
    # FR endpoints
    "node:create_task", "node:get_tasks", "node:get_task",
    "node:update_task", "node:delete_task", "node:health_check",
    # FR validation rules (business rule ngam, code tach ham validate_*)
    "node:validate_title", "node:validate_description",
    "node:validate_priority", "node:validate_status", "node:validate_due_date",
    # threshold-as-constant
    "threshold:PORT", "threshold:MAX_LIMIT", "threshold:DEFAULT_LIMIT",
    "threshold:TITLE_MAX_LENGTH", "threshold:DESCRIPTION_MAX_LENGTH",
    "threshold:API_V1_PREFIX", "threshold:API_VERSION",
    # enum
    "enum:VALID_PRIORITIES", "enum:VALID_STATUSES", "enum:_UPDATABLE_FIELDS",
    # NFR-structural
    "NFR-struct:validation", "NFR-struct:error-handling",
    "NFR-struct:health-check", "NFR-struct:env-config",
    "NFR-struct:containerization", "NFR-struct:logging",
    # FR entity note: code khong co class Task (SQLite raw) -> gold khong co
    # entity node; nhung requirement CO the neu "Task" -> se roi vao align\gold
    # (khong tru diem la hop ly: day la thong tin dung, chi khong co node code).
}


def align(greq: dict):
    """Anh xa LLM output -> tap unit gold-space. Tra ve set unit_key.
    Ghi ro moi luat anh xa (codebook)."""
    units = set()

    # 1. operations -> FR endpoint nodes
    ACT2NODE = {"create": "node:create_task", "list": "node:get_tasks",
                "retrieve": "node:get_task", "update": "node:update_task",
                "delete": "node:delete_task", "health": "node:health_check"}
    for op in greq.get("operations", []) or []:
        act = (op.get("action") or "").lower()
        if act in ACT2NODE:
            units.add(ACT2NODE[act])
        # health cung ngu y NFR health-check + endpoint
        if act == "health":
            units.add("NFR-struct:health-check")

    # 2. attributes -> validation rule + enum + threshold
    for at in greq.get("attributes", []) or []:
        name = (at.get("name") or "").lower()
        # co bat ky rang buoc/kieu -> ngu y co validate_<field>
        has_spec = (at.get("type") or at.get("required") is not None
                    or at.get("max_length") or at.get("enum")
                    or at.get("default"))
        if name in ("title", "description", "priority", "status", "due_date") \
                and has_spec:
            units.add(f"node:validate_{name}")
        # enum
        if at.get("enum"):
            if name == "priority":
                units.add("enum:VALID_PRIORITIES")
            elif name == "status":
                units.add("enum:VALID_STATUSES")
        # max_length -> threshold
        if at.get("max_length"):
            if name == "title":
                units.add("threshold:TITLE_MAX_LENGTH")
            elif name == "description":
                units.add("threshold:DESCRIPTION_MAX_LENGTH")

    # 3. thresholds -> threshold units
    for th in greq.get("thresholds", []) or []:
        n = (th.get("name") or "").lower()
        if "port" in n:
            units.add("threshold:PORT"); units.add("NFR-struct:env-config")
        if "max" in n and ("page" in n or "limit" in n):
            units.add("threshold:MAX_LIMIT")
        if "default" in n and ("page" in n or "limit" in n):
            units.add("threshold:DEFAULT_LIMIT")
        if "prefix" in n or "api_prefix" in n or "base" in n:
            units.add("threshold:API_V1_PREFIX")
        if "version" in n:
            units.add("threshold:API_VERSION")
        if "title" in n and "length" in n:
            units.add("threshold:TITLE_MAX_LENGTH")
        if "desc" in n and "length" in n:
            units.add("threshold:DESCRIPTION_MAX_LENGTH")

    # 4. nfr -> NFR-struct
    NFR2 = {"validation": "NFR-struct:validation",
            "error_handling": "NFR-struct:error-handling",
            "logging": "NFR-struct:logging",
            "health_check": "NFR-struct:health-check",
            "deployment": "NFR-struct:env-config",
            "configuration": "NFR-struct:env-config",
            "containerization": "NFR-struct:containerization"}
    for nf in greq.get("nfr", []) or []:
        cat = (nf.get("category") or "").lower()
        if cat in NFR2:
            units.add(NFR2[cat])

    return units


def score(units):
    inter = units & GOLD
    cov = len(inter) / len(GOLD)
    prec = len(inter) / len(units) if units else 0.0
    hallu = units - GOLD          # LLM sinh ma gold khong co
    miss = GOLD - units           # gold ma LLM bo
    return cov, prec, inter, hallu, miss


def main():
    print(f"GOLD = {len(GOLD)} unit\n")
    print(f"{'Muc':<4}{'Cov':>7}{'Prec':>7}{'khop':>6}{'ao':>5}{'sot':>5}")
    rows = {}
    for lvl in ("L1", "L2", "L3"):
        p = Path(f"output/greq_out_{lvl}.json")
        if not p.exists():
            print(f"{lvl:<4}  (chua co {p} — dan output LLM vao day)")
            continue
        greq = json.loads(p.read_text(encoding="utf-8"))
        units = align(greq)
        cov, prec, inter, hallu, miss = score(units)
        rows[lvl] = (cov, prec, inter, hallu, miss, units)
        print(f"{lvl:<4}{cov:>7.2f}{prec:>7.2f}{len(inter):>6}"
              f"{len(hallu):>5}{len(miss):>5}")

    for lvl, (cov, prec, inter, hallu, miss, units) in rows.items():
        print(f"\n=== {lvl} chi tiet ===")
        print(f"  KHOP ({len(inter)}): {sorted(inter)}")
        if hallu:
            print(f"  AO/THUA ({len(hallu)}) [keo Precision xuong]: {sorted(hallu)}")
        if miss:
            print(f"  SOT ({len(miss)}) [luat ngam requirement bo]: {sorted(miss)}")


if __name__ == "__main__":
    main()
