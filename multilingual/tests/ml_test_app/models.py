"""
Models to test multilingual features.
"""
from django.db import models
from multilingual.db.models.base import MultilingualModel


class Article(MultilingualModel):
    slug = models.SlugField()

    class Translation:
        title = models.CharField(max_length=100)
        content = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.slug
