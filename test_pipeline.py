"""Tests for Shopify sales tax economic nexus demo."""

import unittest
from oa_client import OAClient
import nexus_check
import shopify_client


class ShopifySalesTaxDemoTests(unittest.TestCase):
    def setUp(self):
        self.oa = OAClient(token=None)
        self.plan = self.oa.start("Check sales tax economic nexus across states", "US")
        slug = (self.plan.get("skills_to_load") or [None])[0]
        self.skill = self.oa.get_skill(slug)

    def test_mock_oa_client(self):
        self.assertEqual(self.plan["jurisdiction"], "US")
        self.assertEqual(self.skill["tier"], 1)
        self.assertIn("Amir Pelinkovic", self.skill["verifier"])

    def test_home_state_physical_nexus(self):
        st = {
            "state": "FL",
            "sales": 90000.0,
            "orders": 1200,
            "tax_collected": 6300.0,
            "registered": True,
            "home_state": True,
        }
        res = nexus_check.check(st, self.skill)
        self.assertEqual(res["status"], "ok")
        self.assertIn("home state", res["headline"])

    def test_economic_nexus_crossed_not_collecting(self):
        st = {
            "state": "IL",
            "sales": 140000.0,
            "orders": 320,
            "tax_collected": 0.0,
            "registered": False,
            "home_state": False,
        }
        res = nexus_check.check(st, self.skill)
        self.assertEqual(res["status"], "warn")
        self.assertIn("nexus CROSSED", res["headline"])

    def test_ny_and_rule(self):
        st = {
            "state": "NY",
            "sales": 520000.0,
            "orders": 90,
            "tax_collected": 0.0,
            "registered": False,
            "home_state": False,
        }
        res = nexus_check.check(st, self.skill)
        self.assertEqual(res["status"], "info")
        self.assertIn("BOTH tests", res["headline"])

    def test_samples_extraction(self):
        states = shopify_client.extract("samples/sales_by_state.json")
        self.assertEqual(len(states), 5)
        norm = shopify_client.normalize(states[0])
        self.assertEqual(norm["state"], "FL")


if __name__ == "__main__":
    unittest.main()
