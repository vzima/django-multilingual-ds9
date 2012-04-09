# -*- coding: utf-8 -*-
"""
This tests standard behaviour of multilingual models
"""
import unittest

from multilingual.forms.forms import MultilingualModelForm

from models import Foo


class MinimalFooForm(MultilingualModelForm):
    class Meta:
        model = Foo


class FieldsFooForm(MultilingualModelForm):
    class Meta:
        model = Foo
        fields = ('description', 'title')


class ModelFormTest(unittest.TestCase):
    def test01_fixtures(self):
        # Just test whether fixtures were loaded properly
        obj = Foo.objects.get(pk=1)
        self.assertEqual(obj.description, u'regular ěščřžýáíé')

    def test02_minimal_form(self):
        self.assertEqual(MinimalFooForm.base_fields.keys(), ['description', 'title'])

    def test03_fields_form(self):
        self.assertEqual(FieldsFooForm.base_fields.keys(), ['description', 'title'])
