"""
Query for multilingual models
"""
import warnings

from django.db.models.constants import LOOKUP_SEP
from django.db.models.sql.query import get_order_dir, Query

from multilingual.db.models.fields import TRANSLATION_FIELD_NAME
from multilingual.db.models.utils import expand_lookup
from multilingual.languages import get_all, get_active
from multilingual.utils import sanitize_language_code


__all__ = ['MultilingualQuery']


class MultilingualQuery(Query):
    """
    Query for multilingual models

    For proper function we need to take care of JOINs between multilingual and translation tables.
    """
    def build_filter(self, filter_expr, branch_negated=False, current_negated=False,
                     can_reuse=None):
        """
        Build filters with respect to the multilingual fields.
        """
        arg, value = filter_expr
        parts = arg.split(LOOKUP_SEP)

        field_name = parts[0]
        new_name = expand_lookup(self.get_meta(), field_name)
        filter_expr = LOOKUP_SEP.join([new_name] + parts[1:]), value

        return super(MultilingualQuery, self).build_filter(filter_expr, branch_negated=branch_negated,
                                                           current_negated=current_negated, can_reuse=can_reuse)

    def add_fields(self, field_names, allow_m2m=True):
        opts = self.get_meta()
        new_field_names = [expand_lookup(opts, f) for f in field_names]
        return super(MultilingualQuery, self).add_fields(new_field_names, allow_m2m=allow_m2m)

    def add_ordering(self, *ordering):
        new_ordering = []
        for order in ordering:
            field_name, dirn = get_order_dir(order)
            new_name = expand_lookup(self.get_meta(), field_name)
            if dirn == 'DESC':
                new_name = '-%s' % new_name
            new_ordering.append(new_name)
        return super(MultilingualQuery, self).add_ordering(*new_ordering)

    def add_select_related(self, fields):
        """
        Sets up the select_related data structure so that we only select
        certain related models (as opposed to all models, when
        self.select_related=True).
        """
        new_fields = []
        opts = self.model._meta

        # There is not actually any useful code, all this is to handle deprecated arguments.
        for field_name in fields:
            if field_name.startswith('translations'):
                new_name = None

                if field_name == 'translations':
                    new_name = '%s_%s' % (TRANSLATION_FIELD_NAME, sanitize_language_code(get_active()))
                elif '_' in field_name:
                    dummy, language_code = field_name.rsplit('_', 1)
                    if language_code in get_all():
                        new_name = '%s_%s' % (TRANSLATION_FIELD_NAME, sanitize_language_code(language_code))

                if new_name:
                    msg = "Using '%s' in select_related is deprecated, use '%s' or '%s' instead."
                    warnings.warn(msg % (field_name, TRANSLATION_FIELD_NAME, new_name), DeprecationWarning)
                    new_fields.append(TRANSLATION_FIELD_NAME)
                    new_fields.append(new_name)
                    continue

            # In all other cases use the old name
            new_fields.append(field_name)

        new_fields = set(new_fields)
        return super(MultilingualQuery, self).add_select_related(new_fields)
