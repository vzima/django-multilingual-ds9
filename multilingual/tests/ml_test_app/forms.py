"""
Forms for testing
"""
from django import forms

from multilingual.forms import MultilingualModelForm

from .models import Article


class SimpleForm(MultilingualModelForm):
    class Meta:
        model = Article


class FieldsForm(MultilingualModelForm):
    class Meta:
        model = Article
        fields = ('slug', 'title')


class ExcludeForm(MultilingualModelForm):
    class Meta:
        model = Article
        exclude = ('slug', 'title')


class CustomForm(MultilingualModelForm):
    custom = forms.IntegerField()

    class Meta:
        model = Article
