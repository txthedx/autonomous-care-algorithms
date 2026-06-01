# Changelog

All notable changes to this project will be documented in this file. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [semantic versioning](https://semver.org/) with the conventions described in [docs/methodology.md](docs/methodology.md).

## [0.3.0] — 2026-06-01

### Added
- Third condition: **community-acquired pneumonia severity**.
  - **CRB-65** (no labs, primary care first-line): four-criterion clinical score with low/moderate/high severity bands and Lim 2003 mortality estimates.
  - **CURB-65** (with serum urea): five-criterion score with three severity bands plus ICU-consideration language at scores 4 and 5.
  - Both scores explicitly remind the user to synthesize with factors the score does not capture: oxygenation, radiographic extent, comorbidities, social factors, pregnancy.
  - Sources: Lim 2003 (PMID 12728155), BTS 2009 (PMID 19783532), Mandell 2007 / IDSA-ATS (PMID 17278083), NICE NG138 (2019).
- **Continuous integration:** GitHub Actions workflow runs pytest on Python 3.11 and 3.12 for every push and PR to main.
- README status badge (test run state) and language/license badges.
- 64 new tests, including threshold-boundary tests (urea 7.0 vs 7.01, RR 29 vs 30, SBP 89 vs 90, DBP 60 vs 61, age 64 vs 65). Total repo test count: 155.

## [0.2.0] — 2026-06-01

### Added
- Second condition: **acute and subacute low back pain**.
  - Red flag screen with three urgency bands (emergency / high-concern / moderate) and explicit category assignment per feature. Sources: Downie 2013 (PMID 24335669), Henschke 2013 Cochrane (PMID 23450586), Verhagen 2016 (PMID 27376890), NICE NG59 (2020).
  - STarT Back Screening Tool with total score (0 to 9), psychosocial subscale (0 to 5), and validated low/medium/high stratification. Sources: Hill 2008 (PMID 18438893), Hill 2011 Lancet RCT (PMID 21963002).
- Index updated; usage example for the low back pain modules added to README.

## [0.1.0] — 2026-06-01

### Added
- Repository scaffold: README, DISCLAIMER, CONTRIBUTING, methodology, MIT license.
- First condition: **acute pharyngitis** with McIsaac (modified Centor) scoring and IDSA 2012-aligned recommendation bands.
  - Sources: Centor 1981 (PMID 6763125), McIsaac 1998 (PMID 9475915), McIsaac 2004 (PMID 15069046), Shulman 2012 / IDSA (PMID 22965026).
  - 36 unit tests covering Centor points, age adjustment, score range, invalid input, recommendation bands, and abstract clinical vignettes.
- `pyproject.toml` for editable install and pytest configuration.
