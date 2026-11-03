"""Check registry.yaml and facets.yaml against the rules of taxonomy.md.

Usage: python3 scripts/check_registry.py [--base OLD_REGISTRY] [REGISTRY [FACETS]]
With --base, the registry is also checked against the base branch's: no ID removed, no slug changed,
no deprecated ID revived. Exits 1 and prints one line per problem when a rule is broken.
"""

import argparse
import re
import sys

import yaml

STATUSES = {"active", "reserved", "deprecated"}
KEYS = {"id", "slug", "label", "status", "since", "replaced_by", "description"}
AREA = re.compile(r"^[0-9]0$")
DOMAIN = re.compile(r"^[0-9][0-9]$")
SUBDOMAIN = re.compile(r"^([0-9][0-9])\.([0-9][0-9])$")
SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SEMVER = re.compile(r"^([0-9]+)\.([0-9]+)\.([0-9]+)$")


def semver(value):
    """Return a comparable version tuple, or None when the value is not MAJOR.MINOR.PATCH."""
    match = SEMVER.match(str(value))
    return tuple(int(g) for g in match.groups()) if match else None


def check_entry(e, by_id, version):
    """Return the problems of one entry taken alone or against its parents."""
    eid = str(e.get("id"))
    where = f"entry {eid}"
    problems = [f"{where}: unknown key {k}" for k in sorted(set(e) - KEYS)]
    if not SLUG.match(str(e.get("slug", ""))):
        problems.append(f"{where}: slug must be kebab-case")
    if not e.get("label"):
        problems.append(f"{where}: missing label")
    if e.get("status") not in STATUSES:
        problems.append(f"{where}: status must be one of {sorted(STATUSES)}")
    since = semver(e.get("since"))
    if since is None:
        problems.append(f"{where}: since must be MAJOR.MINOR.PATCH")
    elif version and since > version:
        problems.append(f"{where}: since is later than the registry version")
    sub = SUBDOMAIN.match(eid)
    if sub:
        parent = by_id.get(sub.group(1))
        if sub.group(2) == "00":
            problems.append(f"{where}: NN.00 is the reserved general slot, never listed")
        if parent is None or AREA.match(sub.group(1)):
            problems.append(f"{where}: parent {sub.group(1)} must be a listed domain, not an area")
    elif DOMAIN.match(eid):
        if not AREA.match(eid) and eid[0] + "0" not in by_id:
            problems.append(f"{where}: parent area {eid[0]}0 missing")
    else:
        problems.append(f"{where}: id must be NN or NN.MM")
    if e.get("status") == "deprecated":
        target = by_id.get(str(e.get("replaced_by")))
        if target is None or target.get("status") != "active":
            problems.append(f"{where}: deprecated needs replaced_by an active id")
    elif "replaced_by" in e:
        problems.append(f"{where}: replaced_by only on a deprecated entry")
    return problems


def check_registry(data):
    """Return the list of problems in a parsed registry."""
    problems = []
    entries = data.get("entries") or []
    if not isinstance(entries, list) or not all(isinstance(e, dict) for e in entries):
        return ["registry: entries must be a list of mappings"]
    version = semver(data.get("version"))
    if version is None:
        problems.append("registry: version must be MAJOR.MINOR.PATCH")
    if not entries:
        problems.append("registry: no entries")
    by_id = {str(e.get("id")): e for e in entries}
    seen_ids, seen_slugs = set(), set()
    for e in entries:
        eid, slug = str(e.get("id")), e.get("slug")
        if eid in seen_ids:
            problems.append(f"entry {eid}: duplicate id")
        if slug in seen_slugs:
            problems.append(f"entry {eid}: duplicate slug {slug} (slugs are never reused)")
        seen_ids.add(eid)
        seen_slugs.add(slug)
        problems += check_entry(e, by_id, version)
    return problems


def check_base(data, base):
    """Return the problems of the registry against the base branch's registry."""
    problems = []
    current = {str(e.get("id")): e for e in data.get("entries") or []}
    for old in base.get("entries") or []:
        eid = str(old.get("id"))
        new = current.get(eid)
        if new is None:
            problems.append(f"entry {eid}: removed (IDs are never removed, deprecate it)")
        elif new.get("status") == "reserved" and old.get("status") != "reserved":
            problems.append(f"entry {eid}: an ID is never put back to reserved")
        elif old.get("status") == "reserved":
            continue  # a reserved slot has no meaning yet: taking it into use may set every field
        elif new.get("slug") != old.get("slug"):
            problems.append(f"entry {eid}: slug changed (an ID never changes meaning)")
        elif old.get("status") == "deprecated" and new.get("status") != "deprecated":
            problems.append(f"entry {eid}: a deprecated ID is never revived")
    return problems


def check_facets(data):
    """Return the list of problems in a parsed facets file."""
    problems = []
    if semver(data.get("version")) is None:
        problems.append("facets: version must be MAJOR.MINOR.PATCH")
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
    """Parse a YAML file whose top level must be a mapping."""
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise SystemExit(f"{path}: the top level must be a mapping")
    return data


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
        print(f"registry: {len(registry.get('entries') or [])} entries OK")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
