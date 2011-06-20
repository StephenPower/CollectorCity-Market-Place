from django.contrib import admin

from market_buy.models import EditorPick, Show, WishListItem, MarketPlacePick, DealerPick, BestSeller 

admin.site.register(EditorPick)
admin.site.register(BestSeller)
admin.site.register(DealerPick)
admin.site.register(MarketPlacePick)
admin.site.register(Show)
admin.site.register(WishListItem)