import warnings
warnings.warn('Utils module deprecated.')

from multilingual.languages import lock, release, is_locked, get_active

try:
    from django.utils.decorators import auto_adapt_to_methods as method_decorator
except ImportError:
    from django.utils.decorators import method_decorator


def is_multilingual_model(model):
    """
    Return True if `model` is a multilingual model.
    """
    return hasattr(model._meta, 'translation_model')


## DEPRECATED
class GLLError(Exception):
    pass


class GlobalLanguageLock(object):
    """
    The Global Language Lock can be used to force django-multilingual-ng to use
    a specific language and not try to fall back.
    """
    lock = lock
    release = release

    @property
    def language_code(self):
        return get_active()

    @property
    def is_active(self):
        return is_locked()

GLL = GlobalLanguageLock()


def gll_unlock_decorator(func):
    def _decorated(*args, **kwargs):
        if not GLL.is_active:
            return func(*args, **kwargs)
        language_code = GLL.language_code
        GLL.release()
        result = func(*args, **kwargs)
        GLL.lock(language_code)
        return result
    _decorated.__name__ = func.__name__
    _decorated.__doc__ = func.__doc__
    return _decorated
gll_unlock = method_decorator(gll_unlock_decorator)
