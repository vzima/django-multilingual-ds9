# -*- coding: utf-8 -*-
"""
This tests standard behaviour of multilingual models
"""
from django.utils import unittest
from django.utils.translation import activate, deactivate_all, trans_real

from multilingual import MultilingualModelForm

from .base import MultilingualTestCase


class TestModelAdmin(MultilingualTestCase):
    """
    Tests of model admin interface
    """
    fixtures = ('ml_test_models.json', 'ml_test_admin.xml')
    urls = 'ml_test_app.urls'

    def setUp(self):
        self.client.login(username='admin', password='admin')

        activate('cs')
        # Purge translation cache
        trans_real._default = None

    def tearDown(self):
        deactivate_all()
        # Purge translation cache
        trans_real._default = None

    def test_add_view_get(self):
        response = self.client.get('/admin/ml_test_app/multiling/add/')

        self.assertContains(response, u'<title>Add multiling for language Čeština')
        self.assertContains(response, 'multilingual/css/admin_styles.css')
        self.assertContains(response, '<a href="?ml_admin_language=en">English</a>')
        self.assertContains(response, '<input type="hidden" name="ml_admin_language" value="cs" />')
        self.assertIsInstance(response.context['adminform'].form, MultilingualModelForm)
        self.assertEqual(response.context['title'], u'Add multiling for language Čeština')
        self.assertEqual(response.context['ML_ADMIN_LANGUAGE'], 'cs')

    def test_add_view_get_en(self):
        response = self.client.get('/admin/ml_test_app/multiling/add/?ml_admin_language=en')

        self.assertContains(response, '<title>Add multiling for language English')
        self.assertContains(response, 'multilingual/css/admin_styles.css')
        self.assertContains(response, u'<a href="?ml_admin_language=cs">Čeština</a>')
        self.assertContains(response, '<input type="hidden" name="ml_admin_language" value="en" />')
        self.assertIsInstance(response.context['adminform'].form, MultilingualModelForm)
        self.assertEqual(response.context['title'], 'Add multiling for language English')
        self.assertEqual(response.context['ML_ADMIN_LANGUAGE'], 'en')

    def test_add_view_post(self):
        from .ml_test_app.models import Multiling

        data = {'ml_admin_language': 'cs', 'name': 'admin', 'title': 'Admin'}
        response = self.client.post('/admin/ml_test_app/multiling/add/', data=data)

        self.assertRedirects(response, '/admin/ml_test_app/multiling/')

        # Check created object
        obj = Multiling.objects.get(name='admin')
        self.assertEqual(obj.title_cs, 'Admin')
        self.assertIsNone(obj.title_en)

    def test_add_view_post_en(self):
        from .ml_test_app.models import Multiling

        data = {'ml_admin_language': 'en', 'name': 'admin', 'title': 'Admin'}
        response = self.client.post('/admin/ml_test_app/multiling/add/', data=data)

        self.assertRedirects(response, '/admin/ml_test_app/multiling/')

        # Check created object
        obj = Multiling.objects.get(name='admin')
        self.assertIsNone(obj.title_cs)
        self.assertEqual(obj.title_en, 'Admin')

    def test_add_view_post_en_2(self):
        from .ml_test_app.models import Multiling

        # Check `ml_admin_language` in POST has higher priority
        data = {'ml_admin_language': 'en', 'name': 'admin', 'title': 'Admin'}
        response = self.client.post('/admin/ml_test_app/multiling/add/?ml_admin_language=cs', data=data)

        self.assertRedirects(response, '/admin/ml_test_app/multiling/')

        # Check created object
        obj = Multiling.objects.get(name='admin')
        self.assertIsNone(obj.title_cs)
        self.assertEqual(obj.title_en, 'Admin')

    def test_change_view_get(self):
        response = self.client.get('/admin/ml_test_app/multiling/1/')

        self.assertContains(response, u'<title>Change multiling for language Čeština')
        self.assertContains(response, 'multilingual/css/admin_styles.css')
        self.assertContains(response, '<a href="?ml_admin_language=en">English</a>')
        self.assertContains(response, '<input type="hidden" name="ml_admin_language" value="cs" />')
        self.assertIsInstance(response.context['adminform'].form, MultilingualModelForm)
        self.assertEqual(response.context['title'], u'Change multiling for language Čeština')
        self.assertEqual(response.context['ML_ADMIN_LANGUAGE'], 'cs')

    def test_change_view_get_en(self):
        response = self.client.get('/admin/ml_test_app/multiling/1/?ml_admin_language=en')

        self.assertContains(response, '<title>Change multiling for language English')
        self.assertContains(response, 'multilingual/css/admin_styles.css')
        self.assertContains(response, u'<a href="?ml_admin_language=cs">Čeština</a>')
        self.assertContains(response, '<input type="hidden" name="ml_admin_language" value="en" />')
        self.assertIsInstance(response.context['adminform'].form, MultilingualModelForm)
        self.assertEqual(response.context['title'], 'Change multiling for language English')
        self.assertEqual(response.context['ML_ADMIN_LANGUAGE'], 'en')

    def test_change_view_post(self):
        from .ml_test_app.models import Multiling

        data = {'ml_admin_language': 'cs', 'name': 'changed', 'title': 'Changed'}
        response = self.client.post('/admin/ml_test_app/multiling/1/', data=data)

        self.assertRedirects(response, '/admin/ml_test_app/multiling/')

        # Check changed object
        obj = Multiling.objects.get(pk=1)
        self.assertEqual(obj.name, 'changed')
        self.assertEqual(obj.title_cs, 'Changed')
        self.assertEqual(obj.title_en, 'content')

    def test_change_view_post_en(self):
        from .ml_test_app.models import Multiling

        data = {'ml_admin_language': 'en', 'name': 'changed', 'title': 'Changed'}
        response = self.client.post('/admin/ml_test_app/multiling/1/', data=data)

        self.assertRedirects(response, '/admin/ml_test_app/multiling/')

        # Check changed object
        obj = Multiling.objects.get(pk=1)
        self.assertEqual(obj.name, 'changed')
        self.assertEqual(obj.title_cs, u'obsah ěščřžýáíé')
        self.assertEqual(obj.title_en, 'Changed')

    def test_add_view_post_en_2(self):
        # Check `ml_admin_language` in POST has higher priority
        from .ml_test_app.models import Multiling

        data = {'ml_admin_language': 'en', 'name': 'changed', 'title': 'Changed'}
        response = self.client.post('/admin/ml_test_app/multiling/1/?ml_admin_language=cs', data=data)

        self.assertRedirects(response, '/admin/ml_test_app/multiling/')

        # Check changed object
        obj = Multiling.objects.get(pk=1)
        self.assertEqual(obj.name, 'changed')
        self.assertEqual(obj.title_cs, u'obsah ěščřžýáíé')
        self.assertEqual(obj.title_en, 'Changed')


def suite():
    test = unittest.TestSuite()
    test.addTest(unittest.makeSuite(TestModelAdmin))
    return test
