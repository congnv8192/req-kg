"""
Sinh 6 prompt (greq L1/L2/L3 + code L1/L2/L3) cho 1 repo RepoGenesis, TU DONG
cat muc tu README theo taxonomy. README RepoGenesis co cau truc section nhat quan.

Cat:
  L1 = section "Functionality Description" (Task Goal)
  L2 = Functionality + API endpoints + Data Model (CHI ten field, bo constraint)
       -> bo Technical Spec + Deployment (NFR) + Error format + constraint chi tiet
  L3 = README day du

Dung: python prompt_gen.py <repo_dir> <prefix> <port>
  vd: python prompt_gen.py .../simple-rbac-service rbac 8082
"""
import sys
import re
from pathlib import Path

repo = Path(sys.argv[1]).resolve()
prefix = sys.argv[2]
port = sys.argv[3]
readme = (repo / "README.md").read_text(encoding="utf-8")
outdir = Path("prompts")
outdir.mkdir(exist_ok=True)


def section(name, text):
    """Lay noi dung 1 section ## <name> ... den ## tiep theo."""
    m = re.search(rf"^#+\s*{re.escape(name)}.*?$(.*?)(?=^#+\s|\Z)",
                  text, re.M | re.S | re.I)
    return m.group(1).strip() if m else ""


def find_section_header(patterns, text):
    for p in patterns:
        m = re.search(rf"(^#+\s*{p}.*?$.*?)(?=^#+\s*(?:Technical|Deployment|Error|Non-Functional)\b|\Z)",
                      text, re.M | re.S | re.I)
        if m:
            return m.group(1)
    return ""


# L1 = Functionality/Overview/Description section (thu nhieu ten header)
func = ""
for h in ("Functionality Description", "Functional Requirements",
          "Description", "Project Overview", "Overview", "Functionality"):
    func = section(h, readme)
    if func:
        break
# lay doan van dau (bo sub-bullet neu la Functional Requirements dang list)
para = [p for p in func.split("\n\n") if p.strip() and not p.strip().startswith("#")]
L1 = para[0].strip() if para else (func or readme[:600]).strip()

# L2 = Functionality + API endpoints (KHONG schema/constraint) + Data Model
#      (chi ten field). Strip: ```json``` blocks, Input/Output Schema, Port line.
api_part = find_section_header(["API Definition", "API Interfaces", "API"],
                               readme)
data_part = section("Data Model", readme)
# 1. bo moi block ```...``` (schema JSON = mang constraint)
api_l = re.sub(r"```.*?```", "", api_part, flags=re.S)
# 2. bo dong Input/Output Schema, Listening Port, Content Type, Query param detail
drop = re.compile(r"^\s*[-*]?\s*\*?\*?(Input Schema|Output Schema|Listening Port|"
                  r"Content Type|Base Path|Headers|Query Parameters?)\b.*$", re.I)
api_l = "\n".join(l for l in api_l.splitlines() if not drop.match(l))
# 2b. bo dong mang CONSTRAINT (enum/max/min/default/required/optional len...)
#     -> L2 chi con endpoint signature + function, khong constraint
cdrop = re.compile(r"(enum:|max:|min:|max_?length|min_?length|default:|"
                   r"required\)|optional,|characters|alphanumeric|valid email|"
                   r"ISO 8601|unique\b)", re.I)
api_l = "\n".join(l for l in api_l.splitlines() if not cdrop.search(l))
# 3. gom dong trong lien tiep
api_light = re.sub(r"\n{3,}", "\n\n", api_l).strip()
# data model: chi ten field
data_stripped = re.sub(r"^(\s*[-*]\s*`?(\w+)`?).*$", r"- \2",
                       data_part, flags=re.M) if data_part else ""
L2 = (f"{func}\n\nAPI Endpoints (base path /api/v1):\n{api_light}"
      f"\n\nData model fields:\n{data_stripped}").strip()

# L3 = full README
L3 = readme.strip()

LEVELS = {"L1": L1, "L2": L2, "L3": L3}

GREQ_HEAD = """You are a requirements analyst. Extract ONLY the structured information the requirement EXPLICITLY STATES or DIRECTLY IMPLIES. Do NOT invent details. Output STRICTLY a single JSON object in the schema below — no prose, no fences.

========== REQUIREMENT (Level {lvl}) ==========
{body}
========== END REQUIREMENT ==========

Schema (include a key only if supported; use [] or null when nothing applies):
{{
  "entities": ["<entity>"],
  "attributes": [{{"name":"<field>","type":"<type|null>","required":<bool|null>,"max_length":<int|null>,"min_length":<int|null>,"enum":[<values>]|null,"default":"<value|null>","unique":<bool|null>}}],
  "operations": [{{"method":"<GET|POST|PUT|DELETE|null>","path":"<path|null>","action":"<create|list|retrieve|update|delete|login|reset_password|health|other>"}}],
  "relations": [{{"from":"<entity>","to":"<entity>","kind":"<relation>"}}],
  "thresholds": [{{"name":"<e.g. port, max_page_size>","value":<number|string>}}],
  "nfr": [{{"category":"<validation|error_handling|logging|health_check|deployment|configuration|containerization|auth|migration>","detail":"<short>"}}]
}}

Rules: extract at the level of detail the requirement provides. Do NOT add constraints (enum, lengths, port) unless the text states them. Return ONLY the JSON.
"""

CODE_HEAD = """You are a senior backend engineer. Implement the microservice described below as a SINGLE self-contained Python file.

Hard constraints:
- Framework: FastAPI. Expose the app as module-level `app`. Runnable with `uvicorn main:app --host 127.0.0.1 --port {port}`. Include `if __name__ == "__main__":` running uvicorn on 127.0.0.1:{port}.
- Base path prefix /api/v1. In-memory storage. Output ONLY the Python code — no fences, no explanation.

Implement EXACTLY what the requirement states — no more. If a constraint, error format, or validation rule is not specified, do NOT invent one.

========== REQUIREMENT (Level {lvl}) ==========
{body}
========== END REQUIREMENT ==========

Output ONLY the Python code for main.py.
"""

for lvl, body in LEVELS.items():
    (outdir / f"{prefix}_greq_{lvl}.md").write_text(
        GREQ_HEAD.format(lvl=lvl, body=body), encoding="utf-8")
    (outdir / f"{prefix}_code_{lvl}.md").write_text(
        CODE_HEAD.format(lvl=lvl, body=body, port=port), encoding="utf-8")
    print(f"  {prefix}_greq_{lvl}.md ({len(body)} chars) + {prefix}_code_{lvl}.md")

print(f"\nDONE — 6 prompts in prompts/ for {repo.name} (prefix={prefix}, port={port})")
print(f"L1={len(L1)}c  L2={len(L2)}c  L3={len(L3)}c")
