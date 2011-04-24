import warnings
warnings.warn("Midlleware 'multilingual.middleware.DefaultLanguageMiddleware' is deprecated.", DeprecationWarning)

# No addition language setting is necessary
class DefaultLanguageMiddleware(object):
    pass
