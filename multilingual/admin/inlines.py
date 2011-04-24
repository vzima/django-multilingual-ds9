from django.contrib.admin.options import InlineModelAdmin
from django.contrib.admin.util import flatten_fieldsets
from django.utils.functional import curry

from multilingual.forms.forms import MultilingualModelForm
from multilingual.forms.formsets import multilingual_inlineformset_factory


#TODO: I do not know how to handle languages here, because I can not lock language here
# Probably the best solution is to create ModelAdmin that enables usage of multilingual inlines.
# We need to display language tabs somewhere - this might be part of management form
# We need to include language hidden input - also might be part of management form
# We need to lock language somewhere, but main code for this is somewhere else

# This is more or less only shell, it requires more changes to be done, so it works properly

class MultilingualInlineModelAdmin(InlineModelAdmin):
    form = MultilingualModelForm

    def get_formset(self, request, obj=None, **kwargs):
        """Returns a BaseInlineFormSet class for use in admin add/change views."""
        if self.declared_fieldsets:
            fields = flatten_fieldsets(self.declared_fieldsets)
        else:
            fields = None
        if self.exclude is None:
            exclude = []
        else:
            exclude = list(self.exclude)
        exclude.extend(kwargs.get("exclude", []))
        exclude.extend(self.get_readonly_fields(request, obj))
        # if exclude is an empty list we use None, since that's the actual
        # default
        exclude = exclude or None
        defaults = {
            "form": self.form,
            "formset": self.formset,
            "fk_name": self.fk_name,
            "fields": fields,
            "exclude": exclude,
            "formfield_callback": curry(self.formfield_for_dbfield, request=request),
            "extra": self.extra,
            "max_num": self.max_num,
            "can_delete": self.can_delete,
        }
        defaults.update(kwargs)
        return multilingual_inlineformset_factory(self.parent_model, self.model, **defaults)


class MultilingualStackedInline(MultilingualInlineModelAdmin):
    template = 'admin/edit_inline/stacked.html'


class MultilingualTabularInline(MultilingualInlineModelAdmin):
    template = 'admin/edit_inline/tabular.html'
