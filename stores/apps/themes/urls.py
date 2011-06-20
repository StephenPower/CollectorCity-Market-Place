from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'themes.views.theme', name='themes'),
    url(r'^template_edit/([\d]+)/$', 'themes.views.template_edit', name='template_edit'),
    url(r'^template_get_version/([\d]+)/$', 'themes.views.template_get_version', name='template_get_version'),
    url(r'^asset_add/$', 'themes.views.asset_add', name='asset_add'),
    url(r'^asset_delete/([\d]+)/$', 'themes.views.asset_delete', name='asset_delete'),
    url(r'^asset_edit/([\d]+)/$', 'themes.views.asset_edit', name='asset_edit'),
    
    url(r'^theme_export/$', 'themes.views.theme_export', name='theme_export'),
    url(r'^theme_import/$', 'themes.views.theme_import', name='theme_import'),
)