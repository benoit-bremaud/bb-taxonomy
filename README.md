# bb-taxonomy

A personal, versioned classification framework that gives every subject a stable ID, so agent skills, notes, reference material and projects share one way to be filed and found.

## Contents

| File | Purpose |
|---|---|
| [`taxonomy.md`](taxonomy.md) | the rules: levels, IDs, reserved slots, placement, facets, extension |
| [`registry.yaml`](registry.yaml) | the single source of every area, domain and subdomain ID and label |
| [`facets.yaml`](facets.yaml) | the controlled vocabularies of the facets |
| [`scripts/check_registry.py`](scripts/check_registry.py) | the checks every change must pass |

## Use

Give an item one primary ID and its facets. Pin the release, because IDs are stable across MINOR and PATCH releases:

```yaml
metadata:
  taxonomy: "0.1.0"
  taxonomy_id: "16.02"
  kind: skill
```

The first planned consumer is the owner's private agents-skills repository, which will file its Claude Code skills, agents, commands and hooks here.

## Development

```sh
mise install && mise x -- just setup   # pinned toolchain and the pre-push hook
mise x -- just check                   # what the hook runs
```

A change to the registry follows the release rules of [`taxonomy.md` § Extension](taxonomy.md#extension) and gets a `CHANGELOG.md` entry.

## Licence

[CC BY 4.0](LICENSE).
