"""
Provides virtual field to access to translation from multilingual model instance.
"""
from django.db.models import ForeignObject
from django.db.models.deletion import DO_NOTHING
from django.db.models.fields.related import OneToOneRel, ReverseSingleRelatedObjectDescriptor
from django.db.models.related import PathInfo
from django.db.models.sql.where import Constraint

from multilingual.languages import get_active, get_fallbacks, FALLBACK_FIELD_SUFFIX
from multilingual.utils import sanitize_language_code


TRANSLATION_FIELD_NAME = 'translation'


class TranslationRel(OneToOneRel):
    # Relation is always one-to-one
    def __init__(self, field, to, **kwargs):
        # Relation is always bound to 'master'
        kwargs['field_name'] = 'master'
        kwargs['related_name'] = 'master'
        # Semi-virtual relation, do nothing on delete
        kwargs['on_delete'] = DO_NOTHING
        super(TranslationRel, self).__init__(field, to, **kwargs)

    def is_hidden(self):
        # The related object is always hidden.
        return True


class TranslationDescriptor(ReverseSingleRelatedObjectDescriptor):
    # Do not cache the field's cache name.
    def __init__(self, field_with_rel):
        self.field = field_with_rel

    @property
    def cache_name(self):
        return self.field.get_cache_name()


# Based on 'django.contrib.contenttypes.generic.GenericRelation' and
# 'django.tests.foreign_object.models.ActiveTranslationField'
class TranslationRelation(ForeignObject):
    """
    Provides an accessor to related translation.
    """
    requires_unique_target = False  # This avoids django validation

    def __init__(self, to, base_name, language_code=None, **kwargs):
        self._base_name = base_name
        self._language_code = language_code

        # Create the field name
        if language_code:
            name = '%s_%s' % (base_name, sanitize_language_code(language_code))
        else:
            name = base_name
        kwargs['name'] = name
        # Disable any modifications of this field
        kwargs['editable'] = False
        kwargs['serialize'] = False
        # Define 'rel' object
        kwargs['rel'] = TranslationRel(self, to)
        # Let queries to fill master object into translation cache, e.g. in select_related.
        kwargs['unique'] = True
        kwargs['null'] = True

        to_fields = ['master']
        super(TranslationRelation, self).__init__(to, [], to_fields, **kwargs)

    def contribute_to_class(self, cls, name, virtual_only=False):
        super(TranslationRelation, self).contribute_to_class(cls, name, virtual_only=virtual_only)
        setattr(cls, self.name, TranslationDescriptor(self))

    @property
    def language_code(self):
        """
        If _language_code is None we are the _current field, so we use the
        currently used language for lookups.
        """
        if self._language_code is not None:
            return self._language_code
        return get_active()

    def get_cache_name(self):
        # The field for active language needs to use the cache for that language
        return '_%s_%s_cache' % (self._base_name, sanitize_language_code(self.language_code))

    def resolve_related_fields(self):
        self.from_fields = [self.model._meta.pk.name]
        return super(TranslationRelation, self).resolve_related_fields()

    def get_extra_descriptor_filter(self, instance):
        return {'language_code': self.language_code}

    def get_extra_restriction(self, where_class, alias, related_alias):
        # alias - Alias of the joined table (translations)
        # related_alias - Alias of the master table
        field = self.rel.to._meta.get_field('language_code')
        cond = where_class()
        cond.add((Constraint(alias, field.column, field), 'exact', self.language_code), 'AND')
        return cond

    def get_path_info(self):
        """
        Get path from this field to the related model.
        """
        opts = self.rel.to._meta
        from_opts = self.model._meta
        #XXX: Changed to indirect
        return [PathInfo(from_opts, opts, self.foreign_related_fields, self, False, False)]


# It would be better if field could be derived just from object, but property is currently
# easiest way to enable initiation of multilingual models with translations
# Problem reported to Django: #16508
#class TranslationProxyField(object):
class TranslationProxyField(property):
    """
    Provides an easy access to field translations.

    Based on code for 'GenericForeignKey' field
    """
    def __init__(self, field_name, language_code=None, fallback=False):
        self._field_name = field_name
        self._language_code = language_code
        self._fallback = fallback

        name = field_name
        if language_code is not None:
            name = '%s_%s' % (name, sanitize_language_code(language_code))
        if fallback:
            name = '%s_%s' % (name, FALLBACK_FIELD_SUFFIX)
        self.name = name

        super(TranslationProxyField, self).__init__()

    def contribute_to_class(self, cls, name):
        self.name = name
        self.model = cls
        cls._meta.add_virtual_field(self)

        # Connect myself as the descriptor for this field
        setattr(cls, name, self)

    @property
    def field_name(self):
        """
        Returns base field name.
        """
        return self._field_name

    @property
    def language_code(self):
        """
        Returns effective language code.
        """
        if self._language_code is not None:
            return self._language_code
        return get_active()

    def __get__(self, instance, instance_type=None):
        """
        Returns field translation or None
        """
        if instance is None:
            return self

        translation_model = self.model._meta.translation_model

        # Find language codes to be tried
        lang_codes = [self.language_code]
        if self._fallback:
            lang_codes += get_fallbacks(self.language_code)

        for lang_code in lang_codes:
            # Find translation
            translation_name = '%s_%s' % (TRANSLATION_FIELD_NAME, sanitize_language_code(lang_code))
            try:
                # Translation is nullable, so it may return None
                translation = getattr(instance, translation_name)
            except translation_model.DoesNotExist:
                translation = None

            if translation is None:
                # Translation does not exist, try another language
                continue

            # Once we have the translation object we return what's there
            return getattr(translation, self._field_name)

        return None

    def __set__(self, instance, value):
        """
        Sets field translation
        """
        translation_model = self.model._meta.translation_model

        # Find translation
        translation_name = '%s_%s' % (TRANSLATION_FIELD_NAME, sanitize_language_code(self.language_code))

        try:
            # Translation is nullable, so it may return None
            translation = getattr(instance, translation_name)
        except translation_model.DoesNotExist:
            translation = None

        if translation is None:
            # Translation does not exist, create one
            translation = translation_model(master=instance, language_code=self.language_code)
            setattr(instance, translation_name, translation)

        # Set the field translation
        setattr(translation, self._field_name, value)
