"""
T1 — Reverse code -> Knowledge Graph (deterministic, tree-sitter, NO LLM).

Trich cau truc code Python thanh KG gold:
  Nodes: module, class, method, function, field (class attribute / self.x)
  Edges: contains (module->class/func), has_method (class->method),
         has_field (class->field), calls (method/func -> callee name)

Chay: python reverse_kg.py <file.py> [--out out.json]
Xuat KG dang JSON (nodes, edges) + in thong ke.
"""
import sys
import json
import argparse
from pathlib import Path

from tree_sitter import Parser, Language
import tree_sitter_python as tspython

# Bat/tat che do call-tree tong quat (nguyen tac CPG) qua CLI --calltree.
CALLTREE_MODE = False


def build_parser() -> Parser:
    lang = Language(tspython.language())
    return Parser(lang)


def text(node, src: bytes) -> str:
    return src[node.start_byte:node.end_byte].decode("utf-8", "replace")


def child_field(node, field: str):
    return node.child_by_field_name(field)


class KGExtractor:
    def __init__(self, src: bytes, module_name: str):
        self.src = src
        self.nodes = {}   # id -> {id, kind, name, qualified, line}
        self.edges = []   # {src, dst, type}
        self.module_id = self._add(module_name, "module", module_name,
                                   line=1)

    def _add(self, node_id, kind, name, qualified=None, line=None):
        if node_id not in self.nodes:
            self.nodes[node_id] = {
                "id": node_id, "kind": kind, "name": name,
                "qualified": qualified or node_id, "line": line,
            }
        return node_id

    def _edge(self, s, d, t):
        self.edges.append({"src": s, "dst": d, "type": t})

    def extract(self, root):
        self._walk_module(root, self.module_id, prefix="")

    def _walk_module(self, node, parent_id, prefix):
        for child in node.children:
            if child.type == "class_definition":
                self._handle_class(child, parent_id, prefix)
            elif child.type == "function_definition":
                self._handle_function(child, parent_id, prefix,
                                      is_method=False)
            elif child.type == "decorated_definition":
                # bo decorator, xu ly dinh nghia ben trong
                inner = child.child_by_field_name("definition")
                if inner is None:
                    for c in child.children:
                        if c.type in ("class_definition",
                                      "function_definition"):
                            inner = c
                            break
                if inner and inner.type == "class_definition":
                    self._handle_class(inner, parent_id, prefix)
                elif inner and inner.type == "function_definition":
                    self._handle_function(inner, parent_id, prefix,
                                          is_method=False)
            elif child.type == "expression_statement":
                # module-level constant -> co the la ENUM NGAM
                # (VALID_PRIORITIES = ("low","medium","high"))
                self._handle_module_const(child, parent_id)

    def _handle_module_const(self, expr_stmt, module_id):
        """Bat hang module-level la UPPER_CASE gan tuple/list/set literal
        -> node kind='const' voi attribute 'enum' (cac gia tri).
        Day la luat ngam kieu enum, hay bi requirement bo. KHONG parse
        logic than ham (dat, nhieu) — chi bat const khai bao truc tiep."""
        for child in expr_stmt.children:
            if child.type != "assignment":
                continue
            left = child_field(child, "left")
            right = child_field(child, "right")
            if left is None or right is None or left.type != "identifier":
                continue
            name = text(left, self.src)
            if not (name.isupper() and "_" in name or name.isupper()):
                continue
            if right.type in ("tuple", "list", "set"):
                vals = []
                for el in right.children:
                    if el.type in ("string", "integer", "float", "true",
                                   "false", "identifier"):
                        vals.append(text(el, self.src).strip("\"'"))
                if vals:
                    cid = f"const:{name}"
                    self._add(cid, "const", name, cid,
                              child.start_point[0] + 1)
                    self.nodes[cid]["enum"] = vals
                    self._edge(module_id, cid, "defines_enum")

    def _handle_class(self, node, parent_id, prefix):
        name_n = child_field(node, "name")
        name = text(name_n, self.src) if name_n else "<anon>"
        qual = f"{prefix}{name}"
        cid = self._add(qual, "class", name, qual, node.start_point[0] + 1)
        self._edge(parent_id, cid, "contains")

        # LAYER cua class: doc superclass -> quyet dinh co enrich field khong.
        # Chi Model-layer (ke thua models.Model/Model) moi la dinh nghia field
        # nghiep vu; field o View/Serializer chi la GAN GIA TRI cau hinh.
        supers = self._superclasses(node)
        is_model = any(s.endswith("Model") for s in supers)
        self.nodes[cid]["bases"] = supers
        self.nodes[cid]["is_model"] = is_model

        body = child_field(node, "body")
        if body is None:
            return
        for child in body.children:
            if child.type == "function_definition":
                self._handle_function(child, cid, f"{qual}.",
                                      is_method=True, class_id=cid)
            elif child.type == "decorated_definition":
                inner = child.child_by_field_name("definition")
                if inner and inner.type == "function_definition":
                    self._handle_function(inner, cid, f"{qual}.",
                                          is_method=True, class_id=cid)
            elif child.type == "expression_statement":
                # class-level assignment -> field
                self._handle_class_field(child, cid, qual,
                                         enrich=is_model)

    def _superclasses(self, class_node):
        supers = []
        args = child_field(class_node, "superclasses")
        if args is not None:
            for a in args.children:
                if a.type in ("identifier", "attribute"):
                    supers.append(text(a, self.src))
        return supers

    def _handle_class_field(self, expr_stmt, class_id, class_qual,
                            enrich=False):
        for child in expr_stmt.children:
            if child.type == "assignment":
                left = child_field(child, "left")
                if left and left.type == "identifier":
                    fname = text(left, self.src)
                    fid = f"{class_qual}.{fname}"
                    self._add(fid, "field", fname, fid,
                              child.start_point[0] + 1)
                    self._edge(class_id, fid, "has_field")
                    # LAM GIAU chi cho Model-layer field (enrich=True):
                    # trich RHS -> field type + constraint + FK relation.
                    # Field o View/Serializer khong enrich (tranh nhieu
                    # order_by/all tu chuoi call cau hinh).
                    right = child_field(child, "right")
                    if right is not None:
                        if CALLTREE_MODE:
                            # TONG QUAT: emit call-tree cho MOI field co RHS la
                            # call — KHONG gate theo is_model (do la bias Django).
                            if right.type == "call":
                                root_call = self._emit_call_tree(fid, right)
                                self._edge(fid, root_call, "invokes")
                        elif enrich:
                            # CU: dien giai Django-specific (chi Model-layer)
                            self._enrich_field(fid, fname, right, class_id)

    def _enrich_field(self, fid, fname, rhs, class_id):
        """Trich field type (PositiveInteger...), constraint kwargs (max_length,
        required...) va quan he ForeignKey/OneToOne -> edge relates_to."""
        if rhs.type != "call":
            return
        callee = child_field(rhs, "function")
        if callee is None:
            return
        ftype = text(callee, self.src)          # vd models.PositiveIntegerField
        short = ftype.rsplit(".", 1)[-1]        # PositiveIntegerField
        self.nodes[fid]["fieldtype"] = short    # attribute cua field node

        args = child_field(rhs, "arguments")
        if args is None:
            return
        constraints = {}
        rel_target = None
        for a in args.children:
            if a.type == "keyword_argument":
                k = child_field(a, "name")
                v = child_field(a, "value")
                if k is not None and v is not None:
                    constraints[text(k, self.src)] = text(v, self.src)
            elif a.type in ("identifier", "attribute", "string"):
                # positional arg dau cua ForeignKey(User, ...) = target
                if rel_target is None and short in (
                        "ForeignKey", "OneToOneField", "ManyToManyField"):
                    rel_target = text(a, self.src).strip("\"'")
        if constraints:
            self.nodes[fid]["constraints"] = constraints
        # quan he -> edge relates_to (luat ngam nam o EDGE, khong o node name)
        if rel_target:
            tgt = f"rel:{rel_target}"
            self._add(tgt, "class", rel_target, rel_target)
            self._edge(class_id, tgt, "relates_to")
            self.nodes[fid]["relation"] = f"{short}->{rel_target}"

    # ---- CALL-TREE TONG QUAT (nguyen tac CPG/Kythe: emit cau truc, KHONG
    #      dien giai ten framework). Dung cho MOI framework. ----
    def _emit_call_tree(self, parent_id, expr_node, depth=0):
        """De quy emit call/literal/ref thanh node + has_arg edge.
        KHONG biet Django/SQLAlchemy la gi — chi ghi cau truc cu phap.
        Tra ve node_id cua expr (de cha noi has_arg)."""
        t = expr_node.type
        if t == "call":
            callee = child_field(expr_node, "function")
            cname = text(callee, self.src) if callee else "<anon>"
            short = cname.rsplit(".", 1)[-1]
            cid = f"{parent_id}~call:{short}#{expr_node.start_byte}"
            self._add(cid, "call", short, cname,
                      expr_node.start_point[0] + 1)
            # Canh noi cha->cid do CALLER quyet (invokes cho field->call goc,
            # has_arg cho call->call long nhau) — tranh canh trung.
            args = child_field(expr_node, "arguments")
            if args is not None:
                idx = 0
                for a in args.children:
                    if a.type in ("(", ")", ","):
                        continue
                    if a.type == "keyword_argument":
                        k = child_field(a, "name")
                        v = child_field(a, "value")
                        if k is not None and v is not None:
                            child_id = self._emit_call_tree(cid, v, depth + 1)
                            self._edge_kw(cid, child_id, "has_arg",
                                          arg_name=text(k, self.src))
                    elif a.type not in ("comment",):
                        child_id = self._emit_call_tree(cid, a, depth + 1)
                        self._edge_kw(cid, child_id, "has_arg", arg_index=idx)
                        idx += 1
            return cid
        elif t in ("integer", "float", "string", "true", "false", "none"):
            val = text(expr_node, self.src).strip("\"'")
            lid = f"{parent_id}~lit:{val}#{expr_node.start_byte}"
            self._add(lid, "literal", val, val, expr_node.start_point[0] + 1)
            return lid
        elif t in ("identifier", "attribute"):
            ref = text(expr_node, self.src)
            rid = f"ref:{ref}#{expr_node.start_byte}"
            self._add(rid, "ref", ref, ref, expr_node.start_point[0] + 1)
            return rid
        else:
            oid = f"{parent_id}~expr#{expr_node.start_byte}"
            self._add(oid, "expr", t, t, expr_node.start_point[0] + 1)
            return oid

    def _edge_kw(self, s, d, t, **kw):
        e = {"src": s, "dst": d, "type": t}
        e.update(kw)
        self.edges.append(e)

    def _handle_function(self, node, parent_id, prefix, is_method,
                         class_id=None):
        name_n = child_field(node, "name")
        name = text(name_n, self.src) if name_n else "<anon>"
        qual = f"{prefix}{name}"
        kind = "method" if is_method else "function"
        fid = self._add(qual, kind, name, qual, node.start_point[0] + 1)
        edge_type = "has_method" if is_method else "contains"
        self._edge(parent_id, fid, edge_type)

        body = child_field(node, "body")
        if body is None:
            return
        # trich: self.x = ...  (field); loi goi ham (calls)
        self._scan_body(body, fid, class_id, class_qual=prefix.rstrip("."))

    def _scan_body(self, node, func_id, class_id, class_qual):
        for child in _iter_descendants(node):
            # self.x = ...  -> field cua class
            if child.type == "assignment":
                left = child_field(child, "left")
                if left and left.type == "attribute":
                    obj = child_field(left, "object")
                    attr = child_field(left, "attribute")
                    if (obj and text(obj, self.src) == "self"
                            and attr and class_id):
                        fname = text(attr, self.src)
                        fid = f"{class_qual}.{fname}"
                        self._add(fid, "field", fname, fid,
                                  child.start_point[0] + 1)
                        self._edge(class_id, fid, "has_field")
            # loi goi ham -> calls (luu ten callee, chua resolve)
            elif child.type == "call":
                callee = child_field(child, "function")
                if callee is not None:
                    cname = text(callee, self.src)
                    # chi giu ten ngan gon
                    self._edge(func_id, f"call:{cname}", "calls")
                    # LAM GIAU: keyword-arg cua call lo luat ngam NGHIEP VU.
                    # CHI giu khi gia tri la truy cap NGU CANH RUNTIME
                    # (request.user, self.x) -> luat nhu ownership.
                    # BO literal (required=True, 200, "x") -> tham so ky thuat,
                    # khong phai luat nghiep vu (tranh nhieu).
                    args = child_field(child, "arguments")
                    if args is not None:
                        for a in args.children:
                            if a.type == "keyword_argument":
                                k = child_field(a, "name")
                                v = child_field(a, "value")
                                if (k is not None and v is not None
                                        and _is_runtime_ctx(v, self.src)):
                                    kv = f"{text(k, self.src)}={text(v, self.src)}"
                                    self._edge(func_id, f"arg:{kv}",
                                               "sets_arg")

    def result(self):
        return {"nodes": list(self.nodes.values()), "edges": self.edges}


def _iter_descendants(node):
    stack = list(node.children)
    while stack:
        n = stack.pop()
        yield n
        stack.extend(n.children)


# goc truy cap runtime ma luat nghiep vu hay tham chieu.
_RUNTIME_ROOTS = {"request", "self", "g", "current_user", "session"}


def _is_runtime_ctx(value_node, src) -> bool:
    """True neu value la attribute-access bat re tu ngu canh runtime
    (request.user, self.request.user, g.user). False cho literal
    (True/200/"x") va bien local don gian -> loc nhieu sets_arg."""
    if value_node.type != "attribute":
        return False
    # di xuong den object goc cung nhat
    node = value_node
    while node.type == "attribute":
        node = node.child_by_field_name("object")
        if node is None:
            return False
    if node.type == "call":
        node = node.child_by_field_name("function")
        while node is not None and node.type == "attribute":
            node = node.child_by_field_name("object")
    if node is None or node.type != "identifier":
        return False
    return src[node.start_byte:node.end_byte].decode("utf-8", "replace") \
        in _RUNTIME_ROOTS


def main():
    global CALLTREE_MODE
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--out", default=None)
    ap.add_argument("--calltree", action="store_true",
                    help="emit call-tree tong quat (nguyen tac CPG) thay vi "
                         "dien giai Django-specific")
    args = ap.parse_args()
    CALLTREE_MODE = args.calltree

    path = Path(args.file)
    src = path.read_bytes()
    module_name = path.stem

    parser = build_parser()
    tree = parser.parse(src)

    ex = KGExtractor(src, module_name)
    ex.extract(tree.root_node)
    kg = ex.result()

    # thong ke
    from collections import Counter
    kinds = Counter(n["kind"] for n in kg["nodes"])
    etypes = Counter(e["type"] for e in kg["edges"])
    print(f"FILE: {path.name}")
    print(f"NODES: {len(kg['nodes'])}  {dict(kinds)}")
    print(f"EDGES: {len(kg['edges'])}  {dict(etypes)}")

    out = args.out or str(path.with_suffix(".kg.json"))
    Path(out).write_text(json.dumps(kg, indent=2, ensure_ascii=False),
                         encoding="utf-8")
    print(f"SAVED: {out}")


if __name__ == "__main__":
    main()
