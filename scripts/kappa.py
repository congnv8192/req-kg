"""
Tinh Cohen's kappa giua 2 annotator (2 file CSV da dien).
  - LAYER: nhi phan KEEP/DROP
  - TAXONOMY: da lop G1-G5/NA
Dung: python kappa.py A_annotation.csv B_annotation.csv
"""
import sys
import csv


def read(path):
    d = {}
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            i = row["id"]
            layer = (row.get("layer(KEEP/DROP)") or "").strip().upper()
            taxo = (row.get("taxonomy(G1-G5/NA)") or "").strip().upper()
            d[i] = (layer, taxo)
    return d


def cohen_kappa(labels_a, labels_b):
    """labels_a, labels_b: list nhan cung thu tu."""
    n = len(labels_a)
    if n == 0:
        return None
    cats = sorted(set(labels_a) | set(labels_b))
    # observed agreement
    po = sum(1 for a, b in zip(labels_a, labels_b) if a == b) / n
    # expected
    pa = {c: labels_a.count(c) / n for c in cats}
    pb = {c: labels_b.count(c) / n for c in cats}
    pe = sum(pa[c] * pb[c] for c in cats)
    if pe == 1:
        return 1.0
    return (po - pe) / (1 - pe), po, pe


def interp(k):
    if k is None:
        return "?"
    if k < 0.2:
        return "rat thap"
    if k < 0.4:
        return "thap"
    if k < 0.6:
        return "vua (CHUA dat nguong)"
    if k < 0.8:
        return "TOT (dat >=0.6)"
    return "rat tot"


def main():
    A, B = read(sys.argv[1]), read(sys.argv[2])
    ids = [i for i in A if i in B]
    # bo cac id chua dien (rong)
    ids = [i for i in ids if A[i][0] and B[i][0]]
    print(f"So unit ca 2 da dien: {len(ids)}")
    if not ids:
        print("Chua co du lieu — 2 annotator dien layer+taxonomy truoc.")
        return

    la = [A[i][0] for i in ids]
    lb = [B[i][0] for i in ids]
    r = cohen_kappa(la, lb)
    k, po, pe = r
    print(f"\n[LAYER KEEP/DROP]  kappa = {k:.3f}  ({interp(k)})")
    print(f"   agreement quan sat={po:.2f}  ky vong={pe:.2f}")

    # taxonomy: chi tren unit ca 2 deu KEEP
    kept = [i for i in ids if A[i][0] == "KEEP" and B[i][0] == "KEEP"]
    if kept:
        ta = [A[i][1] for i in kept]
        tb = [B[i][1] for i in kept]
        rk = cohen_kappa(ta, tb)
        print(f"\n[TAXONOMY G1-G5] (tren {len(kept)} unit ca 2 KEEP)  "
              f"kappa = {rk[0]:.3f}  ({interp(rk[0])})")
    # liet ke bat dong (de review + sua codebook)
    print("\n=== BAT DONG (review de sua codebook muc 3) ===")
    for i in ids:
        if A[i] != B[i]:
            print(f"  id {i}: A={A[i]}  B={B[i]}")


if __name__ == "__main__":
    main()
