from django.conf import settings
from django.contrib.flatpages.views import render_flatpage
from django.contrib.sites.models import get_current_site
from django.http import Http404, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404

from .models import FlatPage

# This view is called from FlatpageFallbackMiddleware.process_response
# when a 404 is raised, which often means CsrfViewMiddleware.process_view
# has not been called even if CsrfViewMiddleware is installed. So we need
# to use @csrf_protect, in case the template needs {% csrf_token %}.
# However, we can't just wrap this view; if no matching flatpage exists,
# or a redirect is required for authentication, the 404 needs to be returned
# without any CSRF checks. Therefore, we only
# CSRF protect the internal implementation.
def flatpage(request, url):
    """
    Public interface to the multilingual flat page view.

    Models: `mlflatpages.flatpage`
    Templates: Uses the template defined by the ``template_name`` field,
        or `flatpages/default.html` if template_name is not defined.
    Context:
        flatpage
            `mlflatpages.flatpage` object
    """
    if not url.startswith('/'):
        url = '/' + url
    site_id = get_current_site(request).id
    try:
        f = get_object_or_404(FlatPage,
            url__exact=url, sites__id__exact=site_id)
    except Http404:
        if not url.endswith('/') and settings.APPEND_SLASH:
            url += '/'
            f = get_object_or_404(FlatPage,
                url__exact=url, sites__id__exact=site_id)
            return HttpResponsePermanentRedirect('%s/' % request.path)
        else:
            raise

    # Use django flatpage render
    return render_flatpage(request, f)
