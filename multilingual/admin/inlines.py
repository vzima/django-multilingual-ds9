"""
Inline model admin for multilingual models
"""
from django.contrib.admin.options import InlineModelAdmin

from multilingual.forms import MultilingualModelForm


#TODO: I do not know how to handle languages here, because I can not lock language here
# Probably the best solution is to create ModelAdmin that enables usage of multilingual inlines.
# We need to display language tabs somewhere - this might be part of management form
# We need to include language hidden input - also might be part of management form
# We need to lock language somewhere, but main code for this is somewhere else

# This is more or less only shell, it requires more changes to be done, so it works properly

class MultilingualInlineModelAdmin(InlineModelAdmin):
    """
    Inline model admin for multilingual models
    """
    form = MultilingualModelForm


class MultilingualStackedInline(MultilingualInlineModelAdmin):
    template = 'admin/edit_inline/stacked.html'


class MultilingualTabularInline(MultilingualInlineModelAdmin):
    template = 'admin/edit_inline/tabular.html'
