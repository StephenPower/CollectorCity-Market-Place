from django.conf.urls.defaults import *

urlpatterns = patterns('',
    #url(r'^ipn/$', 'payments.gateways.paypal.ipn', name='paypal_ipn'),
    url(r'^cancel/$', 'payments.gateways.paypal.cancel', name='paypal_cancel'),
    url(r'^success/$', 'payments.gateways.paypal.success', name='paypal_success'),
    url(r'^paynow/$', 'payments.gateways.paypal.paynow', name='payments_paypal_paynow'),
    url(r'^ipn/$', 'payments.gateways.paypal.ipn', name='payments_paypal_ipn'),
)