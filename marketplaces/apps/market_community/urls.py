from django.conf.urls.defaults import *


urlpatterns = patterns('',
    url('^$', 'market_community.views.overview', name='market_community'),
    url(r'^overview/$', 'market_community.views.overview', name='community_overview'),
    url(r'^forums/$', 'market_community.views.forums', name='community_forums'),
    url(r'^blogs/$', 'market_community.views.blogs', name='community_blogs'),
    url(r'^faq/$', 'market_community.views.faq', name='community_faq'),
    url(r'^profiles/$', 'market_community.views.profiles', name='community_profiles'),
    url(r'^profiles/(?P<letter>[\w]+)/$', 'market_community.views.profiles_list', name='community_profiles_list'),
)
