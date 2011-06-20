from django.contrib.syndication.views import Feed

from for_sale.models import Item

class LatestItemFeed(Feed):
    def get_object(self, request):
        return request.shop

    def title(self, obj):
        return "%s last items for sale feed" % obj.name
    
    def description(self, obj):
        return "%s updates on for sale items" % obj.name    

    def link(self, obj):
        return "http://%s/for_sale/" % obj.default_dns    

    def items(self, obj):
        return Item.objects.filter(shop = obj).order_by('-date_time')[:100]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description
    
    def item_link(self, item):
        return "http://%s%s" % (item.shop.default_dns, item.get_bidding_url())

