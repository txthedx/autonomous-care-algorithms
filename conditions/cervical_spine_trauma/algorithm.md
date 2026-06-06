# NEXUS and the Canadian C-Spine Rule

Two decision rules for cervical-spine imaging after blunt trauma, implemented as separate functions.

- **NEXUS low-risk criteria** — Hoffman 2000 (*N Engl J Med*).
- **Canadian C-Spine Rule (CCR)** — Stiell 2001 (*JAMA*).
- **Head-to-head comparison** — Stiell 2003 (*N Engl J Med*): the CCR was more sensitive (99.4% vs 90.7%) and more specific (45.1% vs 36.8%) than NEXUS for clinically important cervical-spine injury, and would have resulted in lower imaging rates.

## NEXUS low-risk criteria

Cervical-spine imaging can be deferred only if **all five** criteria are satisfied:

| # | Criterion (satisfied when …) |
|---|---|
| 1 | No posterior midline cervical-spine tenderness |
| 2 | No focal neurologic deficit |
| 3 | Normal level of alertness |
| 4 | No evidence of intoxication |
| 5 | No painful distracting injury |

If any criterion is not satisfied (a risk finding is present), imaging is indicated.

## Canadian C-Spine Rule

Applies to alert (GCS 15) and stable adults with blunt trauma. Three sequential steps:

### Step 1 — high-risk factors (mandate radiography)

- Age ≥ 65 years
- Dangerous mechanism
- Paresthesias in the extremities

If any is present → **image** (do not test range of motion).

**Dangerous mechanism:** fall from ≥ 1 m or 5 stairs; axial load to the head (e.g., diving); high-speed MVC (> 100 km/h), rollover, or ejection; motorized recreational-vehicle crash; bicycle collision.

### Step 2 — low-risk factors (allow safe range-of-motion assessment)

- Simple rear-end MVC
- Sitting position in the emergency department
- Ambulatory at any time since injury
- Delayed onset of neck pain
- Absence of midline cervical-spine tenderness

If **none** is present → **image**. Otherwise proceed to step 3.

**Simple rear-end MVC excludes:** pushed into oncoming traffic; hit by a bus or large truck; rollover; hit by a high-speed vehicle.

### Step 3 — active rotation

Is the patient able to actively rotate the neck **45° to the left and right**?

- Able → **no imaging**.
- Unable → **image**.

## Performance comparison

The Canadian C-Spine Rule generally **outperforms NEXUS** (Stiell 2003): higher sensitivity for clinically important injuries and higher specificity, translating into fewer images for the same safety. Both are rule-out tools designed for very high sensitivity at the expense of specificity, and both depend on correct patient selection.

## Use restrictions

Both rules apply to **alert, stable patients with blunt trauma**. They do **not** apply to penetrating trauma, a reduced level of consciousness (GCS < 15), or unstable patients. The Canadian C-Spine Rule additionally excludes patients **under 16 years**, those with acute paralysis, known vertebral disease, or previous cervical-spine surgery. Pediatric performance of NEXUS is less well established than in adults.

## Implementation note

NEXUS is modelled with the five risk findings as booleans; imaging is indicated if any is present. The Canadian C-Spine Rule is modelled as the literal three-step algorithm, short-circuiting at the first step that determines the outcome; the result reports which step decided it (`determining_step`) and whether range-of-motion was reached (`rotation_assessed`), since rotation is only tested when steps 1 and 2 are passed. "Dangerous mechanism" is taken as a single clinician-judged boolean, with its definition documented above.

## Citations

Short tags map to entries in [references.bib](references.bib):

- `Hoffman 2000` — Hoffman JR et al., *N Engl J Med* 2000 (NEXUS).
- `Stiell 2001` — Stiell IG et al., *JAMA* 2001 (Canadian C-Spine Rule).
- `Stiell 2003` — Stiell IG et al., *N Engl J Med* 2003 (CCR vs NEXUS comparison).
