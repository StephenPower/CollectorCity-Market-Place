from models import *
from django.contrib import admin

admin.site.register(Item, ItemAdmin)
admin.site.register(ImageItem)
admin.site.register(ImageItemURLQueue)


