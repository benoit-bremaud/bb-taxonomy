# Project log

Chronological record of the decisions and operations on bb-taxonomy, newest first, complementing `git log`.

## 2026-11-03 — Repository bootstrapped (#1)

- **Why.** The owner wanted his own reference framework, not a taxonomy borrowed from a standard, to file every agent tool (skills, agents, commands, hooks, plugins, MCP servers) and later his notes and projects. The study behind it covered the agent-skill ecosystem (anthropics/skills, plugin marketplaces, skills.sh, awesome lists, MCP registries), reference trees (SWEBOK v4, OWASP SAMM, NIST SSDF, DORA, ISO 25010, CISSP, PTES) and knowledge-management schemes (Johnny.Decimal, PARA, faceted classification).
- **Decisions, each by MCDA:**

  | Decision | Chosen | Score | Runners-up |
  |---|---|---|---|
  | Structure | numbered areas, domains and subdomains plus facets | 445/500 | facets only 335; flat 12 domains 305; SWEBOK mirror 305 |
  | Where it lives | a dedicated public repository | 435/500 | inside agents-skills 370; a widened agents-skills vault 355 |
  | Name | `bb-taxonomy` | 460/500 | `bb-bok` 395; `bb-referential` 385 |
  | Order | built from the agents-skills chat | 380/500 | dedicated chat 395, chosen against by the owner |

  The owner validated each one. The agents-skills issue #282 depends on this repository.
- **What.**
  - Registry 0.1.0: 120 entries (10 areas, 36 domains, 74 subdomains).
  - Facet vocabularies, the check script and its tests.
  - CI: `just check` locally, the same checks in GitHub Actions.
  - Licence: CC BY 4.0.
