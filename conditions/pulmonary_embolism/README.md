# Pulmonary embolism: Wells PE score and PERC

Two paired bedside tools for the workup of suspected acute pulmonary embolism:

1. **Wells PE score** (Wells 2000, 2001) — pretest probability assessment in both the original three-tier and modified two-tier forms.
2. **PERC** (Kline 2004, 2008) — the Pulmonary Embolism Rule-out Criteria, used **only when pretest probability is low** to exclude PE without further testing.

Both are endorsed in the ESC 2019 acute PE guideline (Konstantinides) and the ACCP CHEST guidelines.

## Clinical context

Patients with non-specific chest pain or dyspnea are common in emergency and primary care. Over-investigation with CT pulmonary angiography (CT-PA) carries costs (radiation, contrast, incidental findings) without diagnostic yield in low-probability patients. Under-investigation misses a treatable cause of preventable death. The Wells PE score structures the pretest probability decision; PERC further refines the rule-out pathway for low-probability patients.

## Recommended sequence

```
Wells PE (or clinical gestalt) -> pretest probability
   |
   v
   Low / "PE unlikely"      ->   PERC
                                   |
                                   v
                                  all negative -> PE excluded, no further testing
                                  any positive -> sensitive D-dimer; CT-PA if positive
   Moderate                  ->   Sensitive D-dimer; CT-PA if positive
   High / "PE likely"        ->   CT-PA directly; D-dimer not required for rule-out
```

## Scope of this module

- Computes the **Wells PE score** (range 0 to 12.5).
- Returns the **two-tier interpretation** (PE *unlikely* vs *likely*) recommended in current guidelines.
- Returns the **three-tier interpretation** (low / moderate / high) for completeness.
- Evaluates the **PERC criteria** and, given an explicit `pretest_probability_is_low` flag, returns whether PE can be excluded without further testing.

It does **not**:

- Apply to patients with hemodynamic instability or suspected massive PE; those patients warrant immediate evaluation regardless of score.
- Diagnose PE; only imaging or pathology does.
- Apply to pregnant patients without independent clinical synthesis (pregnancy-specific algorithms exist, e.g., the YEARS pregnancy-adapted algorithm).
- Recommend specific anticoagulant regimens, doses, or durations.

See [DISCLAIMER.md](../../DISCLAIMER.md).

## When PERC must not be used

PERC was derived and validated **only in patients with low pretest probability**. Applying PERC to intermediate- or high-probability patients yields false negatives and misses PE. The PERC function in this module requires the caller to pass an explicit `pretest_probability_is_low` boolean; if False, the function refuses to rule out PE and returns guidance to use the Wells PE / D-dimer pathway instead.

## Wells PE inputs

| Input | Type | Points |
|---|---|---|
| `clinical_signs_of_dvt` | bool | +3 |
| `pe_at_least_as_likely_as_alternative` | bool | +3 |
| `heart_rate_over_100` | bool | +1.5 |
| `immobilization_3_days_or_surgery_within_4_weeks` | bool | +1.5 |
| `previous_dvt_or_pe` | bool | +1.5 |
| `hemoptysis` | bool | +1 |
| `malignancy` | bool | +1 |

## PERC inputs

| Input | Type | PERC criterion (criterion is met when this is False) |
|---|---|---|
| `age_50_or_older` | bool | Age < 50 |
| `heart_rate_100_or_more` | bool | Heart rate < 100 |
| `spo2_below_95_on_room_air` | bool | SpO₂ ≥ 95% on room air |
| `hemoptysis` | bool | No hemoptysis |
| `estrogen_use` | bool | No estrogen use |
| `prior_dvt_or_pe` | bool | No prior DVT or PE |
| `unilateral_leg_swelling` | bool | No unilateral leg swelling |
| `recent_surgery_or_trauma_within_4_weeks_requiring_hospitalization` | bool | No recent surgery or trauma requiring hospitalization in past 4 weeks |

Each input is the *positive finding*. PERC passes (PE can be ruled out) only when **all eight inputs are False** AND `pretest_probability_is_low` is True.

## Outputs

### Wells PE — two-tier

- `score` (float, range 0 to 12.5).
- `risk_band` (`"unlikely"` or `"likely"`).
- `recommended_action`, `rationale`, `citations`.

### Wells PE — three-tier

- `score` (float).
- `risk_band` (`"low"`, `"moderate"`, or `"high"`).
- `estimated_pe_prevalence_band` (approximate from Wells 2001).
- `recommended_action`, `rationale`, `citations`.

### PERC

- `pretest_probability_is_low` (echoed back).
- `perc_failure_criteria_present` (positive criteria, if any).
- `pe_ruled_out` (True only when all eight criteria are absent and pretest probability is low).
- `recommended_action`, `rationale`, `citations`.

## See also

- [algorithm.md](algorithm.md) — both rules with citations per threshold.
- [references.bib](references.bib) — full bibliographic entries.
- [tests/](tests/) — boundary tests.
