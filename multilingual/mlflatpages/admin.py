from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from multilingual.admin import MultilingualModelAdmin

from .forms import FlatpageForm
from .models import FlatPage


class FlatPageAdmin(MultilingualModelAdmin):
    form = FlatpageForm
    fieldsets = (
        (None, {'fields': ('url', 'title', 'content', 'sites')}),
        (_('Advanced options'), {'classes': ('collapse',), 'fields': ('enable_comments', 'registration_required', 'template_name')}),
    )
    list_display = ('url', 'title')
    list_filter = ('sites', 'enable_comments', 'registration_required')
    search_fields = ('url', 'title')

admin.site.register(FlatPage, FlatPageAdmin)
