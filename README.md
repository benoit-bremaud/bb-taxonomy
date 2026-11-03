# bb-taxonomy

A personal, versioned classification framework that gives every subject a stable ID, so agent skills, notes, reference material and projects share one way to be filed and found.

## Contents

| File | Purpose |
|---|---|
| [`taxonomy.md`](taxonomy.md) | the rules: levels, IDs, reserved slots, placement, facets, extension |
| [`registry.yaml`](registry.yaml) | the single source of every area, domain and subdomain ID |
| [`facets.yaml`](facets.yaml) | the controlled vocabularies of the facets |
| [`scripts/check_registry.py`](scripts/check_registry.py) | the checks every change must pass |

## Areas

| ID | Area |
|---|---|
| 00 | Meta: agent tooling and personal method |
| 10 | Software engineering |
| 20 | Delivery and operations |
| 30 | Security |
| 40 | Design and experience |
| 50 | Hardware and embedded |
| 60 | Creative and games |
| 70 | Communication and growth |
| 80 | Knowledge and productivity |
| 90 | Reserved |

## Use

Give an item one primary ID and its facets. Pin the release, because IDs are stable across MINOR and PATCH releases:

```yaml
metadata:
  taxonomy: "0.1.0"
  domain: "16"
  subdomain: "16.02"
  kind: skill
```

The first consumer is [agents-skills](https://github.com/benoit-bremaud/agents-skills), which files every Claude Code skill, agent, command and hook here.

## Development

```sh
mise install        # pinned toolchain
mise x -- just check
```

A change to the registry follows the release rules of [`taxonomy.md` § Extension](taxonomy.md#extension) and gets a `CHANGELOG.md` entry.

## Licence

[CC BY 4.0](LICENSE).
