# Acute knee injury

Implementation of the **Ottawa Knee Rule** (Stiell 1995, 1996) for selective use of radiography in adults with acute knee injury. One of the most extensively validated decision rules in emergency medicine, with approximately 100% sensitivity for clinically significant knee fractures (Bachmann 2004 systematic review).

## Clinical context

Most patients presenting with acute knee injury do not have a fracture. Imaging all patients leads to unnecessary radiation, cost, and time. The Ottawa Knee Rule uses five bedside findings to identify patients who require radiography. Applying the rule has been shown to reduce knee radiography rates by approximately 20 to 30% without missed clinically significant fractures.

## Scope of this module

- Implements the Ottawa Knee Rule for adult patients with acute knee injury.
- Returns whether the rule applies (population caveats below), and when it applies, whether imaging is indicated and which criteria triggered the decision.

It does **not**:

- Diagnose a fracture; only the radiograph does.
- Apply to children. The Pittsburgh Knee Rules (Bauer 1995, Moore 2005) are an alternative for pediatric patients and are not implemented here.
- Recommend specific imaging modality beyond the indication for plain radiography.
- Replace clinical judgment in the presence of features the rule does not capture.

See [DISCLAIMER.md](../../DISCLAIMER.md).

## When the rule does not apply

Per the original derivation (Stiell 1995) and subsequent reviews, the Ottawa Knee Rule was not validated in, and should not be applied to, patients with any of the following:

- Age under 18 years.
- Isolated skin injury without underlying bony concern.
- Gross deformity of the knee.
- Paraplegia or multiple injuries.
- Decreased level of consciousness.
- Re-presentation more than 7 days after the initial injury.

When any of these is present, the module returns `rule_applies=False` with the excluding factor named.

## Inputs

### Clinical features

| Input | Type | Definition |
|---|---|---|
| `age_years` | int | Patient age in completed years. Must be non-negative. |
| `isolated_patellar_tenderness` | bool | Tenderness of the patella that is the **only** bony tenderness on examination of the knee. |
| `tender_fibular_head` | bool | Bone tenderness at the head of the fibula. |
| `unable_to_flex_to_90_degrees` | bool | Inability to actively flex the affected knee to 90°. |
| `unable_to_bear_weight_immediately_and_now` | bool | Inability to bear weight (four steps, regardless of limp) **both** immediately after the injury **and** at presentation. |

### Applicability factors

| Input | Type | Definition |
|---|---|---|
| `age_under_18` | bool | Patient is under 18 years old. |
| `isolated_skin_injury` | bool | An isolated skin injury without bony concern. |
| `gross_deformity` | bool | Gross deformity of the knee. |
| `decreased_consciousness` | bool | Decreased level of consciousness. |
| `paraplegia_or_multiple_injuries` | bool | Paraplegia or multiple injuries. |
| `re_presentation_more_than_7_days` | bool | Re-presentation more than seven days after the initial injury. |

## Outputs

The function returns a result with:

- `rule_applies` (bool) — False when any applicability factor is present.
- `excluded_by` (tuple of str) — names of any applicability factors triggering exclusion.
- `imaging_indicated` (bool) — True when at least one criterion is met.
- `indicating_criteria` (tuple of str) — names of the criteria that triggered imaging.
- `recommended_action` (narrative).
- `rationale`.
- `citations`.

## Pediatric note

The Ottawa Knee Rule was derived in adults; this module returns `rule_applies=False` for ages under 18. The Pittsburgh Knee Rules (Bauer 1995) and subsequent pediatric-specific validation studies are a separate algorithm and will be implemented in a future module.

## See also

- [algorithm.md](algorithm.md) — the rule with citations.
- [references.bib](references.bib) — full bibliographic entries.
- [tests/](tests/) — boundary tests.
