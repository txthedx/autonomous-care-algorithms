# REST API

The engine can run as a FastAPI HTTP service — the same operations as the
[MCP server](mcp.md), for non-agent callers. Stateless: nothing is stored and no
inputs are logged; a *not-a-medical-device* disclaimer rides on every result.

## Install and run

FastAPI is an optional extra (the core stays standard-library-only):

```bash
pip install ".[api]"
uvicorn "engine.api:create_app" --factory
# or
python -m engine.api
```

Interactive OpenAPI docs are served at `/docs`.

## Endpoints

| Method & path | Purpose |
|---|---|
| `GET /` | Service info + disclaimer |
| `GET /conditions` | Catalog (key, label, presentations) |
| `GET /presentations` | Presentation tags |
| `GET /conditions/{condition}` | A condition's full record |
| `GET /conditions/{condition}/schema` | JSON Schema of a condition's inputs |
| `POST /conditions/{condition}/run` | Run one algorithm; body = the features object |
| `POST /suggest` | Body `{features, presentation?}` → ranked applicability |
| `POST /run-applicable` | Body `{features, presentation?}` → run everything satisfied |

`POST /conditions/{condition}/run` returns `200 {"result": ..., "disclaimer": ...}`
on success, `404` for an unknown condition, and `422` with
`{"errors": [...], "missing_inputs": [...]}` for missing or rejected inputs.

## Example

```bash
curl -s localhost:8000/conditions/heart/run -H 'content-type: application/json' -d '{
  "history": "moderately_suspicious", "ecg": "normal", "age_years": 58,
  "hypertension": true, "hypercholesterolemia": true, "diabetes_mellitus": false,
  "current_or_recent_smoking": false, "family_history_of_cad": false,
  "obesity_bmi_over_30": false, "history_of_atherosclerotic_disease": false,
  "troponin": "at_or_below_normal_limit"
}'
# {"result": {"score": 3, "risk_band": "low", ...}, "disclaimer": "Not a medical device. ..."}
```

## Boundary

The API accepts only **structured features** (numbers, booleans, enums) — never
raw clinical notes. Note→features extraction is the optional adapter (Phase 5),
which runs in the caller's secure environment. See
[docs/architecture.md](architecture.md).
