# -*- coding: utf-8 -*-
"""
This tests multilingual forms
"""
from django.test import TestCase
from django.utils.translation import activate, deactivate_all

from .base import MultilingualSetupMixin


class TestModelForm(MultilingualSetupMixin, TestCase):
    fixtures = ('ml_test_models.json', )

    def setUp(self):
        activate('cs')

    def tearDown(self):
        deactivate_all()

    def test_modelforms(self):
        # Test various definitions of model forms
        from .ml_test_app.forms import SimpleForm, FieldsForm, ExcludeForm, CustomForm

        self.assertEqual(SimpleForm.base_fields.keys(), ['slug', 'title', 'content'])
        self.assertEqual(FieldsForm.base_fields.keys(), ['slug', 'title'])
        self.assertEqual(ExcludeForm.base_fields.keys(), ['content'])
        self.assertEqual(CustomForm.base_fields.keys(), ['slug', 'custom', 'title', 'content'])

    def test_form_unbound(self):
        from .ml_test_app.forms import SimpleForm
        from .ml_test_app.models import Article

        form = SimpleForm()
        self.assertFalse(form.is_bound)
        self.assertEqual(form.initial, {})

        obj = Article.objects.get(slug='first')
        form = SimpleForm(instance=obj)
        self.assertFalse(form.is_bound)
        self.assertEqual(form.initial,
                         {'id': 1, 'slug': 'first', 'title': u'První článek', 'content': u'Žluťoučký kůň'})

        obj = Article.objects.get(slug='untranslated')
        form = SimpleForm(instance=obj)
        self.assertFalse(form.is_bound)
        self.assertEqual(form.initial, {'id': 4, 'slug': 'untranslated', 'title': '', 'content': None})

    def test_form_bound(self):
        from .ml_test_app.forms import SimpleForm, ExcludeForm

        data = {'slug': 'new', 'title': 'Titulek', 'content': 'Obsah'}
        form = SimpleForm(data)
        self.assertTrue(form.is_bound)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.instance.slug, 'new')
        self.assertEqual(form.instance.title, 'Titulek')

        data = {'content': 'New content'}
        form = ExcludeForm(data)
        self.assertTrue(form.is_bound)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.instance.content, 'New content')
