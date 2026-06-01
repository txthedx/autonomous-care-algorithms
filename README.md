# autonomous-care-algorithms

Open-source, citation-backed clinical decision algorithms for the most common primary care presentations. Implementations follow published scoring systems and society guidelines, with every clinical rule traceable to a primary reference.

## Status

Early-stage. The first implemented algorithm is **acute pharyngitis** (Centor / McIsaac scoring, IDSA 2012-aligned interpretation). The roadmap targets the 50 most common primary care presenting complaints, prioritized by frequency in Canadian and US family practice.

> **Important: This is not a medical device.** This software does not provide medical advice, diagnosis, or treatment. It is provided for research, education, and discussion. See [DISCLAIMER.md](DISCLAIMER.md) before using or referencing this code in any clinical context.

## Why this exists

Most "AI in primary care" projects either generate unsourced advice or wrap proprietary guideline content. The goal here is the opposite: small, deterministic, auditable implementations of algorithms that are already published, with citations baked into the code and tests.

Each algorithm aims to be:

1. **Traceable** — every threshold, point, and recommendation cites a peer-reviewed paper or society guideline.
2. **Testable** — pure functions with unit tests covering published scoring boundaries.
3. **Versioned** — when a guideline updates, the algorithm version increments and the changelog records the source.
4. **Bounded** — outputs are scores and recommendation bands, not diagnoses or prescriptions.

See [docs/methodology.md](docs/methodology.md) for how algorithms are sourced, reviewed, and versioned.

## Index of conditions

| Condition | Folder | Source | Status |
|---|---|---|---|
| Acute pharyngitis | [conditions/pharyngitis](conditions/pharyngitis) | McIsaac 1998, 2004; IDSA 2012 | Implemented |

The remaining 49 are tracked in issues and added one at a time.

## Quick start

```bash
git clone https://github.com/txthedx/autonomous-care-algorithms.git
cd autonomous-care-algorithms
pip install -e ".[dev]"
pytest
```

Use the pharyngitis module:

```python
from conditions.pharyngitis.score import PharyngitisFeatures, mcisaac_recommendation

features = PharyngitisFeatures(
    age_years=28,
    history_of_fever=True,
    tonsillar_exudate=True,
    tender_anterior_cervical_nodes=True,
    no_cough=True,
)
rec = mcisaac_recommendation(features)
print(rec.score, rec.action, rec.citations)
```

## Contributing

Clinical contributions require a primary source citation (peer-reviewed paper or recognized society guideline). Implementation contributions require tests covering scoring boundaries. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE). Citations and clinical text remain attributable to their original authors.

## Maintainer

[txthedx](https://github.com/txthedx). Clinical correspondence and erratum reports are welcome via issues.
