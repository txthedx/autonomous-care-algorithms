# Atrial fibrillation: stroke and bleeding risk

Two paired tools for the most consequential deterministic decision in atrial fibrillation management — whether to anticoagulate, and how to monitor for bleeding once anticoagulation is started:

1. **CHA₂DS₂-VASc** — stroke and systemic embolism risk in non-valvular AF (Lip 2010 derivation, ESC 2020 endorsement).
2. **HAS-BLED** — major bleeding risk on antithrombotic therapy (Pisters 2010 derivation, ESC 2020 endorsement).

A note on the Canadian context: the Canadian Cardiovascular Society's 2020 AF guideline uses the simpler **CHADS-65** algorithm in place of CHA₂DS₂-VASc for the anticoagulation decision (any patient ≥ 65 with AF is offered anticoagulation; otherwise modified CHADS₂ factors are used). The two algorithms produce similar outputs for most patients but diverge at the margins. This module implements CHA₂DS₂-VASc; the [algorithm.md](algorithm.md) describes how to map a CHA₂DS₂-VASc result to the CHADS-65 frame.

## Clinical context

Atrial fibrillation affects roughly 1 to 2% of adults overall and 5 to 10% of adults over 65. Untreated, AF roughly quintuples the risk of ischemic stroke. Oral anticoagulation reduces stroke risk by about two-thirds but introduces a bleeding risk that must be assessed and monitored. CHA₂DS₂-VASc and HAS-BLED are the most widely used decision aids for these paired questions; both have been validated across multiple populations and are endorsed by major societies.

**HAS-BLED is not a tool to withhold anticoagulation.** Per ESC 2020, a high HAS-BLED score identifies modifiable bleeding risk factors that should be addressed and indicates a need for closer monitoring, not avoidance of anticoagulation in otherwise eligible patients.

## Scope of this module

- Computes the **CHA₂DS₂-VASc** score (0 to 9) and returns an anticoagulation recommendation aligned with ESC 2020.
- Computes the **HAS-BLED** score (0 to 9) and returns a bleeding risk band with explicit ESC-aligned management language.

It does **not**:

- Apply to **valvular AF** (moderate-to-severe mitral stenosis or mechanical valve) — those patients require anticoagulation regardless of score; CHA₂DS₂-VASc was not derived in this population.
- Choose between warfarin and DOACs.
- Recommend specific drugs, doses, or monitoring intervals.
- Replace shared decision-making, individual patient preferences, or fall-risk assessment.

See [DISCLAIMER.md](../../DISCLAIMER.md).

## Limitations to acknowledge in use

- **Score derivations used binary sex.** CHA₂DS₂-VASc assigns a sex-category point to female sex. Application to transgender and non-binary patients requires individualized clinical judgment; the underlying evidence base is in cisgender populations.
- **Recent guideline debate.** ESC 2024 has shifted to framing female sex as a "risk modifier" rather than an independent risk factor, with anticoagulation decisions more weighted on the non-sex CHA₂DS₂-VASc components. This module implements the 2010-derived score and the ESC 2020 recommendation framing. Future versions will track guideline evolution.
- **Population effects.** Stroke and bleeding rates by score vary across populations. Reported risk percentages are taken from the original derivation cohorts and are not re-estimated.

## Inputs and outputs

### CHA₂DS₂-VASc

Input: a `Cha2ds2VascFeatures` dataclass with explicit booleans for each component plus `age_years` and `sex`.

Output: a `Cha2ds2VascResult` with:

- `score` (0 to 9).
- `criteria_present` (tuple of component labels with point values).
- `annual_stroke_risk_band` (approximate from Lip 2010).
- `recommended_anticoagulation` (narrative aligned with ESC 2020).
- `rationale`.
- `citations`.

### HAS-BLED

Input: a `HasBledFeatures` dataclass with explicit booleans for each component plus `age_years`.

Output: a `HasBledResult` with:

- `score` (0 to 9).
- `criteria_present`.
- `risk_band` (`"low_to_moderate"` or `"high"`).
- `recommended_management` (ESC 2020-aligned, with the explicit caveat that high HAS-BLED does not justify withholding anticoagulation).
- `rationale`.
- `citations`.

## See also

- [algorithm.md](algorithm.md) — both rules with citations per threshold, including the CHADS-65 mapping note.
- [references.bib](references.bib) — full bibliographic entries.
- [tests/](tests/) — boundary tests and recommendation tests.
