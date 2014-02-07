from django.conf.urls import patterns

urlpatterns = patterns('multilingual.mlflatpages.views',
    (r'^(?P<url>.*)$', 'flatpage'),
)
