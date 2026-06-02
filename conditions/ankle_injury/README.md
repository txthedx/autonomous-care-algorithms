# Acute ankle and midfoot injury

Implementation of the **Ottawa Ankle Rules** and the **Ottawa Foot Rules** for selective use of radiography in adults with acute ankle or midfoot injury. Derived by Stiell et al. (1992, 1993) and one of the most extensively validated decision rules in medicine, with approximately 100% sensitivity for clinically significant fractures and a reported reduction in unnecessary radiography of about 30 to 40%.

## Clinical context

Most patients presenting with acute ankle or midfoot injury do not have a clinically significant fracture. Imaging every patient leads to wasted radiation exposure, cost, and time without improving outcomes. The Ottawa Rules use four bedside findings per joint to identify the small subset who do require radiography. The rules have been validated in many emergency department and primary care cohorts internationally.

## Scope of this module

- Implements the **Ottawa Ankle Rules** for ankle imaging selection.
- Implements the **Ottawa Foot Rules** for midfoot imaging selection.
- Returns whether the rule applies in the first place (population caveats below) and, when it applies, whether imaging is indicated and which criteria are driving the decision.

It does **not**:

- Diagnose a fracture; only the radiograph does.
- Recommend specific imaging modality beyond the indication for plain radiography.
- Replace clinical judgment in the presence of features the rule does not capture.

See [DISCLAIMER.md](../../DISCLAIMER.md).

## When the rules do not apply

Per the original derivation and subsequent reviews, the Ottawa Rules were not validated in, and should not be applied to, patients with any of the following:

- Age under 18 years. Pediatric-specific rules (Low Risk Ankle Rule, Plint 1999) exist for older children; younger children warrant clinical judgment.
- Intoxication.
- Distracting injury that may mask local tenderness or weight-bearing assessment.
- Decreased sensation or focal neurologic deficit in the affected limb.
- Gross deformity of the ankle or foot.
- Isolated skin injury without underlying bony concern (different evaluation pathway).
- Head injury or decreased level of consciousness.

When any of these is present, the module returns `rule_applies=False` with the excluding factor named; the clinician applies independent judgment.

## Inputs

### Ankle rule

| Input | Type | Definition |
|---|---|---|
| `pain_in_malleolar_zone` | bool | Pain located in the malleolar zone (around the medial or lateral malleolus). |
| `tender_lateral_malleolus_distal_6cm` | bool | Bone tenderness at the posterior edge or tip of the lateral malleolus, including the distal 6 cm. |
| `tender_medial_malleolus_distal_6cm` | bool | Bone tenderness at the posterior edge or tip of the medial malleolus, including the distal 6 cm. |
| `unable_to_bear_weight_immediately_and_now` | bool | Inability to bear weight (four steps) **both** immediately after the injury **and** at presentation. |

### Foot rule

| Input | Type | Definition |
|---|---|---|
| `pain_in_midfoot_zone` | bool | Pain located in the midfoot zone. |
| `tender_5th_metatarsal_base` | bool | Bone tenderness at the base of the fifth metatarsal. |
| `tender_navicular` | bool | Bone tenderness at the navicular bone. |
| `unable_to_bear_weight_immediately_and_now` | bool | Inability to bear weight (four steps) immediately and at presentation. |

### Applicability factors (shared)

| Input | Type | Definition |
|---|---|---|
| `age_under_18` | bool | Patient is under 18 years old. |
| `intoxication` | bool | Clinical intoxication. |
| `distracting_injury` | bool | A distracting injury elsewhere. |
| `decreased_sensation_or_neurologic_deficit` | bool | Decreased sensation or focal neurologic deficit in the affected limb. |
| `gross_deformity` | bool | Gross deformity of the ankle or foot. |
| `isolated_skin_injury` | bool | An isolated skin injury without bony concern. |
| `head_injury_or_decreased_consciousness` | bool | Head injury or decreased level of consciousness. |

## Outputs

Both functions return a result with:

- `rule_applies` (bool) — False when any applicability factor is present.
- `excluded_by` (tuple of str) — names of any applicability factors triggering exclusion.
- `imaging_indicated` (bool) — True if the relevant zone pain is present and at least one criterion is met.
- `indicating_criteria` (tuple of str) — names of the criteria that triggered imaging.
- `recommended_action` (narrative).
- `rationale`.
- `citations`.

## See also

- [algorithm.md](algorithm.md) — both rules with citations per criterion.
- [references.bib](references.bib) — full bibliographic entries.
- [tests/](tests/) — boundary tests.
