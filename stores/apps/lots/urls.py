from django.conf.urls.defaults import *



urlpatterns = patterns('',   
    url(r'^lots_all/$', 'lots.views.lots_all', name='lots_all'),
    url(r'^lots_active/$', 'lots.views.lots_active', name='lots_active'),
    url(r'^lots_sold/$', 'lots.views.lots_sold', name='lots_sold'),
    url(r'^lots_didnt_sell/$', 'lots.views.lots_didnt_sell', name='lots_didnt_sell'),

    url(r'^lots_payment_all/$', 'lots.views.lots_payment_all', name='lots_payment_all'),

    url(r'^lots_shipping_all/$', 'lots.views.lots_shipping_all', name='lots_shipping_all'),
    url(r'^lots_dispatched/([\d]+)/$', 'lots.views.lots_dispatched', name='lots_dispatched'),
    url(r'^lots_fulfilled/([\d]+)/$', 'lots.views.lots_fulfilled', name='lots_fulfilled'),

    url(r'^lots_open/$', 'lots.views.lots_open', name='lots_open'),
    url(r'^lots_closed/$', 'lots.views.lots_closed', name='lots_closed'),
    url(r'^lot_details/([\d]+)/$', 'lots.views.lot_details', name='lot_details'),
    url(r'^lot_add/$', 'lots.views.lot_add', name='lot_add'),
    url(r'^lot_edit/([\d]+)/$', 'lots.views.lot_edit', name='lot_edit'),
    url(r'^set_primary_picture/([\d]+)/([\d]+)/$', 'lots.views.set_primary_picture', name='set_lot_primary_picture'),
#    url(r'^ajax_category_add/$', 'lots.views.ajax_category_add', name='ajax_category_add'),
#    url(r'^ajax_category/$', 'lots.views.ajax_category', name='ajax_category'),
#    url(r'^ajax_sub_category_add/$', 'lots.views.ajax_sub_category_add', name='ajax_sub_category_add'),
#    url(r'^ajax_sub_category/$', 'lots.views.ajax_sub_category', name='ajax_sub_category'),
#    url(r'^ajax_session_add/$', 'lots.views.ajax_session_add', name='ajax_session_add'),
#    url(r'^ajax_session/$', 'lots.views.ajax_session', name='ajax_session'),

#    url(r'^add_image/([\d]+)/$', 'lots.views.add_image', name='add_image'),
    url(r'^add_image/([\d]+)/$', 'lots.views.add_img', name='add_image'),
    url(r'^del_image/([\d]+)/([\d]+)/$', 'lots.views.del_image', name='del_image'),
    
    
#    url(r'^category_delete/$', 'lots.views.category_delete', name='category_delete'),
#    url(r'^category_edit/$', 'lots.views.category_edit', name='category_edit'),
)