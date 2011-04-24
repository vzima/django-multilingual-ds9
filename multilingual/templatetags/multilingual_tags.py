import warnings

from django import template

from multilingual.templatetags.multiling import language_lock


warnings.warn("Library 'multilingual_tags' is deprecated in favor of 'multiling' library", DeprecationWarning)
register = template.Library()


def gll(parser, token):
    warnings.warn("Template tag 'gll' is deprecated in favor of 'lang_lock' tag.", DeprecationWarning)
    return language_lock(parser, token)

register.tag('gll', gll)
