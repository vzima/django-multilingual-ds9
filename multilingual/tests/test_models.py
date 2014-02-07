# -*- coding: utf-8 -*-
"""
This tests standard behaviour of multilingual models
"""
from django.db import models
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import unittest
from django.utils.translation import activate, deactivate_all

from multilingual.db.models.base import MultilingualModel, MultilingualModelBase
from multilingual.db.models.manager import MultilingualManager
from multilingual.db.models.query import MultilingualQuerySet
from multilingual.db.models.sql.query import MultilingualQuery
from multilingual.db.models.translation import TranslationModel
from multilingual.languages import lock, release

from .base import MultilingualTestCase, TEST_LANGUAGES


@override_settings(LANGUAGE_CODE='cs', LANGUAGES=TEST_LANGUAGES)
class TestModel(TestCase):
    """
    Test model without database.
    """
    def tearDown(self):
        deactivate_all()
        release()

    def test_base_models_properties(self):
        # Make sure base models are abstract
        self.assertIsNone(models.get_model('models', 'MultilingualModel'))
        self.assertIsNone(models.get_model('models', 'TranslationModel'))

    def test_model_class(self):
        from .ml_test_app.models import Multiling

        self.assertTrue(issubclass(Multiling, MultilingualModel))
        translation = Multiling._meta.translation_model

        self.assertTrue(issubclass(translation, TranslationModel))
        self.assertEqual(translation.__name__, 'MultilingTranslation')

        self.assertTrue(hasattr(Multiling, 'translations'))
        self.assertTrue(hasattr(Multiling, 'title'))
        self.assertTrue(hasattr(Multiling, 'title_cs'))
        self.assertTrue(hasattr(Multiling, 'title_en'))
        self.assertTrue(hasattr(Multiling, 'title_fr'))
        self.assertTrue(hasattr(Multiling, 'title_any'))
        self.assertIsInstance(Multiling.objects, MultilingualManager)

    def test_invalid_manager(self):
        # Test error when creating model with invalid manager
        self.assertRaises(ValueError, MultilingualModelBase, 'DynamicModel', (MultilingualModel, ),
                          {'objects': models.Manager(), '__module__': __name__})

    def test_fields(self):
        # Test fields with default language
        from .ml_test_app.models import Multiling
        obj = Multiling(name='name')

        # No translations, we use default language
        obj.title = 'Titulek'
        self.assertEqual(obj.title, 'Titulek')
        self.assertEqual(obj.title_any, 'Titulek')
        self.assertEqual(obj.title_cs, 'Titulek')
        self.assertIsNone(obj.title_en)
        self.assertIsNone(obj.title_fr)

        obj.title_fr = 'Titre'
        self.assertEqual(obj.title, 'Titulek')
        self.assertEqual(obj.title_cs, 'Titulek')
        self.assertIsNone(obj.title_en)
        self.assertEqual(obj.title_fr, 'Titre')

    def test_fields_active(self):
        # Test fields with active language
        from .ml_test_app.models import Multiling
        activate('fr')
        obj = Multiling(name='name')

        obj.title = 'Titre'
        self.assertEqual(obj.title, 'Titre')
        self.assertEqual(obj.title_any, 'Titre')
        self.assertIsNone(obj.title_cs)
        self.assertIsNone(obj.title_en)
        self.assertEqual(obj.title_fr, 'Titre')

    def test_fields_lock(self):
        # Test fields with active language and lock
        from .ml_test_app.models import Multiling
        activate('fr')
        lock('en')
        obj = Multiling(name='name')

        obj.title = 'Title'
        self.assertEqual(obj.title, 'Title')
        self.assertEqual(obj.title_any, 'Title')
        self.assertIsNone(obj.title_cs)
        self.assertEqual(obj.title_en, 'Title')
        self.assertIsNone(obj.title_fr)

    def test_fields_fallback(self):
        # Test fields with fallbacks
        from .ml_test_app.models import Multiling
        activate('en-us')
        obj = Multiling(name='name')

        self.assertIsNone(obj.title)
        self.assertIsNone(obj.title_any)

        obj.title_cs = 'Titulek'

        self.assertIsNone(obj.title)
        self.assertEqual(obj.title_any, 'Titulek')

        obj.title_en = 'Title'

        self.assertIsNone(obj.title)
        self.assertEqual(obj.title_any, 'Title')

        obj.title = 'American Title'

        self.assertEqual(obj.title, 'American Title')
        self.assertEqual(obj.title_any, 'American Title')

    def test_init_kwargs(self):
        # Test instance initiation with translations in kwargs
        from .ml_test_app.models import Multiling
        obj = Multiling(name='name', title_cs='Titulek', title_en='Title', title_fr='Titre')

        self.assertEqual(obj.title, 'Titulek')
        self.assertEqual(obj.title_cs, 'Titulek')
        self.assertEqual(obj.title_en, 'Title')
        self.assertEqual(obj.title_fr, 'Titre')


class TestModelQueries(MultilingualTestCase):
    """
    Test model queries (save and load).
    """
    def test_load(self):
        from .ml_test_app.models import Multiling
        obj = Multiling.objects.get(pk=1)
        self.assertEqual(obj.name, u'first')

        self.assertEqual(obj.title, u'obsah ěščřžýáíé')
        self.assertEqual(obj.title_any, u'obsah ěščřžýáíé')
        self.assertEqual(obj.title_cs, u'obsah ěščřžýáíé')
        self.assertEqual(obj.title_en, u'content')

    def test_save_no_translation(self):
        from .ml_test_app.models import Multiling
        obj = Multiling(name='new')
        obj.save()

        obj = Multiling.objects.get(pk=obj.pk)
        self.assertEqual(list(obj.translations.all()), [])

    def test_save(self):
        from .ml_test_app.models import Multiling
        obj = Multiling(name='new', title='Titulek', title_en='Title')
        obj.save()

        obj = Multiling.objects.get(pk=obj.pk)
        self.assertEqual(obj.title, 'Titulek')
        self.assertEqual(obj.title_en, 'Title')


class TestManager(MultilingualTestCase):
    """
    Test multilingual managers.
    """
    def test_get_query_set(self):
        from .ml_test_app.models import Multiling
        queryset = Multiling.objects.get_query_set()
        self.assertIsInstance(queryset, MultilingualQuerySet)
        self.assertEqual(queryset.model, Multiling)

        self.assertIsInstance(queryset.query, MultilingualQuery)
        self.assertEqual(queryset.query.model, Multiling)

    def test_regular_filters(self):
        # Test queries for non-multilingual fields
        from .ml_test_app.models import Multiling

        # Test get
        obj = Multiling.objects.get(pk=1)
        self.assertIsInstance(obj, Multiling)
        self.assertEqual(obj.pk, 1)
        self.assertEqual(obj.name, 'first')

        obj = Multiling.objects.get(name='first')
        self.assertIsInstance(obj, Multiling)
        self.assertEqual(obj.pk, 1)

        # Test all
        queryset = Multiling.objects.all()
        self.assertEqual(len(queryset), 4)
        for obj in queryset:
            self.assertIsInstance(obj, Multiling)
        self.assertEqual(set((o.pk for o in queryset)), set((1, 2, 3, 4)))

        # Test filters
        queryset = Multiling.objects.filter(pk=1)
        self.assertEqual([o.pk for o in queryset], [1])

        queryset = Multiling.objects.exclude(name='first')
        self.assertEqual(len(queryset), 3)
        self.assertEqual(set((o.pk for o in queryset)), set((2, 3, 4)))

        # Test ordering
        queryset = Multiling.objects.all().order_by('-pk')
        self.assertEqual([o.pk for o in queryset], [4, 3, 2, 1])

        # Test lookups
        queryset = Multiling.objects.filter(name__startswith='only')
        self.assertEqual(len(queryset), 2)
        self.assertEqual(set((o.pk for o in queryset)), set((2, 3)))

        # Test select_related
        Multiling.objects.select_related('name').get(name='first')

    def test_filter(self):
        from .ml_test_app.models import Multiling
        queryset = Multiling.objects.filter(title_cs=u'obsah ěščřžýáíé')
        self.assertEqual([o.pk for o in queryset], [1])

        #XXX: Because of the way the jois works, this test will fail. It will actually search for objects with ANY (!)
        # Czech translation which does not have the specified title. It does not take objects without Czech translation
        # into account.
        #queryset = Multiling.objects.exclude(title_cs=u'obsah ěščřžýáíé')
        #self.assertEqual(len(queryset), 3)
        #self.assertEqual(set((o.pk for o in queryset)), set((2, 3, 4)))

    def test_order_by(self):
        # Watch out: ordering is dependent on database locales
        # So if you apply ordering rules on set of words from different language it will be
        # ordered differently than it should. That also may cause problems if application is run
        # with different locales than database.
        from .ml_test_app.models import Multiling
        queryset = Multiling.objects.filter(title_cs__isnull=False).order_by('title_cs')
        self.assertEqual([o.title for o in queryset], [u'obsah ěščřžýáíé', u'pouze čeština'])

    def test_complex_lookups(self):
        from .ml_test_app.models import Multiling
        queryset = Multiling.objects.filter(title_en__isnull=True).order_by('pk')
        self.assertEqual([o.pk for o in queryset], [2, 4])

    def test_select_related(self):
        from .ml_test_app.models import Multiling
        def _test(select_field, query_fields):
            queryset = Multiling.objects.select_related(select_field)
            obj = queryset.get(name='first')
            for field in query_fields:
                getattr(obj, field)

        self.assertNumQueries(1, _test, 'translations', ('title', 'title_cs'))
        self.assertNumQueries(1, _test, 'translations_cs', ('title', 'title_cs'))
        self.assertNumQueries(1, _test, 'translations_en', ('title_en', ))

    def test_values(self):
        from .ml_test_app.models import Multiling
        values = Multiling.objects.filter(name='first').values('title')
        values = [dict(v) for v in values]
        self.assertEqual(values, [{'title': u'obsah ěščřžýáíé'}])

    def test_values_list(self):
        from .ml_test_app.models import Multiling
        values = Multiling.objects.filter(name='first').values_list('title')
        values = [tuple(v) for v in values]
        self.assertEqual(values, [(u'obsah ěščřžýáíé', )])

        values = Multiling.objects.filter(name='first').values_list('title', flat=True)
        values = [v for v in values]
        self.assertEqual(values, [u'obsah ěščřžýáíé'])

    def test_create(self):
        from .ml_test_app.models import Multiling
        obj = Multiling.objects.create(name='created', title_cs=u'vytvořen', title_en='created')
        self.assertEqual(obj.title, u'vytvořen')
        self.assertEqual(obj.title_any, u'vytvořen')
        self.assertEqual(obj.title_cs, u'vytvořen')
        self.assertEqual(obj.title_en, u'created')

        obj = Multiling.objects.get(name='created')
        self.assertEqual(obj.title, u'vytvořen')
        self.assertEqual(obj.title_any, u'vytvořen')
        self.assertEqual(obj.title_cs, u'vytvořen')
        self.assertEqual(obj.title_en, u'created')

    def test_get_or_create(self):
        from .ml_test_app.models import Multiling
        obj, created = Multiling.objects.get_or_create(name='new', title_cs=u'nový', title_en='new one')
        self.assertTrue(created)
        self.assertEqual(obj.title, u'nový')
        self.assertEqual(obj.title_any, u'nový')
        self.assertEqual(obj.title_cs, u'nový')
        self.assertEqual(obj.title_en, u'new one')

        obj = Multiling.objects.get(name='new')
        self.assertEqual(obj.title, u'nový')
        self.assertEqual(obj.title_any, u'nový')
        self.assertEqual(obj.title_cs, u'nový')
        self.assertEqual(obj.title_en, u'new one')

    def test_delete(self):
        from .ml_test_app.models import Multiling
        translation_model = Multiling._meta.translation_model
        obj = Multiling.objects.create(name='to_be_deleted', title_cs=u'na smazání', title_en='for deletion')
        obj.delete()
        self.assertEqual(list(translation_model.objects.filter(master=obj)), [])


def suite():
    test = unittest.TestSuite()
    test.addTest(unittest.makeSuite(TestModel))
    test.addTest(unittest.makeSuite(TestModelQueries))
    test.addTest(unittest.makeSuite(TestManager))
    return test
