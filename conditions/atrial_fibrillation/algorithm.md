# Atrial fibrillation: CHA₂DS₂-VASc and HAS-BLED

Two scores used together to inform anticoagulation decisions in non-valvular atrial fibrillation: CHA₂DS₂-VASc for stroke risk, HAS-BLED for bleeding risk. Both were derived in the Euro Heart Survey cohort and validated in subsequent registries.

## CHA₂DS₂-VASc

Stroke and systemic embolism risk in non-valvular AF. Original derivation: Lip 2010 (*Chest*). Endorsed in ESC 2020 AF guideline (Hindricks 2021).

### Components

| Letter | Criterion | Points | Source |
|---|---|---|---|
| C | Congestive heart failure or moderate-to-severe LV dysfunction | 1 | Lip 2010 |
| H | Hypertension (treated or on therapy) | 1 | Lip 2010 |
| A₂ | Age ≥ 75 years | 2 | Lip 2010 |
| D | Diabetes mellitus | 1 | Lip 2010 |
| S₂ | Prior stroke, TIA, or thromboembolism | 2 | Lip 2010 |
| V | Vascular disease (prior MI, peripheral arterial disease, or aortic plaque) | 1 | Lip 2010 |
| A | Age 65 to 74 years | 1 | Lip 2010 |
| Sc | Female sex | 1 | Lip 2010 |

Age 65–74 and Age ≥75 are mutually exclusive. Maximum score: 9.

### Approximate annual stroke risk by score (Lip 2010 derivation)

| Score | Annual stroke risk (approximate) |
|---|---|
| 0 | ~0% |
| 1 | ~1.3% |
| 2 | ~2.2% |
| 3 | ~3.2% |
| 4 | ~4.0% |
| 5 | ~6.7% |
| 6 | ~9.8% |
| 7 | ~9.6% |
| 8 | ~6.7% |
| 9 | ~15.2% |

Sample sizes at the highest scores are small; rates are not monotonic across the full range in the original cohort.

### Anticoagulation recommendations (ESC 2020 frame)

| Patient | Recommendation |
|---|---|
| Male with score 0; female with score 1 (sex point only) | Anticoagulation not recommended. |
| Male with score 1 (non-sex); female with score 2 (sex plus one) | Consider anticoagulation after shared decision-making (Class IIa). |
| Male with score ≥ 2; female with score ≥ 3 | Anticoagulation recommended (Class I). |

### Canadian CCS frame: CHADS-65

The 2020 CCS AF guideline uses a simpler algorithm:

- Age ≥ 65: offer anticoagulation.
- Age < 65 with any prior stroke, hypertension, heart failure, or diabetes: offer anticoagulation.
- Otherwise: no anticoagulation.

Mapping from CHA₂DS₂-VASc output: any patient who scores 1 point from age ≥ 65 (the `A`/`A₂` components) automatically meets the CHADS-65 anticoagulation threshold. The two frames diverge for younger patients with isolated low-weight risk factors.

## HAS-BLED

Major bleeding risk on antithrombotic therapy. Original derivation: Pisters 2010 (*Chest*). Endorsed in ESC 2020 AF guideline.

### Components

| Letter | Criterion | Points | Source |
|---|---|---|---|
| H | Hypertension, uncontrolled (SBP > 160 mmHg) | 1 | Pisters 2010 |
| A | Abnormal renal function (Cr > 200 µmol/L, dialysis, or transplant) | 1 | Pisters 2010 |
| A | Abnormal liver function (cirrhosis, bilirubin > 2× ULN, AST/ALT/ALP > 3× ULN) | 1 | Pisters 2010 |
| S | Prior stroke | 1 | Pisters 2010 |
| B | Bleeding history or predisposition (anemia, prior major bleed) | 1 | Pisters 2010 |
| L | Labile INR (time in therapeutic range < 60%; warfarin only) | 1 | Pisters 2010 |
| E | Elderly (age > 65) | 1 | Pisters 2010 |
| D | Drugs predisposing to bleeding (concurrent antiplatelet, NSAID) | 1 | Pisters 2010 |
| D | Alcohol use (≥ 8 units per week) | 1 | Pisters 2010 |

Maximum score: 9.

### Risk bands

| Score | Risk band | Management implication |
|---|---|---|
| 0 to 2 | Low to moderate | Standard monitoring. |
| 3 or more | High | Identify and address modifiable bleeding risk factors. Closer follow-up. **Do not withhold anticoagulation on the basis of HAS-BLED alone (ESC 2020).** |

### Modifiable HAS-BLED factors

The ESC 2020 guideline emphasizes that several HAS-BLED components are modifiable:

- Uncontrolled hypertension — treat to target.
- Labile INR — review warfarin management; consider DOAC if available.
- Concurrent antiplatelet or NSAID use — review necessity, discontinue if possible.
- Excess alcohol — counsel on reduction.

Addressing modifiable factors lowers actual bleeding risk independent of the score itself.

## Citations

Short tags map to entries in [references.bib](references.bib):

- `Lip 2010` — Lip GY et al., *Chest* 2010 (CHA₂DS₂-VASc derivation).
- `Pisters 2010` — Pisters R et al., *Chest* 2010 (HAS-BLED derivation).
- `ESC 2020` — Hindricks G et al., *Eur Heart J* 2021 (2020 ESC AF guideline).
- `CCS 2020` — Andrade JG et al., *Can J Cardiol* 2020 (CCS AF guideline).
