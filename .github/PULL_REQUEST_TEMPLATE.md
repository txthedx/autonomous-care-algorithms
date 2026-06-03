<!-- Thanks for contributing. The checklist below mirrors CONTRIBUTING.md. -->

## Summary

<One paragraph describing what this PR does and why.>

Closes #<issue number>.

## What this adds (or changes)

- ...
- ...

## Sources

<List the primary sources cited for any clinical thresholds or recommendations, with PMID/DOI.>

## Test plan

- [ ] `pytest` passes locally
- [ ] CI passes on Python 3.11 and 3.12
- [ ] Tests cover every individual scoring criterion or decision branch added
- [ ] At least one validated clinical scenario test where the source provides a worked example
- [ ] README index updated (if a new condition)
- [ ] CHANGELOG entry under a new version
- [ ] Version bumped in `pyproject.toml` (if user-facing behaviour changes)

## Disclaimer

- [ ] Module docstring points to `DISCLAIMER.md`
- [ ] Recommended-action language does **not** prescribe specific drugs, doses, or routes
- [ ] No patient-identifiable data anywhere in the change
- [ ] No language framing the output as diagnosis, treatment, or clinical advice
