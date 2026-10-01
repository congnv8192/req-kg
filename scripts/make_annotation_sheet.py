"""
Sinh phieu gan kappa: reverse-KG cac repo -> gom MOI unit ung vien (node) ->
mau ngau nhien phan tang -> CSV cho 2 annotator dien (layer KEEP/DROP + taxonomy).

Dung: python make_annotation_sheet.py <n_sample> <repo_dir1> <repo_dir2> ...
Xuat: output/annotation_sheet.csv (2 annotator copy ra A_.csv, B_.csv de dien)
Cot: id, repo, file, kind, name, context | layer(dien), taxonomy(dien), note(dien)
"""
import sys
import csv
import json
import random
import subprocess
from pathlib import Path
from collections import defaultdict

random.seed(42)
BASE = Path(".").resolve()
RK = str(BASE / "scripts" / "reverse_kg.py")
VENV = str(BASE / ".venv" / "Scripts" / "python.exe")


def candidates(repo_dir: Path):
    tmp = repo_dir / "_kgtmp_ann"
    tmp.mkdir(exist_ok=True)
    out = []
    pys = [p for p in repo_dir.rglob("*.py")
           if "test" not in str(p).lower() and "__init__" not in p.name
           and "_kgtmp" not in str(p)]
    for py in pys:
        o = tmp / (py.stem + ".json")
        subprocess.run([VENV, RK, str(py), "--out", str(o)],
                       capture_output=True)
        if not o.exists():
            continue
        kg = json.loads(o.read_text(encoding="utf-8"))
        for n in kg["nodes"]:
            if n["kind"] == "module":
                continue
            ctx = ""
            if n.get("enum"):
                ctx = "enum=" + str(n["enum"])[:40]
            elif n.get("fieldtype"):
                ctx = "type=" + n["fieldtype"]
            elif n.get("constraints"):
                ctx = "constr=" + str(n["constraints"])[:40]
            out.append({"repo": repo_dir.name, "file": py.name,
                        "kind": n["kind"], "name": n["name"], "context": ctx})
    for f in tmp.glob("*.json"):
        f.unlink()
    try:
        tmp.rmdir()
    except Exception:
        pass
    return out


def main():
    n_sample = int(sys.argv[1])
    repos = [Path(a) for a in sys.argv[2:]]
    allc = []
    for r in repos:
        allc += candidates(r)
    # phan tang theo kind -> lay ti le
    by_kind = defaultdict(list)
    for c in allc:
        by_kind[c["kind"]].append(c)
    sample = []
    total = len(allc)
    for kind, items in by_kind.items():
        k = max(1, round(n_sample * len(items) / total))
        sample += random.sample(items, min(k, len(items)))
    random.shuffle(sample)
    sample = sample[:n_sample]

    out = Path("output/annotation_sheet.csv")
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "repo", "file", "kind", "name", "context",
                    "layer(KEEP/DROP)", "taxonomy(G1-G5/NA)", "note"])
        for i, c in enumerate(sample, 1):
            w.writerow([i, c["repo"], c["file"], c["kind"], c["name"],
                        c["context"], "", "", ""])
    print(f"SAVED {out} — {len(sample)} unit (tu {total} ung vien, "
          f"{len(repos)} repo)")
    print("Phan tang theo kind:",
          {k: sum(1 for c in sample if c['kind'] == k) for k in by_kind})
    print("\n2 annotator: copy annotation_sheet.csv -> A_annotation.csv + "
          "B_annotation.csv, dien 2 cot layer+taxonomy DOC LAP (theo codebook).")


if __name__ == "__main__":
    main()
