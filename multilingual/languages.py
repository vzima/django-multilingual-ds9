"""
Pre-processing of language settings and other language related functions.
"""
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.datastructures import SortedDict
from django.utils.thread_support import currentThread
from django.utils.translation import get_language


FALLBACK_FIELD_SUFFIX = 'any'

#TODO: enable locks included in each other
#TODO: decorator for language locks
_locks = {}


def get_dict():
    """
    So far only wrapper on LANGUAGES setting.
    """
    return SortedDict(settings.LANGUAGES)


def get_all():
    """
    Tuple of defined language codes.
    """
    return get_dict().keys()


def get_settings_default():
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
    _locks[currentThread()] = language_code


def release():
    """
    Releases language lock
    """
    _locks.pop(currentThread(), None)


def is_locked():
    """
    Returns state of lock
    """
    return currentThread() in _locks


def get_active():
    """
    Differs from django's get_language:
    - always returns one of LANGUAGES in settings
    - is influenced by language locks
    """
    # 1. check locked language
    # 2. get language from django if one of LANGUAGES
    # 3. get default language from settings

    # This is faster that call is_locked() method
    language_code = _locks.get(currentThread())
    if language_code is not None:
        return language_code

    language_code = get_language()
    if language_code not in get_all():
        # Try to use only first component
        parts = language_code.split('-', 1)
        if len(parts) == 2 and parts[0] in get_all():
            language_code = parts[0]
        else:
            language_code = get_settings_default()
    return language_code


def get_fallbacks(language_code):
    """
    Returns enabled fallbacks for language.
    """
    fallbacks = []
    language = language_code[:2]
    if language != language_code and language in get_all():
        fallbacks.append(language)

    language = get_settings_default()
    if language != language_code:
        fallbacks.append(language)

    return fallbacks


def _db_prep_language_code(language_code):
    return language_code.replace('-', '_')


def get_table_alias(table_name, language_code):
    return '%s_%s' % (table_name, _db_prep_language_code(language_code))


def get_field_alias(field_name, language_code):
    return '_trans_%s_%s' % (field_name, _db_prep_language_code(language_code))


### DEPRECATED ###

def get_language_name(language_code):
    return dict(settings.LANGUAGES)[language_code]

def get_language_bidi(language_code):
    return language_code in settings.LANGUAGES_BIDI

def get_language_idx(language_code):
    return get_all().index(language_code)
