"""PDE5 inhibitor + nitrate / NO-donor / sGC-stimulator contraindication screen.

References:
    Schwartz BG, Kloner RA. Drug interactions with phosphodiesterase-5
        inhibitors used for the treatment of erectile dysfunction or pulmonary
        hypertension. Circulation. 2010;122(1):88-95. PMID: 20606131.
    Kloner RA, Hutter AM, Emmick JT, Mitchell MI, Denne J, Jackson G. Time
        course of the interaction between tadalafil and nitrates. J Am Coll
        Cardiol. 2003;42(10):1855-1860. PMID: 14642699.

Co-administration of a phosphodiesterase-5 (PDE5) inhibitor with an organic
nitrate, another nitric-oxide (NO) donor, or a soluble guanylate cyclase (sGC)
stimulator can cause profound, prolonged hypotension, and has been associated
with myocardial infarction and death (Schwartz 2010). Nitrates and NO donors
raise intracellular cGMP; PDE5 inhibitors block its breakdown; together they
produce an exaggerated, sustained vasodilatory drop in blood pressure. This is
an **absolute** contraindication — there is no safe dose adjustment.

This module provides two deterministic checks:

1. ``pde5i_nitrate_contraindication`` — the forward screen used when a PDE5
   inhibitor is being considered: any concomitant nitrate / NO donor or sGC
   stimulator is an absolute contraindication.
2. ``nitrate_timing_after_pde5i`` — the reverse, time-dependent check used when
   a nitrate is being considered for someone who has recently taken a PDE5
   inhibitor: it reports the agent-specific interval beyond which the acute
   interaction is no longer observed (sildenafil/vardenafil 24 h, avanafil 12 h,
   tadalafil 48 h).

Inputs are structured features (booleans, an agent enum, and a measured number
of hours), never raw clinical notes. Outputs are contraindication verdicts and
timing flags, not prescriptions, doses, or routes. The screen covers only this
single interaction; it is not a full medication-interaction or eligibility
review and supports, rather than replaces, clinical judgement. See DISCLAIMER.md
at the repository root.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ContraindicationVerdict = Literal[
    "absolute_contraindication",
    "no_contraindication_detected",
]

# Phosphodiesterase-5 inhibitors with a published nitrate-interaction interval.
Pde5Inhibitor = Literal["sildenafil", "vardenafil", "avanafil", "tadalafil"]

# Agent-specific interval (hours) after the last PDE5-inhibitor dose beyond which
# the nitrate interaction is no longer observed. Sildenafil and vardenafil:
# ~24 h / 6 half-lives (Schwartz 2010). Avanafil: 12 h (U.S. FDA STENDRA
# prescribing information, NDA 202276). Tadalafil: 48 h — the hemodynamic
# interaction with sublingual nitroglycerin lasted 24 h and was absent at or
# beyond 48 h (Kloner 2003; Schwartz 2010).
_INTERACTION_INTERVAL_HOURS: dict[str, float] = {
    "sildenafil": 24.0,
    "vardenafil": 24.0,
    "avanafil": 12.0,
    "tadalafil": 48.0,
}

_FORWARD_CAVEATS: tuple[str, ...] = (
    "Screens a single, high-consequence interaction; it is not a full "
    "medication-interaction, contraindication, or service-eligibility review.",
    "Nitrates and NO donors include organic nitrates (e.g. nitroglycerin, "
    "isosorbide mononitrate or dinitrate), nitrite-based recreational inhalants "
    "('poppers'; amyl, butyl, or isopropyl nitrite), and other nitric-oxide "
    "donors; sGC stimulators include riociguat. Any of these with a PDE5 "
    "inhibitor is an absolute contraindication (Schwartz 2010; Adempas label).",
    "Whether the patient takes any of these agents is a clinician or intake "
    "judgement supplied as input; this screen does not establish drug exposure.",
    "The contraindication is bidirectional and time-dependent: when a nitrate is "
    "being considered after a recent PDE5-inhibitor dose, use the timing check "
    "for the agent-specific interval during which co-administration remains "
    "contraindicated even in an emergency.",
    "Supports but does not replace clinical judgement; outputs are a "
    "contraindication verdict, not a prescription. See DISCLAIMER.md.",
)

_TIMING_CAVEATS: tuple[str, ...] = (
    "Intervals are the agent-specific times beyond which the acute nitrate "
    "interaction is no longer observed: sildenafil and vardenafil 24 h, "
    "avanafil 12 h, tadalafil 48 h (Schwartz 2010; Kloner 2003; Stendra label).",
    "Elapse of the interval is necessary, not sufficient: if a nitrate is judged "
    "medically necessary in a life-threatening situation, it is given only under "
    "close hemodynamic monitoring (Schwartz 2010).",
    "Half-lives are prolonged by hepatic or renal impairment and by interacting "
    "drugs; the fixed intervals assume standard pharmacokinetics.",
    "Covers only the nitrate / NO-donor / sGC-stimulator interaction; supports "
    "but does not replace clinical judgement. See DISCLAIMER.md.",
)


@dataclass(frozen=True)
class Pde5iNitrateFeatures:
    """Inputs for the forward PDE5-inhibitor contraindication screen.

    Attributes:
        nitrate_or_no_donor_use: The patient uses an organic nitrate or another
            nitric-oxide donor — including nitrite-based recreational inhalants
            ('poppers'). Clinician/intake judgement.
        sgc_stimulator_use: The patient uses a soluble guanylate cyclase
            stimulator (e.g. riociguat). Clinician/intake judgement.
    """

    nitrate_or_no_donor_use: bool
    sgc_stimulator_use: bool


@dataclass(frozen=True)
class Pde5iNitrateResult:
    """Result of the forward contraindication screen.

    Attributes:
        verdict: ``absolute_contraindication`` if any nitrate / NO donor or sGC
            stimulator is present, else ``no_contraindication_detected``.
        contraindicated: True when the verdict is an absolute contraindication.
        triggering_agents: Labels of the agent classes that triggered the
            contraindication (empty when none).
        recommended_action: Narrative recommendation.
        rationale: Short justification.
        population_caveats: Scope and interpretation caveats.
        citations: Source short tags.
    """

    verdict: ContraindicationVerdict
    contraindicated: bool
    triggering_agents: tuple[str, ...]
    recommended_action: str
    rationale: str
    population_caveats: tuple[str, ...]
    citations: tuple[str, ...]


@dataclass(frozen=True)
class NitrateTimingFeatures:
    """Inputs for the reverse, time-dependent nitrate-after-PDE5i check.

    Attributes:
        pde5_inhibitor: The PDE5 inhibitor last taken.
        hours_since_last_pde5i_dose: Hours elapsed since the last dose. Must be
            zero or positive.
    """

    pde5_inhibitor: Pde5Inhibitor
    hours_since_last_pde5i_dose: float


@dataclass(frozen=True)
class NitrateTimingResult:
    """Result of the reverse nitrate-timing check.

    Attributes:
        interaction_interval_hours: The agent-specific interaction interval.
        interval_elapsed: True if the elapsed time reaches the interval.
        nitrate_coadministration_contraindicated: True while the interval has
            not elapsed.
        recommended_action: Narrative recommendation.
        rationale: Short justification.
        population_caveats: Scope and interpretation caveats.
        citations: Source short tags.
    """

    interaction_interval_hours: float
    interval_elapsed: bool
    nitrate_coadministration_contraindicated: bool
    recommended_action: str
    rationale: str
    population_caveats: tuple[str, ...]
    citations: tuple[str, ...]


def pde5i_nitrate_contraindication(
    features: Pde5iNitrateFeatures,
) -> Pde5iNitrateResult:
    """Screen for the PDE5-inhibitor / nitrate-class absolute contraindication.

    Args:
        features: Concomitant-medication features. See `Pde5iNitrateFeatures`.

    Returns:
        A `Pde5iNitrateResult`. The verdict is ``absolute_contraindication`` when
        any nitrate / NO donor or sGC stimulator is present.
    """
    citations = ("Schwartz 2010", "Adempas label")
    triggering: list[str] = []
    if features.nitrate_or_no_donor_use:
        triggering.append("nitrate or nitric-oxide donor")
    if features.sgc_stimulator_use:
        triggering.append("soluble guanylate cyclase stimulator")

    if triggering:
        agents = " and ".join(triggering)
        return Pde5iNitrateResult(
            verdict="absolute_contraindication",
            contraindicated=True,
            triggering_agents=tuple(triggering),
            recommended_action=(
                f"Initiating or co-administering a PDE5 inhibitor is "
                f"contraindicated: concomitant {agents} can cause profound, "
                "prolonged hypotension. This is an absolute contraindication "
                "with no safe dose adjustment; do not co-prescribe."
            ),
            rationale=(
                "A nitrate / NO donor or sGC stimulator is present; combined "
                "with a PDE5 inhibitor this is an absolute contraindication "
                "(cGMP-mediated potentiated vasodilation)."
            ),
            population_caveats=_FORWARD_CAVEATS,
            citations=citations,
        )

    return Pde5iNitrateResult(
        verdict="no_contraindication_detected",
        contraindicated=False,
        triggering_agents=(),
        recommended_action=(
            "No PDE5-inhibitor / nitrate-class contraindication was detected "
            "from the inputs screened. This screen covers only this interaction; "
            "complete the full clinical and contraindication review."
        ),
        rationale=(
            "Neither a nitrate / NO donor nor an sGC stimulator was reported."
        ),
        population_caveats=_FORWARD_CAVEATS,
        citations=citations,
    )


def nitrate_timing_after_pde5i(
    features: NitrateTimingFeatures,
) -> NitrateTimingResult:
    """Report whether the nitrate-interaction interval after a PDE5i has elapsed.

    Args:
        features: The PDE5 inhibitor taken and hours since the last dose. See
            `NitrateTimingFeatures`.

    Returns:
        A `NitrateTimingResult`. While the agent-specific interval has not
        elapsed, nitrate co-administration remains contraindicated.

    Raises:
        ValueError: If `hours_since_last_pde5i_dose` is negative.
    """
    hours = features.hours_since_last_pde5i_dose
    if hours < 0:
        raise ValueError(
            "hours_since_last_pde5i_dose must be zero or positive; "
            f"got {hours}"
        )
    agent = features.pde5_inhibitor
    interval = _INTERACTION_INTERVAL_HOURS[agent]
    elapsed = hours >= interval

    citations = ("Schwartz 2010", "Kloner 2003", "Stendra label")
    if not elapsed:
        return NitrateTimingResult(
            interaction_interval_hours=interval,
            interval_elapsed=False,
            nitrate_coadministration_contraindicated=True,
            recommended_action=(
                f"Nitrate co-administration remains contraindicated: only "
                f"{hours:g} h have elapsed since the last {agent} dose and the "
                f"interaction interval is {interval:g} h. Avoid nitrates; if a "
                "nitrate is judged medically necessary in a life-threatening "
                "situation, give it only after the interval has elapsed and "
                "under close hemodynamic monitoring."
            ),
            rationale=(
                f"{hours:g} h since {agent} is within the {interval:g} h "
                "interaction interval."
            ),
            population_caveats=_TIMING_CAVEATS,
            citations=citations,
        )

    return NitrateTimingResult(
        interaction_interval_hours=interval,
        interval_elapsed=True,
        nitrate_coadministration_contraindicated=False,
        recommended_action=(
            f"The agent-specific interaction interval ({interval:g} h) has "
            f"elapsed: {hours:g} h since the last {agent} dose. The acute "
            "nitrate interaction is no longer expected; any nitrate use still "
            "requires clinical judgement and hemodynamic monitoring."
        ),
        rationale=(
            f"{hours:g} h since {agent} reaches or exceeds the {interval:g} h "
            "interaction interval."
        ),
        population_caveats=_TIMING_CAVEATS,
        citations=citations,
    )
