from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'store_admin.views.home_admin', name='home_admin'),
    
    url(r'^change_qty/$', 'store_admin.views.ajax_change_qty', name='ajax_change_qty'),
    url(r'^change_price/$', 'store_admin.views.ajax_change_price', name='ajax_change_price'),
    
    url(r'^back/$', 'store_admin.views.back_to_site', name='back_to_site'),
    url(r'^customers/$', 'store_admin.views.customers_overview', name='customers'),
    url(r'^customers/overview/$', 'store_admin.views.customers_overview', name='customers_overview'),
    url(r'^customers/profiles/$', 'store_admin.views.customers_profiles', name='customers_profiles'),
    url(r'^customers/sold_items/$', 'store_admin.views.customers_sold_items', name='customers_sold_items'),
    url(r'^customers/payments/$', 'store_admin.views.customers_payments', name='customers_payments'),
    url(r'^customers/shipments/$', 'store_admin.views.customers_shipments', name='customers_shipments'),
    url(r'^customers/wish_lists/$', 'store_admin.views.customers_wish_lists', name='customers_wish_lists'),
    url(r'^customers/wish_lists/send_notification/([\d]+)/$', 'store_admin.views.customers_send_notification', name='customers_send_notification'),
    url(r'^customers/mailing_list/$', 'store_admin.views.customers_mailing_list', name='customers_mailing_list'),
    url(r'^customers/mailing_list/export/$', 'store_admin.views.customers_export_mailinglist', name='customers_export_mailinglist'),

    url(r'^web_store/$', 'store_admin.views.web_store_overview', name='web_store'),
    url(r'^web_store/overview/$', 'store_admin.views.web_store_overview', name='web_store_overview'),
    url(r'^web_store/marketing/$', 'preferences.views.marketing', name='web_store_marketing'),
    url(r'^web_store/shows/$', 'preferences.views.shows', name='web_store_shows'),
    url(r'^web_store/show_go/([\d]+)/$', 'preferences.views.show_go', name='web_store_show_go'),
    url(r'^web_store/show_not_go/([\d]+)/$', 'preferences.views.show_not_go', name='web_store_show_not_go'),
    url(r'^web_store/theme/$', 'themes.views.theme', name='web_store_theme'),
    url(r'^web_store/theme/([\d]+)/$', 'themes.views.theme', name='web_store_theme'),
    url(r'^web_store/pages/$', 'blog_pages.views.page_create', name='web_store_pages'),
    url(r'^web_store/blogs/$', 'blog_pages.views.post_add', name='web_store_blogs'),
    url(r'^web_store/navigation/$', 'blog_pages.views.navigation', name='web_store_navigation'),
    
    url(r'^inventory/$', 'store_admin.views.inventory_overview', name='inventory'),
    url(r'^inventory/overview/$', 'store_admin.views.inventory_overview', name='inventory_overview'),
    url(r'^inventory/items/$', 'store_admin.views.inventory_items', name='inventory_items'),
    url(r'^inventory/items/import/$', 'store_admin.views.inventory_items_import', name='inventory_items_import'),
    url(r'^inventory/lots/$', 'store_admin.views.inventory_lots', name='inventory_lots'),
    url(r'^inventory/auctions/$', 'store_admin.views.inventory_auctions', name='inventory_auctions'),
    url(r'^inventory/category/$', 'store_admin.views.inventory_categorize', name='inventory_categorize'),

    url(r'^account/$', 'preferences.views.change_profile', name='account'),
    url(r'^account_profile/$', 'preferences.views.change_profile', name='account_profile'),
    url(r'^account_password/$', 'preferences.views.change_password', name='account_password'),
    url(r'^account/add_photo/$', 'store_admin.views.add_profile_photo', name='add_profile_photo'),
    url(r'^preferences/$', 'store_admin.views.preferences_overview', name='preferences'),
    
)