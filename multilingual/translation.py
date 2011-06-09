"""
Deprecated module

'Translation' class is no longer needed to be a parent of 'Translation' class of multilingual models.
Instead multilingual models should be derived from "multilingual.MultilingualModel" class.

Other parts are moved to 'db' module.
"""
import warnings
warnings.warn("Module 'multilingual.translation' is deprecated. " \
    "Translation meta class does not has to have any parent class.",
    DeprecationWarning)

from multilingual.db.models.translation import BaseTranslationMeta as Translation
