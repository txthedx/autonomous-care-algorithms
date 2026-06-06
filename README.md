# autonomous-care-algorithms

[![tests](https://github.com/txthedx/autonomous-care-algorithms/actions/workflows/tests.yml/badge.svg)](https://github.com/txthedx/autonomous-care-algorithms/actions/workflows/tests.yml)
[![Latest release](https://img.shields.io/github/v/release/txthedx/autonomous-care-algorithms?sort=semver)](https://github.com/txthedx/autonomous-care-algorithms/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![DOI-ready](https://img.shields.io/badge/cite-CITATION.cff-orange.svg)](CITATION.cff)
[![Live demo](https://img.shields.io/badge/demo-try%20in%20browser-2da44e.svg)](https://txthedx.github.io/autonomous-care-algorithms/)

Open-source, citation-backed clinical decision algorithms for the most common primary care presentations. Implementations follow published scoring systems and society guidelines, with every clinical rule traceable to a primary reference.

> **▶ Try it in your browser:** [txthedx.github.io/autonomous-care-algorithms](https://txthedx.github.io/autonomous-care-algorithms/) — an interactive demo that runs the actual algorithm source via Pyodide (WebAssembly). No install, no server, and no data leaves your device.

## Status

Active. Sixteen conditions are implemented (21 algorithm modules, 654 passing tests), spanning infectious, cardiovascular, thromboembolic, musculoskeletal, gastrointestinal, neurologic, geriatric, trauma, and renal presentations. The roadmap targets the 50 most common primary care presenting complaints, prioritized by frequency in Canadian and US family practice.

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
| Pulmonary embolism (Wells PE + PERC) | [conditions/pulmonary_embolism](conditions/pulmonary_embolism) | Wells 2000, 2001; Kline 2004, 2008; ESC 2019 | Implemented |
| Chest pain (HEART score) | [conditions/chest_pain](conditions/chest_pain) | Six 2008; Backus 2013; Mahler 2015 | Implemented |
| Upper GI bleeding (Glasgow-Blatchford) | [conditions/upper_gi_bleeding](conditions/upper_gi_bleeding) | Blatchford 2000; Stanley 2009, 2017; NICE CG141 | Implemented |
| Appendicitis (Alvarado / MANTRELS) | [conditions/appendicitis](conditions/appendicitis) | Alvarado 1986; Ohle 2011 | Implemented |
| Syncope (San Francisco Syncope Rule) | [conditions/syncope](conditions/syncope) | Quinn 2004, 2006; Sun 2007; Birnbaum 2008 | Implemented |
| Chronic kidney disease (KDIGO staging) | [conditions/chronic_kidney_disease](conditions/chronic_kidney_disease) | KDIGO 2024; KDIGO 2012 | Implemented |
| Delirium (4AT screen) | [conditions/delirium](conditions/delirium) | Bellelli 2014; Shenkin 2019 | Implemented |
| Cervical-spine trauma (NEXUS, Canadian C-Spine) | [conditions/cervical_spine_trauma](conditions/cervical_spine_trauma) | Hoffman 2000; Stiell 2001, 2003 | Implemented |

The remaining 34 are tracked in [issue #9 — roadmap](https://github.com/txthedx/autonomous-care-algorithms/issues/9). Suggestions for the next high-priority rules are welcome — open an issue or see [CONTRIBUTING.md](CONTRIBUTING.md).

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

Use the chest pain module (HEART score for 6-week MACE risk):

```python
from conditions.chest_pain import HeartFeatures, heart_assessment

features = HeartFeatures(
    history="moderately_suspicious",
    ecg="normal",
    age_years=58,
    hypertension=True,
    hypercholesterolemia=True,
    diabetes_mellitus=False,
    current_or_recent_smoking=False,
    family_history_of_cad=False,
    obesity_bmi_over_30=False,
    history_of_atherosclerotic_disease=False,
    troponin="at_or_below_normal_limit",
)
result = heart_assessment(features)
print(result.score, result.risk_band, result.recommended_disposition)
```

Use the upper GI bleeding module (Glasgow-Blatchford score; SI units):

```python
from conditions.upper_gi_bleeding import (
    GlasgowBlatchfordFeatures,
    glasgow_blatchford_assessment,
)

features = GlasgowBlatchfordFeatures(
    sex="male",
    urea_mmol_per_l=5.0,
    hemoglobin_g_per_l=150.0,
    systolic_bp_mmhg=120,
    pulse_per_minute=80,
    melena=False,
    syncope=False,
    hepatic_disease=False,
    cardiac_failure=False,
)
result = glasgow_blatchford_assessment(features)
print(result.score, result.risk_band, result.outpatient_management_candidate)
```

Use the appendicitis module (Alvarado score; SI units):

```python
from conditions.appendicitis import AlvaradoFeatures, alvarado_assessment

features = AlvaradoFeatures(
    migration_of_pain_to_rlq=True,
    anorexia=True,
    nausea_or_vomiting=True,
    tenderness_in_rlq=True,
    rebound_tenderness=False,
    temperature_celsius=37.6,
    white_cell_count_x10e9_per_l=12.5,
    neutrophil_percent=80.0,
)
result = alvarado_assessment(features)
print(result.score, result.risk_band, result.recommended_disposition)
```

Use the syncope module (San Francisco Syncope Rule; CHESS):

```python
from conditions.syncope import SfsrFeatures, sfsr_assessment

features = SfsrFeatures(
    congestive_heart_failure_history=False,
    hematocrit_percent=42.0,
    abnormal_ecg=True,
    shortness_of_breath=False,
    systolic_bp_mmhg=128,
)
result = sfsr_assessment(features)
print(result.high_risk, result.risk_band, result.positive_criteria)
```

Use the chronic kidney disease module (KDIGO staging; SI units):

```python
from conditions.chronic_kidney_disease import KdigoFeatures, kdigo_assessment

features = KdigoFeatures(
    egfr_ml_min_1_73m2=35.0,
    acr_mg_per_mmol=12.0,
    persistent_over_3_months=True,
)
result = kdigo_assessment(features)
print(result.stage_label, result.risk_band, result.nephrology_referral_indicated)
```

Use the delirium module (4AT screen):

```python
from conditions.delirium import FourATFeatures, four_at_assessment

features = FourATFeatures(
    alertness="normal",
    amt4="one_mistake",
    attention_months_backwards="fewer_than_seven_or_refuses",
    acute_change_or_fluctuating_course=True,
)
result = four_at_assessment(features)
print(result.score, result.interpretation_band)
```

Use the cervical-spine trauma module (NEXUS and the Canadian C-Spine Rule):

```python
from conditions.cervical_spine_trauma import (
    CanadianCSpineFeatures,
    canadian_c_spine_assessment,
)

features = CanadianCSpineFeatures(
    age_65_or_older=False,
    dangerous_mechanism=False,
    paresthesias_in_extremities=False,
    simple_rear_end_mvc=False,
    sitting_position_in_ed=False,
    ambulatory_at_any_time=True,
    delayed_onset_of_neck_pain=False,
    absence_of_midline_c_spine_tenderness=False,
    able_to_rotate_neck_45_degrees=True,
)
result = canadian_c_spine_assessment(features)
print(result.imaging_indicated, result.determining_step)
```

## Contributing

Clinical contributions require a primary source citation (peer-reviewed paper or recognized society guideline). Implementation contributions require tests covering scoring boundaries. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE). Citations and clinical text remain attributable to their original authors.

## Maintainer

[txthedx](https://github.com/txthedx). Clinical correspondence and erratum reports are welcome via issues.
