# Acute pharyngitis

Implementation of the Centor and McIsaac scoring systems for risk stratification of group A streptococcal (GAS) pharyngitis in primary care, with recommendations aligned to the IDSA 2012 clinical practice guideline.

## Clinical context

Acute pharyngitis is one of the most frequent reasons for primary care visits and a common driver of antibiotic prescribing. Most cases are viral. Distinguishing GAS pharyngitis from viral causes by clinical features alone is unreliable, and both over-testing and over-treatment are well-documented harms.

The Centor criteria (Centor 1981) and the McIsaac modification (McIsaac 1998, validated 2004) provide a simple score that, combined with rapid antigen detection testing (RADT) and culture per IDSA 2012, supports a test-confirmed approach to antibiotic prescribing.

## Scope of this module

This module computes the **McIsaac score** from five inputs and returns a recommendation band. It does **not**:

- Diagnose GAS pharyngitis.
- Recommend a specific antibiotic, dose, or duration.
- Replace clinical judgment, RADT, throat culture, or shared decision-making.

See [DISCLAIMER.md](../../DISCLAIMER.md) at the repository root.

## When the rule does not apply

The McIsaac score was derived in patients presenting with acute sore throat in ambulatory care. It should not be applied to:

- Patients with peritonsillar abscess or other complications requiring urgent care.
- Patients with immunocompromise where lower thresholds for testing or treatment may apply.
- Patients with recent or current antibiotic exposure that may alter test performance.
- Outbreak settings where local epidemiology shifts pretest probability.

## Inputs

| Input | Type | Definition |
|---|---|---|
| `age_years` | int | Patient age in completed years. |
| `history_of_fever` | bool | History of fever >38°C (100.4°F) or measured fever. |
| `tonsillar_exudate` | bool | Tonsillar swelling **or** exudate present on examination. |
| `tender_anterior_cervical_nodes` | bool | Tender anterior cervical lymphadenopathy. |
| `no_cough` | bool | Cough is **absent**. |

## Outputs

The module returns:

- `score` (int, range -1 to 5).
- `gas_probability_band` (text band drawn from McIsaac 2004).
- `action` (test / treat / no action, aligned to IDSA 2012).
- `rationale` (one-sentence explanation).
- `citations` (tuple of source short tags).

## See also

- [algorithm.md](algorithm.md) — the rule with citations per threshold.
- [references.bib](references.bib) — full bibliographic entries.
- [tests/](tests/) — boundary tests and validation cases.
