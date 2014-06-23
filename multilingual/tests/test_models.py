# -*- coding: utf-8 -*-
"""
This tests standard behaviour of multilingual models
"""
from django.db import models
from django.test import TestCase
from django.test.utils import override_settings
from django.utils.translation import activate, deactivate_all

from multilingual.models.base import MultilingualModel, MultilingualModelBase
from multilingual.models.manager import MultilingualManager
from multilingual.models.query import MultilingualQuerySet
from multilingual.models.sql.query import MultilingualQuery
from multilingual.models.translation import TranslationModel
from multilingual.languages import lock, release

from .base import MultilingualSetupMixin, TEST_LANGUAGES


@override_settings(LANGUAGE_CODE='cs', LANGUAGES=TEST_LANGUAGES)
class TestModel(TestCase):
    """
    Test models without database.
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
        opts = Article._meta

        self.assertTrue(issubclass(Article, MultilingualModel))
        self.assertIsInstance(Article.objects, MultilingualManager)
        self.assertTrue(issubclass(opts.translation_model, TranslationModel))
        self.assertEqual(opts.translation_model.__name__, 'ArticleTranslation')

        self.assertTrue(opts.get_field_by_name('translations'))
        self.assertTrue(opts.get_field('translation'))
        self.assertTrue(opts.get_field('translation_cs'))
        self.assertTrue(opts.get_field('translation_en'))
        self.assertTrue(opts.get_field('translation_en_us'))
        self.assertTrue(opts.get_field('translation_fr'))
        self.assertTrue(opts.get_virtual_field('title'))
        self.assertTrue(opts.get_virtual_field('title_cs'))
        self.assertTrue(opts.get_virtual_field('title_en'))
        self.assertTrue(opts.get_virtual_field('title_en_us'))
        self.assertTrue(opts.get_virtual_field('title_fr'))
        self.assertTrue(opts.get_virtual_field('title_any'))

        self.assertTrue(opts.translation_model._meta.get_field('master'))

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
        self.assertIsNone(obj.title_en_us)
        self.assertIsNone(obj.title_fr)
        self.assertQuerysetEqual([obj.translation], ["<ArticleTranslation: 'cs' translation for 'name'>"])
        self.assertQuerysetEqual([obj.translation_cs], ["<ArticleTranslation: 'cs' translation for 'name'>"])
        self.assertIsNone(obj.translation_en)
        self.assertIsNone(obj.translation_en_us)
        self.assertIsNone(obj.translation_fr)

        obj.title_fr = 'Titre'
        self.assertEqual(obj.title, 'Titulek')
        self.assertEqual(obj.title_cs, 'Titulek')
        self.assertIsNone(obj.title_en)
        self.assertIsNone(obj.title_en_us)
        self.assertEqual(obj.title_fr, 'Titre')
        self.assertQuerysetEqual([obj.translation], ["<ArticleTranslation: 'cs' translation for 'name'>"])
        self.assertQuerysetEqual([obj.translation_cs], ["<ArticleTranslation: 'cs' translation for 'name'>"])
        self.assertIsNone(obj.translation_en)
        self.assertIsNone(obj.translation_en_us)
        self.assertQuerysetEqual([obj.translation_fr], ["<ArticleTranslation: 'fr' translation for 'name'>"])

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
        self.assertIsNone(obj.title_en_us)
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
        self.assertIsNone(obj.title_en_us)
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
        obj = Article(slug='name', title_cs='Titulek', title_en='Title', title_en_us='US Title', title_fr='Titre')

        self.assertEqual(obj.title, 'Titulek')
        self.assertEqual(obj.title_cs, 'Titulek')
        self.assertEqual(obj.title_en, 'Title')
        self.assertEqual(obj.title_en_us, 'US Title')
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


class TestQueries(MultilingualSetupMixin, TestCase):
    """
    Test model queries (save and load).
    """
    fixtures = ('ml_test_models.json', )

    def setUp(self):
        deactivate_all()

    def test_fields(self):
        # Test fields on instance stored in database
        from .ml_test_app.models import Article
        obj = Article.objects.create(slug='saved')

        self.assertIsNone(obj.title)
        self.assertIsNone(obj.title_any)
        self.assertIsNone(obj.title_cs)
        self.assertIsNone(obj.title_en)
        self.assertIsNone(obj.translation)
        self.assertIsNone(obj.translation_cs)
        self.assertIsNone(obj.translation_en)

    def test_load(self):
        from .ml_test_app.models import Article
        obj = Article.objects.get(pk=1)
        self.assertEqual(obj.slug, u'first')

        self.assertEqual(obj.title, u'První článek')
        self.assertEqual(obj.title_any, u'První článek')
        self.assertEqual(obj.title_cs, u'První článek')
        self.assertEqual(obj.title_en, u'First article')
        self.assertIsNone(obj.title_en_us)

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

    def test_save_new_translation(self):
        # Test saving new translation
        from .ml_test_app.models import Article

        obj = Article.objects.get(slug='only-czech')

        obj.title_en = 'Missing'
        obj.save()

        obj = Article.objects.get(slug='only-czech')
        self.assertEqual(obj.title_en, 'Missing')

    def test_delete(self):
        from .ml_test_app.models import Article
        translation_model = Article._meta.translation_model

        obj = Article.objects.get(pk=1)
        obj.delete()

        self.assertFalse(Article.objects.filter(pk=1).exists())
        self.assertFalse(translation_model.objects.filter(master__pk=1).exists())

    def test_get_queryset(self):
        from .ml_test_app.models import Article
        queryset = Article.objects.get_queryset()
        self.assertIsInstance(queryset, MultilingualQuerySet)
        self.assertEqual(queryset.model, Article)

        self.assertIsInstance(queryset.query, MultilingualQuery)
        self.assertEqual(queryset.query.model, Article)

    def test_regular_filters(self):
        # Test queries for non-multilingual fields
        from .ml_test_app.models import Article

        # Test get
        obj = Article.objects.get(pk=1)
        self.assertEqual(obj.slug, 'first')

        obj = Article.objects.get(slug='first')
        self.assertEqual(obj.pk, 1)

        # Test all
        result = ['<Article: first>', '<Article: only-czech>', '<Article: only-english>', '<Article: untranslated>']
        self.assertQuerysetEqual(Article.objects.all(), result, ordered=False)

        # Test filters
        self.assertQuerysetEqual(Article.objects.filter(pk=1), ['<Article: first>'])
        self.assertQuerysetEqual(Article.objects.filter(slug='untranslated'), ['<Article: untranslated>'])

        self.assertQuerysetEqual(Article.objects.exclude(slug='first'),
                                 ['<Article: only-czech>', '<Article: only-english>', '<Article: untranslated>'],
                                 ordered=False)

        # Test ordering
        result = ['<Article: untranslated>', '<Article: only-english>', '<Article: only-czech>', '<Article: first>']
        self.assertQuerysetEqual(Article.objects.order_by('-pk'), result)

        # Test lookups
        self.assertQuerysetEqual(Article.objects.filter(slug__startswith='only'),
                                 ['<Article: only-czech>', '<Article: only-english>'], ordered=False)

    def test_filter(self):
        from .ml_test_app.models import Article

        self.assertQuerysetEqual(Article.objects.filter(title=u'První článek'), ['<Article: first>'])
        self.assertQuerysetEqual(Article.objects.filter(translation__title=u'První článek'), ['<Article: first>'])

        self.assertQuerysetEqual(Article.objects.filter(title_cs=u'První článek'), ['<Article: first>'])
        self.assertQuerysetEqual(Article.objects.filter(translation_cs__title=u'První článek'), ['<Article: first>'])

        self.assertQuerysetEqual(Article.objects.filter(title_en='English article'), ['<Article: only-english>'])
        self.assertQuerysetEqual(Article.objects.filter(translation_en__title='English article'),
                                 ['<Article: only-english>'])

        # Behavior changed in Django 1.6. When excluding through LEFT JOIN, the condition 'OR IS NULL' is added,
        # So empty lines are returned as well.
        # Excluding title returns also articles with no translation
        result = ['<Article: only-czech>', '<Article: only-english>', '<Article: untranslated>']
        self.assertQuerysetEqual(Article.objects.exclude(title_cs=u'První článek'), result, ordered=False)
        self.assertQuerysetEqual(Article.objects.exclude(translation_cs__title=u'První článek'), result, ordered=False)

        # Lookups for 'IS NULL'
        result = ['<Article: only-english>', '<Article: untranslated>']
        self.assertQuerysetEqual(Article.objects.filter(translation__isnull=True), result, ordered=False)
        self.assertQuerysetEqual(Article.objects.filter(translation_cs__isnull=True), result, ordered=False)

        result = ['<Article: only-czech>', '<Article: untranslated>']
        self.assertQuerysetEqual(Article.objects.filter(translation_en__isnull=True), result, ordered=False)

        self.assertQuerysetEqual(Article.objects.filter(translations__isnull=True), ['<Article: untranslated>'])

    def test_select_related(self):
        from .ml_test_app.models import Article

        with self.assertNumQueries(1):
            obj = Article.objects.select_related('translation').get(slug='first')
            self.assertEqual(obj.title, u'První článek')
            self.assertEqual(obj.title_cs, u'První článek')

        with self.assertNumQueries(1):
            obj = Article.objects.select_related('translation_cs').get(slug='first')
            self.assertEqual(obj.title, u'První článek')
            self.assertEqual(obj.title_cs, u'První článek')

        with self.assertNumQueries(1):
            obj = Article.objects.select_related('translation_en').get(slug='first')
            self.assertEqual(obj.title_en, 'First article')

        # Ensure select related doesn't require the existence of related object
        with self.assertNumQueries(1):
            Article.objects.select_related('translation').get(slug='only-english')

        with self.assertNumQueries(1):
            Article.objects.select_related('translation_cs').get(slug='only-english')

        # Deprecated select_related arguments
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

        result = ["{'title': u'Prvn\\xed \\u010dl\\xe1nek'}",
                  "{'title': u'\\u010cesk\\xfd \\u010dl\\xe1nek'}",
                  "{'title': None}", "{'title': None}"]
        self.assertQuerysetEqual(Article.objects.values('title'), result, ordered=False)
        result = ["{'title_cs': u'Prvn\\xed \\u010dl\\xe1nek'}",
                  "{'title_cs': u'\\u010cesk\\xfd \\u010dl\\xe1nek'}",
                  "{'title_cs': None}", "{'title_cs': None}"]
        self.assertQuerysetEqual(Article.objects.values('title_cs'), result, ordered=False)
        result = ["{'translation__title': u'Prvn\\xed \\u010dl\\xe1nek'}",
                  "{'translation__title': u'\\u010cesk\\xfd \\u010dl\\xe1nek'}",
                  "{'translation__title': None}", "{'translation__title': None}"]
        self.assertQuerysetEqual(Article.objects.values('translation__title'), result, ordered=False)
        result = ["{'translation_cs__title': u'Prvn\\xed \\u010dl\\xe1nek'}",
                  "{'translation_cs__title': u'\\u010cesk\\xfd \\u010dl\\xe1nek'}",
                  "{'translation_cs__title': None}", "{'translation_cs__title': None}"]
        self.assertQuerysetEqual(Article.objects.values('translation_cs__title'), result, ordered=False)

        result = ["(u'Prvn\\xed \\u010dl\\xe1nek',)",
                  "(u'\\u010cesk\\xfd \\u010dl\\xe1nek',)",
                  "(None,)", "(None,)"]
        self.assertQuerysetEqual(Article.objects.values_list('title'), result, ordered=False)
        self.assertQuerysetEqual(Article.objects.values_list('translation__title'), result, ordered=False)
        self.assertQuerysetEqual(Article.objects.values_list('title_cs'), result, ordered=False)
        self.assertQuerysetEqual(Article.objects.values_list('translation_cs__title'), result, ordered=False)

        result = ["u'Prvn\\xed \\u010dl\\xe1nek'",
                  "u'\\u010cesk\\xfd \\u010dl\\xe1nek'",
                  "None", "None"]
        self.assertQuerysetEqual(Article.objects.values_list('title', flat=True), result, ordered=False)
        self.assertQuerysetEqual(Article.objects.values_list('translation__title', flat=True), result, ordered=False)
        self.assertQuerysetEqual(Article.objects.values_list('title_cs', flat=True), result, ordered=False)
        self.assertQuerysetEqual(Article.objects.values_list('translation_cs__title', flat=True), result, ordered=False)

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


class TestQueries2(MultilingualSetupMixin, TestCase):
    """
    Test more complicated queries.
    """
    def setUp(self):
        deactivate_all()

    def test_order_by(self):
        from .ml_test_app.models import Article

        Article.objects.create(slug='one', title='Article 1')
        Article.objects.create(slug='two', title='Article 2')
        Article.objects.create(slug='three', title='Article 3')
        Article.objects.create(slug='four', title='Article 4')

        result = ['<Article: one>', '<Article: two>', '<Article: three>', '<Article: four>']
        self.assertQuerysetEqual(Article.objects.order_by('title'), result)
        self.assertQuerysetEqual(Article.objects.order_by('translation__title'), result)
        self.assertQuerysetEqual(Article.objects.order_by('title_cs'), result)
        self.assertQuerysetEqual(Article.objects.order_by('translation_cs__title'), result)

        result = ['<Article: four>', '<Article: three>', '<Article: two>', '<Article: one>']
        self.assertQuerysetEqual(Article.objects.order_by('-title'), result)
        self.assertQuerysetEqual(Article.objects.order_by('-translation__title'), result)
        self.assertQuerysetEqual(Article.objects.order_by('-title_cs'), result)
        self.assertQuerysetEqual(Article.objects.order_by('-translation_cs__title'), result)

    def test_isnull_lookups(self):
        from .ml_test_app.models import Article

        Article.objects.create(slug='empty')
        Article.objects.create(slug='no-content', title='No content', content=None)
        Article.objects.create(slug='full', title='Full content', content='A content')

        # Due to LEFT OUTER JOIN `field__isnull` doesn't differentiate between missing translation and 'None'
        # in translation field. On the other hand this is consistent with behaviour of `field` proxy in model.
        result = ['<Article: empty>', '<Article: no-content>']
        self.assertQuerysetEqual(Article.objects.filter(content__isnull=True), result, ordered=False)
        self.assertQuerysetEqual(Article.objects.filter(translation__content__isnull=True), result, ordered=False)

        self.assertQuerysetEqual(Article.objects.filter(content_cs__isnull=True), result, ordered=False)
        self.assertQuerysetEqual(Article.objects.filter(translation_cs__content__isnull=True), result, ordered=False)
