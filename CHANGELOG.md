# Changelog

All notable changes to this project will be documented in this file. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [semantic versioning](https://semver.org/) with the conventions described in [docs/methodology.md](docs/methodology.md).

## [0.8.0] — 2026-06-02

### Added
- Eighth condition: **deep vein thrombosis (Wells DVT score)**.
  - `wells_dvt_two_tier(features)` — modified Wells (2003) interpretation returning DVT *unlikely* (score ≤ 1) or *likely* (score ≥ 2).
  - `wells_dvt_three_tier(features)` — original Wells (1997) interpretation returning low / moderate / high pretest probability with prevalence estimates from the derivation cohort.
  - Single `WellsDvtFeatures` dataclass with all ten items. The `previously_documented_dvt` item (added in 2003) contributes to the modified score only; the original 1997 score omits it.
  - Negative point for `alternative_diagnosis_at_least_as_likely` (-2) handled correctly across both interpretations.
  - Sources: Wells 1997 *Lancet* (PMID 9428249), Wells 2003 *NEJM* (PMID 14507948), Scarvelis 2006 *CMAJ* (PMID 17060659).
- 42 new tests covering each item's contribution, the -2 alternative-diagnosis penalty, both interpretation boundaries (two-tier 1/2; three-tier 0/1 and 2/3), version-specific scoring (modified vs original), and the output shape. Total repo test count: 353.

Closes #2.

## [0.7.0] — 2026-06-02

### Added
- Seventh condition: **acute knee injury** — Ottawa Knee Rule.
  - `ottawa_knee_assessment(features, applicability)` returns whether the rule applies, whether imaging is indicated, and which of the five criteria triggered.
  - Five criteria implemented per Stiell 1995: age ≥ 55, isolated patellar tenderness, fibular head tenderness, inability to flex knee to 90°, inability to bear weight (four steps) both immediately and at presentation.
  - Population exclusions per Stiell 1995: age under 18, isolated skin injury, gross deformity, decreased consciousness, paraplegia or multiple injuries, re-presentation more than 7 days after injury. Pediatric patients receive an explicit pointer to the Pittsburgh Knee Rules as the validated alternative.
  - Sources: Stiell 1995 (PMID 7574121), Stiell 1996 (PMID 8594242), Bachmann 2004 systematic review (PMID 14734335), Bauer 1995 (PMID 8530779) referenced for the pediatric Pittsburgh alternative.
- 33 new tests covering each applicability factor, applicability precedence, the age-55 boundary (54 vs 55), each individual criterion, and the output shape. Total repo test count: 311.

Closes #8.

## [0.6.0] — 2026-06-02

### Added
- Sixth condition: **acute ankle and midfoot injury** — Ottawa Ankle and Foot Rules.
  - `ottawa_ankle_assessment` for the malleolar zone (lateral malleolus, medial malleolus, weight-bearing criteria).
  - `ottawa_foot_assessment` for the midfoot zone (5th metatarsal base, navicular, weight-bearing criteria).
  - Shared `ApplicabilityFactors` dataclass enforces the population exclusions from Stiell 1992 (age under 18, intoxication, distracting injury, decreased sensation, gross deformity, isolated skin injury, head injury). When any factor is present, `rule_applies` is False and the recommendation defers to clinical judgment.
  - Sources: Stiell 1992 (PMID 1554175), Stiell 1993 (PMID 8433468), Bachmann 2003 systematic review (PMID 12595378), Plint 1999 pediatric validation (PMID 10530659).
- 39 new tests covering each applicability factor, applicability precedence, zone-pain gating, each individual criterion, and the output shape. Total repo test count: 278.

Closes #1.

## [0.5.0] — 2026-06-01

### Added
- Fifth condition: **uncomplicated UTI in women** (Bent 2002 decision rule).
  - Two-stage logic: complicating-factors gate first, then the Bent symptom-count and vaginal-symptom decision tree.
  - Five probability bands: `not_applicable_complicated`, `alternative_diagnoses_considered`, `low`, `intermediate`, `high`.
  - Recommendations align with Bent 2002 and the IDSA/ESCMID 2010 guideline (Gupta 2011).
  - Sources: Bent 2002 JAMA (PMID 12020306), Gupta 2011 / IDSA (PMID 21292654), NICE NG109 (2018).
- 34 new tests covering each complicating factor, precedence between complicating factors and vaginal symptoms, symptom-count boundaries (0 / 1 / 2+), each cardinal symptom independently, and abstract clinical vignettes. Total repo test count: 239.

## [0.4.0] — 2026-06-01

### Added
- Fourth condition: **atrial fibrillation stroke and bleeding risk**.
  - **CHA₂DS₂-VASc** stroke risk score (0 to 9) with annual stroke risk bands from Lip 2010 and the ESC 2020 sex-stratified anticoagulation recommendation framing (male 0 / 1 / ≥ 2; female 0–1 / 2 / ≥ 3).
  - **HAS-BLED** bleeding risk score (0 to 9) with the explicit ESC 2020 framing that high HAS-BLED does **not** justify withholding anticoagulation; output includes the list of currently-positive modifiable factors.
  - Algorithm doc describes the Canadian CCS 2020 CHADS-65 frame and how to map a CHA₂DS₂-VASc result to it.
  - Sources: Lip 2010 (PMID 19762550), Pisters 2010 (PMID 20299623), ESC 2020 / Hindricks 2021 (PMID 32860505), CCS 2020 / Andrade 2020.
- 50 new tests, including component contributions, age-band exclusivity (CHA₂DS₂-VASc), age threshold strictness for HAS-BLED (65 vs 66), sex-stratified anticoagulation thresholds, modifiable-factor enumeration, and the ESC do-not-withhold language. Total repo test count: 205.

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
