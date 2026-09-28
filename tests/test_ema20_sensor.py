from unittest import TestCase

from quero.brain.ema20_sensor import compare_price_to_ema20


class EMA20SensorTests(TestCase):
    def test_price_above_ema20_is_positive(self):
        result = compare_price_to_ema20(121.5, 120.0)

        self.assertEqual(result["direction"], "positive")
        self.assertTrue(result["confirmedLong"])
        self.assertFalse(result["confirmedShort"])

    def test_price_below_ema20_is_negative(self):
        result = compare_price_to_ema20(118.0, 120.0)

        self.assertEqual(result["direction"], "negative")
        self.assertFalse(result["confirmedLong"])
        self.assertTrue(result["confirmedShort"])

    def test_price_equal_ema20_is_neutral(self):
        result = compare_price_to_ema20(120.0, 120.0)

        self.assertEqual(result["direction"], "neutral")
        self.assertFalse(result["confirmedLong"])
        self.assertFalse(result["confirmedShort"])

    def test_long_sequence_confirms_above_ema20(self):
        confirmed = compare_price_to_ema20(121.0, 120.0, "LONG")

        self.assertTrue(confirmed["validatesSequence"])

    def test_long_sequence_rejects_below_ema20(self):
        rejected = compare_price_to_ema20(119.0, 120.0, "LONG")

        self.assertFalse(rejected["validatesSequence"])

    def test_short_sequence_confirms_below_ema20(self):
        confirmed = compare_price_to_ema20(119.0, 120.0, "SHORT")

        self.assertTrue(confirmed["validatesSequence"])

    def test_short_sequence_rejects_above_ema20(self):
        rejected = compare_price_to_ema20(121.0, 120.0, "SHORT")

        self.assertFalse(rejected["validatesSequence"])

    def test_sensor_updates_when_price_moves_from_above_to_below(self):
        above = compare_price_to_ema20(121.0, 120.0)
        below = compare_price_to_ema20(119.0, 120.0)

        self.assertEqual(above["direction"], "positive")
        self.assertEqual(below["direction"], "negative")

    def test_sensor_updates_when_price_moves_from_below_to_above(self):
        below = compare_price_to_ema20(119.0, 120.0)
        above = compare_price_to_ema20(121.0, 120.0)

        self.assertEqual(below["direction"], "negative")
        self.assertEqual(above["direction"], "positive")

    def test_sensor_does_not_modify_quero_nodes(self):
        node_quero = {"nodeOne": 109.89, "nodeTwo": 121.43, "state": "unchanged"}
        before = node_quero.copy()

        compare_price_to_ema20(121.0, 120.0, "LONG")

        self.assertEqual(node_quero, before)
