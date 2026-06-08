# Ottawa SAH Rule

A highly sensitive rule for excluding subarachnoid hemorrhage in alert patients with acute non-traumatic headache.

Derived: Perry 2013 (*JAMA*), in 2131 patients across ten Canadian emergency departments. Prospectively validated: Perry 2017 (*CMAJ*).

## Applicability

The rule applies **only** to:

- alert patients (GCS 15),
- aged ≥ 15 years,
- with a new severe non-traumatic headache reaching maximum intensity within 1 hour.

It does **not** apply to patients with a new neurologic deficit, a prior aneurysm, a previous SAH, a known brain tumor, or chronic recurrent headaches (≥ 3 episodes of the same character and intensity over > 6 months). These were excluded from the derivation.

## Criteria

Among eligible patients, investigate further for SAH if **any** of:

| Criterion |
|---|
| Age ≥ 40 years |
| Neck pain or stiffness |
| Witnessed loss of consciousness |
| Onset during exertion |
| Thunderclap headache (instantly peaking pain) |
| Limited neck flexion on examination |

## Decision

| Eligible? | Any criterion present? | Interpretation |
|---|---|---|
| No | — | Rule does not apply; use clinical judgement. |
| Yes | No | SAH effectively excluded by the rule. |
| Yes | Yes | SAH cannot be excluded; investigate per clinical judgement. |

## Performance and the sensitivity/specificity tradeoff

In the derivation and validation cohorts the rule had approximately **100% sensitivity** and **15% specificity** for SAH. The rule is therefore a **rule-out** tool: a negative rule reliably excludes SAH, but a positive rule does **not** mean SAH is present — the large majority of rule-positive patients will not have SAH. A positive result indicates that SAH cannot be excluded clinically; the decision to image (non-contrast CT head, and lumbar puncture or CT angiography as indicated) rests on clinical judgement.

## Implementation note

The six criteria are booleans; investigation is indicated if any is present. Applicability is a separate dataclass capturing the three inclusion conditions and three exclusions; the function short-circuits to "rule does not apply" (with reasons) when the patient is ineligible, and only then evaluates the criteria. `investigation_indicated` is `None` when the rule does not apply.

## Citations

Short tags map to entries in [references.bib](references.bib):

- `Perry 2013` — Perry JJ et al., *JAMA* 2013 (derivation).
- `Perry 2017` — Perry JJ et al., *CMAJ* 2017 (validation).
