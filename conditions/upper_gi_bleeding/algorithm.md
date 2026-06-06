# Glasgow-Blatchford score

A pre-endoscopy risk score for acute upper gastrointestinal bleeding that predicts the need for hospital-based intervention (transfusion, endoscopic therapy, or surgery) or death.

Derived: Blatchford 2000 (*Lancet*). Outpatient validation: Stanley 2009 (*Lancet*). International multicentre comparison and the ≤ 1 outpatient threshold: Stanley 2017 (*BMJ*). Recommended for risk assessment in NICE CG141.

The score uses only data available at first assessment — no endoscopic findings. It uses Canadian/SI units: blood urea in mmol/L and hemoglobin in g/L.

## Components

| Component | Bands | Points |
|---|---|---|
| Blood urea (mmol/L) | 6.5–7.9 | +2 |
| | 8.0–9.9 | +3 |
| | 10.0–24.9 | +4 |
| | ≥ 25.0 | +6 |
| Hemoglobin (g/L), men | 120–129 | +1 |
| | 100–119 | +3 |
| | < 100 | +6 |
| Hemoglobin (g/L), women | 100–119 | +1 |
| | < 100 | +6 |
| Systolic BP (mmHg) | 100–109 | +1 |
| | 90–99 | +2 |
| | < 90 | +3 |
| Pulse ≥ 100/min | — | +1 |
| Presentation with melena | — | +1 |
| Presentation with syncope | — | +2 |
| Hepatic disease | — | +2 |
| Cardiac failure | — | +2 |

Total range: 0 to 23.

A score of 0 requires all of: urea < 6.5 mmol/L, hemoglobin ≥ 130 g/L (men) or ≥ 120 g/L (women), systolic BP ≥ 110 mmHg, pulse < 100, and no melena, syncope, hepatic disease, or cardiac failure.

## Interpretation

| Score | Risk band | Action |
|---|---|---|
| 0 | Very low | Outpatient management with early outpatient endoscopy may be considered, given no other reason for admission and reliable follow-up. |
| 1–5 | Intermediate | Admission generally warranted. A score of 1 falls at the validated ≤ 1 outpatient threshold (Stanley 2017) and may be managed as an outpatient with clinical judgement. |
| ≥ 6 | High | Admit, resuscitate as required, expedite endoscopy, and consider a higher-acuity setting. |

The most conservative and most validated decision is the **score-0** outpatient threshold; Stanley 2017 found **≤ 1** the optimum threshold for directing patients to outpatient management (in that low-risk group, 3.4% required hospital-based intervention or died).

## Use restrictions

The GBS does **not** diagnose the bleeding source, does not apply to lower GI bleeding, and does not apply to hemodynamically unstable patients (who warrant immediate resuscitation regardless of score). It predicts the need for intervention rather than confirming or excluding any specific pathology, and does not replace timely endoscopy.

## Implementation note

The urea, hemoglobin, and systolic BP components are computed by banding functions; the hemoglobin bands are sex-specific. The remaining five components are flat point additions. `glasgow_blatchford_assessment` also returns the contributing factors (each component that scored, with its points) so the total can be audited against each input, plus an explicit `outpatient_management_candidate` flag (true only at score 0). Negative measured values raise `ValueError`.

## Citations

Short tags map to entries in [references.bib](references.bib):

- `Blatchford 2000` — Blatchford O et al., *Lancet* 2000 (derivation).
- `Stanley 2009` — Stanley AJ et al., *Lancet* 2009 (outpatient validation).
- `Stanley 2017` — Stanley AJ et al., *BMJ* 2017 (international comparison; ≤ 1 threshold).
- `NICE CG141` — NICE, Acute upper gastrointestinal bleeding in over 16s: management.
