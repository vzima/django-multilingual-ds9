from django.conf.urls import patterns, include

# special urls for flatpage test cases
urlpatterns = patterns('',
    (r'^flatpage_root', include('multilingual.mlflatpages.urls')),
    (r'^accounts/', include('django.contrib.auth.urls')),
)
