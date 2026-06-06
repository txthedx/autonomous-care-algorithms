# Alvarado score (MANTRELS)

A bedside score for the probability of acute appendicitis in patients with suspected appendicitis.

Derived: Alvarado 1986 (*Ann Emerg Med*), from a retrospective analysis of patients admitted with suspected appendicitis. Externally validated and reviewed: Ohle 2011 (*BMC Med*). A pediatric-specific adaptation exists: Samuel 2002 (*J Pediatr Surg*).

The mnemonic **MANTRELS** names the eight components: **M**igration, **A**norexia, **N**ausea/vomiting, **T**enderness in the RLQ, **R**ebound, **E**levated temperature, **L**eukocytosis, and **S**hift of white cells to the left.

## Components

| Component | Points | Threshold |
|---|---|---|
| Migration of pain to the right lower quadrant | +1 | — |
| Anorexia | +1 | — |
| Nausea or vomiting | +1 | — |
| Tenderness in the right lower quadrant | +2 | — |
| Rebound tenderness | +1 | — |
| Elevated temperature | +1 | ≥ 37.3 °C |
| Leukocytosis | +2 | white cell count > 10 × 10⁹/L |
| Shift of white cells to the left | +1 | neutrophils > 75% |

Total range: 0 to 10. The two highest-weighted components — RLQ tenderness and leukocytosis — score 2 points each; all others score 1.

## Interpretation

| Score | Probability band | Action |
|---|---|---|
| ≤ 4 (1–4) | Low | Appendicitis unlikely. Consider alternative diagnoses; observation or discharge with safety-netting. |
| 5–6 | Intermediate | Compatible with appendicitis. Imaging (ultrasound first-line in children and women of reproductive age, otherwise CT) and/or active observation with serial examination. |
| ≥ 7 (7–10) | High | Probable appendicitis. Surgical consultation. |

Within the high band, the original description further distinguishes 7–8 (probable) from 9–10 (very probable).

## Use restrictions and performance

- The score predicts the probability of appendicitis; it does **not** diagnose it. Diagnosis rests on imaging, operative findings, or histology.
- **Derived predominantly in adults.** Performance differs in children, where a pediatric-specific score (Samuel 2002) is often preferred.
- **Lower specificity in women of reproductive age**, because gynecologic conditions mimic appendicitis; imaging is frequently required regardless of score.
- The score supports — but does not replace — serial examination and clinical judgement.

## Implementation note

The five clinical findings are booleans. Temperature, white cell count, and neutrophil percentage are entered as raw measured values (in °C, 10⁹/L, and percent), and the module applies the ≥ 37.3 °C, > 10 × 10⁹/L, and > 75% thresholds in one place. `alvarado_assessment` also returns the contributing factors (each component that scored, with its points) so the total can be audited against each input. Out-of-range measured values raise `ValueError`.

## Citations

Short tags map to entries in [references.bib](references.bib):

- `Alvarado 1986` — Alvarado A, *Ann Emerg Med* 1986 (derivation).
- `Ohle 2011` — Ohle R et al., *BMC Med* 2011 (systematic review).
- `Samuel 2002` — Samuel M, *J Pediatr Surg* 2002 (pediatric appendicitis score).
