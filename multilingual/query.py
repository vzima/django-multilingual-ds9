"""
Django-multilingual: a QuerySet subclass for models with translatable fields.
"""
from copy import deepcopy

from django.db import connection
from django.db.models.query import QuerySet
from django.db.models.sql.query import Query
from django.db.models.sql.where import AND

from multilingual.languages import get_translation_table_alias, get_translated_field_alias, get_default_language, \
    get_language_code_list


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
        # XXX: did not work in MySQL, so take quoting from default database until correctly fixed
        qn = connection.ops.quote_name
        right_column = '%s AND \'%s\' = %s.%s' % (
                            qn('master_id'),
                            language_code,
                            table_alias, # do not quote, it is alias
                            qn('language_code')
                       )
        trans_alias = self.join((alias, trans_table_name, opts.pk.column, right_column), always_create=True,
                        reuse=reuse, exclusions=exclusions, promote=True, nullable=True)

        # Important step 2: if required alias has not been defined yet, new alias is created in during join
        # We change the alias to language-specific alias, so we can check whether it is already present
        if trans_alias != table_alias:
            self.change_aliases({trans_alias: table_alias})

        # This works, not sure why, but it works :-)
        #return field, target, opts, join_list, last, extra_filter
        return field, field, opts, [table_alias], [0, 1], []


    def add_select_related(self, fields):
        """
        If in fields is related_field for translations, will be replaced by fields in proper languages.
        """
        new_fields = []
        extra_select = {}
        opts = self.model._meta
        trans_opts = opts.translation_model._meta
        related_name = trans_opts.related_name

        translation_fields = [f.name for f in trans_opts.fields if f.name not in ('master', 'language_code')]

        for field in fields:
            # usual select_related
            if not field.startswith(related_name):
                new_fields.append(field)
                continue

            # get language
            if field == related_name:
                language_code = get_default_language()
            else:
                field_and_lang = field.rsplit('_', 1)
                # Coincidental field name might occur if language_code is not correct, do not do anything as 
                # select_related does not raise errors if used with incorrect fields
                if len(field_and_lang) != 2 or field_and_lang[1] not in get_language_code_list():
                    new_fields.append(field)
                    continue
                field, language_code = field_and_lang

            # This is main code of this method, build extra_select that might be used by fill_translation_cache
            for trans_field in translation_fields:
                extra_select[get_translated_field_alias(trans_field, language_code)] = '%s."%s"' % (
                    get_translation_table_alias(trans_opts.db_table, language_code),
                    trans_field
                )

            # XXX: this is not save if translation model has no fields, can it happen??

            # join translatable model (original) table if not joined yet
            alias = self.get_initial_alias()

            # join translation table if not joined yet
            translation_fields.remove(trans_opts.pk.name)
            self.setup_joins(
                ['%s_%s' % (translation_fields[0], language_code)], # any translated_field
                opts,
                alias,
                True,
                can_reuse = set([alias])
            )

        if extra_select:
            self.add_extra(extra_select, None, None, None, None, None)
        super(MultilingualQuery, self).add_select_related(new_fields)


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
