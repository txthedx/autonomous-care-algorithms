# Subarachnoid hemorrhage: Ottawa SAH Rule

The **Ottawa SAH Rule** (Perry 2013; validated Perry 2017) is a highly sensitive rule-out tool for subarachnoid hemorrhage in alert patients with an acute, severe, non-traumatic headache. If none of six criteria is present, SAH is effectively excluded; if any is present, SAH cannot be excluded by the rule and further investigation is warranted.

## Clinical context

Headache is a common presentation, and SAH is a rare but catastrophic cause that is easy to miss. The rule provides a structured, very high-sensitivity screen for the specific population it was derived in — letting clinicians confidently rule out SAH in eligible patients with none of the criteria, while flagging those who need imaging. It is deliberately **high-sensitivity, low-specificity**.

## Scope of this module

- `ottawa_sah_assessment` — returns whether the rule applies, whether investigation is indicated, the criteria present, and (when not applicable) why.

It does **not**:

- Apply outside its population (see applicability) — notably reduced consciousness, prior aneurysm/SAH/brain tumor, new neurologic deficit, or chronic recurrent headache.
- Diagnose or exclude SAH definitively; only imaging (and, where indicated, lumbar puncture or CT angiography) does.
- Mandate imaging for every positive result — given the low specificity, the imaging decision rests on clinical judgement.

See [DISCLAIMER.md](../../DISCLAIMER.md).

## Applies to / does not apply to

**Applies to** alert (GCS 15) patients aged ≥ 15 with a new severe non-traumatic headache reaching maximum intensity within 1 hour.

**Does not apply to** new neurologic deficit, prior aneurysm / SAH / known brain tumor, or chronic recurrent headache (≥ 3 episodes of the same character and intensity over > 6 months).

## Criteria

Investigate further if **any** is present:

1. Age ≥ 40 years
2. Neck pain or stiffness
3. Witnessed loss of consciousness
4. Onset during exertion
5. Thunderclap headache (instantly peaking pain)
6. Limited neck flexion on examination

## Performance

In the derivation/validation cohorts the rule had ~100% sensitivity and ~15% specificity for SAH. A negative rule reliably excludes SAH; a positive rule does **not** mean SAH is present — most positive patients do not have it.

## Inputs

`SahFeatures` (the six criteria, each `bool`): `age_40_or_older`, `neck_pain_or_stiffness`, `witnessed_loss_of_consciousness`, `onset_during_exertion`, `thunderclap_headache`, `limited_neck_flexion_on_exam`.

`SahApplicability` (inclusion + exclusions, each `bool`): `new_severe_atraumatic_headache_peaking_within_1_hour`, `alert_gcs_15`, `age_15_or_older`, `new_neurologic_deficit`, `prior_aneurysm_sah_or_brain_tumor`, `chronic_recurrent_headache`.

## Outputs

- `rule_applicable` (bool).
- `investigation_indicated` (`True` / `False` / `None` when the rule does not apply).
- `positive_criteria`, `inapplicability_reasons` (tuples of labels).
- `recommended_action`, `rationale`, `population_caveats`, `citations`.

## Usage

```python
from conditions.subarachnoid_hemorrhage import (
    SahFeatures,
    SahApplicability,
    ottawa_sah_assessment,
)

features = SahFeatures(
    age_40_or_older=False,
    neck_pain_or_stiffness=False,
    witnessed_loss_of_consciousness=False,
    onset_during_exertion=False,
    thunderclap_headache=False,
    limited_neck_flexion_on_exam=False,
)
applicability = SahApplicability(
    new_severe_atraumatic_headache_peaking_within_1_hour=True,
    alert_gcs_15=True,
    age_15_or_older=True,
    new_neurologic_deficit=False,
    prior_aneurysm_sah_or_brain_tumor=False,
    chronic_recurrent_headache=False,
)
result = ottawa_sah_assessment(features, applicability)
print(result.rule_applicable, result.investigation_indicated)
# True False
```

## See also

- [algorithm.md](algorithm.md) — criteria and applicability with citations.
- [references.bib](references.bib) — full bibliographic entries.
- [tests/](tests/) — boundary tests.
