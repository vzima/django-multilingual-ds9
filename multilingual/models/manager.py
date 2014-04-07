"""
Manager for multilingual models
"""
from django.db.models import Manager

from .query import MultilingualQuerySet


class MultilingualManager(Manager):
    """
    A manager for multilingual models.
    """
    #TODO: turn this into a proxy manager that would allow developers
    # to use any manager they need.  It should be sufficient to extend
    # and additionaly filter or order querysets returned by that manager.
    def get_queryset(self):
        return MultilingualQuerySet(self.model)
