from models import *
from django.contrib import admin

admin.site.register(Coin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductType)