"""
T2 — Phan giao (intersection): loc G_code -> phan requirement CO TRACH NHIEM ngu y.

Hai tang loc doc lap, giao nhau (mot node vao phan giao khi qua CA HAI):
  Quy tac 1 LAYER   : giu node o tang requirement cham, bo ha tang/glue/boilerplate
  Quy tac 2 TAXONOMY: node phai map duoc vao >=1 nhom requirement (Zi et al.)

Day la BAN HEURISTIC (deterministic) — de-risk T2. Nhan cuoi van can nguoi
xac nhan (kappa). Muc dich: cho thay "phan giao" that trong thuc te trong the nao,
va lam ro cac node RANH GIOI (nguon bat dong annotator).

Chay: python intersection.py output/kg_*.json
"""
import sys
import json
import glob
from pathlib import Path

# ---- Quy tac 1: LAYER ----
# Ten node bi loai vi la framework glue / boilerplate / impl helper.
GLUE_NAMES = {"Meta", "Migration", "AppConfig", "Config"}
BOILERPLATE_METHODS = {"__str__", "__init__", "__repr__", "save", "delete",
                       "clean", "render"}
# field ky thuat auto-sinh, khong phai nghiep vu (tru khi req neu ro).
TECH_FIELDS = {"id", "pk", "objects", "app_label"}

# Node co ten bat dau bang "_" (private) -> impl helper -> loai.
def is_private(name: str) -> bool:
    return name.startswith("_") and not name.startswith("__")

# ---- Quy tac 2: TAXONOMY ----
# Heuristic gan node vao nhom taxonomy requirement (Zi et al. 4 nhom).
# Tra ve nhom hoac None (None = khong map -> ngoai phan giao).
def taxonomy_group(node):
    name = node["name"]
    kind = node["kind"]
    low = name.lower()

    # Nhom 2: Constraints & Robustness — permission, validation, filter
    if any(k in name for k in ("Permission", "IsOwner", "IsAuthenticated")):
        return "2-Constraints (permission)"
    if "permission" in low or "filter" in low or "pagination" in low:
        return "2-Constraints (rule)"
    # Nhom 4: Verification & Integration — serializer (I/O contract), auth
    if "serializer" in low:
        return "4-Integration (I/O contract)"
    # Nhom 1: Functional Spec — Entity (Model), endpoint View, CRUD method
    if kind == "class" and ("Model" in name or "Movie" in name
                            or "User" in name):
        return "1-Functional (entity)"
    if kind == "class" and ("View" in name or "ViewSet" in name):
        return "1-Functional (endpoint)"
    if kind == "field" and name not in TECH_FIELDS:
        return "1-Functional (domain field)"
    if kind == "method" and low in ("create", "list", "retrieve",
                                    "update", "destroy", "perform_create"):
        return "1-Functional (CRUD)"
    return None


BORDERLINE_HINTS = {
    "perform_create": "ky thuat NHUNG ma hoa rule 'creator = current user' (ownership)",
    "queryset": "field cau hinh NHUNG quyet dinh 'thay gi' (co the ngu y scope)",
    "creator": "vua la field vua la quan he Movie->User (edge quan trong hon field)",
    "get_queryset": "method ky thuat NHUNG co the ma hoa rule 'chi thay movie cua minh'",
}


def layer_verdict(node):
    """Tra ve (keep: bool, ly_do: str) theo Quy tac 1 LAYER."""
    name = node["name"]
    kind = node["kind"]
    if kind == "module":
        return False, "module container (khong phai don vi requirement)"
    if name in GLUE_NAMES:
        return False, "framework glue (Meta/Migration/Config)"
    if kind == "method" and name in BOILERPLATE_METHODS:
        return False, "boilerplate ngon ngu/framework"
    if is_private(name):
        return False, "private/impl helper"
    if kind == "field" and name in TECH_FIELDS:
        return False, "field ky thuat auto-sinh"
    return True, "tang requirement cham (domain/api/rule)"


def main():
    files = []
    for pat in sys.argv[1:]:
        files.extend(glob.glob(pat))
    if not files:
        files = glob.glob("output/kg_*.json")

    keep_rows = []
    drop_rows = []
    border_rows = []

    for fp in files:
        kg = json.loads(Path(fp).read_text(encoding="utf-8"))
        for node in kg["nodes"]:
            name = node["name"]
            l_keep, l_reason = layer_verdict(node)
            grp = taxonomy_group(node)
            in_join = l_keep and grp is not None

            border = name in BORDERLINE_HINTS
            row = {
                "file": Path(fp).stem.replace("kg_", ""),
                "kind": node["kind"], "name": name,
                "layer": "KEEP" if l_keep else "drop",
                "taxonomy": grp or "-",
                "verdict": "IN" if in_join else "OUT",
                "reason": l_reason if not l_keep else (grp or "khong map taxonomy"),
            }
            if border:
                row["border_note"] = BORDERLINE_HINTS[name]
                border_rows.append(row)
            if in_join:
                keep_rows.append(row)
            else:
                drop_rows.append(row)

    def pr(rows, title):
        print(f"\n===== {title} ({len(rows)}) =====")
        for r in rows:
            print(f"  [{r['verdict']}] {r['file']}.{r['name']:<22} "
                  f"({r['kind']:<8}) layer={r['layer']:<4} "
                  f"tax={r['taxonomy']:<28} :: {r['reason']}")

    pr(keep_rows, "PHAN GIAO — node VAO (G_req CO trach nhiem ngu y)")
    pr(drop_rows, "BI LOAI — ngoai phan giao")

    print(f"\n===== NODE RANH GIOI (nguon bat dong annotator -> kappa tut) "
          f"({len(border_rows)}) =====")
    for r in border_rows:
        print(f"  {r['file']}.{r['name']} [{r['verdict']}] -> {r['border_note']}")

    total = len(keep_rows) + len(drop_rows)
    print(f"\nTONG: G_code = {total} node | phan giao = {len(keep_rows)} "
          f"| loai = {len(drop_rows)} | ranh gioi = {len(border_rows)}")


if __name__ == "__main__":
    main()
