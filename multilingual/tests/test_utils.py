"""
Tests for utility code.
"""
import unittest

from multilingual.utils import sanitize_language_code


class TestUtils(unittest.TestCase):
    """
    Test utility functions.
    """
    def test_sanitize_language_code(self):
        self.assertEqual(sanitize_language_code('cs'), 'cs')
        self.assertEqual(sanitize_language_code('en'), 'en')
        self.assertEqual(sanitize_language_code('en-us'), 'en_us')
