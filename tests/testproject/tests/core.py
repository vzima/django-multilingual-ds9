from django.test import TestCase
from multilingual.flatpages.models import MultilingualFlatPage
from multilingual.utils import GLL
from multilingual import languages
from django.utils.translation import activate

class CoreTestCase(TestCase):
    fixtures = ['testdata.json']
    
    def test_01_read(self):
        mfp = MultilingualFlatPage.objects.get(url='/test1/')
        self.assertEqual(mfp.title_en, 'MLFP-Title1-en')
        self.assertEqual(mfp.title_ja, 'MLFP-Title1-ja')
        self.assertEqual(mfp.content_en, 'MLFP-Content1-en')
        self.assertEqual(mfp.content_ja, 'MLFP-Content1-ja')
        
    def test_02_gll(self):
        mfp = MultilingualFlatPage.objects.get(url='/test2/')
        GLL.lock('en')
        self.assertEqual(mfp.title, None)
        self.assertEqual(mfp.content, None)
        GLL.release()
        GLL.lock('ja')
        self.assertEqual(mfp.title, 'MLFP-Title2-ja')
        self.assertEqual(mfp.content, 'MLFP-Content2-ja')
        GLL.release()
        
    def test_03_fallbacks(self):
        mfp = MultilingualFlatPage.objects.get(url='/test2/')
        self.assertEqual(mfp.title_ja_any, mfp.title_en_any)
        
    def test_04_magical_methods(self):
        # default lang is 'en'
        activate('en')
        mfp = MultilingualFlatPage.objects.get(url='/test2/')
        self.assertEqual(mfp.title, mfp.title_en_any)
        self.assertNotEqual(mfp.title_en, mfp.title_en_any)
        
    def test_05_default_language(self):
        self.assertEqual(languages.get_default_language(), 'en')
        languages.set_default_language('ja')
        self.assertEqual(languages.get_default_language(), 'ja')
        
    def test_06_get_fallbacks(self):
        self.assertEqual(languages.get_fallbacks('en'), ['en', 'ja'])
        self.assertEqual(languages.get_fallbacks('ja'), ['ja', 'en'])
        
    def test_07_implicit_fallbacks(self):
        self.assertEqual(languages.get_fallbacks('en-us'), ['en-us', 'en'])
        
    def test_08_get_current(self):
        mfp = MultilingualFlatPage.objects.get(url='/test1/')
        activate('ja')
        self.assertEqual(mfp.title_current, mfp.title_ja)
        self.assertEqual(mfp.title_current_any, mfp.title_ja)
        activate('en')
        self.assertEqual(mfp.title_current, mfp.title_en)
        self.assertEqual(mfp.title_current_any, mfp.title_en_any)
        mfp = MultilingualFlatPage.objects.get(url='/test2/')
        activate('en')
        self.assertEqual(mfp.title_current, None)
        self.assertEqual(mfp.title_current_any, mfp.title_ja)

    def test_09_values(self):
        titles = [{'title': 'MLFP-Title1-en'}, {'title': None}]
        titles_en = [{'title_en': 'MLFP-Title1-en'}, {'title_en': None}]
        full = [
            {'id': 1, 'title': 'MLFP-Title1-en', 'content': 'MLFP-Content1-en'}, 
            {'id': 2, 'title': None, 'content': None}
        ]
        full_en = [
            {'id': 1, 'title_en': 'MLFP-Title1-en', 'content_en': 'MLFP-Content1-en'}, 
            {'id': 2, 'title_en': None, 'content_en': None}
        ]
        titles_list = ['MLFP-Title1-en', None]

        languages.set_default_language('en')
        # at first try default language
        self.assertEqual(list(MultilingualFlatPage.objects.values('title')), titles)
        self.assertEqual(list(MultilingualFlatPage.objects.values('id', 'title', 'content')), full)
        self.assertEqual(list(MultilingualFlatPage.objects.values_list('title', flat=True)), titles_list)

        languages.set_default_language('ja')
        # now select specific language
        self.assertEqual(list(MultilingualFlatPage.objects.values('title_en')), titles_en)
        self.assertEqual(list(MultilingualFlatPage.objects.values('id', 'title_en', 'content_en')), full_en)
        self.assertEqual(list(MultilingualFlatPage.objects.values_list('title_en', flat=True)), titles_list)
