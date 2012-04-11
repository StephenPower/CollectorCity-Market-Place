# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

#from shops.views import sign_up 
from shops.views import welcome_shop
from for_sale.feeds import LatestItemFeed
from auctions.feeds import LatestAuctionsFeed
from blog_pages.feeds import LatestPostFeed

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'core.views.home', name='home'),
    url(r'^redirect/$', 'core.views.redirect', name='redirect'),
#    url(r'^sign_up/$', 'shops.views.sign_up', name='sign_up'),
#    url(r'^sign_up/(?P<plan>\d+)$', 'shops.views.sign_up', name='sign_up'),
    url(r'^welcome_shop/([\d]+)/$', 'shops.views.welcome_shop', name='welcome_shop'),
    url(r'^pricing/$', 'subscriptions.views.subscription_plans', name='subscription_plans'),
    url(r'^redirect_admin/$', 'store_admin.views.redirect_admin', name='redirect_admin'),
    
    (r'^admin/', include('store_admin.urls')),
    
    #delete this
    url(r'^admin_login/([\d]+)/$', 'core.views.admin_login', name='admin_login'),
    
    (r'^admin/auctions/', include('auctions.urls')),
    (r'^admin/lots/', include('lots.urls')),
    (r'^admin/preferences/', include('preferences.urls')),
    (r'^admin/blog_pages/', include('blog_pages.urls')),
    
    (r'^admin/category/', include('category.urls')),
    (r'^admin/sale/', include('sell.urls')),
    (r'^admin/for_sale/', include('for_sale.urls')),
    (r'^admin/shops/', include('shops.urls')),
    (r'^admin/themes/', include('themes.urls')),
    
    (r'^admin/subscription/', include('subscriptions.urls')),

    (r'^payments/', include('payments.urls')),
    (r'^users/', include('users.urls')),
    (r'^my_shopping/', include('my_shopping.urls')),
    
    #### Public store views ###
    
    #Auctions
    url(r'^auctions/$', 'bidding.views.bidding_auctions', name='bidding_auctions'),
    url(r'^auctions/([\d]+)/$', 'bidding.views.bidding_auctions', name='bidding_auctions_id'),
    url(r'^auctions/latest/feed/$', LatestAuctionsFeed()),
    url(r'^auctions/view_lot/([\d]+)/$', 'bidding.views.bidding_view_lot', name='bidding_view_lot'),
    url(r'^auctions/view_history_lot/([\d]+)/$', 'bidding.views.bidding_view_history_lot', name='bidding_view_history_lot'),

    #Billing
    url(r'^services/google/ipn/$', 'payments.gateways.googlecheckout.process_google_message', name='payments_googlecheckout_ipn'),

    #For Sale
    url(r'^for_sale/$', 'bidding.views.bidding_for_sale', name='bidding_for_sale'),
    url(r'^for_sale/latest/feed/$', LatestItemFeed()),
    url(r'^for_sale/buy_now/([\d]+)/$', 'bidding.views.bidding_buy_now', name='bidding_buy_now'),
    url(r'^for_sale/view_item/([\d]+)/$', 'bidding.views.bidding_view_item', name='bidding_view_item'),
    

    #Blog Pages
    url(r'^about_us/$', 'bidding.views.bidding_about_us', name='bidding_about_us'),
    url(r'^blog/$', 'bidding.views.bidding_blog', name='bidding_blog'),
    url(r'^blog/latest/feed/$', LatestPostFeed()),
    url(r'^home/$', 'bidding.views.bidding_home', name='bidding_home'),
    url(r'^sitemap\.xml$', 'bidding.views.pages_sitemap', name='bidding_sitemap'),
    url(r'^pages/([^/]+)/$', 'bidding.views.pages', name='bidding_page'),
    url(r'^robots\.txt$', 'bidding.views.pages_robots', name='bidding_robots'),
    url(r'^privacy_policy/$', 'bidding.views.privacy_policy', name='bidding_privacy_policy'),
    url(r'^blog/view_post/([\d]+)/$', 'bidding.views.bidding_view_post', name='bidding_view_post'),
    
    
    url(r'^refund/', 'bidding.views.bidding_refund', name='bidding_refund'),
    url(r'^privacy_policy/', 'bidding.views.privacy_policy', name='bidding_privacy_policy'),
    url(r'^terms_of_service/', 'bidding.views.terms_of_service', name='bidding_terms_of_service'),
    
    #Search
    url(r'^search/$', 'bidding.views.bidding_search', name='bidding_search'),
    
    #Login        
    url(r'^login/$', 'auth.views.login', {'template_name': 'bidding/blocks/login.html'}, name='login'),
    url(r'^logout/$', 'auth.views.logout', name='logout'),
    url(r'^register/$', 'users.views.register', name='user_register'),
    url(r'^login_admin/$', 'auth.views.login', {'template_name': 'core/login.html'}, name='login_admin'),
    
    #Tinymce
    (r'^tinymce/', include('tinymce.urls')),
    
    #Other
    url(r'^map/([\d]+)/$', 'bidding.views.bidding_map', name='bidding_map'),        
    
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', 
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
                           
    (r'^public/(?P<path>.*)$', 'django.views.static.serve', 
        {'document_root': settings.STATIC_ROOT, 'show_indexes': True}),
    
    (r'^media_out_s3/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT_OUT_S3, 'show_indexes': True}),

)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^tests/remove-qa-user/$', 'core.views.remove_qa_user'),
    )
