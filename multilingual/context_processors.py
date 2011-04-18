#UNCHECKED
from multilingual.languages import get_all, get_language
from multilingual.settings import LANG_DICT
from django.conf import settings


def multilingual(request):
    """
    Returns context variables containing information about available languages.
    """
    codes = sorted(get_all())
    #TODO: LANGUAGE_CODES, LANGUAGE_CODES_AND_NAMES available in i18n context processor
    return {'LANGUAGE_CODES': codes,
            'LANGUAGE_CODES_AND_NAMES': [(c, LANG_DICT.get(c, c)) for c in codes], 
            'DEFAULT_LANGUAGE_CODE': get_language(),
            'ADMIN_MEDIA_URL': settings.ADMIN_MEDIA_PREFIX}
