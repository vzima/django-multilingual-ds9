"""
Model form for multilingual models
"""
from django.forms.models import model_to_dict, fields_for_model, ModelFormMetaclass, ModelForm, ALL_FIELDS
from django.forms.util import ErrorList

from multilingual.languages import get_active


class MultilingualModelFormMetaclass(ModelFormMetaclass):
    """
    Alters django model form to include fields for translated model fields
    """
    def __new__(cls, name, bases, attrs):
        """
        Declares multilingual fields before constructor of model form is called.
        """
        if 'Meta' in attrs:
            meta = attrs.get('Meta')
            if getattr(meta, 'model', None):
                translation_model = getattr(meta.model._meta, 'translation_model', None)
                if translation_model:
                    # Exclude translation base fields
                    exclude = getattr(meta, 'exclude', None)
                    if exclude is None:
                        exclude = ('id', 'language_code', 'master')
                    else:
                        exclude = list(exclude) + ['id', 'language_code', 'master']
                    fields = getattr(meta, 'fields', None)
                    widgets = getattr(meta, 'widgets', None)
                    formfield_callback = attrs.get('formfield_callback', None)

                    if fields == ALL_FIELDS:
                        # sentinel for fields_for_model to indicate "get the list of
                        # fields from the model"
                        fields = None

                    model_fields = fields_for_model(translation_model, fields, exclude, widgets, formfield_callback)
                    for field_name, field in model_fields.items():
                        # Exclude untranslated fields
                        if field is not None:
                            attrs.setdefault(field_name, field)
        return super(MultilingualModelFormMetaclass, cls).__new__(cls, name, bases, attrs)


class MultilingualModelForm(ModelForm):
    """
    Alters django model form update initials with data from translation model
    """
    __metaclass__ = MultilingualModelFormMetaclass

    #TODO: unique checks and validation
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=':',
                 empty_permitted=False, instance=None):
        super(MultilingualModelForm, self).__init__(data, files, auto_id, prefix, initial, error_class, label_suffix,
                                                    empty_permitted, instance)

        # Nothing to do if the instance was not provided
        if not instance:
            return

        # Create empty translation if not exists
        if not hasattr(self.instance, 'translation') or self.instance.translation is None:
            self.instance.translation = self.instance._meta.translation_model(master=self.instance,
                                                                              language_code=get_active())

        opts = self._meta
        exclude = ['id', 'language_code', 'master']
        if opts.exclude is not None:
            exclude.extend(opts.exclude)
        object_data = model_to_dict(self.instance.translation, opts.fields, exclude)
        for key, value in object_data.iteritems():
            self.initial.setdefault(key, value)

    def _post_clean(self):
        """
        Stores translation data into translation instance
        """
        # Update master instance
        super(MultilingualModelForm, self)._post_clean()

        # Update translations
        instance = self.instance
        fields = self._meta.fields
        exclude = self._meta.exclude

        # Most effective is to do something like `construct_instance` for virtual fields.
        for f in self.instance._meta.virtual_fields:
            if not f.name in self.cleaned_data:
                continue
            if fields is not None and f.name not in fields:
                continue
            if exclude and f.name in exclude:
                continue
            setattr(instance, f.name, self.cleaned_data[f.name])
