from django.conf.urls.defaults import *


urlpatterns = patterns('',
    url('^$', 'market.views.sell', name='market_sell'),
    url('^signup/$', 'market_sell.views.signup', name='market_sell_signup'),
    url('^privacy/$', 'market_sell.views.privacy_policy', name='market_privacy_policy'),
    url('^welcome/(?P<shop_id>[\d]+)/$', 'market_sell.views.welcome', name='market_sell_welcome'),
    url('^plans/$', 'market_sell.views.plans', name='market_sell_plans'),
    url('^features/$', 'market_sell.views.features', name='market_sell_features'),
)
