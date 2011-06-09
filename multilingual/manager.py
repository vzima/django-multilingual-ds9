"""
Deprecated module

'MultilingualManager' class (with 'Manager' alias) is moved into 'db' module.
It is imported into 'multilingual.__init__' module.
"""
import warnings
warnings.warn("Module 'multilingual.manager' is deprecated, use 'multilingual.MultilingualManager' instead.",
    DeprecationWarning)

from multilingual.db.models.manager import MultilingualManager
Manager = MultilingualManager
