"""
Deprecated module

'DefaultLanguageMiddleware' has no function because of changes in resolving language used by multilingual.
"""
import warnings
warnings.warn("Midlleware 'multilingual.middleware.DefaultLanguageMiddleware' is deprecated.", DeprecationWarning)

# No addition language setting is necessary
class DefaultLanguageMiddleware(object):
    pass
