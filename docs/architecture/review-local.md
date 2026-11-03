# Local review — bb-taxonomy (feat/1-bootstrap-registry)

Pre-push review of the repository bootstrap, run with `review-local --push`.

- Date: 2026-11-03
- Commit: 5edbf57
- Scope: branch diff `main...HEAD` (e4d71d9..5edbf57)
- Checks run:
  - adversarial review (Opus, 3 rounds)
  - correctness and design, within the adversarial rounds
  - local CI (`just check main`)
- Verdict: ship. Must 0 · Should 0 · Nice 7 (deferred to issues)

## Adversarial review (#236)

| Round | On | Result | Push gate |
|---|---|---|---|
| 1 | `da0f750` | Must 3 · Should 13 · Nice 7 | closed |
| 2 | `4a42a91` | 3 Must and 13 Should fixed; 1 regression (first push blocked); new: Must 2 · Should 1 · Nice 2 | closed |
| 3 | `5edbf57` | all fixed · Must 0 · Should 0 · Nice 2 | **open** |

Hosted reviewers: none. The repository has no remote yet and Copilot is out of credits.

## Pre-merge gate (head SHA 5edbf57)

| Step | Result |
|---|---|
| 0 CI mirror | n/a: no GitHub workflow (skill `local-ci` rule 2, ADR-0004) |
| 1 Tests | ✅ 33 unit tests |
| 2 Coverage | tests 98 % branch on `check_registry.py`, measured with coverage 7.10.7 · docs ⏸ deferred to the pre-merge run |
| 3 SonarQube | ⏸ deferred to the pre-merge run (no SonarQube project yet) |
| 4 Secrets | ✅ gitleaks clean (full history) · no tracked `.env` · diff read: nothing sensitive |
| 5 E2E/smoke | n/a: no runtime product |

Gate: **pre-push green**. `just check main` passed. SonarQube and doc coverage are deferred.

## 🔴 Must Have

_None._

## 🟡 Should Have

_None._

## 🔵 Nice to Have (to file as issues)

- `LICENSE`: CC BY 4.0 also covers `scripts/`. Consider MIT for the code.
- `check_registry.py`: allow `reserved` on area entries only. Refuse domains under a reserved area and subdomains under a deprecated domain.
- `check_registry.py`: `check_base` raises a traceback on malformed entries. It still fails safe (exit 1).
- `justfile`: skip the base check only on `git ls-remote` exit status 2, not on a network or authentication error.

## ⚪ Disagree / Intentional

- `PROJECT_LOG.md`: the "Order" decision is the owner's explicit override of the top MCDA score (380 against 395). It is recorded as such.
- `mise.toml`: Python and PyYAML stay system tools, as skill `local-ci` rule 2 allows.

## Out of scope

- agents-skills: skill `security-ci-baseline` requires CodeQL and dependency-review workflows, but ADR-0004 and skill `local-ci` rule 2 allow no workflow other than the release one. This needs a follow-up issue in agents-skills.
