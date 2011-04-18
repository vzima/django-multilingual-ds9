"""
Test language setters, getters and fallbacks
"""
import unittest

from multilingual import languages


class LanguagesTest(unittest.TestCase):

    def setUp(self):
        # Store language settings before tests
        pass

    def tearDown(self):
        # Restore language settings after tests
        pass

    def test01_settings(self):
        self.assertEqual(languages.get_language(), 'cs')

    #TODO: check language re-seting
    #TODO: also do not forget to check good behavior in on of apps
    #TODO: check thread safety

def suite():
    s = unittest.TestSuite()
    s.addTest(unittest.makeSuite(LanguagesTest))
    return s
