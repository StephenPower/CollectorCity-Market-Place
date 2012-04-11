from django.conf.urls.defaults import *


urlpatterns = patterns('',
    url(r'^$', 'market.views.buy', name='market_buy'),
    url(r'^advanced_search/$', 'market_buy.views.advanced_search', name='buy_advanced_search'),
    url(r'^advanced_search_reset/$', 'market_buy.views.advanced_search', {"reset": True}, name='buy_advanced_search_reset'),
    url(r'^categories/$', 'market_buy.views.categories', name='buy_categories'),
    url(r'^confirmemail/(?P<code>[\d\w\-]+)/$', 'market_buy.views.confirmemail', name='buy_confirmemail'),
    url(r'^howtobuy/$', 'market_buy.views.howtobuy', name='buy_howtobuy'),
    url(r'^editor_pick/$', 'market_buy.views.editor_pick', name='buy_editor_pick'),
    url(r'^latest_items/$', 'market_buy.views.latest_items', name='buy_latest_items'),
    url(r'^map_pick/$', 'market_buy.views.map_pick', name='buy_map_pick'),
    url(r'^show_listing/$', 'market_buy.views.show_listing', name='buy_show_listing'),
    url(r'^show_search/$', 'market_buy.views.show_search', name='buy_show_search'),
    url(r'^shop_local/$', 'market_buy.views.shop_local', name='buy_shop_local'),
    url(r'^top_sellers/$', 'market_buy.views.top_sellers', name='buy_top_sellers'),
    url(r'^wish_list/$', 'market_buy.views.wish_list', name='buy_wish_list'),
    url(r'^wish_list/post_item/$', 'market_buy.views.post_wish_list_item', name='post_wish_list_item'),
    url(r'^ajax_get_subcategories/$', 'market_buy.views.ajax_get_subcategories', name='ajax_get_subcategories'),
    
    url(r'^login/$', 'market_buy.views.login', name='market_buy_login'),
    url(r'^signup/$', 'market_buy.views.signup', name='market_buy_signup'),
    url(r'^profile/$', 'market_buy.views.user_profile', name='market_buy_user_profile'),
    url(r'^delete_profile_image/$', 'market_buy.views.delete_profile_image', name='delete_profile_image'),
    
    url(r'^product/p(?P<id>[\d]+)/', 'market_buy.views.product_redirect', name="market_buy_product_redirect"),
    url(r'^product/i(?P<id>[\d]+)/', 'market_buy.views.item_redirect', name="market_buy_item_redirect"),
)
