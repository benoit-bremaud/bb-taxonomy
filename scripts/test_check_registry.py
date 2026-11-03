"""Unit tests for check_registry.py: one test per rule of taxonomy.md."""

import os
import tempfile
import unittest

import check_registry as cr


def entry(eid, slug, **extra):
    """Build a valid active entry."""
    return {"id": eid, "slug": slug, "label": slug, "status": "active", "since": "0.1.0", **extra}


def registry(*entries):
    """Build a registry with a valid area 10 and domain 11 plus the given entries."""
    return {"version": "0.1.0",
            "entries": [entry("10", "area"), entry("11", "domain"), *entries]}


class RegistryTest(unittest.TestCase):
    def assert_problem(self, data, fragment):
        problems = cr.check_registry(data)
        self.assertTrue(any(fragment in p for p in problems), problems)

    def test_valid_registry_has_no_problem(self):
        self.assertEqual(cr.check_registry(registry(entry("11.01", "sub"))), [])

    def test_real_registry_and_facets_pass(self):
        root = os.path.join(os.path.dirname(__file__), "..")
        self.assertEqual(cr.main([os.path.join(root, "registry.yaml"),
                                  os.path.join(root, "facets.yaml")]), 0)

    def test_duplicate_id(self):
        self.assert_problem(registry(entry("11", "other")), "duplicate id")

    def test_duplicate_slug(self):
        self.assert_problem(registry(entry("11.01", "domain")), "duplicate slug")

    def test_bad_slug(self):
        self.assert_problem(registry(entry("11.01", "Bad_Slug")), "kebab-case")

    def test_bad_id_format(self):
        self.assert_problem(registry(entry("1.1", "x")), "id must be")

    def test_general_slot_is_never_listed(self):
        self.assert_problem(registry(entry("11.00", "general")), "reserved general slot")

    def test_subdomain_needs_listed_domain(self):
        self.assert_problem(registry(entry("12.01", "orphan")), "must be a listed domain")

    def test_subdomain_cannot_hang_off_an_area(self):
        self.assert_problem(registry(entry("10.01", "under-area")), "not an area")

    def test_domain_needs_its_area(self):
        self.assert_problem(registry(entry("21", "lost")), "parent area 20 missing")

    def test_bad_status(self):
        self.assert_problem(registry(entry("11.01", "x", status="planned")), "status must be")

    def test_bad_versions(self):
        data = registry(entry("11.01", "x", since="v1"))
        data["version"] = "1"
        problems = cr.check_registry(data)
        self.assertTrue(any("since" in p for p in problems))
        self.assertTrue(any("registry: version" in p for p in problems))

    def test_deprecated_needs_active_replacement(self):
        self.assert_problem(registry(entry("11.01", "old", status="deprecated")), "replaced_by")

    def test_deprecated_with_replacement_passes(self):
        data = registry(entry("11.01", "old", status="deprecated", replaced_by="11.02"),
                        entry("11.02", "new"))
        self.assertEqual(cr.check_registry(data), [])

    def test_replaced_by_only_on_deprecated(self):
        self.assert_problem(registry(entry("11.01", "x", replaced_by="11")), "only on a deprecated")

    def test_removed_id_against_base(self):
        base = registry(entry("11.01", "gone"))
        self.assertEqual(cr.check_base(registry(), base),
                         ["entry 11.01: removed (IDs are never removed, deprecate it)"])

    def test_added_id_against_base_passes(self):
        self.assertEqual(cr.check_base(registry(entry("11.01", "new")), registry()), [])


class FacetsTest(unittest.TestCase):
    def test_valid_facets(self):
        self.assertEqual(cr.check_facets({"facets": {"kind": {"values": ["skill"]}}}), [])

    def test_empty_facets(self):
        self.assertEqual(cr.check_facets({}), ["facets: no facet defined"])

    def test_facet_without_values(self):
        self.assertIn("facet kind: no values", cr.check_facets({"facets": {"kind": {}}}))

    def test_duplicate_and_bad_values(self):
        problems = cr.check_facets({"facets": {"kind": {"values": ["a", "a", "B c"]}}})
        self.assertIn("facet kind: duplicate values", problems)
        self.assertIn("facet kind: value B c must be kebab-case", problems)


class MainTest(unittest.TestCase):
    def test_main_reports_and_fails_on_problem(self):
        with tempfile.TemporaryDirectory() as tmp:
            reg, fac = os.path.join(tmp, "r.yaml"), os.path.join(tmp, "f.yaml")
            with open(reg, "w", encoding="utf-8") as f:
                f.write('version: 0.1.0\nentries:\n  - {id: "1", slug: x, label: x, status: active, since: 0.1.0}\n')
            with open(fac, "w", encoding="utf-8") as f:
                f.write("facets:\n  kind:\n    values: [skill]\n")
            self.assertEqual(cr.main([reg, fac, "--base", reg]), 1)


if __name__ == "__main__":
    unittest.main()
