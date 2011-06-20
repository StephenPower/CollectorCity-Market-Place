from django.conf.urls.defaults import *
#
urlpatterns = patterns('',
    url(r'^ajax_category_add/$', 'category.views.ajax_category_add', name='ajax_category_add'),
    url(r'^ajax_category/$', 'category.views.ajax_category', name='ajax_category'),
    url(r'^ajax_sub_category_add/$', 'category.views.ajax_sub_category_add', name='ajax_sub_category_add'),
    url(r'^ajax_sub_category/$', 'category.views.ajax_sub_category', name='ajax_sub_category'),
    url(r'^ajax_session_add/$', 'category.views.ajax_session_add', name='ajax_session_add'),
    url(r'^ajax_session/$', 'category.views.ajax_session', name='ajax_session'),
#    
##    url(r'^category_delete/$', 'lots.views.category_delete', name='category_delete'),
##    url(r'^category_edit/$', 'lots.views.category_edit', name='category_edit'),
)