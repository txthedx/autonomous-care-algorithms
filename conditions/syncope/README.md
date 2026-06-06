# Syncope: San Francisco Syncope Rule (CHESS)

The **San Francisco Syncope Rule (SFSR)** (Quinn 2004) identifies patients presenting with syncope or near-syncope who are at risk of a **short-term serious outcome**. It is a binary rule built on the **CHESS** mnemonic: if any one criterion is present, the patient is classified as high risk.

## Clinical context

Syncope is a common ED presentation with a wide range of causes, from benign vasovagal episodes to life-threatening arrhythmia or hemorrhage. The SFSR structures the disposition decision: patients with none of the five criteria are low risk and may be considered for outpatient evaluation, while any positive criterion flags a patient who warrants admission or monitored observation with further cardiac evaluation.

A "serious outcome" in the derivation means death, myocardial infarction, arrhythmia, pulmonary embolism, stroke, subarachnoid hemorrhage, significant hemorrhage, or a return ED visit and admission for a related event.

## Scope of this module

- Evaluates the five **CHESS** criteria and returns whether **any** is present (`high_risk`).
- Returns the **positive criteria**, the risk band (low / high), a narrative disposition, and population caveats.

It does **not**:

- Diagnose the cause of syncope.
- Apply to syncope clearly attributable to a non-cardiac cause (e.g., seizure, intoxication, hypoglycemia).
- Serve as a discharge guarantee; it is a screening aid (see the validation caveats below).
- Produce a numeric score — the SFSR is a binary rule, not a points sum.

See [DISCLAIMER.md](../../DISCLAIMER.md).

## Criteria (CHESS)

| Letter | Criterion | Positive when |
|---|---|---|
| **C** | Congestive heart failure history | history present |
| **H** | Hematocrit | < 30% |
| **E** | Abnormal ECG | any new change or non-sinus rhythm |
| **S** | Shortness of breath | symptom present |
| **S** | Systolic blood pressure (at triage) | < 90 mmHg |

**Any one positive → high risk.**

## Units

Hematocrit is entered as a **percentage** (e.g., 29.0). The module applies the < 30% and < 90 mmHg thresholds. Convert if local results report hematocrit as a fraction (e.g., 0.29).

## Performance and validation

The derivation (Quinn 2004) reported about 96% sensitivity and 62% specificity for serious outcomes, and the authors' prospective validation (Quinn 2006) about 98% sensitivity. Independent external validations have reported **lower sensitivity** (Sun 2007; Birnbaum 2008). The rule should be used as a screening aid alongside clinical judgement, not as a stand-alone discharge guarantee.

## Inputs

| Input | Type |
|---|---|
| `congestive_heart_failure_history` | bool |
| `hematocrit_percent` | float |
| `abnormal_ecg` | bool |
| `shortness_of_breath` | bool |
| `systolic_bp_mmhg` | int |

## Outputs

- `high_risk` (bool — True if any criterion present).
- `positive_criteria` (tuple of labels for the criteria present).
- `risk_band` (`"low"` or `"high"`).
- `recommended_disposition`, `rationale`.
- `population_caveats`, `citations`.

## Usage

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
# True high ('abnormal ECG',)
```

## See also

- [algorithm.md](algorithm.md) — criteria with citations and validation notes.
- [references.bib](references.bib) — full bibliographic entries.
- [tests/](tests/) — boundary tests.
