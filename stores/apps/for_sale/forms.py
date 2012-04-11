from django.forms import ModelForm, ModelChoiceField

from models import Item, ImageItem
from market.models import MarketCategory

class CategoryChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s" % obj.name

class ItemForm(ModelForm):
    category = CategoryChoiceField(queryset = MarketCategory.objects.all())
    
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

# forms.ModelSelect

class ImageItemForm(ModelForm):
    class Meta:
        model = ImageItem
        fields = ['image']
