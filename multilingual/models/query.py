"""
Queryset for multilingual models
"""
from django.db.models.query import QuerySet

from .sql.query import MultilingualQuery


class MultilingualQuerySet(QuerySet):
    """
    A specialized QuerySet that knows how to handle translatable
    fields in ordering and filtering methods.
    """
    def __init__(self, model=None, query=None, using=None):
        query = query or MultilingualQuery(model)
        super(MultilingualQuerySet, self).__init__(model, query, using)
