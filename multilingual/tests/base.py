# -*- coding: utf-8 -*-
import os
import sys

from django.conf import settings
from django.core.management import call_command
from django.db.models.loading import cache, load_app
from django.test.utils import override_settings


# All tests using ml_test_app need the same LANGUAGES settings. Define it here.
TEST_LANGUAGES = (('cs', u'Čeština'), ('en', u'English'), ('en-us', u'American'), ('fr', u'Français'))


class MultilingualSetupMixin(object):
    """
    Sets up environment for testing multilingual application.

    Defines languages settings so models are created with defined translation fields.
    """
    @classmethod
    def setUpClass(cls):
        # Modify sys path
        cls.old_sys_path = sys.path[:]
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))

        # Change settings, we can't use decorator that would change settings too late for us.
        cls.override = override_settings(LANGUAGE_CODE='cs', LANGUAGES=TEST_LANGUAGES,
                                         INSTALLED_APPS=list(settings.INSTALLED_APPS) + ['ml_test_app'])
        cls.override.enable()
        # Install test app
        load_app('ml_test_app')
        call_command('syncdb', verbosity=0)

    @classmethod
    def tearDownClass(cls):
        # Restore sys path
        sys.path = cls.old_sys_path

        # Restore settings
        cls.override.disable()

        # Clean app cache
        cache._get_models_cache.clear()
        cache.handled.clear()
        cache.loaded = False
        cache._populate()
