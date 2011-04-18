import warnings

from multilingual.languages import get_dict, get_all, get_language
from django.conf import settings


def multilingual(request):
    """
    Returns context variables containing information about available languages.
    """
    warnings.warn('Context processor multilingual is deprecated, use template tags instead.')

    codes = sorted(get_all())
    #TODO: LANGUAGE_CODES, LANGUAGE_CODES_AND_NAMES available in i18n context processor
    return {'LANGUAGE_CODES': codes,
            'LANGUAGE_CODES_AND_NAMES': get_dict(), 
            'DEFAULT_LANGUAGE_CODE': get_language(),
            'ADMIN_MEDIA_URL': settings.ADMIN_MEDIA_PREFIX}
