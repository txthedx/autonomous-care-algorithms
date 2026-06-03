---
name: Add a condition
about: Propose a new clinical algorithm to implement
title: 'Add condition: <name> (<primary source short tag>)'
labels: ['algorithm']
assignees: ''
---

**Domain:** <musculoskeletal | cardiovascular | infectious | renal | endocrine | other>

**Primary source(s):** <Author Year, Journal Volume(Issue):Pages. PMID: NNNNNNNN.>

**Brief rationale for inclusion:**

<2 to 3 sentences on why this condition belongs in the project: frequency in primary care, strength of evidence, decision impact.>

## Proposed module path

`conditions/<name>/`

## Algorithm overview

<Bullet list of the score components or decision logic, with sources per threshold.>

## Population caveats

<Bullet list of excluded populations or settings where the rule does not apply.>

## Acceptance criteria

- [ ] Primary source citation in module docstring, `references.bib`, and `algorithm.md`
- [ ] Tests cover every individual criterion and scoring boundary
- [ ] At least one validated clinical scenario test where the source provides a worked example
- [ ] Disclaimer pointer in module docstring
- [ ] CHANGELOG entry under the new minor version
- [ ] README index updated
- [ ] Linked from the roadmap issue
