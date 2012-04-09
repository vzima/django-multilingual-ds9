"""
Model form for multilingual models
"""
from django.forms.models import construct_instance, model_to_dict, fields_for_model, ModelFormMetaclass, ModelForm
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
                    fields = fields_for_model(translation_model, fields, exclude, widgets, formfield_callback)
                    for field_name, field in fields.items():
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
        opts = self._meta
        initial_data = {}
        if instance is not None:
            trans_model = getattr(instance._meta, 'translation_model', None)
            if trans_model is not None:
                try:
                    translation = instance._get_translation(get_active(), can_create=True)
                except trans_model.DoesNotExist:
                    pass
                else:
                    if opts.exclude is None:
                        exclude = ('id', 'language_code', 'master')
                    else:
                        exclude = list(opts.exclude) + ['id', 'language_code', 'master']
                    initial_data = model_to_dict(translation, opts.fields, exclude)
        initial_data.update(initial or {})
        super(MultilingualModelForm, self).__init__(
            data, files, auto_id, prefix, initial_data, error_class, label_suffix, empty_permitted, instance
        )

    def _post_clean(self):
        """
        Stores translation data into translation instance
        """
        opts = self._meta
        translation = self.instance._get_translation(get_active(), can_create=True)
        if opts.exclude is None:
            exclude = ('id', 'language_code', 'master')
        else:
            exclude = list(opts.exclude) + ['id', 'language_code', 'master']
        # Update instance translation
        construct_instance(self, translation, opts.fields, exclude)
        super(MultilingualModelForm, self)._post_clean()


# TODO: I had to copy whole function because of hardcoded MetaClass at the end. This was fixed in Django 1.4
# When Django 1.3 will not be supported, remove this method and use vanilla one.
def multilingual_modelform_factory(model, form=MultilingualModelForm, fields=None, exclude=None,
                       formfield_callback=None):
    # Create the inner Meta class. FIXME: ideally, we should be able to
    # construct a ModelForm without creating and passing in a temporary
    # inner class.

    # Build up a list of attributes that the Meta object will have.
    attrs = {'model': model}
    if fields is not None:
        attrs['fields'] = fields
    if exclude is not None:
        attrs['exclude'] = exclude

    # If parent form class already has an inner Meta, the Meta we're
    # creating needs to inherit from the parent's inner meta.
    parent = (object,)
    if hasattr(form, 'Meta'):
        parent = (form.Meta, object)
    Meta = type('Meta', parent, attrs)

    # Give this new form class a reasonable name.
    class_name = model.__name__ + 'Form'

    # Class attributes for the new form class.
    form_class_attrs = {
        'Meta': Meta,
        'formfield_callback': formfield_callback
    }

    # HACK: change meta class
    return MultilingualModelFormMetaclass(class_name, (form, ), form_class_attrs)
