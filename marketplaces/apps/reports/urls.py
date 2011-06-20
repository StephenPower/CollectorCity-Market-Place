from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'reports.views.admin_reports', name='admin_reports'),
    url(r'^subscriptions/$', 'reports.views.admin_shop_subscriptions_report', name='admin_shop_subscriptions'),
    url(r'^subscription/(?P<id>[\d]+)/$', 'reports.views.admin_shop_subscription_details', name='admin_shop_subscription_details'),
    url(r'^activity/$', 'reports.views.admin_daily_activity_report', name='admin_daily_activity'),
    url(r'^revenue/$', 'reports.views.admin_monthly_revenue_report', name='admin_monthly_revenue'),
    url(r'^transactions/$', 'reports.views.admin_daily_transactions_report', name='admin_daily_transactions'),
)