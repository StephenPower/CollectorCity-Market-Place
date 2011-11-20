from django.contrib.syndication.views import Feed

from blog_pages.models import Post

class LatestPostFeed(Feed):
    def get_object(self, request):
        return request.shop

    def title(self, obj):
        return "%s latest post feed" % obj.name
    
    def description(self, obj):
        return "updates on %s blog posts" % obj.name    

    def link(self, obj):
        return "http://%s/blog/" % obj.default_dns

    def items(self, obj):
        return Post.objects.filter(shop = obj).filter(draft=False).order_by('-date_time')[:100]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return "%s ..." % item.body[:50]
    
    def item_link(self, item):
        return "http://%s%s" % (item.shop.default_dns, item.get_bidding_url())

