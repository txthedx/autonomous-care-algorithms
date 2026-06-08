# Alcohol withdrawal: CIWA-Ar

The **CIWA-Ar** (Sullivan 1989) quantifies alcohol withdrawal severity from ten rater-scored items (nine 0–7, orientation 0–4; total 0–67) to guide symptom-triggered therapy.

Requires a cooperative, communicative patient; unreliable in delirium or communication barriers. The score that triggers medication and the agent used are set by local protocol; bands here are the commonly used interpretation. See [DISCLAIMER.md](../../DISCLAIMER.md).

## Bands

| Score | Band |
|---|---|
| < 8 | minimal |
| 8–15 | mild to moderate |
| 16–20 | moderate to severe |
| > 20 | severe |

## Inputs

`CiwaArFeatures`: nine items (0–7) — `nausea_vomiting`, `tremor`, `paroxysmal_sweats`, `anxiety`, `agitation`, `tactile_disturbances`, `auditory_disturbances`, `visual_disturbances`, `headache_fullness_in_head` — plus `orientation_clouding_of_sensorium` (0–4).

## Usage

```python
from conditions.alcohol_withdrawal import CiwaArFeatures, ciwa_ar_assessment
r = ciwa_ar_assessment(CiwaArFeatures(nausea_vomiting=2, tremor=4, paroxysmal_sweats=3,
    anxiety=3, agitation=2, tactile_disturbances=1, auditory_disturbances=0,
    visual_disturbances=0, headache_fullness_in_head=1, orientation_clouding_of_sensorium=1))
print(r.score, r.severity_band)
```

See [algorithm.md](algorithm.md), [references.bib](references.bib), and [tests/](tests/).
