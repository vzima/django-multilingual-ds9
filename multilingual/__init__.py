"""
Django-multilingual-ds9: multilingual model support for Django 1.4 and newer

Multilingual models automatically overrides base class of multilingual models

Multilingual must be installed before any application with multilingual model
or imported before any multilingual model class is loaded by django.
"""
__version__ = '0.4.0'


from .admin import MultilingualModelAdmin
from .db.models.base import MultilingualModel
from .db.models.manager import MultilingualManager
from .forms import MultilingualModelForm
