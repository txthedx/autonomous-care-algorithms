# Uncomplicated urinary tract infection (cystitis) in women

Symptom-based assessment for acute uncomplicated cystitis in non-pregnant adult women, following the Bent 2002 *JAMA* "Rational Clinical Examination" review and the IDSA/ESCMID 2010 guideline for empirical management.

The module separates two questions:

1. **Is this an uncomplicated pattern at all?** Several factors take a patient out of the "uncomplicated cystitis in women" frame and require broader workup (urine culture, imaging considerations, alternative diagnoses).
2. **If uncomplicated, what is the pretest probability?** Symptom combinations and the presence or absence of vaginal symptoms drive the probability band, which in turn drives the testing-versus-empirical-treatment decision.

## Clinical context

Acute uncomplicated cystitis is among the most common presentations in primary care. Bent 2002 demonstrated that history alone — specifically the combination of dysuria and frequency without vaginal symptoms — yields a pretest probability of approximately 90%, sufficient to support empirical treatment without urine culture in most settings. Patients with a less typical pattern, with vaginal symptoms, or with any complicating factor warrant a different workup.

## Scope of this module

- Detects features that take a patient out of the "uncomplicated cystitis in women" frame.
- For uncomplicated patterns, classifies pretest probability into low, intermediate, or high using the Bent 2002 decision logic.
- Returns recommended actions aligned with Bent 2002 and IDSA 2010 (test versus empirical treatment versus broader workup).

It does **not**:

- Apply to men, pregnant patients, children, or catheterized patients.
- Recommend specific antibiotics, doses, or durations.
- Replace clinical judgment, urinalysis interpretation, or culture results.
- Diagnose pyelonephritis, urolithiasis, vaginitis, sexually transmitted infections, or interstitial cystitis.

See [DISCLAIMER.md](../../DISCLAIMER.md).

## When the rule does not apply

Any of the following takes a patient out of the uncomplicated frame; the module flags these explicitly:

- Pregnancy.
- Male sex.
- Uncontrolled diabetes or immunocompromise.
- Indwelling catheter or recent urinary tract instrumentation.
- Known anatomic or functional urinary tract abnormality.
- Recent antibiotic use.
- Symptoms more than seven days.
- Recurrent UTI (three or more in twelve months, or two or more in six months).
- Suspicion of pyelonephritis (flank pain, fever, nausea/vomiting, or other systemic symptoms).

When any of these is present, the module returns "complicated pattern" without applying the Bent decision rule.

## Inputs

### Presenting symptoms

| Input | Type | Definition |
|---|---|---|
| `dysuria` | bool | Pain or burning on urination. |
| `urinary_frequency` | bool | Increased urinary frequency. |
| `hematuria` | bool | Visible or reported blood in urine. |
| `suprapubic_or_back_pain` | bool | Suprapubic pain or low back pain. |
| `vaginal_discharge` | bool | Abnormal vaginal discharge. |
| `vaginal_irritation` | bool | Vaginal itching or irritation. |

### Complicating factors

| Input | Type | Definition |
|---|---|---|
| `pregnancy` | bool | Currently pregnant. |
| `male` | bool | Male anatomy or assigned male at birth with intact urinary anatomy. |
| `diabetes_uncontrolled_or_immunocompromise` | bool | Uncontrolled diabetes mellitus or immunocompromised state. |
| `indwelling_catheter_or_recent_instrumentation` | bool | Indwelling urinary catheter or recent urinary tract instrumentation. |
| `known_urinary_tract_abnormality` | bool | Known anatomic or functional abnormality. |
| `recent_antibiotic_use` | bool | Recent antibiotic exposure. |
| `symptoms_more_than_7_days` | bool | Symptom duration greater than seven days. |
| `recurrent_uti` | bool | Three or more UTIs in twelve months, or two or more in six months. |
| `flank_pain_or_fever_or_systemic_symptoms` | bool | Features suggesting pyelonephritis. |

## Outputs

The assessment returns a result with:

- `is_complicated_pattern` (bool).
- `complicating_factors_present` (tuple of factor labels).
- `vaginal_symptoms_present` (bool).
- `uti_symptom_count` (int, 0 to 4).
- `pretest_probability_band` (`"not_applicable_complicated"`, `"alternative_diagnoses_considered"`, `"low"`, `"intermediate"`, or `"high"`).
- `recommended_action` (narrative aligned to Bent 2002 and IDSA 2010).
- `rationale`.
- `citations`.

## See also

- [algorithm.md](algorithm.md) — the rule with citations.
- [references.bib](references.bib) — full bibliographic entries.
- [tests/](tests/) — boundary tests.
