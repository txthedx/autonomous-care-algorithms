# PDE5 inhibitor + nitrate contraindication

A deterministic medication-safety screen for the absolute contraindication between phosphodiesterase-5 (PDE5) inhibitors and nitrates, other nitric-oxide (NO) donors, or soluble guanylate cyclase (sGC) stimulators.

## Clinical context

PDE5 inhibitors (sildenafil, vardenafil, avanafil, tadalafil) and nitrates act on the same nitric-oxide–cGMP pathway from opposite ends: nitrates and NO donors raise cGMP, PDE5 inhibitors stop its breakdown. Given together they cause exaggerated, prolonged vasodilation and severe hypotension, with reported myocardial infarction and death (Schwartz 2010). The combination is an **absolute** contraindication with no safe dose adjustment. sGC stimulators (e.g. riociguat) are contraindicated with PDE5 inhibitors for the same reason (Adempas label).

The interaction is time-dependent in the other direction: after a PDE5-inhibitor dose, a nitrate must be withheld for an agent-specific interval — sildenafil/vardenafil 24 h, avanafil 12 h, tadalafil 48 h — and then used only under hemodynamic monitoring if medically necessary (Kloner 2003; Schwartz 2010; Stendra label).

## Scope

- **In scope:** a yes/no contraindication screen when a PDE5 inhibitor is being considered, and an agent-specific timing check when a nitrate is being considered after a recent PDE5-inhibitor dose.
- **Out of scope:** any other drug interaction, cardiovascular eligibility for sexual activity, service- or jurisdiction-level prescribing eligibility, and prescriptions, doses, or routes. This is one focused safety check, not a full review.

## Inputs and outputs

### `pde5i_nitrate_contraindication`

| Input (`Pde5iNitrateFeatures`) | Type | Meaning |
|---|---|---|
| `nitrate_or_no_donor_use` | bool | Organic nitrate, nitrite inhalant ("poppers"), or other NO donor in use |
| `sgc_stimulator_use` | bool | sGC stimulator (e.g. riociguat) in use |

| Output (`Pde5iNitrateResult`) | Meaning |
|---|---|
| `verdict` | `absolute_contraindication` or `no_contraindication_detected` |
| `contraindicated` | True when the verdict is an absolute contraindication |
| `triggering_agents` | Which agent classes triggered the verdict |
| `recommended_action`, `rationale`, `population_caveats`, `citations` | Narrative and provenance |

### `nitrate_timing_after_pde5i`

| Input (`NitrateTimingFeatures`) | Type | Meaning |
|---|---|---|
| `pde5_inhibitor` | `sildenafil` / `vardenafil` / `avanafil` / `tadalafil` | Agent last taken |
| `hours_since_last_pde5i_dose` | float (≥ 0) | Hours since the last dose |

| Output (`NitrateTimingResult`) | Meaning |
|---|---|
| `interaction_interval_hours` | Agent-specific interval (24 / 24 / 12 / 48 h) |
| `interval_elapsed` | True if elapsed time reaches the interval |
| `nitrate_coadministration_contraindicated` | True while the interval has not elapsed |
| `recommended_action`, `rationale`, `population_caveats`, `citations` | Narrative and provenance |

A negative `hours_since_last_pde5i_dose` raises `ValueError`.

## Usage

```python
from conditions.pde5i_nitrate import (
    NitrateTimingFeatures,
    Pde5iNitrateFeatures,
    nitrate_timing_after_pde5i,
    pde5i_nitrate_contraindication,
)

# Forward screen: a PDE5 inhibitor is being considered.
screen = pde5i_nitrate_contraindication(
    Pde5iNitrateFeatures(nitrate_or_no_donor_use=True, sgc_stimulator_use=False)
)
print(screen.verdict, screen.triggering_agents)
# absolute_contraindication ('nitrate or nitric-oxide donor',)

# Reverse timing: a nitrate is being considered after a recent dose.
timing = nitrate_timing_after_pde5i(
    NitrateTimingFeatures(pde5_inhibitor="tadalafil", hours_since_last_pde5i_dose=36.0)
)
print(timing.interval_elapsed, timing.nitrate_coadministration_contraindicated)
# False True
```

## Citations

See [references.bib](references.bib) and [algorithm.md](algorithm.md). Primary sources: Schwartz 2010 (*Circulation*), Kloner 2003 (*J Am Coll Cardiol*), and the U.S. FDA STENDRA (avanafil) and ADEMPAS (riociguat) prescribing information.

Not a medical device. See [DISCLAIMER.md](../../DISCLAIMER.md).
