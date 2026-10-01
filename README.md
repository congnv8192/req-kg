# Diagnosing Knowledge Gaps in Requirement-Derived Knowledge Graphs 🔎

[![Paper](http://img.shields.io/badge/Paper-Requirement_KG_Diagnosis-99D4C8.svg)](#citation)
[![Benchmark](https://img.shields.io/badge/Benchmark-RepoGenesis-E3E4C8.svg)](https://github.com/microsoft/DKI_LLM/tree/main/RepoGenesis)
[![Python](https://img.shields.io/badge/Python-3.13-E3E4C8.svg)](https://www.python.org/)

This repository contains the scripts, prompts, model outputs, and derived data for
a study of **what knowledge a requirement actually carries** for repository-level
code generation, and of **why generated repositories fail their tests**.

A requirement-derived knowledge graph (KG) is used as a *diagnostic instrument*,
not as an input to the generator. The KG extracted from a specification is scored
against a **responsibility set** — the part of a graph reverse-engineered from a
reference implementation that a specification is expected to determine. Reading
the resulting knowledge gap together with the failing tests separates three causes
that a pass rate conflates: specification insufficiency, generator
non-conformance, and benchmark ambiguity.

> **Paper**: *Diagnosing Knowledge Gaps in Requirement-Derived Knowledge Graphs
> for Repository-Level Code Generation* — Cong Nguyen Van, Trong Hieu Tran,
> Ngoc Thanh Nguyen.

## Table of Contents

- [Overview](#overview)
- [Pipeline](#pipeline)
- [Measures](#measures)
- [Data Access](#data-access)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Experiment Workflow](#experiment-workflow)
  - [Step 1 — Cut the specification and build prompts](#step-1--cut-the-specification-and-build-prompts)
  - [Step 2 — Collect the LLM outputs](#step-2--collect-the-llm-outputs)
  - [Step 3 — Build the responsibility set](#step-3--build-the-responsibility-set)
  - [Step 4 — Run the generated services against the benchmark tests](#step-4--run-the-generated-services-against-the-benchmark-tests)
  - [Step 5 — Compute the metrics table](#step-5--compute-the-metrics-table)
- [Results](#results)
- [Repository Structure](#repository-structure)
- [Reproducibility Notes](#reproducibility-notes)
- [Citation](#citation)
- [Contact](#contact)

## Overview ⭐

Repository-level benchmarks grade generated code by running its tests. A failing
test does not say whether the specification lacked the knowledge or the generator
failed to use it, yet the two call for opposite interventions.

This study inserts a knowledge layer between the two. For each repository, the
README is reduced by rule to three nested detail levels, and each level feeds two
independent branches:

- the **knowledge branch** extracts a requirement KG and scores it against the
  responsibility set (coverage, knowledge gap, precision, consistency);
- the **generation branch** generates a service from the same text and runs the
  benchmark's black-box test suite.

**Key properties:**

- **Reference-grounded, not code-free** — the responsibility set `R` is derived
  deterministically from the reference implementation and then filtered, so a
  requirement is never penalized for failing to predict engineering decisions.
- **Two filters define `R`** — a *layer* filter (`λ`: is the element in a layer
  the specification is responsible for?) and a *taxonomy* filter (`τ`: does it
  map to a requirement content group?). Only their intersection is scored.
- **No LLM judge** — code parsing, responsibility construction, alignment, and
  every measure are deterministic scripts. The LLM appears only where the object
  of study requires it: extracting the KG and generating code.
- **No circularity** — neither the KG nor `R` enters the generation prompt, which
  carries the level text and nothing else. Passing `R` to the generator would
  leak knowledge taken from the implementation whose tests grade the output.
- **Framework-agnostic code KG** — a tree-sitter call-tree extractor, verified on
  FastAPI, Flask, Django ORM, and SQLAlchemy without framework-specific rules.

## Pipeline

```
                         ┌──────────────────┐
  README (= SRS)  ──────▶│ 1. Cut by        │──── L1 ⊂ L2 ⊂ L3
                         │    taxonomy      │        │
                         └──────────────────┘        │
                                 ┌───────────────────┴───────────────────┐
                                 ▼                                       ▼
                    ┌─────────────────────┐                  ┌─────────────────────┐
                    │ 2a. Extract G_req   │                  │ 2b. Generate code   │
                    │     (LLM, per level)│                  │     (LLM, per level)│
                    └──────────┬──────────┘                  └──────────┬──────────┘
                               │                                        │
  reference code               ▼                                        ▼
  (golden oracle)   ┌─────────────────────┐                  ┌─────────────────────┐
        │           │ 4. Align α and      │                  │ 5. Patched black-box│
        ▼           │    measure fitness  │                  │    tests → pass rate│
┌────────────────┐  └──────────┬──────────┘                  └──────────┬──────────┘
│ 3. Code KG →   │─────────────┘                                        │
│    filter λ ∩ τ│  responsibility set R                                │
└────────────────┘             └────────────► 6. compare & diagnose ◀────┘
```

Steps 1, 3, 4, 5 and 6 are deterministic. Steps 2a and 2b are the only LLM calls.

## Measures

Let `A(G_req)` be the assertions of the requirement KG, `R` the responsibility
set, and `M = α(A(G_req)) \ {⊥}` the matched units.

| Measure | Definition | Diagnostic question |
|---|---|---|
| **Coverage** | `\|M\| / \|R\|` | How much of what the specification should determine does the KG supply? |
| **Group coverage** | `\|M ∩ R_g\| / \|R_g\|` | Which knowledge categories are supplied? |
| **Knowledge gap** | `R \ M` | Which responsibility units are missing? |
| **Precision** | `\|M\| / \|A(G_req)\|` | How much of the KG is grounded in the reference? |
| **Consistency** | `V(G_req) = ∅` | Is the KG internally coherent (SHACL-style shapes)? |
| **Test pass rate** | `passed / \|Θ\|` | How much of the benchmark suite the generated service satisfies |

Content groups `G` follow the taxonomy of Zi et al. (Functional, Constraints &
Robustness, Solution Structure, Verification & Integration), extended with an
**NFR** group for system-level requirements (health checks, configuration,
logging, containerization). In the studied repositories, `R` instantiates
Functional, Constraints & Robustness, and NFR.

Precision divides by *all* assertions, not only the aligned ones: alignment
targets `R` only, so the ratio over aligned assertions alone would be 1 by
construction.

## Data Access

**The golden-oracle implementations are not redistributed here.** They are shared
by the RepoGenesis authors for non-commercial research under terms that forbid
public redistribution, training use, and mirroring in a public repository.

To reproduce the full pipeline you need:

1. **The public benchmark** — READMEs and test suites:
   <https://github.com/microsoft/DKI_LLM/tree/main/RepoGenesis>
2. **The verified golden oracles** — request them from the RepoGenesis authors,
   then place the archive at `data/RepoGenesis-Verified-GoldenOracle-v1/` so that
   the paths below resolve:

```
data/RepoGenesis-Verified-GoldenOracle-v1/
└── expert_supervised/python/
    ├── TaskManagement/{app,main.py,tests,Dockerfile,README.md}
    ├── UserManagement/{api.py,models.py,tests,...}
    └── Customization/{app,tests,...}
```

Everything that does **not** depend on the oracles — prompts, extracted KGs,
generated services, metrics, and figures — is included and can be inspected
without the archive.

## Installation

### Prerequisites

| Requirement | Version | Purpose |
|---|---|---|
| Python | 3.13 | Analysis scripts and execution harness |
| LLM access | Any chat or API model | KG extraction and code generation |

Two virtual environments are used, because the analysis side and the execution
side have conflicting dependencies.

```bash
# analysis: parsing, metrics, figures
python -m venv .venv
.venv/Scripts/activate            # Linux/macOS: source .venv/bin/activate
pip install tree-sitter tree-sitter-python tree-sitter-java python-docx

# execution: run the generated services and the benchmark tests
python -m venv .venv-run
.venv-run/Scripts/activate
pip install fastapi uvicorn flask flask-sqlalchemy pytest requests
```

All commands below are run from the repository root with `.venv` active, unless
stated otherwise. Set `PYTHONIOENCODING=utf-8` on Windows for clean console
output.

## Quick Start

The committed outputs are enough to reproduce every number and figure in the
paper without re-running the LLM:

```bash
# metrics table (coverage, group coverage, precision, gap, pass rate)
python scripts/metrics_groups.py
cat output/metrics_groups.json
```

The figures of the paper are included as rendered artifacts under `output/`
(`fig2_fitness`, `fig3_category`, `fig4_conformance`, in SVG, PDF and PNG). They
are drawn from `output/metrics_groups.json`, so every value in them can be
checked against that file.

## Experiment Workflow

### Step 1 — Cut the specification and build prompts

`prompt_gen.py` reduces a README to three nested levels and writes six prompts
per repository (three for KG extraction, three for code generation):

```bash
python scripts/prompt_gen.py \
    data/RepoGenesis-Verified-GoldenOracle-v1/expert_supervised/python/TaskManagement \
    req 8080
```

| Level | Content kept |
|---|---|
| `L1` | first paragraph of the functionality description (the task goal) |
| `L2` | functionality, API endpoints, data-model field *names*; constraint lines, technical/deployment sections and error formats removed |
| `L3` | the complete README |

The cut is rule-based deletion from a fixed source, so the levels are nested by
construction and the manipulation is reproducible.

### Step 2 — Collect the LLM outputs

Each prompt is sent to the model once, and the answers are saved under
`llm-answers/`:

| File | Content |
|---|---|
| `<prefix>_req{1,2,3}.json` | requirement KG per level (entities, attributes, operations, relations, thresholds, NFR statements) |
| `<prefix>_code_L{1,2,3}.py` | single-file service generated from the same level text |
| `<prefix>_code_L2NFR.py` | ablation variant: `L2` plus the NFR block, field constraints withheld |

The prefixes used in the paper are `req` (TaskManagement), `um_req`
(UserManagement) and `cust_req` (Customization).

### Step 3 — Build the responsibility set

`general_gold.py` reverse-engineers the reference implementation with tree-sitter
and applies the layer and taxonomy filters:

```bash
python scripts/general_gold.py \
    data/RepoGenesis-Verified-GoldenOracle-v1/expert_supervised/python/TaskManagement
# → output/gold_TaskManagement.json
```

The result maps each responsibility unit to one of five kinds: `FR-endpoint`,
`FR-validation`, `enum`, `threshold`, `NFR-struct`. Use `intersection.py` to
inspect which elements a filter keeps or drops and why.

### Step 4 — Run the generated services against the benchmark tests

The benchmark harness contains two artifacts that make failures cascade
independently of the implementation under test: a clean-up fixture that assumes
list responses are wrapped in an object, and a health-check gate that skips every
dependent test when `/health` is missing. `patch_tests.py` neutralizes both
identically for every level, touching no assertion:

```bash
python scripts/patch_tests.py <repo_dir>          # → output/tests_patched_<Repo>/
python scripts/run_repo.py <repo_dir> <prefix> <port>
# → output/repo_<Repo>.json  (coverage, pass counts, Spearman ρ)
```

`run_repo.py` starts each generated service with uvicorn, waits for the health
endpoint, runs pytest, and kills the process tree. Use `run_passk.py` for a
single service or `run_all_passk.py` for a batch.

### Step 5 — Compute the metrics table

```bash
python scripts/metrics_groups.py      # → output/metrics_groups.json
```

Each record holds `cov`, `cov_g` (per content group), `prec`, `violations`, the
full `gap` list, and the pass counts, for one repository and level.

## Results

Reproduced by `scripts/metrics_groups.py` (`|R|` split into Functional /
Constraints & Robustness / NFR units):

| Repository | Level | Cov | Cov_F | Cov_C | Cov_N | Prec | Gap | Pass rate |
|---|---|---|---|---|---|---|---|---|
| TaskMgmt. (27: 7/15/5) | L1 | 0.19 | 0.71 | 0.00 | 0.00 | 0.62 | 22 | 6/44 (0.14) |
| | L2 | 0.26 | 0.86 | 0.00 | 0.20 | 0.44 | 20 | 7/44 (0.16) |
| | L3 | 0.78 | 0.86 | 0.67 | 1.00 | 0.70 | 6 | 31/44 (0.70) |
| UserMgmt. (21: 8/8/5) | L1 | 0.24 | 0.62 | 0.00 | 0.00 | 0.38 | 16 | 0/69 (0.00) |
| | L2 | 0.33 | 0.75 | 0.00 | 0.20 | 0.29 | 14 | 7/69 (0.10) |
| | L3 | 0.86 | 0.75 | 0.88 | 1.00 | 0.42 | 3 | 24/69 (0.35) |
| Customiz. (38: 33/2/3) | L1 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 38 | 1/64 (0.02) |
| | L2 | 0.11 | 0.12 | 0.00 | 0.00 | 0.15 | 34 | 4/64 (0.06) |
| | L3 | 0.24 | 0.12 | 1.00 | 1.00 | 0.21 | 29 | 10/64 (0.16) |

All nine KGs satisfy every consistency constraint. The ablation
(`output/passk_3source_canonical.json`) decomposes the gain from `L2` to `L3`:
field-level constraints account for 43 of the 47 tests gained, the NFR block for
4, with inconsistent sign across repositories.

## Repository Structure

```
req-kg/
├── scripts/
│   ├── prompt_gen.py           # README → L1/L2/L3 → six prompts per repository
│   ├── reverse_kg.py           # Python → code KG (tree-sitter, deterministic)
│   ├── reverse_kg_java.py      # Java variant of the extractor
│   ├── general_gold.py         # code KG → responsibility set R (layer ∩ taxonomy)
│   ├── intersection.py         # inspect which units a filter keeps or drops
│   ├── general_score.py        # alignment rules α: assertions → units of R
│   ├── metrics_full.py         # SHACL-style consistency + implicit-coverage profile
│   ├── metrics_groups.py       # the metrics table used in the paper
│   ├── general_metrics.py      # earlier multi-repository table
│   ├── patch_tests.py          # neutralize the two harness artifacts
│   ├── run_passk.py            # start service → health → pytest → kill
│   ├── run_all_passk.py        # batch variant
│   ├── run_repo.py             # end-to-end: coverage + pass rate + ρ per repository
│   ├── correlate_passk.py      # coverage ↔ pass-rate correlations
│   ├── diag_passk.py           # per-test diagnosis of a run
│   └── score_*.py              # phase-0 hand-coded scorers (superseded)
├── prompts/                    # the exact prompts sent to the model
├── llm-answers/                # requirement KGs and generated services
├── output/                     # gold sets, metrics, pass-rate runs, rendered figures
└── data/                       # benchmark inputs (oracles not redistributed)
```

## Reproducibility Notes

- **Alignment tie-breaking.** When the threshold and endpoint rules find several
  candidate units, the current implementation takes the first candidate found
  while iterating a set, so the choice depends on `PYTHONHASHSEED`. In
  Customization this moves one matched unit at `L2` and one at `L3` (coverage
  0.08 or 0.11, and 0.21 or 0.24). `metrics_groups.py` pins the seed so the
  reported table is reproducible; neither the order of the levels nor any
  correlation changes under the alternative resolution.
- **Lexical alignment.** Rules compare identifiers, not meaning. A unit can stay
  in the gap although the specification states it, for example
  `VALID_PRIORITIES` against the attribute `priority`. Coverage is therefore a
  lower bound; of the 38 units missing at `L3`, 23 are of this kind.
- **Single sample.** One generation and one extraction per level. Differences of
  a few units or tests lie within model noise.
- **Reference dependence.** `R` comes from one reference implementation, which
  for these three repositories was produced by a model under expert supervision.
  The layer filter can still admit infrastructure: in Customization, 14 of 33
  functional units are application factories or dependency providers.

## Citation

If you find this repository useful, please cite the paper and the benchmark:

```bibtex
@inproceedings{nguyen2027reqkg,
  title     = {Diagnosing Knowledge Gaps in Requirement-Derived Knowledge Graphs
               for Repository-Level Code Generation},
  author    = {Nguyen Van, Cong and Tran, Trong Hieu and Nguyen, Ngoc Thanh},
  year      = {2027},
  note      = {Under review}
}

@inproceedings{peng2026repogenesis,
  title     = {RepoGenesis: Benchmarking End-to-End Microservice Generation from
               Readme to Repository},
  author    = {Peng, Zhiyuan and Yin, X. and Zhao, P. and others},
  booktitle = {Proc. ACL, Long Papers},
  year      = {2026}
}
```

## Acknowledgements

We sincerely thank the RepoGenesis authors for generously sharing
the verified golden-oracle implementations, which supported our experiments and
analysis in this work.

## Contact

For questions about this work, please contact: `congnv24@fe.edu.vn`.
