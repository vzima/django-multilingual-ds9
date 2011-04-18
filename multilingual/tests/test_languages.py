# -*- coding: utf-8 -*-
"""
Test language setters, getters and fallbacks
"""
import unittest

from django.conf import settings
from django.utils.datastructures import SortedDict
from django.utils.translation import get_language, activate

from multilingual import languages


class LanguagesTest(unittest.TestCase):
    LANGUAGES = (
        ('cs', u'Čeština'),
        ('en', u'English'),
    )
    LANGUAGE_CODE = 'cs'

    def setUp(self):
        self.old_language = get_language()
        self.old_languages = settings.LANGUAGES
        self.old_language_code = settings.LANGUAGE_CODE
        settings.LANGUAGES = self.LANGUAGES
        settings.LANGUAGE_CODE = self.LANGUAGE_CODE
        activate(self.LANGUAGE_CODE)

    def tearDown(self):
        # Reset old language
        activate(self.old_language)
        settings.LANGUAGES = self.old_languages
        settings.LANGUAGE_CODE = self.old_language_code

    def test01_basics(self):
        self.assertEqual(languages.get_dict(), SortedDict(self.LANGUAGES))
        self.assertEqual(languages.get_all(), ['cs', 'en'])
        self.assertEqual(languages.get_settings_default(), 'cs')
        self.assertEqual(languages.get_active(), 'cs')

    def test02_fallbacks(self):
        self.assertEqual(languages.get_fallbacks('cs'), ['en'])
        self.assertEqual(languages.get_fallbacks('en'), ['cs'])

    def test03_language_change(self):
        activate('en')
        self.assertEqual(languages.get_active(), 'en')

    def test04_incorrect_language(self):
        activate('INCORRECT_LANGUAGE')
        self.assertEqual(languages.get_active(), 'cs')

    def test05_lock(self):
        languages.lock('en')
        self.assertEqual(languages.is_locked(), True)
        self.assertEqual(languages.get_active(), 'en')
        languages.release()
        self.assertEqual(languages.is_locked(), False)
        self.assertEqual(languages.get_active(), 'cs')

    #TODO: check thread safety


def suite():
    s = unittest.TestSuite()
    s.addTest(unittest.makeSuite(LanguagesTest))
    return s
