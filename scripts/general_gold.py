"""
Gold TONG QUAT cho 1 repo (de scale nhieu repo, khong hard-code tung repo).

reverse-KG toan bo code -> loc phan giao (layer + taxonomy) -> canonical gold units:
  node:<endpoint-fn>     (CRUD/endpoint function)
  node:<validate-fn>     (validation rule function)
  enum:<CONST>           (module-level enum tuple)
  const:<CONFIG>         (threshold/config field UPPER_CASE)
  nfr:<file>             (file/module ma hoa NFR: validators/errors/health/config...)

Dung: python general_gold.py <repo_dir>   -> in gold + phan loai
"""
import sys
import json
import subprocess
from pathlib import Path
import importlib.util

_BASE = Path(__file__).resolve().parents[1]
RK = str(_BASE / "scripts" / "reverse_kg.py")
VENV = str(_BASE / ".venv" / "Scripts" / "python.exe")

# ten file -> NFR-structural category (tong quat, theo quy uoc dat ten)
NFR_FILES = {
    "validators": "nfr:validation", "validator": "nfr:validation",
    "errors": "nfr:error-handling", "error": "nfr:error-handling",
    "exceptions": "nfr:error-handling",
    "health": "nfr:health-check",
    "config": "nfr:config", "settings": "nfr:config",
    "logging": "nfr:logging", "logger": "nfr:logging",
    "auth": "nfr:auth", "security": "nfr:auth", "permissions": "nfr:auth",
}
# ten ham endpoint/CRUD (tong quat)
CRUD_HINTS = ("create", "list", "get", "retrieve", "update", "delete",
              "post", "put", "patch", "remove", "add", "fetch", "health",
              "login", "register", "search", "index")
CONFIG_FIELD_HINTS = ("LIMIT", "MAX", "LENGTH", "SIZE", "PREFIX", "VERSION",
                      "TIMEOUT", "PORT")  # bo HOST/DEFAULT_PAGE (ha tang)
# LAYER drop: ha tang/glue/db — khong phai don vi requirement
LAYER_DROP = {"create_app", "get_connection", "get_db", "db_session",
              "reset_database", "init_db", "close", "startup", "shutdown",
              "main", "run"}


def _is_infra(low: str) -> bool:
    return ("_connection" in low or "_all_" in low or low.startswith("get_db")
            or low.endswith("_db") or "session" in low or "factory" in low)


def kg_of(pyfile, outdir):
    out = outdir / (Path(pyfile).stem + ".json")
    subprocess.run([VENV, RK, str(pyfile), "--out", str(out)],
                   capture_output=True)
    return json.loads(out.read_text(encoding="utf-8")) if out.exists() else \
        {"nodes": [], "edges": []}


def build_gold(repo_dir: Path):
    repo_dir = repo_dir.resolve()
    tmp = repo_dir / "_kgtmp"
    tmp.mkdir(exist_ok=True)
    pyfiles = [p for p in repo_dir.rglob("*.py")
               if "test" not in str(p).lower() and "__init__" not in p.name
               and "_kgtmp" not in str(p)]
    gold = {}   # unit -> category

    def add(u, cat):
        gold[u] = cat

    for py in pyfiles:
        stem = py.stem.lower()
        kg = kg_of(py, tmp)
        # NFR-structural: file ten khop quy uoc
        for key, cat in NFR_FILES.items():
            if key == stem or key in stem:
                add(cat, "NFR-struct")
                break
        for n in kg["nodes"]:
            name, kind = n["name"], n["kind"]
            low = name.lower()
            if kind in ("function", "method"):
                if low.startswith("validate") or low.startswith("valid_"):
                    # bo aggregate validator (validate_create_payload...) —
                    # chi giu validate_<field> (luat tung field)
                    if not low.endswith("_payload"):
                        add(f"node:{name}", "FR-validation")
                elif low in LAYER_DROP or any(low.endswith(s) or low.startswith(p)
                        for s, p in ()) or _is_infra(low):
                    pass  # LAYER: bo ha tang/glue
                elif any(h in low for h in CRUD_HINTS) and not low.startswith("_"):
                    add(f"node:{name}", "FR-endpoint")
            elif kind == "const" and n.get("enum"):
                add(f"enum:{name}", "enum")
            elif kind == "field" and name.isupper():
                if any(h in name for h in CONFIG_FIELD_HINTS):
                    add(f"const:{name}", "threshold")
    # non-code artifacts (reverse-KG khong thay): Dockerfile -> containerization
    if (repo_dir / "Dockerfile").exists() or list(repo_dir.glob("**/Dockerfile")):
        add("nfr:containerization", "NFR-struct")
    # don tmp
    for f in tmp.glob("*.json"):
        f.unlink()
    try:
        tmp.rmdir()
    except Exception:
        pass
    return gold


def main():
    repo = Path(sys.argv[1])
    gold = build_gold(repo)
    from collections import Counter
    cats = Counter(gold.values())
    print(f"REPO: {repo.name}")
    print(f"GOLD = {len(gold)} unit | theo cat: {dict(cats)}")
    for cat in ("FR-endpoint", "FR-validation", "enum", "threshold",
                "NFR-struct"):
        us = sorted(u for u, c in gold.items() if c == cat)
        if us:
            print(f"  [{cat}] {us}")
    # luu
    out = Path(f"output/gold_{repo.name}.json")
    out.write_text(json.dumps(gold, indent=2, ensure_ascii=False),
                   encoding="utf-8")
    print(f"SAVED {out}")


if __name__ == "__main__":
    main()
