"""
Test models as classes, behaviour of models instances will be tested in test apps
"""
import unittest


class ModelClassTest(unittest.TestCase):
    def test01_base_models_properties(self):
        # Make sure base models are abstract
        #TODO: handle that differently
        from django.db.models import get_model

        from multilingual.db.models.base import MultilingualModel
        from multilingual.db.models.translation import TranslationModel
        self.assertEqual(get_model('models', 'MultilingualModel'), None)
        self.assertEqual(get_model('models', 'TranslationModel'), None)

    #TODO: check key structure of multilingual models, like translation_model links and proxy fields

def suite():
    s = unittest.TestSuite()
    s.addTest(unittest.makeSuite(ModelClassTest))
    return s
