from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^general/$', 'preferences.views.preferences_general', name='preferences_general'),
    url(r'^taxes/$', 'preferences.views.preferences_taxes', name='preferences_taxes'),
    url(r'^taxes/add/$', 'preferences.views.add_state_tax', name='preferences_add_state_tax'),
    url(r'^taxes/delete_tax/([\d]+)/$', 'preferences.views.delete_tax', name='preferences_delete_tax'),
    url(r'^taxes/edit_tax/([\d]+)/$', 'preferences.views.edit_tax', name='preferences_edit_tax'),
    
    url(r'^payment/paypal/$', 'preferences.views.preferences_payment_paypal', name='preferences_payment_paypal'),
    url(r'^payment/google_checkout/$', 'preferences.views.preferences_payment_google_checkout', name='preferences_payment_google_checkout'),
    url(r'^payment/credit_cards/$', 'preferences.views.preferences_payment_credit_cards', name='preferences_payment_credit_cards'),
    url(r'^payment/manual/$', 'preferences.views.preferences_payment_manual', name='preferences_payment_manual'),
    
    url(r'^payment/paypal/setpermissions/$', 'preferences.views.payment_paypal_setpermissions',  name='preferences_payment_paypal_setpermissions'),
    url(r'^payment/paypal/disable/$', 'preferences.views.payment_paypal_disable', name='preferences_payment_paypal_disable'),
    url(r'^payment/paypal/return/(?P<action>(agree|cancel|logout))/$', 'preferences.views.payment_paypal_return', name='preferences_payment_paypal_return'),
    url(r'^auctions/$', 'preferences.views.preferences_auctions', name='preferences_auctions'),
    url(r'^shipping/$', 'preferences.views.preferences_shipping', name='preferences_shipping'),
    url(r'^email/$', 'preferences.views.preferences_email', name='preferences_email'),
    url(r'^dns/$', 'preferences.views.preferences_dns', name='preferences_dns'),
    url(r'^policies/$', 'preferences.views.preferences_policies', name='preferences_policies'),

    url(r'^delete_shipping_weight/([\d]+)/$', 'preferences.views.delete_shipping_weight', name='delete_shipping_weight'),
    url(r'^delete_shipping_price/([\d]+)/$', 'preferences.views.delete_shipping_price', name='delete_shipping_price'),
    url(r'^delete_shipping_item/([\d]+)/$', 'preferences.views.delete_shipping_item', name='delete_shipping_item'),

    url(r'^delete_dns/([\d]+)/$', 'preferences.views.delete_dns', name='delete_dns'),
    url(r'^default_dns/([\d]+)/$', 'preferences.views.set_default_dns', name='set_default_dns'),
    
    url(r'^ajax_edit_notification/$', 'preferences.views.ajax_edit_notification', name='ajax_edit_notification'),
    url(r'^send_template/$', 'preferences.views.send_template', name='send_template'),
    
    url(r'^save_manual_payment/$', 'preferences.views.save_manual_payment', name='save_manual_payment'),
    url(r'^delete_manual_payment/(?P<payment_id>[\d]+)/$', 'preferences.views.delete_manual_payment', name='delete_manual_payment'),
    url(r'^edit_manual_payment/(?P<payment_id>[\d]+)/$', 'preferences.views.edit_manual_payment', name='edit_manual_payment'),
    
    url(r'^save_googlecheckout_settings/$', 'preferences.views.save_googlecheckout_settings', name='save_googlecheckout_settings'),
    url(r'^delete_googlecheckout_settings/(?P<setting_id>[\d]+)/$', 'preferences.views.delete_googlecheckout_settings', name='delete_googlecheckout_settings'),
    
    url(r'^save_braintree_settings/$', 'preferences.views.save_braintree_settings', name='save_braintree_settings'),
    url(r'^delete_braintree_settings/(?P<setting_id>[\d]+)/$', 'preferences.views.delete_braintree_settings', name='delete_braintree_settings'),
    
)