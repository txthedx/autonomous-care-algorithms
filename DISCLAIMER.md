# Disclaimer

## Not a medical device

This repository contains software implementations of published clinical scoring systems and decision algorithms. It is **not** a medical device under the meaning of:

- The US **Food, Drug, and Cosmetic Act** as interpreted by the FDA, including the Software as a Medical Device (SaMD) framework.
- The Canadian **Food and Drugs Act** and the **Medical Devices Regulations** (SOR/98-282) as interpreted by Health Canada.
- The **EU Medical Device Regulation 2017/745** (MDR).
- Other applicable national regulatory frameworks.

It has not been reviewed, certified, cleared, or approved by any regulator.

## Not medical advice

The outputs of this software are scores and recommendation bands derived from published literature. They are **not** medical advice, diagnosis, treatment, or a substitute for clinical judgment. Use of these outputs to make clinical decisions about an identified patient is outside the scope of this project and is not endorsed by its maintainers.

## Intended use

This software is intended for:

- Education and training of clinicians and learners.
- Research on the behavior, validation, and limitations of published clinical scoring systems.
- Discussion, comparison, and reproducible re-implementation of decision rules.

It is **not** intended for:

- Direct integration into a clinical workflow without independent clinical and regulatory review.
- Automated triage of real patients.
- Generation of binding prescriptions or treatment plans.

## Source fidelity, not clinical correctness

Each algorithm aims to faithfully reproduce its cited source. Faithful reproduction does **not** imply that the source itself is current, complete, or applicable to a given patient or population. Guidelines change. Local prevalence, resistance patterns, and patient context can shift the appropriate action. The treating clinician is responsible for interpretation.

If you find a discrepancy between the implementation and the cited source, please open an issue.

## No warranty

This software is provided "as is", without warranty of any kind, express or implied, including but not limited to warranties of merchantability, fitness for a particular purpose, and noninfringement. See [LICENSE](LICENSE).

## Contact

For clinical concerns or erratum reports, open an issue at https://github.com/txthedx/autonomous-care-algorithms/issues.
