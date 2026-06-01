# Methodology

How algorithms in this repository are selected, sourced, implemented, reviewed, and versioned.

## Selection

The roadmap targets the **50 most common primary care presenting complaints** in Canadian and US family practice. The reference list for selection is drawn from published frequency studies of family medicine encounters, with priority given to:

1. Presentations where a well-validated published scoring system exists.
2. Presentations where antibiotic, imaging, or referral overuse is a documented problem and a decision rule can reduce it.
3. Presentations where the rule is genuinely deterministic and not a thin wrapper over clinical gestalt.

Conditions that are predominantly handled by gestalt without a published rule are deferred.

## Sourcing

Each algorithm must have a **primary source** before implementation begins:

- Peer-reviewed primary research, with PubMed ID recorded.
- A recognized society guideline (IDSA, NICE, CMAJ-published Canadian guideline, USPSTF, CFPC, AHA/ACC, ADA, equivalent).
- A regulatory publication where applicable (Health Canada, FDA, EMA).

When multiple sources conflict, the most recent guideline-level source from a body with jurisdictional relevance to the maintainer takes precedence, and the conflict is recorded in `algorithm.md`.

## Implementation

Each condition lives under `conditions/<name>/` with the following layout:

```
conditions/<name>/
├── README.md          # clinical context, scope, when to use
├── algorithm.md       # the rule, with citations per threshold
├── score.py           # pure functions, type-hinted, no side effects
├── tests/
│   └── test_score.py  # boundary tests + published validation cases
└── references.bib     # BibTeX for all cited sources
```

Implementation rules:

- Public functions are pure and type-hinted.
- Inputs are explicit data classes, not loose argument lists.
- Outputs include the **score**, the **probability band** (where the source provides one), the **recommended action**, the **rationale**, and the **citations** that justify it.
- No prescription text. No drug doses. No patient-identifiable examples.

## Testing

Each algorithm ships with tests that cover:

1. Every additive term and every age (or other) adjustment.
2. The full score range (e.g., -1 to 5 for McIsaac).
3. Recommendation thresholds at each boundary.
4. Invalid input (negative ages, missing required fields).
5. At least one validation case structured to match a published worked example, where one exists.

Tests should fail loudly if a clinical threshold is changed without a corresponding citation update.

## Clinical review

Pull requests that change clinical logic require review by someone with relevant clinical training. The reviewer's name and role are recorded in the PR. If no qualified reviewer is available, the PR waits.

## Versioning

The repository uses semantic versioning with the following meaning for **clinical** changes:

- **Major** — the recommended action at one or more scores changes, or a new source supersedes the previous one.
- **Minor** — new condition added, or additional cited refinements (e.g., a pediatric-specific note).
- **Patch** — implementation fixes, documentation, or test additions with no change to clinical output.

Every change to clinical logic adds a CHANGELOG line naming the source and the version of the guideline driving the change.

## Limits we accept

- Algorithms are population-level rules. They do not capture all individual context.
- Probability bands depend on local prevalence. Reported probabilities are taken from the cited validation studies and are not re-estimated.
- This project does not perform external validation. Anyone using these algorithms in a new population is responsible for confirming applicability.
