from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'support.views.admin_support', name='admin_support'),
    url(r'^features/$', 'support.views.admin_support_features', name='admin_support_features')
)