# Contributing

Thanks for considering a contribution. This project has a narrower scope than most: every clinical rule must be traceable to a primary source, and every implementation must be testable.

## What we accept

- Implementations of **published** clinical scoring systems and guideline-derived algorithms for primary care presenting complaints.
- Improvements to existing algorithms when a newer or more rigorous source supersedes the current citation.
- Test additions, especially boundary cases drawn from published validation studies.
- Documentation, methodology, and disclaimer improvements.

## What we do not accept

- Algorithms based on personal experience, expert opinion that has not been published, or unsourced "best practice" claims.
- Prescriptive outputs (dosing, prescription text, treatment scripts).
- Patient-identifiable data of any kind in code, tests, or examples.
- Marketing language or unsupported superlatives in clinical text.

## Citation requirements

Every clinical threshold, point allocation, and recommendation must cite at least one of:

1. A peer-reviewed primary research paper (PubMed-indexed preferred).
2. A guideline from a recognized society (IDSA, CMAJ-published guideline, NICE, USPSTF, CFPC, AHA/ACC, ADA, equivalent).
3. A regulatory body publication (Health Canada, FDA, EMA, MHRA) where applicable.

Citations belong in three places:

- The module docstring (short form).
- `references.bib` in the condition's folder (BibTeX).
- The condition's `algorithm.md` (with the specific page or section relevant to each rule).

## Pull request checklist

- [ ] Source citations added in module docstring, `references.bib`, and `algorithm.md`.
- [ ] Tests cover scoring boundaries and at least one published validation example.
- [ ] No patient-identifiable data anywhere in the change.
- [ ] Disclaimer reference unchanged or strengthened, never weakened.
- [ ] CHANGELOG entry naming the source and the version of the guideline.
- [ ] Reviewer with primary care or relevant specialty experience tagged.

## Code style

- Python 3.11+, type hints required for public functions.
- Pure functions where possible; avoid hidden state.
- `pytest` for tests. Coverage thresholds will be enforced in CI when set up.
- No external dependencies for the core algorithms (only standard library). Dev tooling may pull dependencies.

## Clinical review

Pull requests touching clinical logic should be reviewed by someone with clinical training in the relevant area. If no qualified reviewer is available, the PR is held until one is.

## Reporting issues

Open an issue describing:

- The condition and the source you believe is misrepresented.
- The specific line, threshold, or recommendation in question.
- The citation that supports your correction.

Security-sensitive issues (none expected, but possible if dependencies are added) should be reported per the standard GitHub private vulnerability reporting flow.
