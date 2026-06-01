# Pharyngitis algorithm: McIsaac score with IDSA 2012 interpretation

## Score components

Each of the four Centor criteria contributes 1 point when present.

| Criterion | Points | Source |
|---|---|---|
| History of fever >38°C | +1 | Centor 1981 |
| Tonsillar swelling or exudate | +1 | Centor 1981 |
| Tender anterior cervical lymphadenopathy | +1 | Centor 1981 |
| Absence of cough | +1 | Centor 1981 |

The McIsaac modification adds an age adjustment:

| Age (years) | Adjustment | Source |
|---|---|---|
| 3 to 14 | +1 | McIsaac 1998 |
| 15 to 44 | 0 | McIsaac 1998 |
| 45 or older | -1 | McIsaac 1998 |

Total score range: **-1 to 5**.

## Approximate GAS probability by score

From the Canadian primary care validation cohort in McIsaac 2004. These are population-level estimates and depend on local prevalence; do not treat them as individual probabilities without local validation.

| Score | Approximate GAS probability |
|---|---|
| -1 or 0 | ~1 to 2.5% |
| 1 | ~5 to 10% |
| 2 | ~11 to 17% |
| 3 | ~28 to 35% |
| 4 or more | ~51 to 53% |

## Recommendation bands

Recommendations follow the IDSA 2012 guideline (Shulman et al.), which favors **test-confirmed** treatment over empirical antibiotics in adults, and recommends backup throat culture for children with a negative RADT.

| Score | Recommended action | Source |
|---|---|---|
| -1 or 0 | No testing. No antibiotics. Symptomatic care. | McIsaac 1998, 2004; Shulman 2012 |
| 1 | No routine testing in adults. No empirical antibiotics. | McIsaac 1998, 2004; Shulman 2012 |
| 2 or 3 | Perform RADT. Treat only if positive. In children with negative RADT, send backup culture. | Shulman 2012 |
| 4 or more | Perform RADT. Treat only if positive. IDSA 2012 does not endorse empirical antibiotics in adults without test confirmation. | McIsaac 2004; Shulman 2012 |

## Conflicts with older guidance

Some older sources, including the original McIsaac 1998 paper, suggested empirical antibiotic treatment at scores of 4 or higher in adults. The IDSA 2012 guideline supersedes this for jurisdictions that follow IDSA, in favor of RADT-confirmed treatment. NICE NG84 (2018) takes a similar test-and-treat stance for adults in the UK. This module follows the IDSA 2012 position.

If your jurisdiction follows a different guideline, do not assume the recommendations here apply unchanged.

## Citations

Short tags used in code map to entries in [references.bib](references.bib):

- `Centor 1981` — Centor RM et al., *Med Decis Making* 1981.
- `McIsaac 1998` — McIsaac WJ et al., *CMAJ* 1998.
- `McIsaac 2004` — McIsaac WJ et al., *JAMA* 2004.
- `Shulman 2012` — Shulman ST et al. (IDSA), *Clin Infect Dis* 2012.
- `NICE NG84` — NICE Guideline NG84, 2018.
