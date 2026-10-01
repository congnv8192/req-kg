"""
Score TaskManagement (RepoGenesis expert-supervised, Gemini-oracle).
Repo giau NFR -> lan dau do NFR-coverage theo muc chi tiet L1/L2/L3.

Gold = phan giao gom 3 loai TANG NFR (tra loi cau hoi "NFR danh gia sao"):
  T1 NFR-structural       : file/module ma hoa mot NFR (validators, errors, health, config, docker)
  T2 NFR-threshold-const  : config field co GIA TRI nguong (PORT=8080, MAX_LIMIT=100, TITLE_MAX_LENGTH=200)
  T3 NFR-runtime          : KHONG co dau vet source -> ngoai gold (chi ghi threats)
+ FR units (entity/endpoint/field/rule) nhu truoc.

G_req 3 muc trich tay tu README TaskMgmt (README da phan tang san):
  L1 = "Functionality Description" (1 doan)
  L2 = + "API Definition" (endpoint + I/O schema + data model)
  L3 = + "Technical Specifications" + "Deployment Requirements" (== NFR block)
"""
import json
from pathlib import Path

KGDIR = Path("output/taskmgmt")

# --- map file/module -> NFR-structural unit (T1) ---
NFR_FILE = {
    "validators": ("NFR-struct:validation", "5-NFR (reliability/validation)"),
    "errors":     ("NFR-struct:error-handling", "5-NFR (reliability/errors)"),
    "health":     ("NFR-struct:health-check", "5-NFR (observability/health)"),
    "config":     ("NFR-struct:env-config", "5-NFR (configurability)"),
}
# Dockerfile khong phai .py -> them tay (co ton tai trong repo)
EXTRA_STRUCT = [
    ("NFR-struct:containerization", "5-NFR (deployment/docker)"),  # Dockerfile
    ("NFR-struct:logging", "5-NFR (observability/logging)"),        # rai rac -> ke ca (thay o dau)
]

# --- config field co gia tri nguong (T2) ---
THRESHOLD_FIELDS = {
    "PORT": "5-NFR (deployment/port)",
    "MAX_LIMIT": "2-Constraints (pagination limit)",
    "DEFAULT_LIMIT": "2-Constraints (pagination default)",
    "TITLE_MAX_LENGTH": "2-Constraints (field constraint)",
    "DESCRIPTION_MAX_LENGTH": "2-Constraints (field constraint)",
    "API_V1_PREFIX": "5-NFR (maintainability/versioning)",
    "API_VERSION": "5-NFR (maintainability/versioning)",
}

# --- FR taxonomy (rut gon) ---
# Luu y: repo nay KHONG co ORM class Task (dung SQLite raw + dict).
# -> "entity" khong ton tai duoi dang node class. Day la PHAT HIEN:
#    requirement co "Task Entity" nhung code KHONG co node entity
#    -> luat ngam kieu moi: entity tan trong schema SQL/dict, khong co node.
FR_ENTITY = set()  # khong co class entity trong code nay
FR_ENDPOINT_FUNCS = {"create_task", "get_tasks", "list_tasks", "get_task",
                     "update_task", "delete_task", "health_check"}
FR_RULE_FUNCS = {"validate_title", "validate_description", "validate_priority",
                 "validate_status", "validate_due_date",
                 "validate_create_payload", "validate_update_payload"}


def build_gold():
    gold = {}

    def add(key, group, tier):
        gold[key] = {"group": group, "tier": tier}

    # NFR-structural (T1): file ton tai
    for stem, (key, grp) in NFR_FILE.items():
        if (KGDIR / f"kg_{stem}.json").exists():
            add(key, grp, "T1-struct")
    for key, grp in EXTRA_STRUCT:
        add(key, grp, "T1-struct")

    # duyet nodes
    for p in KGDIR.glob("kg_*.json"):
        kg = json.loads(p.read_text(encoding="utf-8"))
        for n in kg["nodes"]:
            name, kind = n["name"], n["kind"]
            # T2 threshold const (config fields)
            if kind == "field" and name in THRESHOLD_FIELDS:
                add(f"threshold:{name}", THRESHOLD_FIELDS[name], "T2-threshold")
            # FR entity
            if kind == "class" and name in FR_ENTITY:
                add(f"node:{name}", "1-Functional (entity)", "FR")
            # FR endpoint
            if name in FR_ENDPOINT_FUNCS:
                add(f"node:{name}", "1-Functional (endpoint)", "FR")
            # FR rule (validation functions = business rule ngam)
            if name in FR_RULE_FUNCS:
                add(f"node:{name}", "2-Constraints (validation rule)", "FR")
            # ENUM-const (luat ngam moi tu T1 nang cap) = enum constraint
            if kind == "const" and n.get("enum"):
                add(f"enum:{name}", "2-Constraints (enum constraint)",
                    "T2-threshold")
    return gold


# --- G_req 3 muc (trich tay tu README) ---
G_REQ = {
    # L1: chi Functionality Description — CRUD + status/priority, KHONG NFR
    "L1": [
        "node:create_task", "node:get_tasks", "node:get_task",
        "node:update_task", "node:delete_task",
    ],
    # L2: + API Definition (endpoint day du + data model + health)
    "L2": [
        "node:create_task", "node:list_tasks", "node:get_task",
        "node:update_task", "node:delete_task", "node:health_check",
        "node:validate_title", "node:validate_priority",
        "node:validate_status",
        "threshold:TITLE_MAX_LENGTH", "threshold:DESCRIPTION_MAX_LENGTH",
        "threshold:DEFAULT_LIMIT", "threshold:MAX_LIMIT",
        # enum priority/status = README neu ngay o Data Model (L2)
        "enum:VALID_PRIORITIES", "enum:VALID_STATUSES",
    ],
    # L3: + Technical Specifications + Deployment Requirements (== NFR block)
    "L3": [
        "node:create_task", "node:list_tasks", "node:get_task",
        "node:update_task", "node:delete_task", "node:health_check",
        "node:validate_title", "node:validate_description",
        "node:validate_priority", "node:validate_status",
        "node:validate_due_date",
        "threshold:TITLE_MAX_LENGTH", "threshold:DESCRIPTION_MAX_LENGTH",
        "threshold:DEFAULT_LIMIT", "threshold:MAX_LIMIT",
        "threshold:PORT", "threshold:API_V1_PREFIX", "threshold:API_VERSION",
        "NFR-struct:validation", "NFR-struct:error-handling",
        "NFR-struct:health-check", "NFR-struct:env-config",
        "NFR-struct:containerization", "NFR-struct:logging",
        # enum + partial-update rule
        "enum:VALID_PRIORITIES", "enum:VALID_STATUSES",
        "enum:_UPDATABLE_FIELDS",
    ],
}


def score(gold, req):
    gk = set(gold)
    r = set(req)
    inter = r & gk
    cov = len(inter) / len(gk) if gk else 0
    prec = len(inter) / len(r) if r else 0
    return cov, prec, inter, r - gk


def main():
    gold = build_gold()
    tiers = {}
    for v in gold.values():
        tiers[v["tier"]] = tiers.get(v["tier"], 0) + 1
    print(f"=== GOLD = {len(gold)} unit | theo tang: {tiers} ===\n")

    print(f"{'Muc':<4}{'Cov':>7}{'Prec':>7}{'inter':>7}{'gold':>6}{'ao':>4}")
    for lvl in ("L1", "L2", "L3"):
        cov, prec, inter, hallu = score(gold, G_REQ[lvl])
        print(f"{lvl:<4}{cov:>7.2f}{prec:>7.2f}{len(inter):>7}{len(gold):>6}"
              f"{len(hallu):>4}")

    # NFR-coverage rieng theo tang NFR
    print("\n=== NFR-coverage theo tung TANG (tra loi 'NFR danh gia sao') ===")
    for tier in ("T1-struct", "T2-threshold"):
        tier_gold = {k for k, v in gold.items() if v["tier"] == tier}
        print(f"\n  [{tier}] gold = {len(tier_gold)}: "
              f"{sorted(tier_gold)}")
        for lvl in ("L1", "L2", "L3"):
            cov = set(G_REQ[lvl]) & tier_gold
            print(f"    {lvl}: {len(cov)}/{len(tier_gold)} "
                  f"-> {sorted(x.split(':',1)[-1] for x in cov)}")

    print("\n  [T3-runtime] = 0 unit trong gold (khong dau vet source) "
          "-> NGOAI scope, ghi threats")

    # FR vs NFR tach bach
    print("\n=== FR-coverage vs NFR-coverage (L3) ===")
    fr_gold = {k for k, v in gold.items() if v["tier"] == "FR"}
    nfr_gold = {k for k, v in gold.items()
                if v["tier"] in ("T1-struct", "T2-threshold")}
    for lvl in ("L1", "L2", "L3"):
        r = set(G_REQ[lvl])
        fc = len(r & fr_gold) / len(fr_gold)
        nc = len(r & nfr_gold) / len(nfr_gold)
        print(f"  {lvl}: FR-cov={fc:.2f}  NFR-cov={nc:.2f}")


if __name__ == "__main__":
    main()
