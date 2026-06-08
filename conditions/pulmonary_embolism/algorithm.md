# Wells PE score and PERC

Two paired tools for the workup of suspected acute pulmonary embolism, used in sequence: Wells PE for pretest probability, then PERC for low-probability patients.

## Wells PE score

Derived: Wells 2000 (*Thromb Haemost*); validated: Wells 2001 (*Ann Intern Med*). Endorsed in ESC 2019 (Konstantinides).

### Items

| Item | Points |
|---|---|
| Clinical signs and symptoms of DVT (minimum: leg swelling and pain with palpation of deep veins) | +3 |
| PE is at least as likely as alternative diagnosis | +3 |
| Heart rate > 100/min | +1.5 |
| Immobilization (≥3 days) or surgery in past 4 weeks | +1.5 |
| Previous DVT or PE | +1.5 |
| Hemoptysis | +1 |
| Malignancy (treatment within 6 months or palliative) | +1 |

Total range: 0 to 12.5.

### Three-tier interpretation (Wells 2000 original)

| Score | Risk band | Approximate prevalence (Wells 2001) |
|---|---|---|
| < 2 | Low | ~3.6% |
| 2 to 6 | Moderate | ~20.5% |
| > 6 | High | ~66.7% |

### Two-tier interpretation (current standard)

| Score | Risk band |
|---|---|
| ≤ 4 | PE unlikely |
| > 4 | PE likely |

### Recommended actions

| Two-tier | Three-tier | Action |
|---|---|---|
| Unlikely | Low | Apply PERC (see below). If PERC fails, obtain sensitive D-dimer; CT-PA if positive. |
| Unlikely | Moderate | Sensitive D-dimer; CT-PA if positive. |
| Likely | High | CT-PA directly. D-dimer is not required for rule-out at this probability. |

The two-tier and three-tier interpretations sometimes disagree at the score = 4 boundary; the current standard is the two-tier interpretation.

## PERC

Derived: Kline 2004 (*J Thromb Haemost*); multinational validation: Kline 2008 (*J Thromb Haemost*).

### Criteria

All eight must be **negative** to rule out PE:

| Criterion | Source |
|---|---|
| Age < 50 | Kline 2004 |
| Heart rate < 100 | Kline 2004 |
| SpO₂ ≥ 95% on room air | Kline 2004 |
| No hemoptysis | Kline 2004 |
| No estrogen use (oral contraceptives, hormone replacement) | Kline 2004 |
| No prior DVT or PE | Kline 2004 |
| No unilateral leg swelling | Kline 2004 |
| No recent surgery or trauma requiring hospitalization in past 4 weeks | Kline 2004 |

### Use restriction

PERC may be used **only** when pretest probability is low (either Wells PE < 2, two-tier "unlikely", or clinical gestalt of < 15% probability). Applying PERC at higher pretest probabilities misses PE.

### Decision

| Pretest probability | All 8 criteria negative? | Action |
|---|---|---|
| Low | Yes | PE excluded; no further testing required. |
| Low | No (≥1 positive) | PERC fails; obtain sensitive D-dimer; CT-PA if positive. |
| Not low | Any | Do not apply PERC. Use Wells PE / D-dimer pathway. |

## Implementation note

The two-tier and three-tier Wells interpretations both reference the same score function. The PERC function requires an explicit `pretest_probability_is_low: bool` parameter; if False, the function returns `pe_ruled_out=False` and routes the caller to the Wells / D-dimer pathway instead of PERC.

## Citations

Short tags map to entries in [references.bib](references.bib):

- `Wells 2000` — Wells PS et al., *Thromb Haemost* 2000.
- `Wells 2001` — Wells PS et al., *Ann Intern Med* 2001.
- `Kline 2004` — Kline JA et al., *J Thromb Haemost* 2004.
- `Kline 2008` — Kline JA et al., *J Thromb Haemost* 2008.
- `Konstantinides 2019` — ESC 2019 PE guideline.

## Revised Geneva score (alternative pretest probability)

A fully clinical alternative to Wells PE (no gestalt item). Derived: Le Gal 2006 (*Ann Intern Med*).

| Item | Points |
|---|---|
| Age > 65 | +1 |
| Previous DVT or PE | +3 |
| Surgery (GA) or lower-limb fracture within 1 month | +2 |
| Active malignancy | +2 |
| Unilateral lower-limb pain | +3 |
| Hemoptysis | +2 |
| Heart rate 75–94 | +3 |
| Heart rate ≥ 95 | +5 |
| Pain on lower-limb deep venous palpation and unilateral edema | +4 |

Bands (approx. PE prevalence, Le Gal 2006): 0–3 low (~8%), 4–10 intermediate (~29%), ≥ 11 high (~74%).

- `Le Gal 2006` — Le Gal G et al., *Ann Intern Med* 2006 (revised Geneva score).
