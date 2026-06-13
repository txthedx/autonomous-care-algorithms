# Finasteride safety screens

Two deterministic safety checks at the point of prescribing finasteride (a Type II 5α-reductase inhibitor for male androgenetic alopecia and BPH): a teratogenicity contraindication and the Health Canada pre-prescribe psychiatric screen.

## 1. Teratogenicity contraindication — `finasteride_contraindication`

| Input | Meaning |
|---|---|
| `pregnant_or_able_to_become_pregnant` | The patient is pregnant or is a person of reproductive potential who could become pregnant |

**Rule:** if true → `absolute_contraindication`. Finasteride lowers dihydrotestosterone and can cause abnormalities of the external genitalia of a male fetus; it is contraindicated in pregnancy and in anyone who is or may become pregnant (FDA Pregnancy Category X). Pregnant people should also avoid handling crushed or broken tablets (Propecia label). Otherwise → `no_contraindication_detected`.

The input captures the **reproductive situation, not gender identity** — the teratogenic risk is to a male fetus, so the contraindication applies to anyone able to become pregnant.

## 2. Pre-prescribe psychiatric screen — `finasteride_psychiatric_screen`

Health Canada updated the Canadian product monographs (Propecia, Proscar) in **January 2024** with mood alterations — depressed mood, depression, self-harm, and suicidal ideation, including worsening of pre-existing depression — and recommends screening every patient for suicidal ideation, self-harm, and depression **before** prescribing (Health Canada 2024).

| Input | Meaning |
|---|---|
| `active_suicidal_ideation_or_self_harm` | Current suicidal ideation or self-harm on screening |
| `current_or_past_depression` | Current or past depression, without active suicidal ideation |

**Rule (in precedence order):**

1. `active_suicidal_ideation_or_self_harm` → `active_risk_do_not_initiate`: do not initiate; address acute risk and surface crisis resources through the appropriate clinical pathway.
2. else `current_or_past_depression` → `history_clinician_review`: route to clinician review; finasteride can worsen pre-existing depression.
3. else → `screen_negative`: still counsel on the mood-alteration risk and document the screen.

## Scope and caveats

- Two focused checks, not a full eligibility, interaction, or psychiatric assessment. The psychiatric screen is **not** a validated suicide-risk instrument.
- Drug exposure and the reproductive/psychiatric situation are clinician/intake judgements supplied as inputs.
- Post-marketing psychiatric symptoms have been reported to continue after finasteride is stopped; the screen addresses initiation only.
- Outputs are contraindication and screen verdicts — not prescriptions, doses, or routes. The screens support, and do not replace, clinical judgement. See [DISCLAIMER.md](../../DISCLAIMER.md).

## Citations

Short tags map to entries in [references.bib](references.bib):

- `Propecia label` — U.S. FDA PROPECIA (finasteride) prescribing information, NDA 020788 (teratogenicity; pregnancy contraindication).
- `Health Canada 2024` — Health Canada Summary Safety Review and the January 2024 Canadian product-monograph update for Propecia/Proscar (mood alterations; pre-prescribe screen for suicidal ideation, self-harm, and depression).
