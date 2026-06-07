# Canadian CT Head Rule

A highly sensitive rule for deciding which adults with minor head injury need CT of the head.

Derived: Stiell 2001 (*Lancet*), from 3121 adults with minor head injury at 10 Canadian emergency departments. Validation and comparison with the New Orleans Criteria: Stiell 2005 (*JAMA*).

CT is indicated if **any** of seven factors is present — five high-risk and two medium-risk.

## High-risk factors (need for neurosurgical intervention)

| Factor |
|---|
| GCS < 15 at 2 hours after injury |
| Suspected open or depressed skull fracture |
| Any sign of basal skull fracture (hemotympanum, raccoon eyes, CSF otorrhea/rhinorrhea, Battle's sign) |
| Vomiting ≥ 2 episodes |
| Age ≥ 65 years |

The five high-risk factors had 100% sensitivity and 68.7% specificity for the need for neurosurgical intervention (Stiell 2001).

## Medium-risk factors (clinically important brain injury on CT)

| Factor |
|---|
| Retrograde amnesia to the event ≥ 30 minutes |
| Dangerous mechanism: pedestrian struck by a motor vehicle, occupant ejected from a motor vehicle, or a fall from an elevation of ≥ 3 feet / 5 stairs |

Across all seven factors, the rule had 98.4% sensitivity and 49.6% specificity for clinically important brain injury (Stiell 2001).

## Decision

CT is indicated if any high- or medium-risk factor is present. If none is present, CT is not required by the rule.

## Inclusion and exclusion

**Applies to** minor head injury — witnessed loss of consciousness, definite amnesia, or witnessed disorientation — with an initial ED GCS of 13–15 and injury within the past 24 hours.

**Excluded** (the rule was not derived in and does not apply to): age < 16; oral anticoagulant use or a bleeding disorder; non-traumatic cases; GCS < 13; obvious open skull fracture; post-traumatic seizure; focal neurologic deficit; unstable vital signs; pregnancy.

## Performance and comparison

In a head-to-head comparison (Stiell 2005), the Canadian CT Head Rule had higher specificity than the New Orleans Criteria at equivalent (high) sensitivity for clinically important brain injury, implying fewer CTs. Like the cervical-spine rules, it is a high-sensitivity rule-out tool that depends on correct patient selection.

## Implementation note

The seven factors are modelled as booleans; CT is indicated if any is present. The result reports the high-risk and medium-risk factors separately, and the disposition reflects the high-risk (neurosurgical) tier when a high-risk factor is present, otherwise the medium-risk (brain-injury) tier. "Dangerous mechanism" is a single clinician-judged boolean, with its definition documented above.

## Citations

Short tags map to entries in [references.bib](references.bib):

- `Stiell 2001` — Stiell IG et al., *Lancet* 2001 (derivation).
- `Stiell 2005` — Stiell IG et al., *JAMA* 2005 (comparison with the New Orleans Criteria).
