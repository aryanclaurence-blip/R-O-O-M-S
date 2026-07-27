# -*- coding: utf-8 -*-
"""Comprehensive Unit Tests for Smart Dimension Parsing Engine."""
import sys
import os
import unittest

# Ensure lib directory is in sys.path
lib_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'RoomDimensionManager.extension', 'lib'))
if lib_dir not in sys.path:
    sys.path.insert(0, lib_dir)

from rdm.utils.dimension_parser import SmartDimensionParser, ParseResult


class TestSmartDimensionParser(unittest.TestCase):

    def assertAlmostEqualRel(self, val1, val2, places=3):
        self.assertIsNotNone(val1)
        self.assertIsNotNone(val2)
        self.assertAlmostEqual(val1, val2, places=places)

    def test_example_1_standard_meters(self):
        res = SmartDimensionParser.parse("2.25m x 5.00m")
        self.assertTrue(res.Success)
        self.assertAlmostEqualRel(res.InternalA, 2.25 / 0.3048)  # ~7.3819 ft
        self.assertAlmostEqualRel(res.InternalB, 5.00 / 0.3048)  # ~16.4042 ft
        self.assertEqual(res.Confidence, "High")
        self.assertEqual(res.SourceType, "Explicit Units")
        self.assertEqual(res.DetectedSeparator, "x")

    def test_example_2_uppercase_x(self):
        res = SmartDimensionParser.parse("2.25m X 5.00m")
        self.assertTrue(res.Success)
        self.assertAlmostEqualRel(res.InternalA, 2.25 / 0.3048)
        self.assertAlmostEqualRel(res.InternalB, 5.00 / 0.3048)
        self.assertEqual(res.Confidence, "High")

    def test_example_3_unicode_times_symbol(self):
        res = SmartDimensionParser.parse("2.25m × 5.00m")
        self.assertTrue(res.Success)
        self.assertAlmostEqualRel(res.InternalA, 2.25 / 0.3048)
        self.assertAlmostEqualRel(res.InternalB, 5.00 / 0.3048)
        self.assertEqual(res.Confidence, "High")
        self.assertEqual(res.DetectedSeparator, "×")

    def test_example_4_by_separator(self):
        res = SmartDimensionParser.parse("2.25m by 5.00m")
        self.assertTrue(res.Success)
        self.assertAlmostEqualRel(res.InternalA, 2.25 / 0.3048)
        self.assertAlmostEqualRel(res.InternalB, 5.00 / 0.3048)
        self.assertEqual(res.Confidence, "High")
        self.assertEqual(res.DetectedSeparator, "by")

    def test_example_5_unitless_by(self):
        res = SmartDimensionParser.parse("2.25 by 5.00")
        self.assertTrue(res.Success)
        self.assertEqual(res.SourceType, "Project Units")
        self.assertEqual(res.Confidence, "Low")

    def test_example_6_unitless_integers(self):
        res = SmartDimensionParser.parse("2250 x 5000")
        self.assertTrue(res.Success)
        self.assertEqual(res.SourceType, "Project Units")
        self.assertEqual(res.DetectedSeparator, "x")

    def test_example_7_millimeters(self):
        res = SmartDimensionParser.parse("2250mm x 5000mm")
        self.assertTrue(res.Success)
        self.assertAlmostEqualRel(res.InternalA, 2250.0 / 304.8) # ~7.3819 ft
        self.assertAlmostEqualRel(res.InternalB, 5000.0 / 304.8) # ~16.4042 ft
        self.assertEqual(res.SourceType, "Explicit Units")

    def test_example_8_space_separated(self):
        res = SmartDimensionParser.parse("2.25 m 5.00 m")
        self.assertTrue(res.Success)
        self.assertAlmostEqualRel(res.InternalA, 2.25 / 0.3048)
        self.assertAlmostEqualRel(res.InternalB, 5.00 / 0.3048)

    def test_example_9_labeled_input_order_preservation(self):
        res = SmartDimensionParser.parse("L=2.25m W=5.00m")
        self.assertTrue(res.Success)
        self.assertAlmostEqualRel(res.InternalA, 2.25 / 0.3048)
        self.assertAlmostEqualRel(res.InternalB, 5.00 / 0.3048)
        self.assertEqual(res.SourceType, "Labeled Input")

    def test_example_9b_labeled_input_reversed_order_preservation(self):
        res = SmartDimensionParser.parse("W=5.00m L=2.25m")
        self.assertTrue(res.Success)
        # MUST NOT SWAP! InternalA must be 5.00m, InternalB must be 2.25m
        self.assertAlmostEqualRel(res.InternalA, 5.00 / 0.3048)
        self.assertAlmostEqualRel(res.InternalB, 2.25 / 0.3048)
        self.assertEqual(res.SourceType, "Labeled Input")

    def test_example_10_reversed_order(self):
        res = SmartDimensionParser.parse("5.00m x 2.25m")
        self.assertTrue(res.Success)
        # MUST NOT SWAP! InternalA must be 5.00m, InternalB must be 2.25m
        self.assertAlmostEqualRel(res.InternalA, 5.00 / 0.3048)
        self.assertAlmostEqualRel(res.InternalB, 2.25 / 0.3048)

    def test_tolerant_zero_space(self):
        res = SmartDimensionParser.parse("2.25mx5.00m")
        self.assertTrue(res.Success)
        self.assertAlmostEqualRel(res.InternalA, 2.25 / 0.3048)
        self.assertAlmostEqualRel(res.InternalB, 5.00 / 0.3048)

    def test_tolerant_mixed_case_zero_space(self):
        res = SmartDimensionParser.parse("2250MMX5000MM")
        self.assertTrue(res.Success)
        self.assertAlmostEqualRel(res.InternalA, 2250.0 / 304.8)
        self.assertAlmostEqualRel(res.InternalB, 5000.0 / 304.8)

    def test_tolerant_asterisk_and_slash(self):
        res1 = SmartDimensionParser.parse("2.25m*5.00m")
        self.assertTrue(res1.Success)
        self.assertAlmostEqualRel(res1.InternalA, 2.25 / 0.3048)

        res2 = SmartDimensionParser.parse("2.25m/5.00m")
        self.assertTrue(res2.Success)
        self.assertAlmostEqualRel(res2.InternalA, 2.25 / 0.3048)

    def test_feet_and_inches(self):
        res = SmartDimensionParser.parse("10'-6\" x 12'-0\"")
        self.assertTrue(res.Success)
        self.assertAlmostEqualRel(res.InternalA, 10.5)
        self.assertAlmostEqualRel(res.InternalB, 12.0)
        self.assertEqual(res.SourceType, "Feet & Inches")

    def test_unit_inheritance_first_has_unit(self):
        res = SmartDimensionParser.parse("2.25m x 5.00")
        self.assertTrue(res.Success)
        self.assertEqual(res.SourceType, "Inherited Units")
        self.assertAlmostEqualRel(res.InternalA, 2.25 / 0.3048)
        self.assertAlmostEqualRel(res.InternalB, 5.00 / 0.3048)
        self.assertTrue(len(res.ParseWarnings) > 0)

    def test_unit_inheritance_second_has_unit(self):
        res = SmartDimensionParser.parse("2.25 x 5.00m")
        self.assertTrue(res.Success)
        self.assertEqual(res.SourceType, "Inherited Units")
        self.assertAlmostEqualRel(res.InternalA, 2.25 / 0.3048)
        self.assertAlmostEqualRel(res.InternalB, 5.00 / 0.3048)
        self.assertTrue(len(res.ParseWarnings) > 0)

    def test_invalid_formats(self):
        invalid_inputs = [
            "",
            "   ",
            "hello world",
            "100",
            "abc x def",
            "10 x 20 x 30",  # ambiguous 3D
        ]
        for inp in invalid_inputs:
            res = SmartDimensionParser.parse(inp)
            self.assertFalse(res.Success, "Expected failure for: {}".format(inp))
            self.assertEqual(res.ErrorMessage, "Invalid Format")


if __name__ == '__main__':
    unittest.main()
