from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^', include('market.urls')),
    (r'^buy/', include('market_buy.urls')),
    (r'^sell/', include('market_sell.urls')),
    (r'^community/', include('market_community.urls')),
    (r'^admin/reports/', include('reports.urls')),
    
    url(r'^admin/', include(admin.site.urls), name="admin"),
    url(r'^logout/$', 'auth.views.logout', name='logout'),
    url(r'^map/([\d]+)/$', 'bidding.views.bidding_map', name='bidding_map'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    )