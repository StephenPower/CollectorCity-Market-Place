from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'blog_pages.views.blog_pages', name='blog_pages'),

    #url(r'^post_list_admin/$', 'blog_pages.views.post_list_admin', name='post_list_admin'),
    url(r'^post_add/$', 'blog_pages.views.post_add', name='post_add'),
    url(r'^post_edit/([\d]+)/$', 'blog_pages.views.post_edit', name='post_edit'),
    url(r'^post_delete/([\d]+)/$', 'blog_pages.views.post_delete', name='post_delete'),
    
    url(r'^page_edit_home/$', 'blog_pages.views.page_edit_home', name='page_edit_home'),
    url(r'^page_edit_about/$', 'blog_pages.views.page_edit_about', name='page_edit_about'),
    url(r'^page_create/$', 'blog_pages.views.page_create', name='page_create'),
    url(r'^page_edit_static/([\d]+)/$', 'blog_pages.views.page_edit_static', name='page_edit_static'),
    url(r'^page_edit_dynamic/([\d]+)/$', 'blog_pages.views.page_edit_dynamic', name='page_edit_dynamic'),
    url(r'^page_delete/([\d]+)/$', 'blog_pages.views.page_delete', name='page_delete'),
    
    url(r'^navigation/$', 'blog_pages.views.navigation', name='navigation'),
    url(r'^link_add/([\d]+)/$', 'blog_pages.views.link_add', name='link_add'),
    url(r'^link_edit/([\d]+)/$', 'blog_pages.views.link_edit', name='link_edit'),
    url(r'^link_delete/([\d]+)/$', 'blog_pages.views.link_delete', name='link_delete'),
    
    url(r'^link_order/$', 'blog_pages.views.link_order', name='link_order'),

)