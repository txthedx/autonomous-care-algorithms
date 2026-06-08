# Extraction adapter (note → features)

The `adapters/` package is the optional bridge from a **free-text clinical note**
to the structured features the deterministic engine consumes. It is the only part
of the system that sees a raw note.

> **PHI boundary.** In production the note is sent to the model with the
> **caller's** API key, inside the **caller's** secure environment. The open
> engine never receives the note — only the structured features the adapter
> returns. The adapter stores nothing and logs nothing. See
> [docs/architecture.md](architecture.md).

## Install

The Claude extractor needs the optional `[adapter]` extra (the core stays
standard-library-only):

```bash
pip install ".[adapter]"
```

## How it works

`assess_note(note, extractor, presentation=None)`:

1. builds a union JSON Schema of the candidate conditions' features,
2. asks the `extractor` to fill what the note supports (omitting the rest),
3. runs every algorithm whose inputs are satisfied, and reports the gaps.

The extractor is injected, so the same flow runs with a deterministic extractor
(tests/examples) or with Claude (production).

## Example — deterministic (no API key)

```python
from adapters import assess_note, DictExtractor

# Pretend a note already yielded these features:
features = {
    "history": "moderately_suspicious", "ecg": "normal", "age_years": 58,
    "hypertension": True, "hypercholesterolemia": True, "diabetes_mellitus": False,
    "current_or_recent_smoking": False, "family_history_of_cad": False,
    "obesity_bmi_over_30": False, "history_of_atherosclerotic_disease": False,
    "troponin": "at_or_below_normal_limit",
}
out = assess_note("58yo with chest pain ...", DictExtractor(features),
                  presentation="chest pain")
for r in out["applicable"]:
    print(r["key"], r["result"]["score"], r["result"]["risk_band"])
# heart 3 low
```

## Example — Claude (production)

```python
from adapters import assess_note, ClaudeExtractor

note = "..."  # PHI — stays in your secure environment
out = assess_note(note, ClaudeExtractor(), presentation="chest pain")
#                            ^ uses ANTHROPIC_API_KEY from your environment
```

`ClaudeExtractor` uses tool-use to force structured output against the schema and
is instructed to **report only values the note explicitly supports** — it never
infers or assumes defaults. A pre-built client can be injected for testing.

## What you get back

```python
{
  "extracted_features": {...},        # what the extractor found
  "applicable":        [{"key","label","result"}],   # algorithms that ran
  "needs_more_data":   [{"key","label","missing_inputs"}],
  "errors":            [{"key","label","error"}],
  "disclaimer":        "Not a medical device. ...",
}
```
