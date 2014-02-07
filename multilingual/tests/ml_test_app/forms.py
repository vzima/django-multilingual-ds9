"""
Forms for testing
"""
from django import forms

from multilingual.forms.forms import MultilingualModelForm

from .models import Multiling


class SimpleForm(MultilingualModelForm):
    class Meta:
        model = Multiling


class FieldsForm(MultilingualModelForm):
    class Meta:
        model = Multiling
        fields = ('name', 'title')


class ExcludeForm(MultilingualModelForm):
    class Meta:
        model = Multiling
        exclude = ('title', )


class CustomForm(MultilingualModelForm):
    custom = forms.IntegerField()

    class Meta:
        model = Multiling
