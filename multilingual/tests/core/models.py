from django.db import models
from multilingual.db.models.base import MultilingualModel


class Basic(MultilingualModel):
    """
    Model for testing basic multilingual functions
    """
    description = models.CharField(max_length=20)

    class Translation:
        title = models.CharField(max_length=20)


class Managing(MultilingualModel):
    """
    Model for testing manager of multilingual model
    """
    shortcut = models.CharField(max_length=20)

    class Translation:
        name = models.CharField(max_length=20)
