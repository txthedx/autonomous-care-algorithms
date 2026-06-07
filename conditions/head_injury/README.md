# Head injury: Canadian CT Head Rule

The **Canadian CT Head Rule** (Stiell 2001) identifies which adults with minor head injury need CT of the head. It is a highly sensitive rule-out tool that safely reduces unnecessary imaging. It pairs naturally with the [cervical-spine trauma](../cervical_spine_trauma) module.

## Clinical context

Most patients with minor head injury have no clinically important brain injury, yet CT is frequently ordered. The rule structures the decision: CT is required only when at least one of seven factors is present. The five **high-risk** factors predict the need for **neurosurgical intervention**; the two **medium-risk** factors add detection of **clinically important brain injury** on CT.

## Scope of this module

- `canadian_ct_head_assessment` — returns whether CT is indicated, the high- and medium-risk factors present, a disposition, and inclusion/exclusion caveats.

It does **not**:

- Apply to patients outside the validated population (see caveats) — notably under-16s, anticoagulated patients or those with a bleeding disorder, GCS < 13, or non-traumatic presentations.
- Diagnose or exclude brain injury definitively.
- Replace clinical judgement.

See [DISCLAIMER.md](../../DISCLAIMER.md).

## Criteria

CT head is indicated if **any** of the following is present.

**High risk (need for neurosurgical intervention):**
1. GCS < 15 at 2 hours after injury
2. Suspected open or depressed skull fracture
3. Any sign of basal skull fracture (hemotympanum, raccoon eyes, CSF otorrhea/rhinorrhea, Battle's sign)
4. Vomiting ≥ 2 episodes
5. Age ≥ 65 years

**Medium risk (clinically important brain injury on CT):**
6. Retrograde amnesia to the event ≥ 30 minutes
7. Dangerous mechanism (pedestrian struck by a motor vehicle, occupant ejected from a motor vehicle, or fall from an elevation of ≥ 3 feet / 5 stairs)

## Applies to / does not apply to

**Applies to** minor head injury (witnessed loss of consciousness, definite amnesia, or witnessed disorientation) with an initial ED GCS of 13–15 and injury within the past 24 hours.

**Does not apply to** age < 16; anticoagulant use or bleeding disorder; non-traumatic cases; GCS < 13; obvious open skull fracture; post-traumatic seizure; focal neurologic deficit; unstable vital signs; or pregnancy.

## Inputs

| Input | Type |
|---|---|
| `gcs_below_15_at_2_hours` | bool |
| `suspected_open_or_depressed_skull_fracture` | bool |
| `sign_of_basal_skull_fracture` | bool |
| `vomiting_2_or_more_episodes` | bool |
| `age_65_or_older` | bool |
| `retrograde_amnesia_30_min_or_more` | bool |
| `dangerous_mechanism` | bool |

## Outputs

- `ct_indicated` (bool).
- `high_risk_factors_present`, `medium_risk_factors_present` (tuples of labels).
- `recommended_action`, `rationale`.
- `population_caveats`, `citations`.

## Usage

```python
from conditions.head_injury import (
    CanadianCtHeadFeatures,
    canadian_ct_head_assessment,
)

features = CanadianCtHeadFeatures(
    gcs_below_15_at_2_hours=False,
    suspected_open_or_depressed_skull_fracture=False,
    sign_of_basal_skull_fracture=False,
    vomiting_2_or_more_episodes=False,
    age_65_or_older=True,
    retrograde_amnesia_30_min_or_more=False,
    dangerous_mechanism=False,
)
result = canadian_ct_head_assessment(features)
print(result.ct_indicated, result.high_risk_factors_present)
# True ('age 65 or older',)
```

## See also

- [algorithm.md](algorithm.md) — criteria with citations and the validation comparison.
- [references.bib](references.bib) — full bibliographic entries.
- [tests/](tests/) — boundary tests.
