# Acute and subacute low back pain

Two complementary tools for the primary care assessment of low back pain:

1. **Red flag screening** for serious underlying pathology (cauda equina, malignancy, infection, fracture). Outputs a triage urgency assessment, not a single score.
2. **STarT Back Screening Tool** (Hill 2008; validated in Hill 2011 *Lancet* RCT) for risk-stratified management of non-specific low back pain.

The intended flow is: **red flag screen first**, then **STarT Back** only when no urgent pathology is identified and the presentation is consistent with non-specific low back pain.

## Clinical context

Low back pain is among the most common reasons for primary care visits worldwide and a leading cause of disability. Most acute presentations are non-specific (no identifiable structural cause) and resolve with conservative care. A small but important fraction involves serious underlying pathology that must be identified early. Stratifying patients with non-specific LBP by prognostic risk and matching treatment intensity to that risk reduced disability and saved costs in the Hill 2011 RCT.

## Scope of this module

This module:

- Categorizes red flag features into emergency, high-concern, and moderate-concern bands.
- Scores the STarT Back tool (total 0 to 9, psychosocial subscale 0 to 5) and returns the validated low/medium/high risk stratification.

It does **not**:

- Diagnose any specific cause of low back pain.
- Recommend specific imaging studies, medications, doses, or referral destinations.
- Replace clinical judgment, hands-on examination, or shared decision-making.

See [DISCLAIMER.md](../../DISCLAIMER.md).

## When the rules do not apply

- **STarT Back was derived in non-specific LBP.** Do not use it as a risk stratifier in patients with identified red flag pathology, post-surgical pain, or radiculopathy requiring specific workup.
- **Red flag screening has known limits.** Individual red flags often have high false-positive rates (Downie 2013, BMJ). The tool reports presence; synthesis remains clinical.
- **Trauma protocols supersede this module.** Patients with mechanism-of-injury concerns or fracture risk should be assessed per the relevant trauma protocol.
- **Known specific etiology** (e.g., established cancer with new pain, prior spine surgery, congenital deformity) requires individualized workup.

## Inputs and outputs

### Red flag screen

Input: a `RedFlagFeatures` dataclass with explicit booleans for each screened feature.

Output: a `RedFlagAssessment` with:

- `emergency_flags` — tuple of cauda equina-suggestive features present.
- `high_concern_flags` — tuple of malignancy or infection-suggestive features present.
- `moderate_flags` — tuple of fracture-suggestive or otherwise concerning features present.
- `recommended_urgency` — narrative urgency band.
- `rationale` — short justification.
- `citations` — source tags.

### STarT Back

Input: a `StartBackResponses` dataclass with eight agree/disagree items plus the final bothersome-ness item.

Output: a `StartBackResult` with:

- `total_score` (0 to 9).
- `psychosocial_subscale_score` (0 to 5).
- `risk_band` — `"low"`, `"medium"`, or `"high"`.
- `recommended_management` — narrative aligned to Hill 2011.
- `citations`.

## See also

- [algorithm.md](algorithm.md) — both rules with citations per threshold.
- [references.bib](references.bib) — full bibliographic entries.
- [tests/](tests/) — boundary tests for both modules.
