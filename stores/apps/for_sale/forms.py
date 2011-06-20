from django.forms import ModelForm

from models import Item, ImageItem 
from market.models import MarketCategory


class ItemForm(ModelForm):
    
    class Meta:
        model = Item
        fields = ['title', 'description', 'price', 'subcategory', 'category', 'weight', 'qty']
    
    def __init__(self, request=None, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        # Filter sessions and categorys for specific shop 
        if request:
            self.shop = request.shop
            category = self.fields.get('category')
            category.queryset = MarketCategory.objects.filter(marketplace=self.shop.marketplace)


class ImageItemForm(ModelForm):
    class Meta:
        model = ImageItem
        fields = ['image']