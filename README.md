# autonomous-care-algorithms

[![tests](https://github.com/txthedx/autonomous-care-algorithms/actions/workflows/tests.yml/badge.svg)](https://github.com/txthedx/autonomous-care-algorithms/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

Open-source, citation-backed clinical decision algorithms for the most common primary care presentations. Implementations follow published scoring systems and society guidelines, with every clinical rule traceable to a primary reference.

## Status

Early-stage. The first implemented algorithm is **acute pharyngitis** (Centor / McIsaac scoring, IDSA 2012-aligned interpretation). The roadmap targets the 50 most common primary care presenting complaints, prioritized by frequency in Canadian and US family practice.

> **Important: This is not a medical device.** This software does not provide medical advice, diagnosis, or treatment. It is provided for research, education, and discussion. See [DISCLAIMER.md](DISCLAIMER.md) before using or referencing this code in any clinical context.

## Why this exists

Most "AI in primary care" projects either generate unsourced advice or wrap proprietary guideline content. The goal here is the opposite: small, deterministic, auditable implementations of algorithms that are already published, with citations baked into the code and tests.

Each algorithm aims to be:

1. **Traceable** — every threshold, point, and recommendation cites a peer-reviewed paper or society guideline.
2. **Testable** — pure functions with unit tests covering published scoring boundaries.
3. **Versioned** — when a guideline updates, the algorithm version increments and the changelog records the source.
4. **Bounded** — outputs are scores and recommendation bands, not diagnoses or prescriptions.

See [docs/methodology.md](docs/methodology.md) for how algorithms are sourced, reviewed, and versioned.

## Index of conditions

| Condition | Folder | Source | Status |
|---|---|---|---|
| Acute pharyngitis | [conditions/pharyngitis](conditions/pharyngitis) | McIsaac 1998, 2004; IDSA 2012 | Implemented |
| Acute and subacute low back pain | [conditions/low_back_pain](conditions/low_back_pain) | Downie 2013; Hill 2008, 2011; NICE NG59 | Implemented |
| Community-acquired pneumonia (severity) | [conditions/pneumonia](conditions/pneumonia) | Lim 2003; BTS 2009; NICE NG138 | Implemented |
| Atrial fibrillation (stroke and bleeding risk) | [conditions/atrial_fibrillation](conditions/atrial_fibrillation) | Lip 2010; Pisters 2010; ESC 2020; CCS 2020 | Implemented |
| Uncomplicated UTI in women | [conditions/urinary_tract_infection](conditions/urinary_tract_infection) | Bent 2002; Gupta 2011 (IDSA); NICE NG109 | Implemented |
| Acute ankle and midfoot injury | [conditions/ankle_injury](conditions/ankle_injury) | Stiell 1992, 1993; Bachmann 2003 | Implemented |
| Acute knee injury | [conditions/knee_injury](conditions/knee_injury) | Stiell 1995, 1996; Bachmann 2004 | Implemented |
| Deep vein thrombosis (Wells score) | [conditions/deep_vein_thrombosis](conditions/deep_vein_thrombosis) | Wells 1997; Wells 2003; Scarvelis 2006 | Implemented |

The remaining 42 are tracked in [issue #9 — roadmap](https://github.com/txthedx/autonomous-care-algorithms/issues/9), with individual issues open for the next high-priority published rules: Wells PE + PERC, HEART score, NEXUS / Canadian C-Spine, KDIGO CKD, and Glasgow-Blatchford UGI bleeding score.

## Quick start

```bash
git clone https://github.com/txthedx/autonomous-care-algorithms.git
cd autonomous-care-algorithms
pip install -e ".[dev]"
pytest
```

Use the pharyngitis module:

```python
from conditions.pharyngitis import PharyngitisFeatures, mcisaac_recommendation

features = PharyngitisFeatures(
    age_years=28,
    history_of_fever=True,
    tonsillar_exudate=True,
    tender_anterior_cervical_nodes=True,
    no_cough=True,
)
rec = mcisaac_recommendation(features)
print(rec.score, rec.action, rec.citations)
```

Use the low back pain modules:

```python
from conditions.low_back_pain import (
    StartBackResponses,
    start_back_stratification,
)

responses = StartBackResponses(
    leg_pain_in_last_2_weeks=True,
    shoulder_or_neck_pain_in_last_2_weeks=False,
    walked_only_short_distances=True,
    dressed_more_slowly=False,
    not_safe_to_be_physically_active=True,
    worrying_thoughts_a_lot=True,
    pain_is_terrible_never_better=False,
    not_enjoying_usual_things=True,
    bothersomeness="moderately",
)
result = start_back_stratification(responses)
print(result.risk_band, result.recommended_management)
```

Use the pneumonia severity module (CRB-65 in primary care, CURB-65 with labs):

```python
from conditions.pneumonia import Crb65Features, crb_65_assessment

features = Crb65Features(
    age_years=72,
    confusion=False,
    respiratory_rate_per_minute=24,
    systolic_bp_mmhg=110,
    diastolic_bp_mmhg=70,
)
result = crb_65_assessment(features)
print(result.score, result.severity_band, result.recommended_disposition)
```

Use the atrial fibrillation modules (CHA₂DS₂-VASc for stroke risk, HAS-BLED for bleeding risk):

```python
from conditions.atrial_fibrillation import (
    Cha2ds2VascFeatures,
    cha2ds2_vasc_assessment,
)

features = Cha2ds2VascFeatures(
    age_years=72,
    sex="female",
    congestive_heart_failure=False,
    hypertension=True,
    diabetes=True,
    prior_stroke_tia_or_thromboembolism=False,
    vascular_disease=False,
)
result = cha2ds2_vasc_assessment(features)
print(result.score, result.recommended_anticoagulation)
```

Use the UTI module (Bent 2002 decision rule for uncomplicated cystitis in women):

```python
from conditions.urinary_tract_infection import (
    UtiComplicatingFactors,
    UtiPresentingFeatures,
    uti_assessment,
)

symptoms = UtiPresentingFeatures(
    dysuria=True,
    urinary_frequency=True,
    hematuria=False,
    suprapubic_or_back_pain=False,
    vaginal_discharge=False,
    vaginal_irritation=False,
)
factors = UtiComplicatingFactors(
    pregnancy=False,
    male=False,
    diabetes_uncontrolled_or_immunocompromise=False,
    indwelling_catheter_or_recent_instrumentation=False,
    known_urinary_tract_abnormality=False,
    recent_antibiotic_use=False,
    symptoms_more_than_7_days=False,
    recurrent_uti=False,
    flank_pain_or_fever_or_systemic_symptoms=False,
)
result = uti_assessment(symptoms, factors)
print(result.pretest_probability_band, result.recommended_action)
```

Use the ankle injury module (Ottawa Ankle Rule):

```python
from conditions.ankle_injury import (
    AnkleAssessmentFeatures,
    ApplicabilityFactors,
    ottawa_ankle_assessment,
)

features = AnkleAssessmentFeatures(
    pain_in_malleolar_zone=True,
    tender_lateral_malleolus_distal_6cm=False,
    tender_medial_malleolus_distal_6cm=False,
    unable_to_bear_weight_immediately_and_now=True,
)
applicability = ApplicabilityFactors(
    age_under_18=False,
    intoxication=False,
    distracting_injury=False,
    decreased_sensation_or_neurologic_deficit=False,
    gross_deformity=False,
    isolated_skin_injury=False,
    head_injury_or_decreased_consciousness=False,
)
result = ottawa_ankle_assessment(features, applicability)
print(result.imaging_indicated, result.indicating_criteria)
```

## Contributing

Clinical contributions require a primary source citation (peer-reviewed paper or recognized society guideline). Implementation contributions require tests covering scoring boundaries. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE). Citations and clinical text remain attributable to their original authors.

## Maintainer

[txthedx](https://github.com/txthedx). Clinical correspondence and erratum reports are welcome via issues.
