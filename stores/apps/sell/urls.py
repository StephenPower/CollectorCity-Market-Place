from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^sell_all/$', 'sell.views.sell_all', name='sell_all'),
    url(r'^sell_details/([\d]+)/$', 'sell.views.sell_details', name='sell_details'),
    url(r'^sell_dispatched/([\d]+)/$', 'sell.views.sell_dispatched', name='sell_dispatched'),
    url(r'^sel_undispatched/([\d]+)/$', 'sell.views.sel_undispatched', name='sel_undispatched'),
    url(r'^sell_fulfilled/([\d]+)/$', 'sell.views.sell_fulfilled', name='sell_fulfilled'),

    url(r'^sell_manual_pay/([\d]+)/$', 'sell.views.sell_manual_pay', name='sell_manual_pay'),
    url(r'^sell_manual_fail/([\d]+)/$', 'sell.views.sell_manual_fail', name='sell_manual_fail'),

    url(r'^sell_open/([\d]+)/$', 'sell.views.sell_open', name='sell_open'),
    url(r'^sell_close/([\d]+)/$', 'sell.views.sell_close', name='sell_close'),

    url(r'^sell_cancel/([\d]+)/$', 'sell.views.sell_cancel', name='sell_cancel'),
    url(r'^sell_refund/([\d]+)/$', 'sell.views.sell_refund', name='sell_refund'),
)