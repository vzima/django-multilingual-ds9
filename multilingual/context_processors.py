from django.conf import settings
from multilingual.languages import get_active, get_dict, get_all, get_settings_default


def multilingual(request):
    """
    Returns context variables containing information about available languages.
    """
    codes = sorted(get_all())
    return {
        'active_language': get_active(),

        # DEPRECATED context
        #TODO: LANGUAGE_CODES, LANGUAGE_CODES_AND_NAMES available in i18n context processor
            'LANGUAGE_CODES': codes,
            'LANGUAGE_CODES_AND_NAMES': get_dict(), 
            'DEFAULT_LANGUAGE_CODE': get_settings_default(),
            'ADMIN_MEDIA_URL': settings.ADMIN_MEDIA_PREFIX}
