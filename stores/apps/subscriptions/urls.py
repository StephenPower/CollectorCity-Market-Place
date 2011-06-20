from django.conf.urls.defaults import *

urlpatterns = patterns('',
        url(r'^plans/$', 'subscriptions.views.shop_subscription_plans', name='subscription_plans'),
        url(r'^overview/$', 'subscriptions.views.shop_subscription_overview', name='subscription_overview'),
)