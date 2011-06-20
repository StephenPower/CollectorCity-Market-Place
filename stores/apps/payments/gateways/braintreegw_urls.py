from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^confirm/$', 'payments.gateways.braintreegw.confirm', name='braintree_confirm'),
)