"""Unit tests for check_registry.py: one test per rule of taxonomy.md."""

import contextlib
import io
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
        with contextlib.redirect_stdout(io.StringIO()):
            code = cr.main([os.path.join(root, "registry.yaml"), os.path.join(root, "facets.yaml")])
        self.assertEqual(code, 0)

    def test_empty_registry(self):
        self.assertIn("registry: no entries", cr.check_registry({"version": "0.1.0"}))

    def test_entries_must_be_a_list_of_mappings(self):
        expected = ["registry: entries must be a list of mappings"]
        self.assertEqual(cr.check_registry({"version": "0.1.0", "entries": {"a": 1}}), expected)
        self.assertEqual(cr.check_registry({"version": "0.1.0", "entries": ["a"]}), expected)

    def test_duplicate_id(self):
        self.assert_problem(registry(entry("11", "other")), "duplicate id")

    def test_duplicate_slug(self):
        self.assert_problem(registry(entry("11.01", "domain")), "duplicate slug")

    def test_deprecated_slug_is_never_reused_in_either_order(self):
        old = entry("11.01", "x", status="deprecated", replaced_by="11.02")
        new = entry("11.02", "x")
        self.assert_problem(registry(old, new), "never reused")
        self.assert_problem(registry(new, old), "never reused")

    def test_bad_slug(self):
        self.assert_problem(registry(entry("11.01", "Bad_Slug")), "kebab-case")

    def test_unknown_key(self):
        self.assert_problem(registry(entry("11.01", "x", colour="red")), "unknown key colour")

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
        self.assertTrue(any("since must be" in p for p in problems))
        self.assertTrue(any("registry: version" in p for p in problems))

    def test_since_after_registry_version(self):
        self.assert_problem(registry(entry("11.01", "x", since="9.9.9")), "later than the registry")

    def test_deprecated_needs_replacement(self):
        self.assert_problem(registry(entry("11.01", "old", status="deprecated")), "replaced_by")

    def test_deprecated_cannot_point_to_reserved(self):
        data = registry(entry("11.01", "old", status="deprecated", replaced_by="90"),
                        entry("90", "reserved", status="reserved"))
        self.assert_problem(data, "replaced_by an active id")

    def test_deprecated_with_replacement_passes(self):
        data = registry(entry("11.01", "old", status="deprecated", replaced_by="11.02"),
                        entry("11.02", "new"))
        self.assertEqual(cr.check_registry(data), [])

    def test_replaced_by_only_on_deprecated(self):
        self.assert_problem(registry(entry("11.01", "x", replaced_by="11")), "only on a deprecated")


class BaseTest(unittest.TestCase):
    def test_removed_id(self):
        self.assertEqual(cr.check_base(registry(), registry(entry("11.01", "gone"))),
                         ["entry 11.01: removed (IDs are never removed, deprecate it)"])

    def test_added_id_passes(self):
        self.assertEqual(cr.check_base(registry(entry("11.01", "new")), registry()), [])

    def test_slug_change(self):
        problems = cr.check_base(registry(entry("11.01", "new-name")), registry(entry("11.01", "old")))
        self.assertEqual(problems, ["entry 11.01: slug changed (an ID never changes meaning)"])

    def test_deprecated_revived(self):
        old = registry(entry("11.01", "x", status="deprecated", replaced_by="11"))
        self.assertEqual(cr.check_base(registry(entry("11.01", "x")), old),
                         ["entry 11.01: a deprecated ID is never revived"])

    def test_put_back_to_reserved(self):
        problems = cr.check_base(registry(entry("11.01", "x", status="reserved")),
                                 registry(entry("11.01", "x")))
        self.assertEqual(problems, ["entry 11.01: an ID is never put back to reserved"])

    def test_reserved_slot_taken_into_use(self):
        old = registry(entry("90", "reserved", status="reserved"))
        self.assertEqual(cr.check_base(registry(entry("90", "business")), old), [])


class FacetsTest(unittest.TestCase):
    def test_valid_facets(self):
        data = {"version": "0.1.0", "facets": {"kind": {"values": ["skill"]}}}
        self.assertEqual(cr.check_facets(data), [])

    def test_empty_facets(self):
        self.assertEqual(cr.check_facets({}), ["facets: version must be MAJOR.MINOR.PATCH",
                                               "facets: no facet defined"])

    def test_facet_without_values(self):
        self.assertIn("facet kind: no values", cr.check_facets({"facets": {"kind": {}}}))

    def test_duplicate_and_bad_values(self):
        problems = cr.check_facets({"facets": {"kind": {"values": ["a", "a", "B c"]}}})
        self.assertIn("facet kind: duplicate values", problems)
        self.assertIn("facet kind: value B c must be kebab-case", problems)


class MainTest(unittest.TestCase):
    def write(self, tmp, name, text):
        path = os.path.join(tmp, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def test_main_fails_on_removed_id_against_base(self):
        line = '  - {{id: "{0}", slug: s{0}, label: x, status: active, since: 0.1.0}}\n'
        with tempfile.TemporaryDirectory() as tmp:
            reg = self.write(tmp, "r.yaml", "version: 0.1.0\nentries:\n" + line.format("10"))
            base = self.write(tmp, "b.yaml", "version: 0.1.0\nentries:\n" + line.format("10")
                              + line.format("11"))
            fac = self.write(tmp, "f.yaml", "version: 0.1.0\nfacets:\n  kind:\n    values: [skill]\n")
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                code = cr.main([reg, fac, "--base", base])
        self.assertEqual(code, 1)
        self.assertIn("entry 11: removed", err.getvalue())

    def test_load_refuses_a_non_mapping(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(tmp, "list.yaml", "- a\n")
            with self.assertRaises(SystemExit):
                cr.load(path)


if __name__ == "__main__":
    unittest.main()
