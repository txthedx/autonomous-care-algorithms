# NEWS2 (National Early Warning Score 2)

Aggregate physiological score for detecting and responding to acute deterioration in adults. Source: Royal College of Physicians, NEWS2 (RCP 2017).

## Parameters

**Respiration rate (/min):** ≤8 → 3; 9–11 → 1; 12–20 → 0; 21–24 → 2; ≥25 → 3.

**SpO₂ Scale 1 (%):** ≤91 → 3; 92–93 → 2; 94–95 → 1; ≥96 → 0.

**SpO₂ Scale 2 (%)** (hypercapnic respiratory failure, target 88–92%):
≤83 → 3; 84–85 → 2; 86–87 → 1; 88–92 → 0; on air ≥93 → 0; on oxygen 93–94 → 1, 95–96 → 2, ≥97 → 3.

**Air or oxygen:** air → 0; any supplemental oxygen → 2.

**Systolic BP (mmHg):** ≤90 → 3; 91–100 → 2; 101–110 → 1; 111–219 → 0; ≥220 → 3.

**Pulse (/min):** ≤40 → 3; 41–50 → 1; 51–90 → 0; 91–110 → 1; 111–130 → 2; ≥131 → 3.

**Consciousness (ACVPU):** Alert → 0; new Confusion or Voice/Pain/Unresponsive → 3.

**Temperature (°C):** ≤35.0 → 3; 35.1–36.0 → 1; 36.1–38.0 → 0; 38.1–39.0 → 1; ≥39.1 → 2.

## Clinical response (aggregate)

| Aggregate | Band | Response |
|---|---|---|
| 0 | low | Routine monitoring |
| 1–4 (no parameter = 3) | low | Ward-based assessment |
| any single parameter = 3 | low-medium | Urgent clinician review (red score) |
| 5–6 | medium | Urgent review by a clinician |
| ≥ 7 | high | Emergency assessment, critical-care competencies |

A single parameter scoring 3 (a "red score") triggers urgent review even at a low aggregate.

## Use restrictions

Validated in adults; not for children (under 16) or pregnancy. SpO₂ Scale 2 is only for confirmed hypercapnic (type 2) respiratory failure with an agreed 88–92% target. Clinical judgement overrides the score.

## Implementation note

Vitals are entered as raw values; all bands are applied internally. SpO₂ scoring depends on the chosen scale and, for Scale 2 at ≥ 93%, on whether the patient is on supplemental oxygen. `news2_assessment` returns the per-parameter breakdown, the aggregate, a red-score flag, the monitoring band, and the response. Out-of-range values raise `ValueError`.

## Citations

- `RCP 2017` — Royal College of Physicians, *NEWS2* 2017.
