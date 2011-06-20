from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^list/$', 'shops.views.shop_list', name='shop_list'),
    url(r'^subscription/(?P<shop_id>[\d]+)/$', 'shops.views.shop_subscription', name='shop_subscription'),
    url(r'^subscription/cancel/(?P<shop_id>[\d]+)/$', 'shops.views.shop_cancel_subscription', name='shop_cancel_subscription'),
    url(r'^subscription/change/(?P<plan_id>[\d]+)/$', 'shops.views.change_subscription_plan', name='change_subscription_plan'),
    #url(r'^sign_up/$', 'shops.views.sign_up', name='sign_up'),
)