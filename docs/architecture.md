# Architecture: a queryable clinical decision-support engine

## North star

Make this repository an open-source, deterministic, citation-backed **clinical
decision-support (CDS) engine** that a clinical-note-driven assistant can query
in **near-real-time** — the reasoning layer that surfaces the right scores,
recommendations, citations, and population caveats for a primary-care case as it
is being documented.

The core stays exactly what it is today: pure, auditable, standard-library-only
functions with a published source behind every threshold. We add agent-facing
edges (an MCP server and a REST API) over a machine-readable registry, and keep
the messy, PHI-bearing part — turning a free-text note into structured inputs —
**outside** the core, in an optional adapter that the caller runs in their own
secure environment.

## Layered design

```
clinical note (PHI)              ── exists only in the caller's secure environment
   │
   ▼  extraction adapter (optional, separate; Claude-powered, caller's API key)
structured features              ── numbers / booleans / enums. NO PHI past this line.
   │
   ▼  MCP server  +  REST API     ── stateless · no storage · no input logging
   │
   ▼  dispatch / applicability     ── "which algorithms can run on these inputs?"
   │
   ▼  registry / catalog           ── per-condition JSON Schema + citations + tags
   │
   ▼  deterministic core (conditions/*)   ── pure functions, unchanged, always green
results + citations + population caveats + "missing inputs"
```

### Deterministic core — `conditions/`

Unchanged by everything above it. Pure functions over frozen dataclasses, no
third-party imports, `ValueError` on out-of-range inputs, a published citation
per threshold. This is the source of truth and must always stay green.

### Registry / catalog — `engine/registry.py`

A machine-readable catalog of every condition, **derived by introspection** of
the dataclasses (`typing.get_type_hints` + `dataclasses.fields`) — the same
technique the browser demo already uses. For each condition it exposes: a JSON
Schema of the input features (field → boolean / integer / number / enum), the
callable, the output shape, the source citations, and trigger-presentation tags.
It is the single source of truth that the demo, the MCP server, and the REST API
all consume, replacing any hand-maintained list.

### Dispatch / applicability — `engine/dispatch.py`

Given the structured inputs available for a case, returns which algorithms can
run, their results, and which need more data — optionally filtered by a
presentation tag (e.g. *chest pain* → HEART, Wells PE, PERC). Because the core
is deterministic, this is instant; latency in production comes from extraction,
not from here.

### Interfaces — `engine/mcp_server.py`, `engine/api.py`

Thin, **stateless** wrappers over the registry and dispatch:

- **MCP server** — tools (`list_conditions`, `get_condition_schema`,
  `run_algorithm`, `suggest_algorithms`) so a Claude-based clinical assistant
  can call the engine directly as a real-time tool. Agent-native.
- **REST API** (FastAPI) — the same operations over HTTP, with OpenAPI docs, for
  non-agent callers.

Both carry a *not-a-medical-device* notice in every response, store nothing, and
log no inputs.

### Extraction adapter — `adapters/` (optional, separate)

A reference, Claude-powered note → features filler that calls the engine. It is
deliberately **out of the core**: it is the only component that sees raw notes,
it depends on an LLM, and it runs with the **caller's** API key in the
**caller's** secure environment. This is where products such as Autochart.ai
integrate. Shipped as an optional extra and a worked example, never a core
dependency.

## The PHI boundary (why the core is safe)

PHI never enters the core or the interfaces. They accept only already-structured
features — discrete numbers, booleans, and enums — and they persist and log
nothing. A clinical note exists only upstream, inside the caller's extraction
adapter, within the caller's secure environment. This is enforced by the design
(structured-features-in), not by policy, which keeps the open engine free of
PHI-handling obligations while still enabling "a clinical note can query it."

## Dependency discipline

The core imports only the standard library. Every engine dependency (MCP SDK,
FastAPI, the Anthropic SDK for the adapter) is an **optional extra** in
`pyproject.toml` (`[mcp]`, `[api]`, `[adapter]`). `import conditions...` must
always work with a bare Python install.

## Build phases

| Phase | Deliverable | Risk | Merge |
|---|---|---|---|
| 0 | Algorithm coverage — keep clearing the roadmap | low | hands-off on green CI |
| 1 | `engine/registry.py` — catalog + schemas (keystone) | low | PR + human merge |
| 2 | `engine/dispatch.py` — applicability/suggestion | low | PR + human merge |
| 3 | `engine/mcp_server.py` — MCP tools | medium | PR + human merge |
| 4 | `engine/api.py` — FastAPI service | medium | PR + human merge |
| 5 | `adapters/` — reference extraction adapter | medium | PR + human merge |
| 6 | Near-real-time hardening + vignette eval harness | medium | PR + human merge |

Phase 0 runs continuously and unattended. Phases 1–6 are each deep-planned with
ultraplan on Claude Code on the web, reviewed in-browser, and executed by a
cloud Routine that opens a PR for human merge — see
[docs/autonomous-setup.md](autonomous-setup.md).

## Boundaries to respect

- The open engine (`txthedx/autonomous-care-algorithms`) is generic and
  vendor-neutral. Autochart.ai is one consumer, not part of this repo.
- The core never gains an LLM dependency, never sees a raw note, and never loses
  its "runs on the standard library, every number has a citation" identity.
