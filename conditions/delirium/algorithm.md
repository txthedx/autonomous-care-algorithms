# 4AT delirium screen

A four-item bedside instrument for rapid delirium screening in older adults.

Source: Bellelli 2014 (*Age Ageing*), validated against DSM-IV in 234 hospitalised older people. Subsequent large-scale diagnostic accuracy evidence: Shenkin 2019 (*BMC Med*). Endorsed by SIGN, NICE, and the European Delirium Association.

The four items are **A**lertness, the **A**MT4 orientation test, **A**ttention, and **A**cute change — hence "4 A's Test".

## Items and scoring

| Item | Response | Points |
|---|---|---|
| 1. Alertness | Normal (fully alert, or mild sleepiness < 10 s after waking then normal) | 0 |
| | Clearly abnormal (markedly drowsy, stuporous, or agitated/hyperactive) | 4 |
| 2. AMT4 (age, date of birth, place, current year) | No mistakes | 0 |
| | 1 mistake | 1 |
| | 2 or more mistakes, or untestable | 2 |
| 3. Attention (months of the year backwards from December) | 7 months or more correct | 0 |
| | Starts but < 7 months, or refuses to start | 1 |
| | Untestable (cannot start because unwell, drowsy, or inattentive) | 2 |
| 4. Acute change or fluctuating course | No | 0 |
| | Yes (change/fluctuation in the last 2 weeks, still evident in last 24 h) | 4 |

Total range: 0 to 12. Items 1 and 4 are scored 0 or 4; items 2 and 3 are scored 0, 1, or 2.

## Interpretation

| Score | Band | Meaning |
|---|---|---|
| 0 | Unlikely | Delirium and moderate-to-severe cognitive impairment unlikely |
| 1–3 | Possible cognitive impairment | Possible moderate-to-severe cognitive impairment, more likely chronic than delirium |
| ≥ 4 | Possible delirium | Possible delirium, with or without cognitive impairment |

The 3/4 cut-off was **pre-specified in the design** of the instrument rather than derived statistically (Bellelli 2014).

## Use restrictions

The 4AT is a **screen, not a diagnostic test**. A score of 4 or above indicates possible delirium and warrants a full clinical assessment — identifying and treating precipitants and reviewing medications — not an automatic diagnosis. A single application does not distinguish delirium from dementia; the trajectory of change, serial assessment, and collateral history are essential, and item 4 depends on reliable baseline information. Where that information is missing, a low score does not exclude delirium. The instrument was validated in hospitalised older adults.

## Implementation note

Each item is entered as a named response level (a boolean for item 4), and the module maps responses to points. `four_at_assessment` also returns the per-item breakdown (`FourATComponentScores`) so the total can be audited against each item. Because items 1 and 4 each contribute 4 points, either one alone produces a "possible delirium" band.

## Citations

Short tags map to entries in [references.bib](references.bib):

- `Bellelli 2014` — Bellelli G et al., *Age Ageing* 2014 (derivation and validation).
- `Shenkin 2019` — Shenkin SD et al., *BMC Med* 2019 (multicentre diagnostic accuracy).
