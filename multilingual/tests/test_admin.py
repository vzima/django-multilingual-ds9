# -*- coding: utf-8 -*-
"""
This tests standard behaviour of multilingual models
"""
from django.test import TransactionTestCase
from django.utils.translation import activate, deactivate_all, trans_real

from multilingual import MultilingualModelForm

from .base import MultilingualSetupMixin


class TestModelAdmin(MultilingualSetupMixin, TransactionTestCase):
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
        response = self.client.get('/admin/ml_test_app/article/add/')

        self.assertContains(response, u'<title>Add article for language Čeština')
        self.assertContains(response, 'multilingual/css/admin_styles.css')
        self.assertContains(response, '<a href="?ml_admin_language=en">English</a>')
        self.assertContains(response, '<input type="hidden" name="ml_admin_language" value="cs" />')
        self.assertIsInstance(response.context['adminform'].form, MultilingualModelForm)
        self.assertEqual(response.context['title'], u'Add article for language Čeština')
        self.assertEqual(response.context['ml_admin_language'], 'cs')

    def test_add_view_get_en(self):
        response = self.client.get('/admin/ml_test_app/article/add/?ml_admin_language=en')

        self.assertContains(response, '<title>Add article for language English')
        self.assertContains(response, 'multilingual/css/admin_styles.css')
        self.assertContains(response, u'<a href="?ml_admin_language=cs">Čeština</a>')
        self.assertContains(response, '<input type="hidden" name="ml_admin_language" value="en" />')
        self.assertIsInstance(response.context['adminform'].form, MultilingualModelForm)
        self.assertEqual(response.context['title'], 'Add article for language English')
        self.assertEqual(response.context['ml_admin_language'], 'en')

    def test_add_view_post(self):
        from .ml_test_app.models import Article

        data = {'ml_admin_language': 'cs', 'slug': 'added', 'title': 'Nový článek', 'content': 'Nový obsah'}
        response = self.client.post('/admin/ml_test_app/article/add/', data=data)

        self.assertRedirects(response, '/admin/ml_test_app/article/')

        # Check created object
        obj = Article.objects.get(slug='added')
        self.assertEqual(obj.title_cs, u'Nový článek')
        self.assertIsNone(obj.title_en)
        self.assertEqual(obj.content_cs, u'Nový obsah')
        self.assertIsNone(obj.content_en)

    def test_add_view_post_en(self):
        from .ml_test_app.models import Article

        data = {'ml_admin_language': 'en', 'slug': 'added', 'title': 'New article', 'content': 'New content'}
        response = self.client.post('/admin/ml_test_app/article/add/', data=data)

        self.assertRedirects(response, '/admin/ml_test_app/article/')

        # Check created object
        obj = Article.objects.get(slug='added')
        self.assertIsNone(obj.title_cs)
        self.assertEqual(obj.title_en, 'New article')
        self.assertIsNone(obj.content_cs)
        self.assertEqual(obj.content_en, 'New content')

    def test_add_view_post_en_2(self):
        from .ml_test_app.models import Article

        # Check `ml_admin_language` in POST has higher priority
        data = {'ml_admin_language': 'en', 'slug': 'added', 'title': 'New article', 'content': 'New content'}
        response = self.client.post('/admin/ml_test_app/article/add/?ml_admin_language=cs', data=data)

        self.assertRedirects(response, '/admin/ml_test_app/article/')

        # Check created object
        obj = Article.objects.get(slug='added')
        self.assertIsNone(obj.title_cs)
        self.assertEqual(obj.title_en, 'New article')
        self.assertIsNone(obj.content_cs)
        self.assertEqual(obj.content_en, 'New content')

    def test_change_view_get(self):
        response = self.client.get('/admin/ml_test_app/article/1/')

        self.assertContains(response, u'<title>Change article for language Čeština')
        self.assertContains(response, 'multilingual/css/admin_styles.css')
        self.assertContains(response, '<a href="?ml_admin_language=en">English</a>')
        self.assertContains(response, '<input type="hidden" name="ml_admin_language" value="cs" />')
        self.assertIsInstance(response.context['adminform'].form, MultilingualModelForm)
        self.assertEqual(response.context['title'], u'Change article for language Čeština')
        self.assertEqual(response.context['ml_admin_language'], 'cs')

    def test_change_view_get_en(self):
        response = self.client.get('/admin/ml_test_app/article/1/?ml_admin_language=en')

        self.assertContains(response, '<title>Change article for language English')
        self.assertContains(response, 'multilingual/css/admin_styles.css')
        self.assertContains(response, u'<a href="?ml_admin_language=cs">Čeština</a>')
        self.assertContains(response, '<input type="hidden" name="ml_admin_language" value="en" />')
        self.assertIsInstance(response.context['adminform'].form, MultilingualModelForm)
        self.assertEqual(response.context['title'], 'Change article for language English')
        self.assertEqual(response.context['ml_admin_language'], 'en')

    def test_change_view_post(self):
        from .ml_test_app.models import Article

        data = {'ml_admin_language': 'cs', 'slug': 'changed', 'title': 'Opravený článek', 'content': 'Úplně jiný obsah'}
        response = self.client.post('/admin/ml_test_app/article/1/', data=data)

        self.assertRedirects(response, '/admin/ml_test_app/article/')

        # Check changed object
        obj = Article.objects.get(pk=1)
        self.assertEqual(obj.slug, 'changed')
        self.assertEqual(obj.title_cs, u'Opravený článek')
        self.assertEqual(obj.title_en, 'First article')
        self.assertEqual(obj.content_cs, u'Úplně jiný obsah')
        self.assertEqual(obj.content_en, 'Yellow horse')

    def test_change_view_post_en(self):
        from .ml_test_app.models import Article

        data = {'ml_admin_language': 'en', 'slug': 'changed', 'title': 'Changed article',
                'content': 'Brand new content'}
        response = self.client.post('/admin/ml_test_app/article/1/', data=data)

        self.assertRedirects(response, '/admin/ml_test_app/article/')

        # Check changed object
        obj = Article.objects.get(pk=1)
        self.assertEqual(obj.slug, 'changed')
        self.assertEqual(obj.title_cs, u'První článek')
        self.assertEqual(obj.title_en, 'Changed article')
        self.assertEqual(obj.content_cs, u'Žluťoučký kůň')
        self.assertEqual(obj.content_en, 'Brand new content')

    def test_change_view_post_en_2(self):
        # Check `ml_admin_language` in POST has higher priority
        from .ml_test_app.models import Article

        data = {'ml_admin_language': 'en', 'slug': 'changed', 'title': 'Changed article',
                'content': 'Brand new content'}
        response = self.client.post('/admin/ml_test_app/article/1/?ml_admin_language=cs', data=data)

        self.assertRedirects(response, '/admin/ml_test_app/article/')

        # Check changed object
        obj = Article.objects.get(pk=1)
        self.assertEqual(obj.slug, 'changed')
        self.assertEqual(obj.title_cs, u'První článek')
        self.assertEqual(obj.title_en, 'Changed article')
        self.assertEqual(obj.content_cs, u'Žluťoučký kůň')
        self.assertEqual(obj.content_en, 'Brand new content')
