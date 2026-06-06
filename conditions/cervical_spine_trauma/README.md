# Cervical-spine trauma: NEXUS and the Canadian C-Spine Rule

Two validated decision rules for deciding whether cervical-spine imaging is needed after **blunt trauma**: the **NEXUS low-risk criteria** (Hoffman 2000) and the **Canadian C-Spine Rule** (Stiell 2001). Both aim to safely reduce unnecessary imaging in alert, stable patients. In a head-to-head comparison (Stiell 2003), the Canadian C-Spine Rule had higher sensitivity and specificity than NEXUS.

## Clinical context

Most patients imaged for possible cervical-spine injury have no fracture. A sensitive, easy-to-apply rule lets clinicians clear the cervical spine clinically in low-risk patients while reserving imaging for those who need it. These are **rule-out** tools: they are designed for very high sensitivity, accepting lower specificity.

## Scope of this module

- `nexus_assessment` — applies the five NEXUS low-risk criteria and returns whether imaging is indicated and which criteria are present.
- `canadian_c_spine_assessment` — applies the three-step Canadian C-Spine Rule and returns whether imaging is indicated, which step decided it, the high- and low-risk factors present, and whether range-of-motion was assessed.

Neither function:

- Applies to **penetrating** trauma, **GCS < 15**, unstable patients, or (for the Canadian rule) patients **under 16**.
- Diagnoses or excludes injury definitively — only imaging and clinical course do.
- Replaces clinical judgement.

See [DISCLAIMER.md](../../DISCLAIMER.md).

## NEXUS low-risk criteria

Imaging is **not required** only when **all five** criteria are satisfied (none of the risk findings present):

1. No posterior midline cervical-spine tenderness
2. No focal neurologic deficit
3. Normal level of alertness
4. No evidence of intoxication
5. No painful distracting injury

Inputs are the *risk findings* (each `bool`): `posterior_midline_cervical_tenderness`, `focal_neurologic_deficit`, `altered_alertness`, `evidence_of_intoxication`, `distracting_injury`. Imaging is indicated if any is `True`.

## Canadian C-Spine Rule

A three-step algorithm (applies to alert, GCS 15, stable adults):

1. **High-risk factor mandating radiography?** Age ≥ 65, a dangerous mechanism, or paresthesias in the extremities. If yes → image.
2. **Low-risk factor allowing safe range-of-motion assessment?** Simple rear-end MVC, sitting position in the ED, ambulatory at any time, delayed onset of neck pain, or absence of midline tenderness. If none → image.
3. **Able to actively rotate the neck 45° left and right?** If unable → image; if able → no imaging.

**Dangerous mechanism:** fall ≥ 1 m / 5 stairs; axial load to the head (e.g., diving); high-speed MVC (> 100 km/h), rollover, or ejection; motorized recreational-vehicle crash; bicycle collision.

**Simple rear-end MVC excludes:** pushed into oncoming traffic, hit by a bus or large truck, rollover, or hit by a high-speed vehicle.

## Outputs

### NEXUS (`NexusResult`)
- `imaging_indicated` (bool), `risk_findings_present` (tuple), `recommended_action`, `rationale`, `population_caveats`, `citations`.

### Canadian C-Spine (`CanadianCSpineResult`)
- `imaging_indicated` (bool), `determining_step` (`"high_risk_factor"` / `"no_low_risk_factor"` / `"unable_to_rotate"` / `"rule_satisfied"`), `high_risk_factors_present`, `low_risk_factors_present`, `rotation_assessed` (bool), `recommended_action`, `rationale`, `population_caveats`, `citations`.

## Usage

```python
from conditions.cervical_spine_trauma import (
    NexusFeatures, nexus_assessment,
    CanadianCSpineFeatures, canadian_c_spine_assessment,
)

# NEXUS: all criteria satisfied -> no imaging
nexus = nexus_assessment(NexusFeatures(
    posterior_midline_cervical_tenderness=False,
    focal_neurologic_deficit=False,
    altered_alertness=False,
    evidence_of_intoxication=False,
    distracting_injury=False,
))
print(nexus.imaging_indicated)  # False

# Canadian C-Spine: no high-risk, ambulatory, can rotate -> no imaging
ccr = canadian_c_spine_assessment(CanadianCSpineFeatures(
    age_65_or_older=False,
    dangerous_mechanism=False,
    paresthesias_in_extremities=False,
    simple_rear_end_mvc=False,
    sitting_position_in_ed=False,
    ambulatory_at_any_time=True,
    delayed_onset_of_neck_pain=False,
    absence_of_midline_c_spine_tenderness=False,
    able_to_rotate_neck_45_degrees=True,
))
print(ccr.imaging_indicated, ccr.determining_step)  # False rule_satisfied
```

## See also

- [algorithm.md](algorithm.md) — both rules with citations and the performance comparison.
- [references.bib](references.bib) — full bibliographic entries.
- [tests/](tests/) — boundary and branch tests.
