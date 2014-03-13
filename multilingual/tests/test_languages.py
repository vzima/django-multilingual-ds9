# -*- coding: utf-8 -*-
"""
Test language setters, getters and fallbacks
"""
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.test.utils import override_settings
from django.utils.datastructures import SortedDict
from django.utils.translation import activate, deactivate_all

from multilingual import languages

from .base import TEST_LANGUAGES


@override_settings(LANGUAGE_CODE='cs', LANGUAGES=TEST_LANGUAGES)
class TestLanguages(TestCase):
    """
    Test language utilities
    """
    def tearDown(self):
        # Reset languages
        deactivate_all()
        languages.release()

    def test_get_dict(self):
        result = SortedDict((('cs', u'Čeština'), ('en', u'English'), ('en-us', u'American'), ('fr', u'Français')))
        self.assertEqual(languages.get_dict(), result)

    def test_get_all(self):
        self.assertEqual(languages.get_all(), ['cs', 'en', 'en-us', 'fr'])

    def test_get_settings_default(self):
        self.assertEqual(languages.get_settings_default(), 'cs')

        # Check activate has no effect on default
        activate('en')
        self.assertEqual(languages.get_settings_default(), 'cs')

    @override_settings(LANGUAGE_CODE='pl')
    def test_get_settings_default_error(self):
        self.assertRaises(ImproperlyConfigured, languages.get_settings_default)

    def test_get_active(self):
        deactivate_all()
        # No active language, returns default
        self.assertEqual(languages.get_active(), 'cs')

        activate('en')
        # Active language is returned
        self.assertEqual(languages.get_active(), 'en')

    def test_get_active_undefined(self):
        # Django allows activation of language not defined in settings, we need to cope for that.
        activate('INCORRECT_LANGUAGE')
        self.assertEqual(languages.get_active(), 'cs')

    def test_get_fallbacks(self):
        self.assertEqual(languages.get_fallbacks('cs'), [])
        # Languages has default as fallback
        self.assertEqual(languages.get_fallbacks('en'), ['cs'])
        self.assertEqual(languages.get_fallbacks('fr'), ['cs'])
        # Short language version is a fallback for language
        self.assertEqual(languages.get_fallbacks('en-us'), ['en', 'cs'])

    def test_lock(self):
        activate('en')
        self.assertFalse(languages.is_locked())
        self.assertEqual(languages.get_active(), 'en')

        languages.lock('fr')

        self.assertTrue(languages.is_locked())
        self.assertEqual(languages.get_active(), 'fr')

        languages.release()

        self.assertFalse(languages.is_locked())
        self.assertEqual(languages.get_active(), 'en')

    def test_get_table_alias(self):
        self.assertEqual(languages.get_table_alias('table_name', 'cs'), 'table_name_cs')
        self.assertEqual(languages.get_table_alias('table_name', 'en'), 'table_name_en')
        self.assertEqual(languages.get_table_alias('table_name', 'en-us'), 'table_name_en_us')

    def test_get_field_alias(self):
        self.assertEqual(languages.get_field_alias('field_name', 'cs'), '_trans_field_name_cs')
        self.assertEqual(languages.get_field_alias('field_name', 'en'), '_trans_field_name_en')
        self.assertEqual(languages.get_field_alias('field_name', 'en-us'), '_trans_field_name_en_us')
