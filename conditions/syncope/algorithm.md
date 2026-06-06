# San Francisco Syncope Rule (CHESS)

A binary clinical decision rule that identifies patients with syncope or near-syncope who are at risk of a short-term serious outcome.

Derived: Quinn 2004 (*Ann Emerg Med*), from a single-center prospective cohort of 684 visits. Prospective validation by the original group: Quinn 2006 (*Ann Emerg Med*). Independent external validations with lower sensitivity: Sun 2007 and Birnbaum 2008 (both *Ann Emerg Med*).

The mnemonic **CHESS** names the five criteria. If **any one** is present, the rule is positive (high risk).

## Criteria

| Letter | Criterion | Positive when |
|---|---|---|
| C | Congestive heart failure history | history present |
| H | Hematocrit | < 30% |
| E | Abnormal ECG | any new change or a non-sinus rhythm |
| S | Shortness of breath | symptom present |
| S | Systolic blood pressure at triage | < 90 mmHg |

## Decision

| Criteria | Risk band | Action |
|---|---|---|
| None present | Low | Outpatient evaluation may be considered, with clinical judgement. |
| Any one present | High | Admission or monitored observation with further cardiac evaluation. |

A "serious outcome" comprises death, myocardial infarction, arrhythmia, pulmonary embolism, stroke, subarachnoid hemorrhage, significant hemorrhage, or a return ED visit and admission for a related event.

## Performance and validation caveats

- Derivation (Quinn 2004): about 96% sensitivity, 62% specificity for serious outcomes.
- Authors' prospective validation (Quinn 2006): about 98% sensitivity.
- **Independent external validations reported lower sensitivity** (Sun 2007; Birnbaum 2008). The rule is a **screening tool, not a discharge guarantee**, and should be applied alongside clinical judgement.

## Use restrictions

The rule applies to patients presenting with syncope or near-syncope whose event is **not clearly attributable to a non-cardiac cause** (e.g., seizure, intoxication, hypoglycemia). The "abnormal ECG" criterion requires clinical interpretation (any new change or a non-sinus rhythm relative to a prior ECG when available).

## Implementation note

The rule is binary, so this module returns no numeric score. The two measured criteria (hematocrit and systolic blood pressure) are entered as raw values and the < 30% and < 90 mmHg thresholds are applied internally; the other three criteria are booleans. `sfsr_assessment` returns `high_risk`, the list of positive criteria, the risk band, a disposition, and caveats. Out-of-range measured values raise `ValueError`.

## Citations

Short tags map to entries in [references.bib](references.bib):

- `Quinn 2004` — Quinn JV et al., *Ann Emerg Med* 2004 (derivation).
- `Quinn 2006` — Quinn J et al., *Ann Emerg Med* 2006 (prospective validation).
- `Sun 2007` — Sun BC et al., *Ann Emerg Med* 2007 (external validation).
- `Birnbaum 2008` — Birnbaum A et al., *Ann Emerg Med* 2008 (failure to validate).
