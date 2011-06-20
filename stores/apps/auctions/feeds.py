from django.contrib.syndication.views import Feed

from auctions.models import AuctionSession

class LatestAuctionsFeed(Feed):
    def get_object(self, request):
        return request.shop

    def title(self, obj):
        return "%s last auctions feed" % obj.name
    
    def description(self, obj):
        return "updates on auctions for %s" % obj.name    

    def link(self, obj):
        return "http://%s/for_sale/" % obj.default_dns

    def items(self, obj):
        return AuctionSession.objects.filter(shop = obj).order_by('-start')[:100]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description
    
    def item_link(self, item):
        return "http://%s%s" % (item.shop.default_dns, item.get_bidding_url())

