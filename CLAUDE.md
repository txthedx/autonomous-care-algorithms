# CLAUDE.md — operating runbook for autonomous agents

This file is the operating procedure for any Claude Code agent working in this
repository, including unattended cloud Routines. Read it fully before acting.
The project's north star is in [docs/architecture.md](docs/architecture.md);
contributor rules are in [CONTRIBUTING.md](CONTRIBUTING.md) and
[docs/methodology.md](docs/methodology.md). This runbook does not override those
— it operationalizes them.

## What this project is

An open-source, deterministic, citation-backed clinical decision-support (CDS)
engine for common primary-care presentations. Every algorithm is a pure
function with a published source behind every threshold. It is **not a medical
device** (see [DISCLAIMER.md](DISCLAIMER.md)); outputs are scores and
recommendation bands, never diagnoses or prescriptions.

## Safety rules (non-negotiable — these gate every change)

1. **Never invent clinical facts.** Every threshold, point value, band, and
   recommendation must come from the cited primary source. Before writing any
   clinical code, **verify each value against the primary source** (PubMed-
   indexed paper or a recognized society guideline) using web search. Quote the
   exact figures you relied on in the PR description.
2. **If a value cannot be verified, do not merge.** Open the PR, comment
   explaining what could not be confirmed, apply the `clinical-review-needed`
   label, and stop. A human will finish it.
3. **Canadian/SI units** throughout (e.g., mmol/L, °C, g/L, mg/mmol). State the
   units in field names and docstrings; add a caveat about converting from
   other unit systems.
4. **Score, not diagnosis.** No drug names, doses, or routes. The module
   docstring points to `DISCLAIMER.md`. Outputs include population caveats.
5. **No PHI, ever.** No patient-identifiable data in code, tests, commits, or
   logs. The deterministic core accepts only structured features (numbers,
   booleans, enums) — never raw clinical notes. See the PHI boundary in
   [docs/architecture.md](docs/architecture.md).
6. **Identity:** commit as `txthedx <txthedx@users.noreply.github.com>` on this
   public repo. Never use any other email.

## Adding a new condition (the per-condition pattern)

Mirror the most recent module, `conditions/head_injury/`. A condition lives in
`conditions/<snake_name>/` and contains:

- `__init__.py` — re-exports the public API (`__all__` sorted).
- `<algorithm>.py` — the implementation: `from __future__ import annotations`;
  frozen `@dataclass` for the inputs (the *features*) and for the result; type
  hints everywhere; **pure functions, standard library only** (no third-party
  imports in the core); raise `ValueError` on out-of-range measured values.
  Take raw measured values (e.g. temperature, eGFR) and apply thresholds
  internally for auditability; model clinical judgements as booleans or
  `Literal` levels. Reference docstring lists the citations.
- `algorithm.md` — the rule with a citation per threshold and a short-tag →
  reference map.
- `README.md` — clinical context, scope, inputs/outputs table, a usage example.
- `references.bib` — full BibTeX for every source (with PMID and DOI). Do not
  fabricate author lists; use `and others` when unsure.
- `tests/__init__.py` and `tests/test_<algorithm>.py` — cover **every**
  criterion/branch, every band/threshold boundary, validation guards, and at
  least one worked example from the source. Use a `_DEFAULT` baseline + an
  override helper (see existing tests).

### Project-level edits required for every new condition

1. `pyproject.toml` — bump `version` (minor bump for a new condition).
2. `CITATION.cff` — bump `version` and set `date-released` (pass the date in;
   do not call `date` in a way that bakes a wrong day — use the date provided to
   the run).
3. `CHANGELOG.md` — prepend `## [x.y.z] — YYYY-MM-DD`, an `### Added` block
   describing the module, functions, sources (with PMIDs), and the new total
   test count, ending with `Closes #N.`
4. `README.md` — add a row to the "## Index of conditions" table; update the
   Status line counts (conditions / modules / tests / domains) and the
   roadmap line; add a usage example before "## Contributing".
5. `index.html` — add the demo REGISTRY entry (key, label, module, fn, folder,
   blurb, params) and the module's `.py` path(s) to `PY_FILES`. Keep entries
   alphabetic-ish by file path. *(Once `engine/registry.py` exists, prefer
   extending the registry; see Engine conventions.)*

## Engine conventions (Phases 1–6 — see docs/architecture.md)

- The deterministic core in `conditions/` stays **pure and untouched** by the
  engine layers. All query/dispatch/interface code lives under `engine/`
  (and optional `adapters/`).
- New runtime dependencies are **optional extras** in `pyproject.toml`
  (`[mcp]`, `[api]`, `[adapter]`), never core deps — the core must remain
  importable with the standard library alone.
- Feature schemas are **derived by introspection** (`typing.get_type_hints` +
  `dataclasses.fields`), not hand-written — the seed is the demo's logic in
  `index.html`. One registry is the single source of truth; the demo, MCP
  server, and REST API all consume it.
- Interfaces (MCP, REST) are **stateless**: no storage, no logging of inputs,
  a *not-a-medical-device* notice in every response.

## Ship sequence (how every change reaches main)

1. Branch: `feature/<slug>` off `main`.
2. Implement; run `.venv/bin/python -m pytest -q` (or create the venv with
   `pip install -e ".[dev]"`) until green locally.
3. Commit (identity above). Push `-u`.
4. `gh pr create` with a body that states: summary, the verified sources with
   PMIDs and the exact figures used, design notes, and the test count.
5. `gh pr checks <n> --watch` — wait for **both** Python 3.11 and 3.12 jobs.
6. **Merge policy:**
   - *Algorithm issues* (label `algorithm`, no `clinical-review-needed` blocker):
     merge on green CI — `gh pr merge <n> --merge --delete-branch` — then
     `git tag -a vX.Y.0 <hash>` + push, `gh release create`, and tick the
     issue's checkbox in roadmap **#9**.
   - *Engine/backend phases:* open the PR and **stop for human merge** (the
     ultraplan was already reviewed in-browser; the PR is the second
     checkpoint). Do not auto-merge architectural changes.
7. If CI is red or any source is unverified: do not merge; comment; label
   `clinical-review-needed`; stop.

## One issue per run

An unattended run implements the single lowest-numbered open issue labeled
`algorithm`, end to end, then stops. Do not batch.
