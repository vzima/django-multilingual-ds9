from django.db import models
from multilingual.db.models.base import MultilingualModel


class Foo(MultilingualModel):
    """
    Model for testing multilingual forms
    """
    description = models.CharField(max_length=20)

    class Translation:
        title = models.CharField(max_length=20)
