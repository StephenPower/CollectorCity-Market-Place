from models import *
from django.contrib import admin


class EmailNotificationHistoryAdmin(admin.ModelAdmin):
    list_display = ('shop','type_notification', 'to', 'datetime')
    list_filter = ('shop','type_notification', 'datetime', 'to')

admin.site.register(Preference)
admin.site.register(ShippingWeight)
admin.site.register(ShippingPrice)
admin.site.register(ShippingItem)
admin.site.register(TaxState)
admin.site.register(DnsShop)
admin.site.register(EmailNotification)
admin.site.register(EmailNotificationHistory, EmailNotificationHistoryAdmin)
admin.site.register(ShopPolicies)


