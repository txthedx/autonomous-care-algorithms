# GLP-1 receptor agonist eligibility screen

A deterministic medication-safety screen for starting a GLP-1 receptor agonist, returning an eligibility verdict (`contraindicated` / `needs_clinician_review` / `eligible`).

## Clinical context

GLP-1 receptor agonists (e.g. semaglutide, liraglutide, dulaglutide) treat type 2 diabetes and chronic weight management. A few high-consequence factors govern initiation:

- **MTC / MEN 2.** The class carries an FDA boxed warning for thyroid C-cell tumors; it is contraindicated with a personal or family history of medullary thyroid carcinoma (MTC) or Multiple Endocrine Neoplasia syndrome type 2 (MEN 2).
- **Pregnancy.** In weight management the drug is discontinued when pregnancy is recognized; weight loss offers no benefit and may cause fetal harm. The long half-life means stopping well before a planned pregnancy.
- **Pancreatitis history / breastfeeding.** Not hard stops: the drugs were not studied after pancreatitis (consider alternatives), and the lactation label weighs benefit against risk — both route to clinician review.

## Scope

- **In scope:** an initiation eligibility screen over the factors above.
- **Out of scope:** efficacy, dosing, titration, other interactions, service/jurisdiction eligibility, and prescriptions, doses, or routes.

## Inputs and outputs

| Input (`Glp1EligibilityFeatures`) | Type | Meaning |
|---|---|---|
| `personal_or_family_history_mtc` | bool | Medullary thyroid carcinoma, personal or family |
| `men2_syndrome` | bool | Multiple Endocrine Neoplasia type 2 |
| `pregnancy` | bool | Pregnant |
| `breastfeeding` | bool | Breastfeeding |
| `history_of_pancreatitis` | bool | Prior pancreatitis |

| Output (`Glp1EligibilityResult`) | Meaning |
|---|---|
| `verdict` | `contraindicated` / `needs_clinician_review` / `eligible` |
| `contraindicated`, `needs_clinician_review` | Verdict booleans |
| `contraindication_factors`, `review_factors` | Which factors fired |
| `recommended_action`, `rationale`, `population_caveats`, `citations` | Narrative and provenance |

## Usage

```python
from conditions.glp1_safety import Glp1EligibilityFeatures, glp1_eligibility

result = glp1_eligibility(
    Glp1EligibilityFeatures(
        personal_or_family_history_mtc=False,
        men2_syndrome=False,
        pregnancy=False,
        breastfeeding=False,
        history_of_pancreatitis=True,
    )
)
print(result.verdict, result.review_factors)
# needs_clinician_review ('history of pancreatitis',)
```

## Citations

See [references.bib](references.bib) and [algorithm.md](algorithm.md). Primary sources: U.S. FDA OZEMPIC (semaglutide, NDA 209637) and WEGOVY (semaglutide, NDA 215256) prescribing information; the MTC/MEN 2 boxed warning is a GLP-1 receptor agonist class effect.

Not a medical device. See [DISCLAIMER.md](../../DISCLAIMER.md).
