## Django Multilingual Deep Space 9 ##

Django-multilingual-DS9 is a branch of django-multilingual, forked from django-multilingual-ng, with restructured core.

**This project is not longer maintained. Recommended replacement is [django-modeltranslation](https://github.com/deschler/django-modeltranslation)**.

### Requirements: ###
* Django 1.6
* Django 1.4 and 1.5 are supported by version 0.4.

Django-multilingual-ds9 does not have to be fully compatible with django-multilingual-ng, but basic features should not
differ.

### Usage ###
Define models

    from django.db import models

    from multilingual import MultilingualModel

    class MyModel(MultilingualModel):
        # Fields without language versions
        data_field = models.IntegerField()

        class Translation:
            # Fields with language versions
            name = models.CharField(max_length=100)

Add to administration

    from django.contrib.admin import site
    from multilingual import MultilingualModelAdmin

    from myapp.models import MyModel

    site.register(MyModel, MultilingualModelAdmin)

Use in views and templates

    e = MyModel.objects.create()
    # Get translation for current language
    e.name
    # Get translation with fallback
    e.name_any
    # Get translation instance
    e.translation
    e.translation_en

    # Get all translation instances
    e.translations.all()

    # Filter objects by translation field
    qs = MyModel.objects.filter(name='some')
    # Returns objects with no translation and objects with missing name translation
    qs = MyModel.objects.filter(name__isnull=True)
    # The values_list may also contain several None objects if translations are missing
    qs = MyModel.objects.values_list('name', flat=True)

    # Get object with translation in one query
    MyModel.objects.select_related('translation').get(pk=1)
    # Get objects with missing translation
    MyModel.objects.filter(translation__isnull=True)

    # Change current language
    from django.utils.translation import activate
    activate('cs')

    # Force usage of specific language in multilingual code
    from multilingual import language
    language.lock('cs')
    language.release()


### Features ###
* Use only language codes from `LANGUAGES` setting.
* Model structure
  * `FIELD_NAME` returns translation of field for current language or `None` if no translation exists.
  * `FIELD_NAME_any` returns translation of field for current language or fallback language or default language or
    `None` if neither translation exists. Fallback language codes are only those with two letters and are used
    only if available in `LANGUAGES` setting.
  * `FIELD_NAME_LANGUAGE_CODE` returns translation of field for the language or `None` if the translation doesn't exist.
  * `translation` returns translation instance for current language or `None` if no translation exists.
  * `translation_LANGUAGE_CODE` returns translation instance for the language or `None` if the translation doesn't
    exist.
  * `RELATED_NAME` (default: translations) returns manager for translation model with filter to master object.
* Queries
  * `get/filter/exclude(FIELD_NAME=value)` and `get/filter/exclude(FIELD_NAME_LANGUAGE_CODE=value)` filters the result
    using multilingual field for current or specified language.
    Take care if you are using `isnull=True` lookup, because the query returns objects with missing translations as well
    as objects with `None` in multilingual field.
  * `order_by/values/values_list(FIELD_NAME)` and `order_by/values/values_list(FIELD_NAME_LANGUAGE_CODE)` works as well.
    Remember that these will keep objects with no translation in result set unless you filter them out.
  * `select_related('translation')` and `select_related('translation_LANGUAGE_CODE')` retrieves translation data from
    query.
  * `get/filter/exclude(RELATED_NAME)` selection by existence and parameters of translation objects.


### Known bugs ###
* Administration
  * `search_fields` does not handle `FIELD_NAME_LANGCODE`, you need to use regular foreign key lookup
    `RELATED_NAME__FIELD_NAME`
