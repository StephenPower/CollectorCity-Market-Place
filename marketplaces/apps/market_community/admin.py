from django.contrib import admin

from market_community.models import MarketPlaceAnnouncement, FAQCategory, FAQEntry, PostEditorPick

admin.site.register(MarketPlaceAnnouncement)
admin.site.register(FAQCategory)
admin.site.register(FAQEntry)
admin.site.register(PostEditorPick)