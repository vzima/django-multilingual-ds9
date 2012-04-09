"""
Model formset for multilingual models
"""
from django.forms.formsets import formset_factory
from django.forms.models import BaseModelFormSet, BaseInlineFormSet, _get_foreign_key

from multilingual.forms.forms import MultilingualModelForm, multilingual_modelform_factory


#TODO: This method uses altered modelform_factory which has to be added as until Django 1.4 it was improperly
# implemented and had to be overridden. Remove this method when Django 1.3 will not be supported and use vanilla one.
# Copied to change modelform_factory.
def multilingual_modelformset_factory(model, form=MultilingualModelForm, formfield_callback=None,
                         formset=BaseModelFormSet,
                         extra=1, can_delete=False, can_order=False,
                         max_num=None, fields=None, exclude=None):
    """
    Returns a FormSet class for the given Django model class.
    """
    form = multilingual_modelform_factory(model, form=form, fields=fields, exclude=exclude,
                             formfield_callback=formfield_callback)
    FormSet = formset_factory(form, formset, extra=extra, max_num=max_num,
                              can_order=can_order, can_delete=can_delete)
    FormSet.model = model
    return FormSet


#TODO: Same as above
def multilingual_inlineformset_factory(parent_model, model, form=MultilingualModelForm,
                          formset=BaseInlineFormSet, fk_name=None,
                          fields=None, exclude=None,
                          extra=3, can_order=False, can_delete=True, max_num=None,
                          formfield_callback=None):
    """
    Returns an ``InlineFormSet`` for the given kwargs.

    You must provide ``fk_name`` if ``model`` has more than one ``ForeignKey``
    to ``parent_model``.
    """
    fk = _get_foreign_key(parent_model, model, fk_name=fk_name)
    # enforce a max_num=1 when the foreign key to the parent model is unique.
    if fk.unique:
        max_num = 1
    kwargs = {
        'form': form,
        'formfield_callback': formfield_callback,
        'formset': formset,
        'extra': extra,
        'can_delete': can_delete,
        'can_order': can_order,
        'fields': fields,
        'exclude': exclude,
        'max_num': max_num,
    }
    FormSet = multilingual_modelformset_factory(model, **kwargs)
    FormSet.fk = fk
    return FormSet
