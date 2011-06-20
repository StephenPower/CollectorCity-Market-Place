from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'my_shopping.views.my_shopping', name='my_shopping'),
    url(r'^my_orders$', 'my_shopping.views.my_orders', name='my_orders'),
    #url(r'^pay/$', 'my_shopping.views.pay_now', name='pay_now'),
    url(r'^checkout/shipping/$', 'my_shopping.views.checkout_shipping', name='myshopping_checkout_shipping'),
    url(r'^checkout/confirm/$', 'my_shopping.views.checkout_confirm', name='myshopping_checkout_confirm'),
    url(r'^checkout/manual_payment/$', 'my_shopping.views.checkout_manual_payment', name='myshopping_checkout_manual_payment'),
    url(r'^remove_from_cart/([\d]+)/$', 'my_shopping.views.remove_from_cart', name='remove_from_cart'),
    url(r'^clean/$', 'my_shopping.views.clean_cart', name='clean_cart'),
    
    
#    url(r'^category_delete/$', 'lots.views.category_delete', name='category_delete'),
#    url(r'^category_edit/$', 'lots.views.category_edit', name='category_edit'),
)