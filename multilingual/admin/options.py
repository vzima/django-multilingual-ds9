"""
Model admin for multilingual models
"""
from django.contrib.admin import ModelAdmin
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext as _

from multilingual.forms import MultilingualModelForm
from multilingual.languages import get_dict, get_active, lock, release

#TODO: Inline model admins


class MultilingualModelAdmin(ModelAdmin):
    """
    Model admin for multilingual models
    """
    form = MultilingualModelForm

    # use special template to render tabs for languages on top
    change_form_template = "multilingual/admin/change_form.html"

    #TODO: select_related on queryset of required
    #TODO: select_related on get_object if required

    def render_change_form(self, request, context, **kwargs):
        # Django 1.4 postponed template rendering, so we have to pass updated language in context and avoid context
        # processor.
        # TODO: Make this a hidden form field.
        context['ML_ADMIN_LANGUAGE'] = get_active()
        return super(MultilingualModelAdmin, self).render_change_form(request, context, **kwargs)

    def add_view(self, request, form_url='', extra_context=None):
        """
        Lock language over add_view and add extra_context
        """
        try:
            lock(request.POST.get('ml_admin_language', request.GET.get('ml_admin_language', get_active())))

            model = self.model
            opts = model._meta
            context = {
                'title': _('Add %s for language %s') % (
                    force_unicode(opts.verbose_name),
                    force_unicode(get_dict()[get_active()])
                ),
            }
            context.update(extra_context or {})
            return super(MultilingualModelAdmin, self).add_view(request, form_url=form_url, extra_context=context)
        finally:
            release()

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """
        Lock language over change_view and add extra_context
        """
        try:
            lock(request.POST.get('ml_admin_language', request.GET.get('ml_admin_language', get_active())))

            model = self.model
            opts = model._meta
            context = {
                'title': _('Change %s for language %s') % (
                    force_unicode(opts.verbose_name),
                    force_unicode(get_dict()[get_active()])
                ),
            }
            context.update(extra_context or {})
            return super(MultilingualModelAdmin, self).change_view(request, object_id, form_url=form_url,
                                                                   extra_context=context)
        finally:
            release()
