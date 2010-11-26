"""
Django-multilingual: a QuerySet subclass for models with translatable
fields.

This file contains the implementation for QSRF Django.
"""
from copy import deepcopy

from django.db.models.query import QuerySet
from django.db.models.sql.query import Query
from django.db.models.sql.where import AND, Constraint

from multilingual.languages import (
    get_translation_table_alias,
    get_default_language,
    get_translated_field_alias)


__ALL__ = ['MultilingualModelQuerySet']


class MultilingualQuery(Query):
    def setup_joins(self, names, opts, alias, dupe_multis, allow_many=True,
            allow_explicit_fk=False, can_reuse=None, negate=False,
            process_extras=True):
        """
        This overrides setup_joins method in case we want to join multilingual field.
        This is hell good place to rewrite something because it is called for every time when we care.
        """
        trans_opts = opts.translation_model._meta
        # So far we only handle fields that are local for TranslationModel (not related)
        # so we can only take care of first of names, see NotImplementedError lower
        field_name = names[0]
        field_and_lang = trans_opts.translated_fields.get(field_name)

        # Field is not multilingual, proceed as usual
        if not field_and_lang:
            return super(MultilingualQuery, self).setup_joins(names, opts, alias, dupe_multis, allow_many,
                                                              allow_explicit_fk, can_reuse, negate, process_extras)

        if len(names) > 1:
            raise NotImplementedError('MultilingualQuery can not now handle relations through multilingual fields')

        field, language_code = field_and_lang
        if language_code is None:
            language_code = get_default_language()
        trans_table_name = trans_opts.db_table
        table_alias = get_translation_table_alias(trans_table_name, language_code)

        # Exclude table aliases for other languages to prevent language mismatch
        # TEST: filter(name_en="some", name_cs="neco")
        exclusions = set(self.table_map.get(trans_table_name, [])) - set([table_alias])

        # Enable reusing of translation table alias for required language so translations for one language are
        # added only once
        # TEST: filter(name_en="some").values('name_en')
        reuse = can_reuse or set()
        reuse.add(table_alias)

        # Important step 1: join translation table under language-specific alias
        # QUESTION: is LEFT OUTER JOIN always required?
        # HACK: this is hell of a hack, but it is only way that django enables for extra joins now :-(
        #       Still hopes, that it will get better someday and there will be correct way how add condition into join
        right_column = '"master_id" AND \'%s\' = "%s"."language_code"' % (language_code, table_alias)
        trans_alias = self.join((alias, trans_table_name, opts.pk.column, right_column), always_create=True,
                        reuse=reuse, exclusions=exclusions, promote=True, nullable=True)

        # Important step 2: if required alias has not been defined yet, new alias is created in during join
        # We change the alias to language-specific alias, so we can check whether it is already present
        if trans_alias != table_alias:
            self.change_aliases({trans_alias: table_alias})

        # This works, not sure why, but it works :-)
        #return field, target, opts, join_list, last, extra_filter
        return field, field, opts, [table_alias], [0, 1], []


class MultilingualModelQuerySet(QuerySet):
    """
    A specialized QuerySet that knows how to handle translatable
    fields in ordering and filtering methods.
    """

    def __init__(self, model=None, query=None, using=None):
        query = query or MultilingualQuery(model)
        super(MultilingualModelQuerySet, self).__init__(model, query, using)

    def __deepcopy__(self, memo):
        """
        Deep copy of a QuerySet doesn't populate the cache
        """
        obj_dict = deepcopy(self.__dict__, memo)
        obj_dict['_iter'] = None
        #=======================================================================
        # Django Multilingual NG Specific Code START
        #=======================================================================
        obj = self.__class__(self.model) # add self.model as first argument
        #=======================================================================
        # Django Multilingual NG Specific Code END
        #=======================================================================
        obj.__dict__.update(obj_dict)
        return obj

    def for_language(self, language_code):
        """
        Set the default language for all objects returned with this
        query.
        """
        clone = self._clone()
        clone._default_language = language_code
        return clone

    def iterator(self):
        """
        Add the default language information to all returned objects.
        """
        default_language = getattr(self, '_default_language', None)
        for obj in super(MultilingualModelQuerySet, self).iterator():
            obj._default_language = default_language
            yield obj

    def _clone(self, klass=None, **kwargs):
        """
        Override _clone to preserve additional information needed by
        MultilingualModelQuerySet.
        """
        clone = super(MultilingualModelQuerySet, self)._clone(klass, **kwargs)
        clone._default_language = getattr(self, '_default_language', None)
        return clone

    def order_by(self, *field_names):
        if hasattr(self.model._meta, 'translation_model'):
            trans_opts = self.model._meta.translation_model._meta
            new_field_names = []
            for field_name in field_names:
                prefix = ''
                if field_name[0] == '-':
                    prefix = '-'
                    field_name = field_name[1:]
                field_and_lang = trans_opts.translated_fields.get(field_name)
                if field_and_lang:
                    field, language_code = field_and_lang
                    if language_code is None:
                        language_code = getattr(self, '_default_language', None)
                    real_name = get_translated_field_alias(field.attname,
                                                           language_code)
                    new_field_names.append(prefix + real_name)
                else:
                    new_field_names.append(prefix + field_name)
            return super(MultilingualModelQuerySet, self).extra(order_by=new_field_names)
        else:
            return super(MultilingualModelQuerySet, self).order_by(*field_names)
