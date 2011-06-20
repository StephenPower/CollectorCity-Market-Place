from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^confirmemail/(?P<code>[\d\w\-]+)/$', 'users.views.confirmemail', name='confirmemail'),
    url(r'^re_send_mail/(?P<user_id>[\d]+)/$', 'users.views.re_send_mail', name='re_send_mail'),
    url(r'^welcome/$', 'users.views.welcome', name='welcome'),
)