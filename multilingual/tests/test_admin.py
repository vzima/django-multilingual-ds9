# -*- coding: utf-8 -*-
"""
This tests standard behaviour of multilingual models
"""
from mock import Mock

from django.contrib.admin import site
from django.contrib.auth.models import User
from django.test.client import RequestFactory
from django.utils import unittest

from multilingual.admin import MultilingualModelAdmin
from multilingual.forms.forms import MultilingualModelForm

from .base import MultilingualTestCase
from .ml_test_app.models import Multiling


class TestModelAdmin(MultilingualTestCase):
    """
    Tests of model admin interface
    """
    fixtures = ('ml_test_models.json', 'ml_test_admin.json')

    def test_add_view_get(self):
        model_admin = MultilingualModelAdmin(Multiling, site)
        request = RequestFactory().get('/dummy/')
        request.user = User.objects.get(pk=1)
        response = model_admin.add_view(request)
        self.assertTemplateUsed(response, 'multilingual/admin/change_form.html')
        self.assertIsInstance(response.context_data['adminform'].form, MultilingualModelForm)
        self.assertEqual(response.context_data['title'], u'Add multiling for language Česky')
        self.assertEqual(response.context_data['ML_LANGUAGE'], 'cs')

    def test_add_view_post(self):
        # Check translation is created for correct language
        model_admin = MultilingualModelAdmin(Multiling, site)
        data = {'csrfmiddlewaretoken': '1', 'ml_language': 'en', 'name': 'admin', 'title': 'Admin', '_popup': '1'}
        reqf = RequestFactory()
        reqf.cookies['csrftoken'] = '1'
        request = reqf.post('/dummy/', data=data)
        request.user = User.objects.get(pk=1)
        response = model_admin.add_view(request)

        self.assertContains(response, 'dismissAddAnotherPopup')

        obj = Multiling.objects.get(name='admin')
        self.assertIsNone(obj.title_cs)
        self.assertEqual(obj.title_en, 'Admin')

    def test_add_view_post_2(self):
        # Check translation is created for correct language - from GET
        model_admin = MultilingualModelAdmin(Multiling, site)
        data = {'csrfmiddlewaretoken': '1', 'name': 'admin', 'title': 'Admin', '_popup': '1'}
        reqf = RequestFactory()
        reqf.cookies['csrftoken'] = '1'
        request = reqf.post('/dummy/?ml_language=en', data=data)
        request.user = User.objects.get(pk=1)
        response = model_admin.add_view(request)

        self.assertContains(response, 'dismissAddAnotherPopup')

        obj = Multiling.objects.get(name='admin')
        self.assertIsNone(obj.title_cs)
        self.assertEqual(obj.title_en, 'Admin')

    def test_change_view_get(self):
        model_admin = MultilingualModelAdmin(Multiling, site)
        request = RequestFactory().get('/dummy/')
        request.user = User.objects.get(pk=1)
        response = model_admin.change_view(request, '1')
        self.assertTemplateUsed(response, 'multilingual/admin/change_form.html')
        self.assertIsInstance(response.context_data['adminform'].form, MultilingualModelForm)
        self.assertEqual(response.context_data['title'], u'Change multiling for language Česky')
        self.assertEqual(response.context_data['ML_LANGUAGE'], 'cs')

    def test_change_view_post(self):
        # Check translation is updated for correct language
        model_admin = MultilingualModelAdmin(Multiling, site)
        data = {'csrfmiddlewaretoken': '1', 'ml_language': 'en', 'name': 'changed', 'title': 'Changed',
                '_continue': '1'}
        reqf = RequestFactory()
        reqf.cookies['csrftoken'] = '1'
        request = reqf.post('/dummy/', data=data)
        request.user = User.objects.get(pk=1)
        request._messages = Mock()
        response = model_admin.change_view(request, '1')

        self.assertEqual(response.status_code, 302)

        obj = Multiling.objects.get(pk=1)
        self.assertEqual(obj.name, 'changed')
        self.assertEqual(obj.title_cs, u'obsah ěščřžýáíé')
        self.assertEqual(obj.title_en, 'Changed')

    def test_change_view_post_2(self):
        # Check translation is updated for correct language - from GET
        model_admin = MultilingualModelAdmin(Multiling, site)
        data = {'csrfmiddlewaretoken': '1', 'name': 'changed', 'title': 'Changed', '_continue': '1'}
        reqf = RequestFactory()
        reqf.cookies['csrftoken'] = '1'
        request = reqf.post('/dummy/?ml_language=en', data=data)
        request.user = User.objects.get(pk=1)
        request._messages = Mock()
        response = model_admin.change_view(request, '1')

        self.assertEqual(response.status_code, 302)

        obj = Multiling.objects.get(pk=1)
        self.assertEqual(obj.name, 'changed')
        self.assertEqual(obj.title_cs, u'obsah ěščřžýáíé')
        self.assertEqual(obj.title_en, 'Changed')


def suite():
    test = unittest.TestSuite()
    test.addTest(unittest.makeSuite(TestModelAdmin))
    return test
