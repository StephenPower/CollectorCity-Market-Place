
from django.contrib import admin

from models import PayPalShopSettings, GoogleCheckoutShopSettings, GoogleCheckoutOrder, ManualPaymentShopSettings, BraintreeShopSettings, BrainTreeTransaction, PayPalToken

admin.site.register(PayPalShopSettings)
admin.site.register(PayPalToken)
admin.site.register(ManualPaymentShopSettings)
admin.site.register(GoogleCheckoutShopSettings)
admin.site.register(GoogleCheckoutOrder)
admin.site.register(BraintreeShopSettings)
admin.site.register(BrainTreeTransaction)