# -*- coding: utf-8 -*-
"""
This tests multilingual forms
"""
from django.utils import unittest
from django.utils.translation import activate, deactivate_all

from .base import MultilingualTestCase


class TestModelForm(MultilingualTestCase):
    def setUp(self):
        activate('cs')

    def tearDown(self):
        deactivate_all()

    def test_modelforms(self):
        # Test various definitions of model forms
        from .ml_test_app.forms import SimpleForm, FieldsForm, ExcludeForm, CustomForm

        self.assertEqual(SimpleForm.base_fields.keys(), ['name', 'title'])
        self.assertEqual(FieldsForm.base_fields.keys(), ['name', 'title'])
        self.assertEqual(ExcludeForm.base_fields.keys(), ['name'])
        self.assertEqual(CustomForm.base_fields.keys(), ['name', 'custom', 'title'])

    def test_form_unbound(self):
        from .ml_test_app.forms import SimpleForm
        from .ml_test_app.models import Multiling

        form = SimpleForm()
        self.assertFalse(form.is_bound)
        self.assertEqual(form.initial, {})

        obj = Multiling.objects.get(name='first')
        form = SimpleForm(instance=obj)
        self.assertFalse(form.is_bound)
        self.assertEqual(form.initial, {'id': 1, 'name': 'first', 'title': u'obsah ěščřžýáíé'})

        obj = Multiling.objects.get(name='untranslated')
        form = SimpleForm(instance=obj)
        self.assertFalse(form.is_bound)
        self.assertEqual(form.initial, {'id': 4, 'name': 'untranslated', 'title': ''})

    def test_form_bound(self):
        from .ml_test_app.forms import SimpleForm, ExcludeForm
        from .ml_test_app.models import Multiling

        data = {'name': 'new', 'title': 'Titulek'}
        form = SimpleForm(data)
        self.assertTrue(form.is_bound)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.instance.name, 'new')
        self.assertEqual(form.instance.title, 'Titulek')

        data = {'name': 'new'}
        form = ExcludeForm(data)
        self.assertTrue(form.is_bound)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.instance.name, 'new')


def suite():
    test = unittest.TestSuite()
    test.addTest(unittest.makeSuite(TestModelForm))
    return test
