"""
Utilities for models and queries.
"""
from django.db.models.constants import LOOKUP_SEP
from django.db.models.fields import FieldDoesNotExist

from multilingual.db.models.fields import TranslationProxyField, TRANSLATION_FIELD_NAME
from multilingual.utils import sanitize_language_code


def _get_proxy_or_none(opts, field_name):
    # Utility to get TranslationProxyField or None
    try:
        field = opts.get_virtual_field(field_name)
    except FieldDoesNotExist:
        return None

    if isinstance(field, TranslationProxyField):
        return field
    else:
        return None


def expand_lookup(opts, field_name):
    """
    Utility that expands simple multilingual lookup to lookup which can be handled by DJango ORM.
    """
    # Check if field is a translation
    field = _get_proxy_or_none(opts, field_name)
    if field is None:
        # Not a multilingual lookup, return
        return field_name

    # Multilingual field, add 'TranslationRelation' to lookup
    translation_name = '%s_%s' % (TRANSLATION_FIELD_NAME, sanitize_language_code(field.language_code))
    return LOOKUP_SEP.join((translation_name, field.field_name))
