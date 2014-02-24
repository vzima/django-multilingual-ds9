"""
Pre-processing of language settings and other language related functions.
"""
from threading import local

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.datastructures import SortedDict
from django.utils.translation import get_language


FALLBACK_FIELD_SUFFIX = 'any'

#TODO: enable locks included in each other
#TODO: decorator for language locks
_lock = local()


def get_dict():
    """
    So far only wrapper on LANGUAGES setting.
    """
    return SortedDict(settings.LANGUAGES)


def get_all():
    """
    Returns tuple of defined language codes.
    """
    return get_dict().keys()


def get_settings_default():
    """
    Returns default language from settings.
    @raise ImproperlyConfigured: If LANGUAGE_CODE is not in LANGUAGES.
    """
    #TODO: move it so it is checked only once
    if settings.LANGUAGE_CODE not in get_all():
        raise ImproperlyConfigured(
            "LANGUAGE_CODE '%s' is not one of LANGUAGES." \
            "Set one of LANGUAGES as LANGUAGE_CODE or add '%s' to LANGUAGES."
            % (settings.LANGUAGE_CODE, settings.LANGUAGE_CODE)
        )
    return settings.LANGUAGE_CODE


def lock(language_code):
    """
    Locks language and disables fallbacks
    """
    if language_code not in get_all():
        raise ValueError("Invalid language '%s'" % language_code)
    _lock.value = language_code


def release():
    """
    Releases language lock
    """
    if hasattr(_lock, "value"):
        del _lock.value

def is_locked():
    """
    Returns state of lock
    """
    return hasattr(_lock, "value")


def get_active():
    """
    Returns active language for multilingual

    Differs from django's get_language:
    - always returns one of settings.LANGUAGES
    - is influenced by language locks
    """
    # Check locked languages
    # This might be faster than call is_locked() method
    language_code = getattr(_lock, "value", None)
    if language_code is not None:
        return language_code

    # Get language from django
    language_code = get_language()
    if language_code not in get_all():
        # Try to use only first component
        parts = language_code.split('-', 1)
        if len(parts) == 2 and parts[0] in get_all():
            language_code = parts[0]
        else:
            # Get default language from settings
            language_code = get_settings_default()
    return language_code


def get_fallbacks(language_code):
    """
    Returns list of fallbacks for language.

    Fallbacks are:
      * language made of first two letters of original
      * default language

    All fallbacks must be set in settings.LANGUAGES and must differ from original language.
    """
    fallbacks = []
    language = language_code[:2]
    if language != language_code and language in get_all():
        fallbacks.append(language)

    language = get_settings_default()
    if language != language_code:
        fallbacks.append(language)

    return fallbacks
