import unittest
from datetime import datetime, timedelta, timezone

from src.cart import calculate_total, calculate_total_with_coupon


class CartContractTests(unittest.TestCase):
    def test_existing_total_contract(self):
        result = calculate_total([{"price": 5, "quantity": 2}, {"price": 3, "quantity": 1}])
        self.assertEqual(result, 13)
        self.assertIsInstance(result, (int, float))

    def test_empty_cart_is_zero(self):
        self.assertEqual(calculate_total([]), 0)


class CouponTests(unittest.TestCase):
    def setUp(self):
        self.expiry = datetime(2026, 10, 28, 12, tzinfo=timezone.utc)
        self.coupon = {
            "code": "SAVE20", "percent": 20,
            "active_from": self.expiry - timedelta(days=1),
            "expires_at": self.expiry,
        }
        self.items = [{"price": 100, "quantity": 1}]

    def total(self, now, code="save20"):
        return calculate_total_with_coupon(self.items, self.coupon, code, now)

    def test_activation_and_grace_boundaries(self):
        cases = [
            (self.coupon["active_from"] - timedelta(microseconds=1), 100),
            (self.coupon["active_from"], 80),
            (self.expiry - timedelta(microseconds=1), 80),
            (self.expiry, 80),
            (self.expiry + timedelta(minutes=30), 80),
            (self.expiry + timedelta(hours=1) - timedelta(microseconds=1), 80),
            (self.expiry + timedelta(hours=1), 100),
            (self.expiry + timedelta(hours=2), 100),
        ]
        for now, expected in cases:
            with self.subTest(now=now):
                self.assertEqual(self.total(now), expected)

    def test_code_matching(self):
        for code, expected in [("SAVE20", 80), ("SaVe20", 80), ("OTHER", 100)]:
            with self.subTest(code=code):
                self.assertEqual(self.total(self.expiry, code), expected)

    def test_percentage_bounds(self):
        for percent, expected in [(-1, 100), (0, 100), (100, 50), (101, 100)]:
            with self.subTest(percent=percent):
                self.coupon["percent"] = percent
                self.assertEqual(self.total(self.expiry), expected)

    def test_discount_cap(self):
        self.items = [{"price": 1000, "quantity": 1}]
        self.assertEqual(self.total(self.expiry), 950)

    def test_full_discount_and_empty_cart(self):
        self.coupon["percent"] = 100
        self.items = [{"price": 20, "quantity": 1}]
        self.assertEqual(self.total(self.expiry), 0)
        self.items = []
        self.assertEqual(self.total(self.expiry), 0)

    def test_equivalent_timezone(self):
        local = timezone(timedelta(hours=5, minutes=30))
        self.assertEqual(self.total(self.expiry.astimezone(local)), 80)

    def test_naive_timestamps_rejected(self):
        for key in ("now", "active_from", "expires_at"):
            with self.subTest(key=key):
                coupon = dict(self.coupon)
                now = self.expiry
                if key == "now":
                    now = now.replace(tzinfo=None)
                else:
                    coupon[key] = coupon[key].replace(tzinfo=None)
                with self.assertRaises(ValueError):
                    calculate_total_with_coupon(self.items, coupon, "SAVE20", now)


if __name__ == "__main__":
    unittest.main()
