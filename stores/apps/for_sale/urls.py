from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^items_all/$', 'for_sale.views.items_all', name='items_all'),
#    url(r'^lots_active/$', 'lots.views.lots_active', name='lots_active'),
#    url(r'^lots_sold/$', 'lots.views.lots_sold', name='lots_sold'),
#    url(r'^lots_didnt_sell/$', 'lots.views.lots_didnt_sell', name='lots_didnt_sell'),
#
#    url(r'^lots_payment_all/$', 'lots.views.lots_payment_all', name='lots_payment_all'),
#
#    url(r'^lots_shipping_all/$', 'lots.views.lots_shipping_all', name='lots_shipping_all'),
#    url(r'^lots_dispatched/([\d]+)/$', 'lots.views.lots_dispatched', name='lots_dispatched'),
#    url(r'^lots_fulfilled/([\d]+)/$', 'lots.views.lots_fulfilled', name='lots_fulfilled'),
#
#
#    url(r'^lots_open/$', 'lots.views.lots_open', name='lots_open'),
#    url(r'^lots_closed/$', 'lots.views.lots_closed', name='lots_closed'),

    url(r'^item_details/([\d]+)/$', 'for_sale.views.item_details', name='item_details'),
    url(r'^item_add/$', 'for_sale.views.item_add', name='item_add'),
    url(r'^item_edit/([\d]+)/$', 'for_sale.views.item_edit', name='item_edit'),
    url(r'^item_delete/([\d]+)/$', 'for_sale.views.item_delete', name='item_delete'),
    url(r'^items_bulk_delete/$', 'for_sale.views.items_bulk_delete', name='items_bulk_delete'),
#
#    url(r'^add_image/([\d]+)/$', 'for_sale.views.add_item_image', name='add_item_image'),
    url(r'^add_image/([\d]+)/$', 'for_sale.views.add_img', name='add_item_image'),
    url(r'^remove_image/([\d]+)/$', 'for_sale.views.remove_img', name='del_item_image'),
    url(r'^del_image/([\d]+)/([\d]+)/$', 'for_sale.views.del_item_image', name='del_item_image'),
    url(r'^set_primary_picture/([\d]+)/([\d]+)/$', 'for_sale.views.set_primary_picture', name='set_forsale_primary_picture'),
    
    url(r'^import_inventory/$', 'for_sale.views.import_inventory', name='import_inventory'),
    
#    url(r'^category_delete/$', 'lots.views.category_delete', name='category_delete'),
#    url(r'^category_edit/$', 'lots.views.category_edit', name='category_edit'),
)