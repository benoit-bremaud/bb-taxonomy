# bb-taxonomy rules

The rules of a personal classification framework: stable numeric IDs for every subject Benoît Bremaud works on, plus facets, so that agent skills, notes, reference material and projects can all be filed in one place.

## Structure

The taxonomy has two navigable levels plus an implicit grouping:

| Level | ID | Example | Folder? |
|---|---|---|---|
| Area | `N0`, the index slot of its domains | `10` Software engineering | no, a group of domains |
| Domain | `NN` | `16` Quality and testing | yes |
| Subdomain | `NN.MM` | `16.02` Test design and planning | yes, when it has items |

- An area groups up to nine domains `N1`–`N9`; its `N0` entry is the area index (a map of content). There are at most ten areas, `00` to `90`.
- A domain may have no subdomains (`23` Release and versioning) until its items call for some.
- Every other dimension (artefact kind, lifecycle phase, stack…) is a **facet**, never a third level.

The full list lives in [`registry.yaml`](registry.yaml); it is the single source of every ID.

## IDs

1. **Stable.** An ID and its slug never change meaning, are never renumbered, never reused and never removed, even once deprecated. Labels and descriptions may change.
2. **Retirement.** A retired ID stays in the registry with `status: deprecated` and `replaced_by: <active id>`.
3. **Reserved slots.**
   - `N0` is the index of area `N`.
   - `NN.00` is the implicit "general" bucket of every domain. It is never listed. Split it into a new subdomain once it holds more than 7 items.
   - Area `90` is the last free area slot (`status: reserved`). A reserved entry has no meaning yet, so taking it into use may set its slug, label and status: the only change of slug the rules allow.
4. **Fan-out.** At most 9 domains per area and 99 subdomains per domain; aim for fewer than 10 subdomains.

## Placement

- **One primary home per item**, chosen by the subject of the work, not by the tool, the project or the lifecycle phase. Cross-links go in links or maps of content, never in a second home.
- Edge cases:
  - ESP32 firmware → `51`.
  - A pentest of a self-built ESP32 IoT hub → `32.01` with `stack: esp-idf`.
  - A meeting recording → `81` whatever its topic.
- Cite an item's place as `bb-taxonomy@<version>:<id>`, for example `bb-taxonomy@0.1.0:16.02`.

## Facets

An item carries one taxonomy ID, the most specific that fits (a subdomain, else a domain), and its facets. For an agent skill, they go under the `metadata:` key of the `SKILL.md` frontmatter, because unknown top-level keys break the claude.ai upload. The vocabularies live in [`facets.yaml`](facets.yaml):

| Facet | Meaning |
|---|---|
| `kind` | what the item is |
| `role` | what it does for its reader |
| `phase` | the lifecycle step where it is used |
| `stack` | the technology it is tied to, `any` when generic |
| `scope` | where it applies |
| `status` | the item's own lifecycle, not its ID's |
| `source` | who owns it |
| `quality` | the ISO/IEC 25010:2023 characteristic it mainly serves (optional) |

Example:

```yaml
metadata:
  taxonomy: "0.1.0"     # the registry release the ID was read from
  taxonomy_id: "16.02"  # the domain is its first two digits, never stored twice
  kind: skill
  role: procedure
  phase: test
  stack: any
```

## Extension

| Need | Action | Release |
|---|---|---|
| A new item | file it in an existing domain or subdomain | none |
| A new subdomain | take the next free `MM` in its domain | MINOR |
| A new domain | take a free `NN` in its area | MINOR |
| A new area | take the reserved `90` into use; a later area needs a MAJOR redesign | MINOR |
| A new facet value | add it to `facets.yaml` | MINOR |
| A new label or description | edit it | PATCH |
| A retired ID | `status: deprecated` + `replaced_by` | MAJOR |
| Changing what an ID means | forbidden: deprecate it and add a new ID | MAJOR |

- **No empty structure.** A slot exists only as a registry line. The folder or note is created when its first item arrives.
- **Review every quarter.** Check the `NN.00` buckets that need a split, the deprecated IDs and the open facet values.
- **Enforced checks.** `scripts/check_registry.py` checks ID formats, parents, uniqueness, statuses, replacements and facet vocabularies. Given the base branch's registry, it also refuses a removed ID, a changed slug (except a reserved slot taken into use), an ID put back to reserved and a revived deprecated ID.

## Sources

The domains draw on:

- SWEBOK v4 (IEEE, 2024)
- OWASP SAMM v2, NIST SSDF and PTES for security
- DORA capabilities for delivery
- ISO/IEC 25010:2023 for quality
- the categories of the agent-skill ecosystem: anthropics/skills, Claude Code plugin marketplaces, skills.sh, awesome-claude-code, MCP registries

The structure draws on:

- Johnny.Decimal: two-digit areas and categories, reserved zero slots
- Ranganathan's faceted classification (PMEST): facets instead of depth, hospitality to new subjects
- PARA: actionability as a facet, not as the hierarchy
