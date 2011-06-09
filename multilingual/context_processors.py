"""
Multilingual context processor

Context variables:
  * ML_LANGUAGE - active language for multilingual usage

Deprecated variables:
  * LANGUAGE_CODES - LANGUAGES variable provided by i18n context processor
  * LANGUAGE_CODES_AND_NAMES - LANGUAGES variable provided by i18n context processor
  * DEFAULT_LANGUAGE_CODE
  * ADMIN_MEDIA_URL
"""
from django.conf import settings
from multilingual.languages import get_active, get_dict, get_all, get_settings_default


def multilingual(request):
    """
    Returns context variables containing information about available languages.
    """
    codes = sorted(get_all())
    return {
        'ML_LANGUAGE': get_active(),

        # DEPRECATED context
        #TODO: LANGUAGE_CODES, LANGUAGE_CODES_AND_NAMES available in i18n context processor
            'LANGUAGE_CODES': codes,
            'LANGUAGE_CODES_AND_NAMES': get_dict(), 
            'DEFAULT_LANGUAGE_CODE': get_settings_default(),
            'ADMIN_MEDIA_URL': settings.ADMIN_MEDIA_PREFIX}
