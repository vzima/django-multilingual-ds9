# -*- coding: utf-8 -*-
"""
This tests standard behaviour of multilingual models
"""
import unittest

from django import get_version
from django.contrib.admin.views.main import ChangeList
from django.test.client import RequestFactory

from multilingual.admin.options import MultilingualModelAdmin

from models import AdminTests


REQ_FACTORY = RequestFactory()


class ModelAdminTest(unittest.TestCase):
    """
    Tests of model admin interface
    """
    def test01_fixtures(self):
        """
        Check whether fixtures were loaded properly
        """
        obj = AdminTests.objects.get(pk=1)
        self.assertEqual(obj.description, u'description ěščřžýáíé')

    def test02_search(self):
        """
        Test full text searching in administration
        """
        request = REQ_FACTORY.get('/admin/admintests/', {'q': 'obsah'})
        # Second argument is admin_site, but it is not used in this test
        model_admin = MultilingualModelAdmin(AdminTests, None)
        kwargs = {'request': request,
                  'model': AdminTests,
                  'list_display': ('__str__', ),
                  'list_display_links': (),
                  'list_filter': (),
                  'date_hierarchy': None,
                  'search_fields': ('translations__title', ),
                  'list_select_related': False,
                  'list_per_page': 100,
                  'list_editable': (),
                  'model_admin': model_admin}
        # This argument was added in Django 1.4
        if get_version() >= '1.4':
            kwargs['list_max_show_all'] = 200

        cl = ChangeList(**kwargs)

        # This argument was added in Django 1.4
        if get_version() >= '1.4':
            queryset = cl.get_query_set(request)
        else:
            queryset = cl.get_query_set()

        self.assertEqual(len(queryset), 1)
        self.assertEqual(queryset[0].description, u'description ěščřžýáíé')
