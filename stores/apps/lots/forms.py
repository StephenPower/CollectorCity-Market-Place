from django.forms import ModelForm, ModelChoiceField

from auctions.models import AuctionSession
from models import Lot, ImageLot
from market.models import MarketCategory, MarketSubCategory

class CategoryChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s" % obj.name


class LotForm(ModelForm):
    category = CategoryChoiceField(queryset = MarketCategory.objects.all())
        
    class Meta:
        model = Lot
        fields = ['title', 'description', 'starting_bid', 'reserve', 'weight', 'subcategory', 'category', 'session']
        
    
    def __init__(self, request=None, *args, **kwargs):
        super(LotForm, self).__init__(*args, **kwargs)
        # Filter sessions and categorys for specific shop 
        if request:
            import datetime
            today = datetime.datetime.today()
            self.shop = request.shop
            session = self.fields.get('session')
            session.queryset = AuctionSession.objects.filter(shop=self.shop).filter(end__gt=today)
            category = self.fields.get('category')
            category.queryset = MarketCategory.objects.filter(marketplace=self.shop.marketplace)

     

class ImageLotForm(ModelForm):
    class Meta:
        model = ImageLot
        fields = ['image']