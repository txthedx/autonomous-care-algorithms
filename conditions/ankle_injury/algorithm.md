# Ottawa Ankle and Foot Rules

Two paired decision rules for selective use of radiography in acute ankle and midfoot injury, derived by Stiell et al. (1992, 1993) in Canadian emergency departments and validated internationally.

## Pre-step — Applicability

The rules were not validated in, and should not be applied to, patients with any of the following:

| Excluding factor | Source |
|---|---|
| Age under 18 years | Stiell 1992 (original derivation cohort), Plint 1999 (pediatric extension) |
| Intoxication | Stiell 1992 |
| Distracting injury | Stiell 1992 |
| Decreased sensation or focal neurologic deficit | Stiell 1992 |
| Gross deformity | Stiell 1992 |
| Isolated skin injury | Stiell 1992 |
| Head injury or decreased level of consciousness | Stiell 1992 |

If any factor is present, the rule does not apply; imaging and management proceed by clinical judgment.

## Ottawa Ankle Rule

**An ankle radiograph series is indicated if there is pain in the malleolar zone AND any of the following findings:**

| Criterion | Source |
|---|---|
| Bone tenderness at the posterior edge or tip of the lateral malleolus, including the distal 6 cm | Stiell 1992 |
| Bone tenderness at the posterior edge or tip of the medial malleolus, including the distal 6 cm | Stiell 1992 |
| Inability to bear weight (four steps) both immediately after injury AND at presentation | Stiell 1992 |

If pain is present in the malleolar zone but none of the criteria are met, imaging is not indicated.

## Ottawa Foot Rule

**A foot radiograph series is indicated if there is pain in the midfoot zone AND any of the following findings:**

| Criterion | Source |
|---|---|
| Bone tenderness at the base of the fifth metatarsal | Stiell 1992 |
| Bone tenderness at the navicular bone | Stiell 1992 |
| Inability to bear weight (four steps) both immediately and at presentation | Stiell 1992 |

If pain is present in the midfoot zone but none of the criteria are met, imaging is not indicated.

## Performance

A systematic review (Bachmann 2003) reported pooled sensitivity of the combined Ottawa rules for clinically important fractures of approximately 96 to 99%, with specificity around 25 to 40%. The intentional design trades specificity for sensitivity: missing a fracture is the harm to avoid; over-imaging is the harm to reduce.

## Pediatric note

The original derivation excluded children under 18. The Low Risk Ankle Rule (Plint 1999, Boutis 2003) is the most validated pediatric alternative for children approximately 3 years and older with acute ankle injury. This module returns `rule_applies=False` for ages under 18 with the `age_under_18` factor named; a future pediatric module may implement Low Risk Ankle.

## Citations

Short tags map to entries in [references.bib](references.bib):

- `Stiell 1992` — Stiell IG et al., *Ann Emerg Med* 1992.
- `Stiell 1993` — Stiell IG et al., *JAMA* 1993.
- `Stiell 1994` — Stiell IG et al., *JAMA* 1994.
- `Bachmann 2003` — Bachmann LM et al., *BMJ* 2003.
- `Plint 1999` — Plint AC et al., *Acad Emerg Med* 1999.
