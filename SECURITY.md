# Security policy

## Supported versions

The latest minor release is supported with security and clinical-correction fixes. Earlier versions are not actively maintained.

| Version | Supported |
|---|---|
| 0.9.x | Yes |
| < 0.9 | No |

## Reporting a software vulnerability

If you find a security vulnerability in the code or in the CI/CD pipeline, please use [GitHub's private vulnerability reporting](https://github.com/txthedx/autonomous-care-algorithms/security/advisories/new) rather than opening a public issue. We will acknowledge within 7 days and aim to resolve within 30 days for typical reports.

Examples in scope:

- Code injection, deserialization, or shell-out vulnerabilities in any module.
- Supply-chain risks from any added dependency.
- CI/CD misconfigurations that could allow unauthorized commits or secret exfiltration.

## Reporting a clinical correction

If you have found a discrepancy between an implemented algorithm and its cited source, or a missing clinical caveat, please open a public **Clinical correction** issue using the template. Clinical accuracy is not treated as a security-sensitive disclosure; transparent discussion is preferred.

## Out of scope

This software is not a medical device and is not deployed in clinical settings by this project. Reports about "incorrect" outputs in patient-facing contexts should be directed at the operator of the system that wrapped this library, not at this repository.

See [DISCLAIMER.md](DISCLAIMER.md) for the full scope and limitations of this software.
