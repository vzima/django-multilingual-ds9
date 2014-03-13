# -*- coding: utf-8 -*-
"""
This tests standard behaviour of multilingual models
"""
from django.db import models
from django.test import TestCase
from django.test.utils import override_settings
from django.utils.translation import activate, deactivate_all

from multilingual.db.models.base import MultilingualModel, MultilingualModelBase
from multilingual.db.models.manager import MultilingualManager
from multilingual.db.models.query import MultilingualQuerySet
from multilingual.db.models.sql.query import MultilingualQuery
from multilingual.db.models.translation import TranslationModel
from multilingual.languages import lock, release

from .base import MultilingualSetupMixin, TEST_LANGUAGES


@override_settings(LANGUAGE_CODE='cs', LANGUAGES=TEST_LANGUAGES)
class TestModel(TestCase):
    """
    Test model without database.
    """
    def setUp(self):
        deactivate_all()

    def tearDown(self):
        deactivate_all()
        release()

    def test_base_models_properties(self):
        # Make sure base models are abstract
        self.assertIsNone(models.get_model('models', 'MultilingualModel'))
        self.assertIsNone(models.get_model('models', 'TranslationModel'))

    def test_model_class(self):
        from .ml_test_app.models import Article

        self.assertTrue(issubclass(Article, MultilingualModel))
        translation = Article._meta.translation_model

        self.assertTrue(issubclass(translation, TranslationModel))
        self.assertEqual(translation.__name__, 'ArticleTranslation')

        self.assertTrue(hasattr(Article, 'translations'))
        self.assertTrue(hasattr(Article, 'title'))
        self.assertTrue(hasattr(Article, 'title_cs'))
        self.assertTrue(hasattr(Article, 'title_en'))
        self.assertTrue(hasattr(Article, 'title_fr'))
        self.assertTrue(hasattr(Article, 'title_any'))
        self.assertIsInstance(Article.objects, MultilingualManager)

    def test_invalid_manager(self):
        # Test error when creating model with invalid manager
        self.assertRaises(ValueError, MultilingualModelBase, 'DynamicModel', (MultilingualModel, ),
                          {'objects': models.Manager(), '__module__': __name__})

    def test_fields(self):
        # Test fields with default language
        from .ml_test_app.models import Article
        obj = Article(slug='name')

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
        from .ml_test_app.models import Article
        activate('fr')
        obj = Article(slug='name')

        obj.title = 'Titre'
        self.assertEqual(obj.title, 'Titre')
        self.assertEqual(obj.title_any, 'Titre')
        self.assertIsNone(obj.title_cs)
        self.assertIsNone(obj.title_en)
        self.assertEqual(obj.title_fr, 'Titre')

    def test_fields_lock(self):
        # Test fields with active language and lock
        from .ml_test_app.models import Article
        activate('fr')
        lock('en')
        obj = Article(slug='name')

        obj.title = 'Title'
        self.assertEqual(obj.title, 'Title')
        self.assertEqual(obj.title_any, 'Title')
        self.assertIsNone(obj.title_cs)
        self.assertEqual(obj.title_en, 'Title')
        self.assertIsNone(obj.title_fr)

    def test_fields_fallback(self):
        # Test fields with fallbacks
        from .ml_test_app.models import Article
        activate('en-us')
        obj = Article(slug='name')

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
        from .ml_test_app.models import Article
        obj = Article(slug='name', title_cs='Titulek', title_en='Title', title_fr='Titre')

        self.assertEqual(obj.title, 'Titulek')
        self.assertEqual(obj.title_cs, 'Titulek')
        self.assertEqual(obj.title_en, 'Title')
        self.assertEqual(obj.title_fr, 'Titre')

    def test_language_switch(self):
        # Test switching the language does not create conflict with translation caches.
        from .ml_test_app.models import Article
        obj = Article(slug='name', title_cs='Titulek', title_en='Title', title_fr='Titre')

        # Czech is default
        self.assertEqual(obj.title, 'Titulek')

        # Switch to English
        activate('en')
        self.assertEqual(obj.title, 'Title')

        # Lock on French
        lock('fr')
        self.assertEqual(obj.title, 'Titre')


class TestModelQueries(MultilingualSetupMixin, TestCase):
    """
    Test model queries (save and load).
    """
    fixtures = ('ml_test_models.json', )

    def setUp(self):
        deactivate_all()

    def test_load(self):
        from .ml_test_app.models import Article
        obj = Article.objects.get(pk=1)
        self.assertEqual(obj.slug, u'first')

        self.assertEqual(obj.title, u'První článek')
        self.assertEqual(obj.title_any, u'První článek')
        self.assertEqual(obj.title_cs, u'První článek')
        self.assertEqual(obj.title_en, u'First article')

    def test_save_no_translation(self):
        from .ml_test_app.models import Article
        obj = Article(slug='new')
        obj.save()

        obj = Article.objects.get(pk=obj.pk)
        self.assertEqual(list(obj.translations.all()), [])

    def test_save(self):
        from .ml_test_app.models import Article
        obj = Article(slug='new', title='Titulek', title_en='Title')
        obj.save()

        obj = Article.objects.get(pk=obj.pk)
        self.assertEqual(obj.title, 'Titulek')
        self.assertEqual(obj.title_en, 'Title')

    def test_delete(self):
        from .ml_test_app.models import Article
        translation_model = Article._meta.translation_model
        obj = Article.objects.create(slug='to_be_deleted', title_cs=u'na smazání', title_en='for deletion')
        obj.save()

        obj.delete()

        self.assertFalse(Article.objects.filter(pk=obj.pk).exists())
        self.assertFalse(translation_model.objects.filter(master=obj).exists())


class TestManager(MultilingualSetupMixin, TestCase):
    """
    Test multilingual managers.
    """
    fixtures = ('ml_test_models.json', )

    def setUp(self):
        deactivate_all()

    def test_get_query_set(self):
        from .ml_test_app.models import Article
        queryset = Article.objects.get_query_set()
        self.assertIsInstance(queryset, MultilingualQuerySet)
        self.assertEqual(queryset.model, Article)

        self.assertIsInstance(queryset.query, MultilingualQuery)
        self.assertEqual(queryset.query.model, Article)

    def test_regular_filters(self):
        # Test queries for non-multilingual fields
        from .ml_test_app.models import Article

        # Test get
        obj = Article.objects.get(pk=1)
        self.assertIsInstance(obj, Article)
        self.assertEqual(obj.pk, 1)
        self.assertEqual(obj.slug, 'first')

        obj = Article.objects.get(slug='first')
        self.assertIsInstance(obj, Article)
        self.assertEqual(obj.pk, 1)

        # Test all
        result = ['<Article: first>', '<Article: only-czech>', '<Article: only-english>', '<Article: untranslated>']
        self.assertQuerysetEqual(Article.objects.all(), result, ordered=False)

        # Test filters
        self.assertQuerysetEqual(Article.objects.filter(pk=1), ['<Article: first>'])

        self.assertQuerysetEqual(Article.objects.exclude(slug='first'),
                                 ['<Article: only-czech>', '<Article: only-english>', '<Article: untranslated>'],
                                 ordered=False)

        # Test ordering
        result = ['<Article: untranslated>', '<Article: only-english>', '<Article: only-czech>', '<Article: first>']
        self.assertQuerysetEqual(Article.objects.all().order_by('-pk'), result)

        # Test lookups
        self.assertQuerysetEqual(Article.objects.filter(slug__startswith='only'),
                                 ['<Article: only-czech>', '<Article: only-english>'], ordered=False)

    def test_filter(self):
        from .ml_test_app.models import Article

        self.assertQuerysetEqual(Article.objects.filter(title_cs=u'První článek'), ['<Article: first>'])

        # Excluding title returns also articles with no translation
        self.assertQuerysetEqual(Article.objects.exclude(title_cs=u'První článek'),
                                 ['<Article: only-czech>'],
                                 ordered=False)

    def test_order_by(self):
        # Watch out: ordering is dependent on database locales
        # So if you apply ordering rules on set of words from different language it will be
        # ordered differently than it should. That also may cause problems if application is run
        # with different locales than database.
        from .ml_test_app.models import Article

        self.assertQuerysetEqual(Article.objects.filter(title_cs__isnull=False).order_by('title_cs'),
                                 ['<Article: first>', '<Article: only-czech>'])

    def test_complex_lookups(self):
        from .ml_test_app.models import Article

        self.assertQuerysetEqual(Article.objects.filter(title_en__isnull=True),
                                 ['<Article: only-czech>', '<Article: untranslated>'],
                                 ordered=False)

    def test_select_related(self):
        from .ml_test_app.models import Article

        with self.assertNumQueries(1):
            obj = Article.objects.select_related('translations').get(slug='first')
            self.assertEqual(obj.title, u'První článek')
            self.assertEqual(obj.title_cs, u'První článek')

        with self.assertNumQueries(1):
            obj = Article.objects.select_related('translations_cs').get(slug='first')
            self.assertEqual(obj.title, u'První článek')
            self.assertEqual(obj.title_cs, u'První článek')

        with self.assertNumQueries(1):
            obj = Article.objects.select_related('translations_en').get(slug='first')
            self.assertEqual(obj.title_en, 'First article')

        # Ensure select related doesn't require the existence of related object
        with self.assertNumQueries(1):
            Article.objects.select_related('translations_cs').get(slug='only-english')

        with self.assertNumQueries(1):
            Article.objects.select_related('translations').get(slug='only-english')

    def test_values(self):
        from .ml_test_app.models import Article

        self.assertQuerysetEqual(Article.objects.filter(slug='first').values('title'),
                                 [repr({'title': u'První článek'})])

        self.assertQuerysetEqual(Article.objects.filter(slug='first').values_list('title'),
                                 [repr((u'První článek', ))])

        self.assertQuerysetEqual(Article.objects.filter(slug='first').values_list('title', flat=True),
                                 [repr(u'První článek')])

    def test_create(self):
        from .ml_test_app.models import Article
        obj = Article.objects.create(slug='created', title_cs=u'vytvořen', title_en='created')
        self.assertEqual(obj.title, u'vytvořen')
        self.assertEqual(obj.title_any, u'vytvořen')
        self.assertEqual(obj.title_cs, u'vytvořen')
        self.assertEqual(obj.title_en, u'created')

        obj = Article.objects.get(slug='created')
        self.assertEqual(obj.title, u'vytvořen')
        self.assertEqual(obj.title_any, u'vytvořen')
        self.assertEqual(obj.title_cs, u'vytvořen')
        self.assertEqual(obj.title_en, u'created')

    def test_get_or_create(self):
        from .ml_test_app.models import Article
        obj, created = Article.objects.get_or_create(slug='new', title_cs=u'nový', title_en='new one')
        self.assertTrue(created)
        self.assertEqual(obj.title, u'nový')
        self.assertEqual(obj.title_any, u'nový')
        self.assertEqual(obj.title_cs, u'nový')
        self.assertEqual(obj.title_en, u'new one')

        obj = Article.objects.get(slug='new')
        self.assertEqual(obj.title, u'nový')
        self.assertEqual(obj.title_any, u'nový')
        self.assertEqual(obj.title_cs, u'nový')
        self.assertEqual(obj.title_en, u'new one')
