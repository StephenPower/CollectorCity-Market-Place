from django.conf.urls.defaults import *


urlpatterns = patterns('',
    url('^$', 'market.views.home', name='market_home'),
    url('^contact_us/$', 'market.views.contact_us', name='market_contact_us'),
    url('^for_sale/$', 'market.views.for_sale', name='market_for_sale'),
    url('^auctions/$', 'market.views.auctions', name='market_auctions'),
    url('^search/$', 'market.views.search', name='market_search'),
    url('^coins-(?P<category_slug>[a-zA-Z0-9.-]+)/$', 
        'market.views.search', name='market_search_category'),
    url('^coins-(?P<category_slug>[a-zA-Z0-9.-]+)/(?P<shop_id>\d+)/$',
        'market.views.search', name='market_search_category_by_shop'),
    url('^coins-(?P<category_slug>[a-zA-Z0-9.-]+)_(?P<subcategory_slug>[a-zA-Z0-9.-]*)/$', 
        'market.views.search', name='market_search_subcategory'),
    url('^view_item/([\d]+)/$', 'market.views.view_item', name='view_item'),
    url('^blog/$', 'market.views.blog', name='market_blog'),
    url('^blog/add_comment/$', 'market.views.add_post_comment', name='add_post_comment'),
    url('^blog/(?P<post_slug>[a-zA-Z0-9_.-]+)/$', 'market.views.view_post', name='market_blog_view_post'),
    url('^switch_listing/$', 'market.views.set_listing_mode', name='set_listing_mode'),
    url('^switch_order/$', 'market.views.set_order_mode', name='set_order_mode'),
    url('^survey/$', 'market.views.survey', name='market_survey'),
)
