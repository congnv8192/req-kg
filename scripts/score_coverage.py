"""
(b) Coverage/Precision tren (nodes u edges u attributes), va phan loai
    luat ngam theo taxonomy.

Buoc:
  1. Doc KG da lam giau (kg_*.json) -> dung tap PHAN GIAO GOLD = cac UNIT
     (node/edge/attr) qua 2 tang loc (layer n taxonomy). Moi unit gan 1 nhom
     taxonomy -> phuc vu Implicit-coverage.
  2. Doc G_req cua tung muc L1/L2/L3 (gia lap tu output/django_L1L2L3 —
     o day ma hoa tay tap khai niem moi muc NGU Y, de chay thu).
  3. Coverage = |G_req n Gold| / |Gold|   (req phu bao nhieu phan gold)
     Precision= |G_req n Gold| / |G_req|  (req noi co bi thua/ao khong)
     -> tinh CHUNG va tach theo nhom taxonomy (lo luat ngam bi bo o L1/L2).

Day la SMOKE TEST tren 1 repo (django). Muc dich: chung minh metric chay tren
edge+attr, va duong cong Coverage tang L1->L3, luat ngam (nhom 2) bi bo som.
"""
import json
from pathlib import Path

KG_FILES = ["models", "serializers", "views", "urls"]

# ---- tang loc (dung lai logic intersection, rut gon cho unit) ----
GLUE = {"Meta", "Migration", "AppConfig", "Config"}
BOILER = {"__str__", "__init__", "__repr__", "save", "delete", "clean", "render"}
TECH_FIELDS = {"id", "pk", "objects", "app_label"}


def is_private(n): return n.startswith("_") and not n.startswith("__")


def taxonomy(name, kind, unit_type, meta=None):
    """Gan nhom taxonomy cho 1 unit. Tra None neu ngoai phan giao."""
    low = name.lower()
    # EDGE / ATTR chо luat ngam
    if unit_type == "edge":
        if name.startswith("relates_to"):
            return "3-Structure (relation)"
        if name.startswith("sets_arg"):
            return "2-Constraints (data invariant/ownership)"
    if unit_type == "attr":
        if "constraints" in name or "max_length" in name:
            return "2-Constraints (field constraint)"
        if "fieldtype" in name:
            return "2-Constraints (type constraint)"
    # NODE
    if any(k in name for k in ("Permission", "IsOwner")) or "permission" in low:
        return "2-Constraints (permission)"
    if "filter" in low or "pagination" in low:
        return "2-Constraints (rule)"
    if "serializer" in low:
        return "4-Integration (I/O contract)"
    if kind == "class" and ("Movie" in name or "User" in name):
        return "1-Functional (entity)"
    if kind == "class" and ("View" in name):
        return "1-Functional (endpoint)"
    if kind == "field" and name not in TECH_FIELDS:
        return "1-Functional (domain field)"
    if kind == "method" and low in ("create", "list", "retrieve", "update",
                                    "destroy", "perform_create"):
        return "1-Functional (CRUD)"
    return None


def layer_ok(name, kind):
    if kind == "module":
        return False
    if name in GLUE or (kind == "method" and name in BOILER):
        return False
    if is_private(name):
        return False
    if kind == "field" and name in TECH_FIELDS:
        return False
    return True


def build_gold():
    """Tra ve dict: unit_key -> {group, type}. unit_key la khai niem chuan hoa
    (dedupe qua file: vd permission_classes gap 2 view -> 1 khai niem)."""
    gold = {}

    def add(key, group, utype):
        if group is not None:
            gold[key] = {"group": group, "type": utype}

    for f in KG_FILES:
        p = Path(f"output/kg_{f}.json")
        if not p.exists():
            continue
        kg = json.loads(p.read_text(encoding="utf-8"))
        nid2name = {n["id"]: n["name"] for n in kg["nodes"]}
        for n in kg["nodes"]:
            name, kind = n["name"], n["kind"]
            if not layer_ok(name, kind):
                continue
            g = taxonomy(name, kind, "node")
            add(f"node:{name}", g, "node")            # dedupe theo ten khai niem
            # ATTR units (chо luat ngam rang buoc)
            if "fieldtype" in n:
                add(f"attr:{name}.type={n['fieldtype']}",
                    taxonomy("fieldtype", kind, "attr"), "attr")
            for ck, cv in n.get("constraints", {}).items():
                add(f"attr:{name}.{ck}",
                    taxonomy("constraints", kind, "attr"), "attr")
        # EDGE units
        for e in kg["edges"]:
            if e["type"] == "relates_to":
                s = nid2name.get(e["src"], e["src"])
                d = e["dst"].replace("rel:", "")
                add(f"edge:relates_to:{s}->{d}",
                    taxonomy("relates_to", "", "edge"), "edge")
            elif e["type"] == "sets_arg":
                add(f"edge:sets_arg:{e['dst']}",
                    taxonomy("sets_arg", "", "edge"), "edge")
    return gold


# ---- G_req cho tung muc: tap khai niem ma requirement NGU Y ----
# Ma hoa tay tu django_L1L2L3.md. Moi phan tu la unit_key (khop gold).
# L1 = task goal 1 cau; L2 = them API+entity; L3 = full SRS (them constraint).
G_REQ = {
    "L1": [
        "node:Movie", "node:MovieListCreateView",
    ],
    "L2": [
        "node:Movie", "node:User", "node:MovieListCreateView",
        "node:MovieRetrieveUpdateDestroyView", "node:MovieSerializer",
        "node:title", "node:genre", "node:year", "node:creator",
        "node:perform_create",
        "edge:relates_to:Movie->User",
        "node:filterset_class", "node:pagination_class",
    ],
    "L3": [
        "node:Movie", "node:User", "node:MovieListCreateView",
        "node:MovieRetrieveUpdateDestroyView", "node:MovieSerializer",
        "node:title", "node:genre", "node:year", "node:creator",
        "node:perform_create",
        "node:permission_classes", "node:filterset_class",
        "node:pagination_class",
        "edge:relates_to:Movie->User",
        "edge:sets_arg:arg:creator=self.request.user",
        "attr:year.type=PositiveIntegerField",
        "attr:title.max_length", "attr:genre.max_length",
        "attr:creator.on_delete",
    ],
}


def score(gold, greq_keys):
    gold_keys = set(gold.keys())
    req = set(greq_keys)
    inter = req & gold_keys
    cov = len(inter) / len(gold_keys) if gold_keys else 0
    prec = len(inter) / len(req) if req else 0
    hallu = req - gold_keys        # req noi ma gold khong co (ao/thua)
    return cov, prec, inter, hallu


def group_of(gold, key):
    return gold[key]["group"].split(" ")[0] if key in gold else "?"


def main():
    gold = build_gold()
    print(f"=== PHAN GIAO GOLD = {len(gold)} unit ===")
    by_type = {}
    by_grp = {}
    for k, v in gold.items():
        by_type[v["type"]] = by_type.get(v["type"], 0) + 1
        g = v["group"].split(" ")[0]
        by_grp[g] = by_grp.get(g, 0) + 1
    print(f"  theo loai unit: {by_type}")
    print(f"  theo nhom taxonomy: {by_grp}")
    print()

    print(f"{'Muc':<4} {'Cov':>6} {'Prec':>6}  {'|req∩gold|':>10} "
          f"{'|gold|':>6} {'ao':>4}")
    prev_inter = set()
    for lvl in ("L1", "L2", "L3"):
        cov, prec, inter, hallu = score(gold, G_REQ[lvl])
        print(f"{lvl:<4} {cov:>6.2f} {prec:>6.2f}  {len(inter):>10} "
              f"{len(gold):>6} {len(hallu):>4}")
        prev_inter = inter

    # Implicit-coverage: nhom 2 (Constraints/luat ngam) phu bao nhieu moi muc?
    print("\n=== Implicit-coverage (nhom 2 Constraints = luat ngam) ===")
    grp2_gold = {k for k, v in gold.items() if v["group"].startswith("2")}
    print(f"  Gold nhom-2 = {len(grp2_gold)} unit: "
          f"{sorted(x.split(':',1)[1] for x in grp2_gold)}")
    for lvl in ("L1", "L2", "L3"):
        covered = set(G_REQ[lvl]) & grp2_gold
        print(f"  {lvl}: phu {len(covered)}/{len(grp2_gold)} luat ngam nhom-2 "
              f"-> {sorted(x.split(':',1)[1] for x in covered)}")

    print("\n=== Gap (luat ngam bi BO) tung muc, theo nhom ===")
    gold_keys = set(gold.keys())
    for lvl in ("L1", "L2", "L3"):
        gap = gold_keys - set(G_REQ[lvl])
        gap_by_grp = {}
        for k in gap:
            g = gold[k]["group"].split(" ")[0]
            gap_by_grp[g] = gap_by_grp.get(g, 0) + 1
        print(f"  {lvl}: bo {len(gap)} unit -> theo nhom {gap_by_grp}")


if __name__ == "__main__":
    main()
