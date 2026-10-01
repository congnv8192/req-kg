"""
T1-Java — Reverse Java code -> KG (deterministic, tree-sitter, NO LLM).

Nodes: file(class/interface), method, field
Edges: contains, has_method, has_field, param_type (method -> type ngu y quan he)

Muc dich: kiem trace link muc-FILE cua eTour co du min cho phan giao khong,
hay KG-code muc-method giau hon han gold link muc-file.

Chay: python reverse_kg_java.py <file.java> [--out out.json]
"""
import sys
import json
import argparse
from pathlib import Path
from collections import Counter

from tree_sitter import Parser, Language
import tree_sitter_java as tsjava


def build_parser():
    return Parser(Language(tsjava.language()))


def text(node, src):
    return src[node.start_byte:node.end_byte].decode("utf-8", "replace")


def field(node, name):
    return node.child_by_field_name(name)


class JavaKG:
    def __init__(self, src, module):
        self.src = src
        self.nodes = {}
        self.edges = []
        self.module_id = self._add(module, "file", module, line=1)

    def _add(self, nid, kind, name, qualified=None, line=None, **extra):
        if nid not in self.nodes:
            self.nodes[nid] = {"id": nid, "kind": kind, "name": name,
                               "qualified": qualified or nid, "line": line,
                               **extra}
        return nid

    def _edge(self, s, d, t):
        self.edges.append({"src": s, "dst": d, "type": t})

    def walk(self, root):
        for n in self._iter(root):
            if n.type in ("class_declaration", "interface_declaration"):
                self._class(n)

    def _iter(self, node):
        stack = [node]
        while stack:
            n = stack.pop()
            yield n
            stack.extend(n.children)

    def _class(self, node):
        nm = field(node, "name")
        name = text(nm, self.src) if nm else "<anon>"
        kind = "interface" if node.type == "interface_declaration" else "class"
        cid = self._add(name, kind, name, name, node.start_point[0] + 1)
        self._edge(self.module_id, cid, "contains")
        body = field(node, "body")
        if body is None:
            return
        for ch in body.children:
            if ch.type == "method_declaration":
                self._method(ch, cid, name)
            elif ch.type == "field_declaration":
                self._field(ch, cid, name)

    def _method(self, node, cid, cname):
        nm = field(node, "name")
        if nm is None:
            return
        name = text(nm, self.src)
        mid = f"{cname}.{name}"
        rtype = field(node, "type")
        rt = text(rtype, self.src) if rtype else None
        self._add(mid, "method", name, mid, node.start_point[0] + 1,
                  returns=rt)
        self._edge(cid, mid, "has_method")
        # param types -> ngu y quan he (Bean/Type nghiep vu)
        params = field(node, "parameters")
        if params is not None:
            for p in params.children:
                if p.type == "formal_parameter":
                    pt = field(p, "type")
                    if pt is not None:
                        tname = text(pt, self.src)
                        self._edge(mid, f"type:{tname}", "param_type")

    def _field(self, node, cid, cname):
        ftype = field(node, "type")
        ft = text(ftype, self.src) if ftype else None
        for ch in node.children:
            if ch.type == "variable_declarator":
                nm = field(ch, "name")
                if nm is not None:
                    fname = text(nm, self.src)
                    fid = f"{cname}.{fname}"
                    self._add(fid, "field", fname, fid,
                              node.start_point[0] + 1, fieldtype=ft)
                    self._edge(cid, fid, "has_field")

    def result(self):
        return {"nodes": list(self.nodes.values()), "edges": self.edges}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    path = Path(args.file)
    src = path.read_bytes()
    parser = build_parser()
    tree = parser.parse(src)
    kg = JavaKG(src, path.stem)
    kg.walk(tree.root_node)
    r = kg.result()
    kinds = Counter(n["kind"] for n in r["nodes"])
    etypes = Counter(e["type"] for e in r["edges"])
    print(f"FILE: {path.name}")
    print(f"NODES: {len(r['nodes'])}  {dict(kinds)}")
    print(f"EDGES: {len(r['edges'])}  {dict(etypes)}")
    out = args.out or str(path.with_suffix(".kg.json"))
    Path(out).write_text(json.dumps(r, indent=2, ensure_ascii=False),
                         encoding="utf-8")
    print(f"SAVED: {out}")


if __name__ == "__main__":
    main()
