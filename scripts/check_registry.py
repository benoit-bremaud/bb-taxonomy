"""Check registry.yaml and facets.yaml against the rules of taxonomy.md.

Usage: python3 scripts/check_registry.py [--base OLD_REGISTRY] [REGISTRY [FACETS]]
With --base, every ID of the old registry must still exist (IDs are never removed). Exits 1 and
prints one line per problem when a rule is broken.
"""

import argparse
import re
import sys

import yaml

STATUSES = {"active", "reserved", "deprecated"}
AREA = re.compile(r"^[0-9]0$")
DOMAIN = re.compile(r"^[0-9][0-9]$")
SUBDOMAIN = re.compile(r"^([0-9][0-9])\.([0-9][0-9])$")
SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")


def check_registry(data):
    """Return the list of problems in a parsed registry."""
    problems = []
    entries = data.get("entries") or []
    if not SEMVER.match(str(data.get("version", ""))):
        problems.append("registry: version must be MAJOR.MINOR.PATCH")
    ids = [str(e.get("id")) for e in entries]
    by_id = {str(e.get("id")): e for e in entries}
    seen_ids, seen_slugs = set(), set()
    for e in entries:
        eid, slug = str(e.get("id")), e.get("slug")
        where = f"entry {eid}"
        if eid in seen_ids:
            problems.append(f"{where}: duplicate id")
        seen_ids.add(eid)
        if not slug or not SLUG.match(slug):
            problems.append(f"{where}: slug must be kebab-case")
        elif slug in seen_slugs and e.get("status") != "deprecated":
            problems.append(f"{where}: duplicate slug {slug}")
        seen_slugs.add(slug)
        if not e.get("label"):
            problems.append(f"{where}: missing label")
        if e.get("status") not in STATUSES:
            problems.append(f"{where}: status must be one of {sorted(STATUSES)}")
        if not SEMVER.match(str(e.get("since", ""))):
            problems.append(f"{where}: since must be MAJOR.MINOR.PATCH")
        sub = SUBDOMAIN.match(eid)
        if sub:
            if sub.group(2) == "00":
                problems.append(f"{where}: NN.00 is the reserved general slot, never listed")
            if sub.group(1) not in ids or AREA.match(sub.group(1)):
                problems.append(f"{where}: parent {sub.group(1)} must be a listed domain, not an area")
        elif DOMAIN.match(eid):
            area = eid[0] + "0"
            if not AREA.match(eid) and area not in ids:
                problems.append(f"{where}: parent area {area} missing")
        else:
            problems.append(f"{where}: id must be NN or NN.MM")
        if e.get("status") == "deprecated":
            target = by_id.get(str(e.get("replaced_by")))
            if target is None or target.get("status") == "deprecated":
                problems.append(f"{where}: deprecated needs replaced_by an active id")
        elif "replaced_by" in e:
            problems.append(f"{where}: replaced_by only on a deprecated entry")
    return problems


def check_base(data, base):
    """Return the IDs of the base registry that the new registry lost."""
    current = {str(e.get("id")) for e in data.get("entries") or []}
    return [f"entry {i}: removed (IDs are never removed, deprecate it)"
            for i in (str(e.get("id")) for e in base.get("entries") or [])
            if i not in current]


def check_facets(data):
    """Return the list of problems in a parsed facets file."""
    problems = []
    facets = data.get("facets") or {}
    if not facets:
        problems.append("facets: no facet defined")
    for name, facet in facets.items():
        values = (facet or {}).get("values") or []
        if not values:
            problems.append(f"facet {name}: no values")
        if len(values) != len(set(values)):
            problems.append(f"facet {name}: duplicate values")
        problems += [f"facet {name}: value {v} must be kebab-case"
                     for v in values if not SLUG.match(str(v))]
    return problems


def load(path):
    """Parse a YAML file."""
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def main(argv=None):
    """Run every check and report."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("registry", nargs="?", default="registry.yaml")
    parser.add_argument("facets", nargs="?", default="facets.yaml")
    parser.add_argument("--base", help="the registry of the base branch")
    args = parser.parse_args(argv)
    registry = load(args.registry)
    problems = check_registry(registry) + check_facets(load(args.facets))
    if args.base:
        problems += check_base(registry, load(args.base))
    for p in problems:
        print(p, file=sys.stderr)
    if not problems:
        print(f"registry: {len(registry['entries'])} entries OK")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
