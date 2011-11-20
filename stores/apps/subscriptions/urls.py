from django.conf.urls.defaults import *

urlpatterns = patterns('',
        url(r'^plans/$', 'subscriptions.views.shop_subscription_plans', name='subscription_plans'),
        url(r'^overview/$', 'subscriptions.views.shop_subscription_overview', name='subscription_overview'),
        url(r'^billing/$', 'subscriptions.views.shop_billing', name='billing_overview'),
        url(r'^billing/update/$', 'subscriptions.views.shop_billing_update_credit_card', name='billing_update_credit_card'),
        url(r'^purchases/$', 'subscriptions.views.shop_purchases', name='purchases_overview'),
)