# Deep vein thrombosis: Wells DVT score

Implementation of the **Wells score for deep vein thrombosis** in both its original three-tier (Wells 1997) and modified two-tier (Wells 2003) forms. The Wells DVT score is the most widely used clinical pretest probability tool for suspected lower-extremity DVT and is recommended in ACCP and ESC guidelines for structuring the D-dimer-versus-imaging decision.

## Clinical context

Most patients presenting with symptoms suggestive of DVT do not have the diagnosis. Imaging every patient with leg pain or swelling is wasteful; treating empirically on suspicion alone risks unnecessary anticoagulation. The Wells score combines history and examination findings into a pretest probability that, paired with sensitive D-dimer testing or compression ultrasound, supports a defensible diagnostic pathway.

## Scope of this module

- Computes the **modified Wells DVT score** (Wells 2003) using ten items, range -2 to 9.
- Returns the **two-tier interpretation** (DVT *unlikely* versus *likely*) recommended by current guidelines.
- Computes the **original Wells DVT score** (Wells 1997) using nine items, range -2 to 8.
- Returns the **three-tier interpretation** (low / moderate / high pretest probability).
- Recommendations align with Wells 2003 and contemporary practice (sensitive D-dimer as the rule-out in *unlikely* patients; compression ultrasound in *likely* patients).

It does **not**:

- Diagnose DVT; only an imaging study (typically compression ultrasound) does.
- Apply to upper-extremity DVT, pregnancy, or hospitalized patients without independent clinical synthesis. Pregnant patients have a separate algorithm (LEFt rule, Chan 2009) that is not implemented here.
- Recommend specific D-dimer assay thresholds or specific anticoagulant regimens.
- Replace clinical judgment, especially when prior DVT, malignancy, or concurrent illness changes the calculus.

See [DISCLAIMER.md](../../DISCLAIMER.md).

## When the rule has reduced applicability

- **Hospitalized patients.** The score was derived and validated in outpatients with suspected DVT. Inpatient performance is poorer.
- **Pregnancy.** The LEFt rule (Left leg, Edema, First-trimester presentation) is a pregnancy-specific alternative.
- **Suspected isolated upper-extremity DVT.** Use the Constans score instead.
- **Patients on therapeutic anticoagulation already.** Pretest probability is altered.

## Inputs

| Input | Type | Points | Definition |
|---|---|---|---|
| `active_cancer` | bool | +1 | Active cancer (treatment within 6 months or palliative). |
| `paralysis_paresis_or_recent_lower_limb_immobilization` | bool | +1 | Paralysis, paresis, or recent plaster immobilization of a lower extremity. |
| `recently_bedridden_3_days_or_major_surgery_within_12_weeks` | bool | +1 | Recently bedridden for at least 3 days, or major surgery within the past 12 weeks requiring general or regional anesthesia. |
| `localized_tenderness_along_deep_venous_system` | bool | +1 | Localized tenderness along the distribution of the deep venous system. |
| `entire_leg_swollen` | bool | +1 | Entire leg swelling. |
| `calf_swelling_more_than_3cm` | bool | +1 | Calf swelling more than 3 cm compared with the asymptomatic leg, measured 10 cm below the tibial tuberosity. |
| `pitting_edema_in_symptomatic_leg` | bool | +1 | Pitting edema confined to the symptomatic leg. |
| `collateral_superficial_veins_non_varicose` | bool | +1 | Non-varicose collateral superficial veins. |
| `previously_documented_dvt` | bool | +1 (2003 modification) | Previously documented DVT. Not included in the original 1997 score. |
| `alternative_diagnosis_at_least_as_likely` | bool | **-2** | Alternative diagnosis at least as likely as DVT. |

## Outputs

### Modified Wells (two-tier)

A `WellsDvtTwoTierResult` with:

- `score` (int, range -2 to 9).
- `risk_band` (`"unlikely"` or `"likely"`).
- `recommended_action` (narrative aligned to Wells 2003).
- `rationale`.
- `citations`.

### Original Wells (three-tier)

A `WellsDvtThreeTierResult` with:

- `score` (int, range -2 to 8). Does **not** include the previously-documented-DVT item.
- `risk_band` (`"low"`, `"moderate"`, or `"high"`).
- `estimated_dvt_prevalence_band` (approximate, from Wells 1997).
- `recommended_action`.
- `rationale`.
- `citations`.

## See also

- [algorithm.md](algorithm.md) — both interpretations with citations per threshold.
- [references.bib](references.bib) — full bibliographic entries.
- [tests/](tests/) — boundary tests.
