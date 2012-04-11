from django.conf.urls.defaults import *

urlpatterns = patterns('flatpages.views',
    (r'^(?P<url>.*)$', 'flatpage'),
)
