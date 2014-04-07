"""
Base model for multilingual models.
"""
from new import classobj

from django.db import models
from django.db.models.base import ModelBase

from multilingual.languages import get_all

from .fields import TranslationProxyField, TranslationRelation, TRANSLATION_FIELD_NAME
from .manager import MultilingualManager
from .options import MultilingualOptions
from .translation import TranslationModelBase, TranslationModel

# TODO: inheritance of multilingual models and translation models


class MultilingualModelBase(ModelBase):
    def __new__(cls, name, bases, attrs):
        ### START - Build translation model
        # At first we build translation model so we can add it to attrs
        # Purpose is to not call 'add_to_class' after model is registered

        # We have to copy attributes because they change during creation of a model
        trans_attrs = attrs.copy()

        # Make a copy of Meta, so changes in it when creating a translation model does not affect
        # creation of multilingual model
        if attrs.has_key('Meta'):
            trans_attrs['Meta'] = classobj.__new__(classobj, 'Meta', (attrs['Meta'],), attrs['Meta'].__dict__.copy())

        translation_name = name + "Translation"
        trans_attrs['multilingual_model_name'] = name
        c_trans_model = TranslationModelBase(translation_name, (TranslationModel, ), trans_attrs)
        ### END - Build translation model

        ### And some changes before we build multilingual model
        meta = attrs.get('Meta', None)
        abstract = getattr(meta, 'abstract', False)

        # Add translation model to attrs
        attrs['translation_model'] = c_trans_model

        if not abstract:
            # Add translation relations
            for language_code in [None] + get_all():
                field = TranslationRelation(c_trans_model, base_name=TRANSLATION_FIELD_NAME,
                                            language_code=language_code)
                attrs[field.name] = field

            # Add proxies for translated fields into attrs
            for field in (c_trans_model._meta.fields + c_trans_model._meta.many_to_many):
                if field.name in ('id', 'language_code', 'master'):
                    continue
                for language_code in get_all():
                    proxy = TranslationProxyField(field.name, language_code)
                    attrs[proxy.name] = proxy
                proxy = TranslationProxyField(field.name, None)
                attrs[proxy.name] = proxy
                proxy = TranslationProxyField(field.name, None, fallback=True)
                attrs[proxy.name] = proxy

        # Handle manager
        if not 'objects' in attrs:
            # If there is no manager, set MultilingualManager as manager
            attrs['objects'] = MultilingualManager()
        elif not isinstance(attrs['objects'], MultilingualManager):
            # Make sure that if the class specifies objects then it is a subclass of our Manager.

            # Don't check other managers since someone might want to have a non-multilingual manager, but assigning
            # a non-multilingual manager to objects would be a common mistake.
            raise ValueError("Model %s specifies translations, so its 'objects' manager must be a subclass of "\
                             "multilingual.Manager." % name)

        # And now just create multilingual model
        return super(MultilingualModelBase, cls).__new__(cls, name, bases, attrs)

    def add_to_class(cls, name, value):
        # Catch meta and change its class, it is HACK, but it is the least ugly one
        if name == '_meta':
            value = MultilingualOptions(value.meta, value.app_label)
        super(MultilingualModelBase, cls).add_to_class(name, value)


class MultilingualModel(models.Model):
    __metaclass__ = MultilingualModelBase

    class Meta:
        abstract = True

    def save(self, force_insert=False, force_update=False, using=None):
        """
        Change save method to save translations when multilingual object is saved.
        """
        super(MultilingualModel, self).save(force_insert=force_insert, force_update=force_update, using=using)
        for field in self._meta.fields:
            if not isinstance(field, TranslationRelation):
                continue

            # Find translation. Use cache name to prevent any unnecessary SQL queries.
            # If it isn't loaded, it isn't changed.
            attr_name = field.get_cache_name()
            translation = getattr(self, attr_name, None)

            if translation is None:
                # Translation does not exist, continue with next
                continue

            # Set the master ID. The master and translation could be just created.
            translation.master_id = self.pk
            translation.save()
