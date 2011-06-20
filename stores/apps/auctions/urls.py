"""
URLConf for Auctions

Usage in your base urls.py:
    (r'^auctions/', include('auctions.urls')),

"""

from django.conf.urls.defaults import *

urlpatterns = patterns('',
                       
#    url(r'^auctions_list/$', 'auctions.views.auctions_list', name='auctions_list'),
    url(r'^auction_add/$', 'auctions.views.auction_add', name='auction_add'),
    url(r'^auction_details/([\d]+)/$', 'auctions.views.auction_details', name='auction_details'),
#    url(r'^item_sell/$', 'auctions.views.item_sell', name='auctions_item_sell'),
#    url(r'^seller_summary/$', 'auctions.views.seller_summary', name='auctions_seller_summary'),
#    url(r'^buyer_summary/$', 'auctions.views.buyer_summary', name='auctions_buyer_summary'),
#    url(r'^item_view/(?P<item_id>([\d]+))/$', 'auctions.views.item_view', name='auctions_item_view'),
#    url(r'^watch_item/(?P<item_id>([\d]+))/$', 'auctions.views.watch_item', name='auctions_watch_item'),
#    url(r'^buy_item/(?P<item_id>([\d]+))/$', 'auctions.views.buy_item', name='auctions_buy_item'),
#    url(r'^history_bids/(?P<item_id>([\d]+))/$', 'auctions.views.history_bids', name='auctions_history_bids'),
)