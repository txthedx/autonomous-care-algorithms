# Changelog

All notable changes to this project will be documented in this file. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [semantic versioning](https://semver.org/) with the conventions described in [docs/methodology.md](docs/methodology.md).

## [0.20.0] — 2026-06-07

### Added
- **MCP server (`engine/mcp_server.py`)** — exposes the engine as Model Context Protocol tools so a Claude-based clinical assistant can call it in real time while drafting a note (Phase 3 of [docs/architecture.md](docs/architecture.md)). Stateless, no storage, no input logging; a *not-a-medical-device* disclaimer on every result.
  - Tools: `list_conditions`, `list_presentations`, `get_condition_schema`, `describe_condition`, `run_algorithm`, `suggest_algorithms`, `run_applicable`.
  - `run_algorithm` returns `{"ok": true, "result": ...}` or `{"ok": false, "error": ..., "missing_inputs": [...]}`, so the assistant can ask the clinician for what's missing rather than failing.
  - The MCP SDK is an **optional extra** (`pip install ".[mcp]"`); the tool logic is plain functions over the registry and dispatch layers, and the SDK is imported lazily, so the core stays standard-library-only and importing the module never requires the SDK. Run with `python -m engine.mcp_server`. See [docs/mcp.md](docs/mcp.md).
- 11 new tests: every tool's behavior (success, missing inputs, unknown condition, out-of-range), plus a server-wiring test (skipped when the SDK is absent) asserting all seven tools register with descriptions and input schemas. Total repo test count: 714.

### Added
- **Engine dispatch (`engine/dispatch.py`)** — applicability over the catalog (Phase 2 of [docs/architecture.md](docs/architecture.md)). Given a flat bag of available structured features, it decides which algorithms can run, runs them, and reports which need more data — optionally narrowed to a clinical presentation. Deterministic and instant.
  - `presentations()` and `by_presentation(tag)` index the catalog by presenting complaint (e.g. "chest pain", "pulmonary embolism").
  - `suggest(features, presentation=None)` ranks every candidate algorithm by how close it is to runnable, reporting `runnable` and `missing_inputs`.
  - `run_applicable(features, presentation=None)` runs every algorithm whose inputs are fully present and returns `applicable` (key, label, result), `needs_more_data` (with missing inputs), and `errors` (inputs an algorithm rejected). Each algorithm reads only the fields it declares, so a broad feature bag drives several rules at once.
- 15 new tests: presentation indexing, applicability ranking, multi-algorithm runs from one feature bag, per-algorithm field projection, missing-data reporting, the out-of-range error path, and presentation filtering. Total repo test count: 703.

### Added
- **Engine registry (`engine/registry.py`)** — the machine-readable catalog and first layer of the clinical decision-support engine (Phase 1 of [docs/architecture.md](docs/architecture.md)). It is the single source of truth for the condition catalog; input schemas are derived by introspection of the `conditions/` dataclasses, so they cannot drift from the implementation.
  - Public API: `condition_keys()`, `list_conditions()`, `get_schema(condition)`, `describe(condition)`, `validate(condition, features)`, `missing_inputs(condition, features)`, and `run(condition, features)`.
  - `get_schema` produces a JSON Schema (boolean / integer / number / string-enum) for each condition's flattened inputs, including multi-dataclass conditions (e.g. the Ottawa rules) and scalar parameters (e.g. PERC's pretest-probability flag). `run` reconstructs the dataclasses, calls the algorithm, and returns a JSON-able result — the operation the MCP server and REST API will wrap.
  - Covers all 24 calculators across the 17 condition modules. The deterministic core in `conditions/` is unchanged and imported lazily; the engine adds no third-party dependencies.
- `engine/` is now packaged and tested (`pyproject.toml` package-find and pytest `testpaths` updated).
- 22 new tests: catalog integrity, a drift guard (every condition module must be registered), schema generation for every condition and every parameter shape, `run`-equals-direct-call equivalence, validation, and JSON-serializability. Total repo test count: 688.

### Added
- Seventeenth condition: **head injury (Canadian CT Head Rule)**.
  - `canadian_ct_head_assessment(features)` — returns whether CT is indicated (any of seven factors present), the high-risk factors present (predicting need for neurosurgical intervention) and medium-risk factors present (predicting clinically important brain injury), a disposition reflecting the triggering tier, and inclusion/exclusion caveats.
  - Five high-risk factors (GCS < 15 at 2 h, suspected open/depressed skull fracture, basal skull fracture sign, vomiting ≥2, age ≥65) and two medium-risk factors (retrograde amnesia ≥30 min, dangerous mechanism).
  - Caveats state the inclusion criteria (minor head injury, GCS 13–15, within 24 h) and the exclusions (age <16, anticoagulation/bleeding disorder, GCS <13, non-traumatic, post-traumatic seizure, focal deficit, unstable vitals, pregnancy).
  - Sources: Stiell 2001 *Lancet* (PMID 11356436, derivation), Stiell 2005 *JAMA* (PMID 16189364, comparison with the New Orleans Criteria).
- 12 new tests covering each of the seven factors, the high- vs medium-risk tier reporting and precedence, the no-factor case, and the output shape. Total repo test count: 666.

Closes #26.

## [0.16.0] — 2026-06-06

### Added
- Sixteenth condition: **cervical-spine trauma (NEXUS low-risk criteria and the Canadian C-Spine Rule)**, implemented as two separate functions.
  - `nexus_assessment(features)` — the five NEXUS low-risk criteria (Hoffman 2000); imaging is indicated unless all five are satisfied. Returns the criteria present, a disposition, and caveats.
  - `canadian_c_spine_assessment(features)` — the three-step Canadian C-Spine Rule (Stiell 2001): high-risk factors (age ≥65, dangerous mechanism, extremity paresthesias) → image; otherwise a low-risk factor must be present to assess range of motion; otherwise → image; otherwise able to rotate the neck 45° left and right → no imaging. Returns the determining step, the high- and low-risk factors present, and whether rotation was assessed.
  - Caveats explicitly exclude penetrating trauma, GCS < 15, and (for the Canadian rule) patients under 16, and note weaker pediatric evidence for NEXUS.
  - Sources: Hoffman 2000 *N Engl J Med* (PMID 10891516), Stiell 2001 *JAMA* (PMID 11597285), Stiell 2003 *N Engl J Med* (PMID 14695411, head-to-head comparison showing the Canadian rule generally outperforms NEXUS).
- 21 new tests covering each NEXUS criterion, every Canadian C-Spine branch and step boundary, step precedence (high-risk overrides low-risk and rotation), that rotation is assessed only at step 3, and the output shape. Total repo test count: 654.

Closes #5.

## [0.15.0] — 2026-06-06

### Added
- Fifteenth condition: **delirium (4AT rapid screen)**.
  - `four_at_assessment(features)` — total score (0–12), per-item breakdown, interpretation band (unlikely 0 / possible cognitive impairment 1–3 / possible delirium ≥4), a narrative action, and population caveats.
  - `four_at_score(features)` and `four_at_component_scores(features)` for the raw total and the per-item (Alertness, AMT4, Attention, Acute change) breakdown.
  - Items are entered as named response levels (a boolean for the acute-change item); items 1 and 4 score 0 or 4, items 2 and 3 score 0–2. The 3/4 cut-off is the pre-specified instrument design.
  - Caveats state the 4AT is a screen, not a diagnostic test, and that a single application does not distinguish delirium from dementia.
  - Sources: Bellelli 2014 *Age Ageing* (PMID 24590568, derivation and validation), Shenkin 2019 *BMC Med* (PMID 31337404, multicentre diagnostic accuracy).
- 27 new tests covering each item at each level, the band boundaries (the 3/4 cut-off, and that alertness or acute change alone reaches "possible delirium"), the maximum score of 12, and the component-sum invariant. Total repo test count: 633.

Closes #17.

## [0.14.0] — 2026-06-06

### Added
- Fourteenth condition: **chronic kidney disease (KDIGO GFR and albuminuria staging)**.
  - `kdigo_assessment(features)` — GFR category (G1–G5), albuminuria category (A1–A3), combined stage label (e.g. `G3bA2`), risk band (low / moderately increased / high / very high) and heat-map colour, a monitoring recommendation, and whether nephrology referral is indicated (G4, G5, or A3).
  - `kdigo_gfr_category()`, `kdigo_albuminuria_category()`, and `kdigo_risk_band()` expose the individual category and heat-map lookups.
  - Takes eGFR (mL/min/1.73 m²) and ACR (mg/mmol, Canadian/SI units) as raw values, plus an explicit `persistent_over_3_months` chronicity flag; staging categories are still reported when chronicity is unconfirmed, but the disposition flags that CKD cannot yet be diagnosed. Negative values raise `ValueError`.
  - The 18-cell risk heat map is encoded explicitly so each combination is directly testable.
  - Sources: KDIGO 2024 *Kidney Int* (105(4S):S117–S314), KDIGO 2012 *Kidney Int Suppl* (3:1–150).
- 52 new tests covering every GFR and albuminuria category boundary, the full 18-cell heat map, referral logic, the chronicity flag, and the validation guards. Total repo test count: 606.

Closes #6.

## [0.13.0] — 2026-06-06

### Added
- Thirteenth condition: **syncope (San Francisco Syncope Rule / CHESS)**.
  - `sfsr_assessment(features)` — applies the five CHESS criteria and returns `high_risk` (True if any criterion present), the positive criteria, the risk band (low / high), a narrative disposition, and population caveats.
  - `sfsr_positive_criteria(features)` returns the labels of the criteria present.
  - Binary rule (no numeric score). The two measured criteria — hematocrit and systolic BP — are entered as raw values with the < 30% and < 90 mmHg thresholds applied internally; the other three are booleans. Out-of-range values raise `ValueError`.
  - Caveats document the screening-not-discharge-guarantee nature, the non-cardiac exclusion, and the lower sensitivity reported in independent external validations.
  - Sources: Quinn 2004 *Ann Emerg Med* (PMID 14747812, derivation), Quinn 2006 *Ann Emerg Med* (PMID 16631985, prospective validation), Sun 2007 *Ann Emerg Med* (PMID 17210201, external validation), Birnbaum 2008 *Ann Emerg Med* (PMID 18282636, failure to validate).
- 22 new tests covering each CHESS criterion, the two threshold boundaries (hematocrit 30%, systolic BP 90), the all-negative low-risk case, multiple positive criteria, disposition and caveat content, and the validation guards. Total repo test count: 554.

Closes #16.

## [0.12.0] — 2026-06-06

### Added
- Twelfth condition: **appendicitis (Alvarado score / MANTRELS)**.
  - `alvarado_assessment(features)` — total score (0–10), contributing factors, risk band (low ≤4 / moderate 5–6 / high ≥7), a narrative disposition, and population caveats.
  - `alvarado_score(features)` and `alvarado_components(features)` for the raw total and the per-component breakdown.
  - The five clinical findings are booleans; temperature, white cell count, and neutrophil percentage are entered as raw values (°C, 10⁹/L, %) with the ≥37.3 °C, >10 ×10⁹/L, and >75% thresholds applied internally. Out-of-range values raise `ValueError`.
  - Caveats note adult-predominant derivation (pediatric performance differs; Samuel 2002) and lower specificity in women of reproductive age.
  - Sources: Alvarado 1986 *Ann Emerg Med* (PMID 3963537, derivation), Ohle 2011 *BMC Med* (PMID 22204638, systematic review), Samuel 2002 *J Pediatr Surg* (PMID 12037754, pediatric score).
- 35 new tests covering each component's weight, the three threshold boundaries (37.3 °C, WBC 10.0, neutrophils 75%), the band cutoffs (4/5 and 6/7), the maximum score of 10, and the validation guards. Total repo test count: 532.

Closes #15.

## [0.11.0] — 2026-06-06

### Added
- Eleventh condition: **upper gastrointestinal bleeding (Glasgow-Blatchford score)**.
  - `glasgow_blatchford_assessment(features)` — total score (0–23), contributing factors, risk band (very low 0 / intermediate 1–5 / high ≥6), an explicit `outpatient_management_candidate` flag (score 0), a narrative disposition, and population caveats.
  - `glasgow_blatchford_score(features)` and `glasgow_blatchford_components(features)` for the raw total and the per-component breakdown.
  - Sex-specific hemoglobin bands; Canadian/SI units (urea mmol/L, hemoglobin g/L). Negative measured values raise `ValueError`.
  - The score-0 outpatient threshold is the conservative default; caveats document the validated ≤ 1 threshold (Stanley 2017).
  - Sources: Blatchford 2000 *Lancet* (PMID 11073021, derivation), Stanley 2009 *Lancet* (PMID 19091393, outpatient validation), Stanley 2017 *BMJ* (PMID 28053181, international comparison and ≤ 1 threshold), NICE CG141.
- 52 new tests covering every urea, sex-specific hemoglobin, and systolic-BP band boundary, each binary marker, the band cutoffs (0/1 and 5/6), score-0 discharge eligibility, the maximum score of 23, and the negative-value guards. Total repo test count: 497.

Closes #7.

## [0.10.0] — 2026-06-05

### Added
- Tenth condition: **chest pain (HEART score)**.
  - `heart_assessment(features)` — total score (0–10), per-component breakdown, risk band (low 0–3 / moderate 4–6 / high 7–10), the approximate 6-week MACE estimate from the Backus 2013 validation cohort, a narrative disposition, and population caveats.
  - `heart_score(features)` and `heart_component_scores(features)` for the raw total and the per-component (History, ECG, Age, Risk factors, Troponin) breakdown.
  - The risk-factor component is derived from the six individual risk-factor booleans plus a `history_of_atherosclerotic_disease` flag, so the +2 atherosclerotic-disease override and the 0 / 1–2 / ≥3 count thresholds are applied in one auditable place. Negative `age_years` raises `ValueError`.
  - Sources: Six 2008 *Neth Heart J* (PMID 18665203, derivation), Backus 2013 *Int J Cardiol* (PMID 23465250, validation and MACE rates), Mahler 2015 *Circ Cardiovasc Qual Outcomes* (PMID 25737484, HEART Pathway trial).
- 41 new tests covering each component's point mapping, the age boundaries (44/45, 64/65), the risk-factor count thresholds and the atherosclerotic-disease override, every band boundary (3/4 and 6/7), disposition and caveat content, the component-sum invariant, and the negative-age guard. Total repo test count: 445.

Closes #4.

## [0.9.0] — 2026-06-02

### Added
- Ninth condition: **pulmonary embolism (Wells PE score and PERC)**.
  - `wells_pe_two_tier(features)` — modified Wells PE interpretation (PE *unlikely* at ≤ 4, *likely* at > 4).
  - `wells_pe_three_tier(features)` — original Wells PE interpretation (low / moderate / high at < 2, 2–6, > 6) with prevalence estimates from Wells 2001.
  - `perc_assessment(features, pretest_probability_is_low)` — eight PERC criteria with an explicit gate: the function refuses to rule out PE when pretest probability is not low, routing instead to the Wells/D-dimer pathway.
  - Sources: Wells 2000 *Thromb Haemost* (PMID 10744147), Wells 2001 *Ann Intern Med* (PMID 11453709), Kline 2004 *J Thromb Haemost* (PMID 15304025), Kline 2008 *J Thromb Haemost* (PMID 18318689), ESC 2019 / Konstantinides (PMID 31504429).
- 51 new tests covering each Wells PE item's contribution, both interpretation boundaries, each PERC criterion, the PERC gate against non-low pretest probability, and the output shape. Total repo test count: 404.

Closes #3.

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
