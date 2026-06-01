# Changelog

All notable changes to this project will be documented in this file. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [semantic versioning](https://semver.org/) with the conventions described in [docs/methodology.md](docs/methodology.md).

## [0.1.0] — 2026-06-01

### Added
- Repository scaffold: README, DISCLAIMER, CONTRIBUTING, methodology, MIT license.
- First condition: **acute pharyngitis** with McIsaac (modified Centor) scoring and IDSA 2012-aligned recommendation bands.
  - Sources: Centor 1981 (PMID 6763125), McIsaac 1998 (PMID 9475915), McIsaac 2004 (PMID 15069046), Shulman 2012 / IDSA (PMID 22965026).
  - 36 unit tests covering Centor points, age adjustment, score range, invalid input, recommendation bands, and abstract clinical vignettes.
- `pyproject.toml` for editable install and pytest configuration.
