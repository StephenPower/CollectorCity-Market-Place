from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^success/$', 'payments.views.success', name='payments_success'),
    url(r'^cancel/$', 'payments.views.cancel', name='payments_cancel'),    
    url(r'^error/$', 'payments.views.cancel', name='payments_error'),
    (r'^paypal/', include('payments.gateways.paypal_urls')),
    (r'^google/', include('payments.gateways.googlecheckout_urls')),
    (r'^braintree/', include('payments.gateways.braintreegw_urls')),
)