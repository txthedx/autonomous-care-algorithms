# PDE5 inhibitor + nitrate contraindication

A deterministic screen for the absolute, potentially fatal interaction between a phosphodiesterase-5 (PDE5) inhibitor and a nitrate, another nitric-oxide (NO) donor, or a soluble guanylate cyclase (sGC) stimulator.

Nitrates and NO donors raise intracellular cGMP through guanylate cyclase; PDE5 inhibitors block the breakdown of cGMP by PDE5. Together they produce an exaggerated, sustained vasodilatory fall in blood pressure that has caused profound hypotension, myocardial infarction, and death (Schwartz 2010). This is an **absolute** contraindication — there is no safe dose adjustment.

This module exposes two checks.

## 1. Forward screen — `pde5i_nitrate_contraindication`

Used when a PDE5 inhibitor is being considered.

| Input | Meaning |
|---|---|
| `nitrate_or_no_donor_use` | Organic nitrate (nitroglycerin, isosorbide mono-/dinitrate), nitrite inhalant ("poppers": amyl/butyl/isopropyl nitrite), or other NO donor |
| `sgc_stimulator_use` | Soluble guanylate cyclase stimulator (e.g. riociguat) |

**Rule:** if **either** input is true → `absolute_contraindication` (do not co-prescribe). Otherwise → `no_contraindication_detected` (by this screen).

The sGC-stimulator contraindication is independent of the nitrate one: riociguat with a PDE5 inhibitor is contraindicated for the same cGMP-pathway reason (Adempas label; Schwartz 2010).

## 2. Reverse timing check — `nitrate_timing_after_pde5i`

Used when a nitrate is being considered for someone who has recently taken a PDE5 inhibitor (e.g. acute chest pain). It reports the agent-specific interval beyond which the acute interaction is no longer observed.

| PDE5 inhibitor | Interaction interval | Source |
|---|---|---|
| Sildenafil | 24 h | Schwartz 2010 |
| Vardenafil | 24 h | Schwartz 2010 |
| Avanafil | 12 h | Stendra label |
| Tadalafil | 48 h | Kloner 2003; Schwartz 2010 |

**Rule:** `interval_elapsed = hours_since_last_pde5i_dose >= interval`. While the interval has not elapsed, `nitrate_coadministration_contraindicated` is true. Elapse is **necessary, not sufficient**: a nitrate in a life-threatening situation is given only under close hemodynamic monitoring (Schwartz 2010). `hours_since_last_pde5i_dose` must be zero or positive; a negative value raises `ValueError`.

The tadalafil interval reflects Kloner 2003: the hemodynamic interaction with sublingual nitroglycerin lasted 24 h and was absent at or beyond 48 h. The sildenafil/vardenafil 24 h reflects ~6 half-lives (Schwartz 2010); avanafil 12 h is from its prescribing information (Stendra label).

## Scope and caveats

- This screens **one** interaction; it is not a full medication-interaction, contraindication, or service-eligibility review.
- Drug exposure (whether the patient takes a nitrate, NO donor, or sGC stimulator) is a clinician/intake judgement supplied as input; the screen does not establish it.
- Fixed intervals assume standard pharmacokinetics; hepatic/renal impairment and interacting drugs prolong half-lives.
- Outputs are contraindication verdicts and timing flags — not prescriptions, doses, or routes. The screen supports, and does not replace, clinical judgement. See [DISCLAIMER.md](../../DISCLAIMER.md).

## Citations

Short tags map to entries in [references.bib](references.bib):

- `Schwartz 2010` — Schwartz BG, Kloner RA, *Circulation* 2010 (mechanism; nitrate and NO-donor contraindication; sildenafil/vardenafil 24 h and tadalafil 48 h intervals).
- `Kloner 2003` — Kloner RA et al., *J Am Coll Cardiol* 2003 (tadalafil–nitrate time course: interaction lasts 24 h, absent by 48 h).
- `Stendra label` — U.S. FDA STENDRA (avanafil) prescribing information (12 h interval).
- `Adempas label` — U.S. FDA ADEMPAS (riociguat) prescribing information (sGC stimulator + PDE5 inhibitor contraindicated).
