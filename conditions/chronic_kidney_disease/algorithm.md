# KDIGO CKD staging

Classification of chronic kidney disease by GFR category and albuminuria category, combined into a risk heat map.

Source: KDIGO 2024 Clinical Practice Guideline (*Kidney Int*), which updates the KDIGO 2012 guideline (*Kidney Int Suppl*). CKD is staged under the "CGA" framework — **C**ause, **G**FR category, **A**lbuminuria category.

## GFR categories (G1–G5)

| Category | eGFR (mL/min/1.73 m²) | Description |
|---|---|---|
| G1 | ≥ 90 | Normal or high |
| G2 | 60–89 | Mildly decreased |
| G3a | 45–59 | Mildly to moderately decreased |
| G3b | 30–44 | Moderately to severely decreased |
| G4 | 15–29 | Severely decreased |
| G5 | < 15 | Kidney failure |

GFR boundaries are applied as: ≥ 90 → G1; 60–89 → G2; 45–59 → G3a; 30–44 → G3b; 15–29 → G4; < 15 → G5.

## Albuminuria categories (A1–A3)

| Category | ACR (mg/mmol) | ACR (mg/g) | Description |
|---|---|---|---|
| A1 | < 3 | < 30 | Normal to mildly increased |
| A2 | 3–30 | 30–300 | Moderately increased |
| A3 | > 30 | > 300 | Severely increased |

This module takes ACR in mg/mmol. Boundaries: < 3 → A1; 3–30 → A2; > 30 → A3.

## Risk heat map

The GFR and albuminuria categories combine into four risk bands (KDIGO colours in parentheses):

| GFR \ Albuminuria | A1 | A2 | A3 |
|---|---|---|---|
| G1 | low (green) | moderately increased (yellow) | high (orange) |
| G2 | low (green) | moderately increased (yellow) | high (orange) |
| G3a | moderately increased (yellow) | high (orange) | very high (red) |
| G3b | high (orange) | very high (red) | very high (red) |
| G4 | very high (red) | very high (red) | very high (red) |
| G5 | very high (red) | very high (red) | very high (red) |

## Monitoring and referral

Recommended minimum monitoring frequency rises with the risk band: low and moderately increased — at least yearly; high — at least twice yearly; very high — at least three times yearly (more often in advanced disease).

Nephrology referral is indicated for **G4–G5** (eGFR < 30) or **A3** (severe albuminuria), and also — per KDIGO, beyond what this module computes — for rapidly progressive CKD, persistent hematuria, suspected hereditary kidney disease, refractory hypertension, or recurrent nephrolithiasis.

## Chronicity and the G1/G2 caveat

CKD requires abnormalities of kidney structure or function present for **more than three months**. This module takes an explicit `persistent_over_3_months` flag; when it is false, the staging categories are still reported but the disposition notes that chronicity must be confirmed and acute kidney injury excluded before diagnosing CKD.

G1 and G2 are CKD **only** when another marker of kidney damage is present (albuminuria, urine-sediment abnormalities, electrolyte or histologic abnormalities, structural abnormalities, or a history of transplantation). G1A1 or G2A1 without such a marker is not CKD.

## Implementation note

The eGFR and ACR are entered as raw values, and the category boundaries are applied internally. The heat map is encoded as an explicit mapping of all 18 (GFR, albuminuria) combinations to risk bands, so each cell is directly testable. Negative eGFR or ACR raises `ValueError`.

## Citations

Short tags map to entries in [references.bib](references.bib):

- `KDIGO 2024` — KDIGO 2024 CKD Guideline, *Kidney Int* 2024 (current).
- `KDIGO 2012` — KDIGO 2012 CKD Guideline, *Kidney Int Suppl* 2013 (the heat-map framework).
