# Finasteride safety screens

Deterministic medication-safety screens at the point of prescribing finasteride: a teratogenicity contraindication and the Health Canada pre-prescribe psychiatric screen.

## Clinical context

Finasteride is a Type II 5α-reductase inhibitor used for male androgenetic alopecia and benign prostatic hyperplasia. Two safety issues govern whether and how it is started:

- **Teratogenicity.** By lowering dihydrotestosterone, finasteride can cause abnormalities of the external genitalia of a male fetus. It is contraindicated in pregnancy and in anyone who is or may become pregnant (historically FDA Pregnancy Category X), and pregnant people should not handle crushed or broken tablets (Propecia label).
- **Psychiatric risk.** Health Canada updated the Canadian product monographs (Propecia, Proscar) in January 2024 with mood alterations — depressed mood, depression, self-harm, and suicidal ideation, including worsening of pre-existing depression — and recommends screening every patient for suicidal ideation, self-harm, and depression before prescribing (Health Canada 2024).

## Scope

- **In scope:** a teratogenicity contraindication screen and a pre-prescribe psychiatric screen.
- **Out of scope:** any other interaction or contraindication, efficacy, dosing, service/jurisdiction eligibility, and prescriptions, doses, or routes. The psychiatric screen is not a validated suicide-risk instrument.

## Inputs and outputs

### `finasteride_contraindication`

| Input (`FinasterideContraindicationFeatures`) | Type | Meaning |
|---|---|---|
| `pregnant_or_able_to_become_pregnant` | bool | Pregnant or a person of reproductive potential |

Output (`FinasterideContraindicationResult`): `verdict` (`absolute_contraindication` / `no_contraindication_detected`), `contraindicated`, plus `recommended_action`, `rationale`, `population_caveats`, `citations`.

### `finasteride_psychiatric_screen`

| Input (`FinasteridePsychiatricFeatures`) | Type | Meaning |
|---|---|---|
| `active_suicidal_ideation_or_self_harm` | bool | Current suicidal ideation or self-harm |
| `current_or_past_depression` | bool | Depression history without active suicidal ideation |

Output (`FinasteridePsychiatricResult`): `verdict` (`active_risk_do_not_initiate` / `history_clinician_review` / `screen_negative`), `block_initiation`, `positive_findings`, plus `recommended_action`, `rationale`, `population_caveats`, `citations`.

## Usage

```python
from conditions.finasteride_safety import (
    FinasterideContraindicationFeatures,
    FinasteridePsychiatricFeatures,
    finasteride_contraindication,
    finasteride_psychiatric_screen,
)

c = finasteride_contraindication(
    FinasterideContraindicationFeatures(pregnant_or_able_to_become_pregnant=True)
)
print(c.verdict)  # absolute_contraindication

p = finasteride_psychiatric_screen(
    FinasteridePsychiatricFeatures(
        active_suicidal_ideation_or_self_harm=False,
        current_or_past_depression=True,
    )
)
print(p.verdict, p.block_initiation)  # history_clinician_review False
```

## Citations

See [references.bib](references.bib) and [algorithm.md](algorithm.md). Primary sources: U.S. FDA PROPECIA (finasteride) prescribing information (NDA 020788) and the Health Canada Summary Safety Review / January 2024 Canadian product-monograph update.

Not a medical device. See [DISCLAIMER.md](../../DISCLAIMER.md).
