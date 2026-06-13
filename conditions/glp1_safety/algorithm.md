# GLP-1 receptor agonist eligibility screen

A deterministic initiation screen for GLP-1 receptor agonists (e.g. semaglutide, liraglutide, dulaglutide), returning an eligibility verdict from the high-consequence factors that govern starting therapy.

## Inputs — `glp1_eligibility`

| Input (`Glp1EligibilityFeatures`) | Class | Meaning |
|---|---|---|
| `personal_or_family_history_mtc` | Contraindication | Personal or family history of medullary thyroid carcinoma |
| `men2_syndrome` | Contraindication | Multiple Endocrine Neoplasia syndrome type 2 |
| `pregnancy` | Contraindication | Pregnant (weight-management indication) |
| `history_of_pancreatitis` | Review | Prior pancreatitis |
| `breastfeeding` | Review | Breastfeeding |

## Rule

Precedence: contraindication → review → eligible.

1. Any of MTC history, MEN 2, or pregnancy → **`contraindicated`**. The MTC / MEN 2 contraindication is the GLP-1 receptor agonist class boxed warning (rodent thyroid C-cell tumors); pregnancy is treated as a contraindication in the weight-management setting (discontinue when recognized; no benefit; possible fetal harm).
2. Else any of pancreatitis history or breastfeeding → **`needs_clinician_review`**. The drugs were not studied after pancreatitis (consider alternatives); the lactation label weighs benefit against risk.
3. Else → **`eligible`** (by this screen).

## Sources for each factor

| Factor | Verdict | Source |
|---|---|---|
| MTC personal/family history | contraindicated | GLP-1 label (boxed warning) |
| MEN 2 | contraindicated | GLP-1 label (boxed warning) |
| Pregnancy | contraindicated | Wegovy label (discontinue when pregnancy recognized; no benefit; fetal harm) |
| History of pancreatitis | needs_clinician_review | Ozempic label (not studied; consider alternatives) |
| Breastfeeding | needs_clinician_review | Wegovy label (lactation: weigh benefit/risk) |

## Scope and caveats

- One initiation screen, not a full eligibility, interaction, or jurisdiction review.
- The MTC/MEN 2 contraindication is a rodent-derived class boxed warning; human causation is not established, but the contraindication stands.
- History items and drug exposure are clinician/intake judgements supplied as inputs.
- Outputs are eligibility verdicts — not prescriptions, doses, or routes. The screen supports, and does not replace, clinical judgement. See [DISCLAIMER.md](../../DISCLAIMER.md).

## Citations

Short tags map to entries in [references.bib](references.bib):

- `GLP-1 label` — U.S. FDA OZEMPIC (semaglutide, NDA 209637) and WEGOVY (semaglutide, NDA 215256) prescribing information. The boxed warning for MTC/MEN 2 is a GLP-1 receptor agonist class effect; the semaglutide labels are cited as the primary exemplar.
