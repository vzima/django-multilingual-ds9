# comfortable imports
from multilingual.admin.options import MultilingualModelAdmin


# DEPRECATED: Original code
"""Admin suppor for inlines

Peter Cicman, Divio GmbH, 2008
"""
import re
from django import forms
from django.contrib import admin
from django.db.models import Model
from django.forms.models import BaseInlineFormSet
from django.forms.util import ErrorList
from django.utils.translation import ugettext as _
from multilingual.utils import GLL

MULTILINGUAL_PREFIX = '_ml__trans_'
MULTILINGUAL_INLINE_PREFIX = '_ml__inline_trans_'


def standard_get_fill_check_field(stdopts):
    if hasattr(stdopts, 'translation_model'):
        opts = stdopts.translation_model._meta
        for field in opts.fields:
            if field.name in ('language_code', 'master'):
                continue
            if not (field.blank or field.null):
                return field.name
    return None

def relation_hack(form, fields, prefix=''):
    opts = form.instance._meta
    localm2m = [m2m.attname for m2m in opts.local_many_to_many]
    externalfk = [obj.field.related_query_name() for obj in opts.get_all_related_objects()]
    externalm2m = [m2m.get_accessor_name() for m2m in opts.get_all_related_many_to_many_objects()]
    for name, db_field in fields:
        full_name = '%s%s' % (prefix, name)
        if full_name in form.fields:
            value = getattr(form.instance, name, '')
            # check for (local) ForeignKeys
            if isinstance(value, Model):
                value = value.pk
            # check for (local) many to many fields
            elif name in localm2m:
                value = value.all()
            # check for (external) ForeignKeys
            elif name in externalfk:
                value = value.all()
            # check for (external) many to many fields
            elif name in externalm2m:
                value = value.all()
            form.fields[full_name].initial = value


class MultilingualInlineModelForm(forms.ModelForm):
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=':',
                 empty_permitted=False, instance=None):
        """
        Fill initial ML Fields
        """
        super(MultilingualInlineModelForm, self).__init__(data, files, auto_id,
            prefix, initial, error_class, label_suffix, empty_permitted, instance)
        
        # only read initial data if the object already exists, not if we're adding it!
        if self.instance.pk:
            relation_hack(self, get_translated_fields(self.instance), MULTILINGUAL_INLINE_PREFIX)


class MultilingualInlineFormSet(BaseInlineFormSet):
    def get_queryset(self):
        if self.queryset is not None:
            qs = self.queryset
        else:
            qs = self.model._default_manager.get_query_set()

        if not qs.ordered:
            qs = qs.order_by(self.model._meta.pk.name)

        if self.max_num > 0:
            _queryset = qs[:self.max_num]
        else:
            _queryset = qs
        return _queryset

    def save_new(self, form, commit=True):
        """
        NOTE: save_new method is completely overridden here, there's no
        other way to pretend double save otherwise. Just assign translated data
        to object  
        """
        kwargs = {self.fk.get_attname(): self.instance.pk}
        new_obj = self.model(**kwargs)
        self._prepare_multilingual_object(new_obj, form)
        return forms.save_instance(form, new_obj, exclude=[self._pk_field.name], commit=commit)
    
    def save_existing(self, form, instance, commit=True):
        """
        NOTE: save_new method is completely overridden here, there's no
        other way to pretend double save otherwise. Just assign translated data
        to object  
        """
        self._prepare_multilingual_object(instance, form)
        return forms.save_instance(form, instance, exclude=[self._pk_field.name], commit=commit)
    
    def _prepare_multilingual_object(self, obj, form):
        opts = obj._meta
        for realname, fieldname in self.ml_fields.items():
            field = opts.get_field_by_name(realname)[0]
            m = re.match(r'^%s(?P<field_name>.*)$' % MULTILINGUAL_INLINE_PREFIX, fieldname)
            if m:
                field.save_form_data(self.instance, form.cleaned_data[fieldname])
                setattr(obj, realname, getattr(self.instance, realname.rsplit('_', 1)[0]))
      
      
class MultilingualInlineAdmin(admin.TabularInline):
    formset = MultilingualInlineFormSet
    form = MultilingualInlineModelForm
    
    template = 'admin/multilingual/edit_inline/tabular.html'
    
    # css class added to inline box
    inline_css_class = None
    
    use_language = None
    
    fill_check_field = None
    #TODO: add some nice template
    
    def __init__(self, parent_model, admin_site):
        super(MultilingualInlineAdmin, self).__init__(parent_model, admin_site)
        if hasattr(self, 'use_fields'):
            # go around admin fields structure validation
            self.fields = self.use_fields
        
    def get_formset(self, request, obj=None, **kwargs):
        FormSet = super(MultilingualInlineAdmin, self).get_formset(request, obj, **kwargs)
        FormSet.use_language = GLL.language_code
        FormSet.ml_fields = {}
        for name, field in get_translated_fields(self.model, GLL.language_code):
            fieldname = '%s%s' % (MULTILINGUAL_INLINE_PREFIX, name)
            FormSet.form.base_fields[fieldname] = self.formfield_for_dbfield(field, request=request)
            FormSet.ml_fields[name] = fieldname
        return FormSet

    def queryset(self, request):
        """
        Filter objects which don't have a value in this language
        """
        qs = super(MultilingualInlineAdmin, self).queryset(request)
        # Don't now what the hell I was thinking here, but this code breaks stuff:
        #
        # checkfield = self.get_fill_check_field()
        # if checkfield is not None:
        #     kwargs = {str('%s_%s__isnull' % (checkfield, GLL.language_code)): False}
        #     from django.db.models.fields import CharField
        #     if isinstance(self.model._meta.translation_model._meta.get_field_by_name(checkfield)[0], CharField):
        #         kwargs[str('%s_%s__gt' % (checkfield, GLL.language_code))] = ''
        #     return qs.filter(**kwargs)
        return qs.filter(translations__language_code=GLL.language_code).distinct()
    
    def get_fill_check_field(self):
        if self.fill_check_field is None:
            self.fill_check_field = standard_get_fill_check_field(self.model._meta)
        return self.fill_check_field
    
    



def get_translated_fields(model, language=None):
    meta = model._meta

    # returns all the translatable fields, except of the default ones
    if not language:
        for field in meta.virtual_fields:
            if field._language_code and not field._fallback:
                yield field.name, field
        #===============================================================================================================
        # for name, (field, non_default) in meta.translated_fields.items():
        #    if non_default:
        #        yield name, field
        #===============================================================================================================

    else:
        for field in meta.virtual_fields:
            if field._language_code == language and not field._fallback:
                yield field.name, field
        #===============================================================================================================
        # # if language is defined return fields in the same order, like they are defined in the 
        # # translation class
        # for field in meta.fields:
        #    if field.primary_key:
        #        continue
        #    name = field.name + "_%s" % language
        #    field = meta.translated_fields.get(name, None)
        #    if field:
        #        yield name, field[0]
        #===============================================================================================================

