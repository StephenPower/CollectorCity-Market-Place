# -*- coding: UTF-8 -*-
import logging
from django import forms
from auth.models import User
from django.db.models import Model
from django.db.models.query import QuerySet
from django.forms import ModelForm
from django.utils.translation import ugettext as _

from haystack.forms import SearchForm
from haystack.query import EmptySearchQuerySet

from auth.forms import UserCreationForm 
from market.models import MarketSubCategory, MarketCategory
from market_buy.models import WishListItem, Show


class WishListItemForm(ModelForm):
    
    class Meta:
        model = WishListItem
        exclude = ['marketplace', 'posted_by']
        
class ShowForm(ModelForm):
    
    class Meta:
        model = Show
        exclude = ['marketplace', 'country', 'contact_info', 'admission', 'location','time_from', 'time_to', 'owner']
        

class BuyerForm(UserCreationForm):
    email =  forms.EmailField()    


SORT_CHOICES = (
    ("relevance", _("Relevance")),                
    ("price", _("Price")),
    ("-starts_at", _("Age")),
    #("dealer", _("Dealer")),
    #("auction", _("Auction")),
    #("forsale", _("For sale")),
)

INCLUDE_CHOICES = (
    ("title", _("Item Title")),
    ("description", _("Item Description")),
    ("dealer", _("Dealer Name")),
)

VIEW_BY_CHOICES = (
    ("gallery", _("Gallery")),
    ("list", _("List")),
)


class SubCategoriesField(forms.ModelMultipleChoiceField):
    """
    A ModelMultipleChoiceField that renders an empty select input
    and validates the selected item against the MarketSubCategories.
    """


    def __init__(self, *args, **kwargs):
        kwargs.update({"required": False, "widget": forms.Select(attrs={"size": 20}),
            "queryset": MarketSubCategory.objects.none()})
        super(SubCategoriesField, self).__init__(*args, **kwargs)

    def clean(self, value):
        if value:
            try:
                subcategory = MarketSubCategory.objects.get(pk=value)
            except MarketSubCategory.DoesNotExist:
                raise forms.ValidationError(_("Choosen subcategory does not exist."))
            return subcategory

        return None


class AdvancedSearchForm(SearchForm):
    
    q = forms.CharField(max_length=200, label=_("Search for"), required=False)
    sort = forms.ChoiceField(initial="price", choices=SORT_CHOICES)

    categories = forms.ChoiceField(required=False,
        choices=MarketCategory.objects.values_list("id", "name").order_by("name"), 
        widget=forms.Select(attrs={"size": 20}))
    subcategories = SubCategoriesField()

    include = forms.MultipleChoiceField(label=_("Include In Search"), 
        required=False, widget=forms.CheckboxSelectMultiple(), 
        initial=["title", "description", "dealer"], choices=INCLUDE_CHOICES)

    from_price = forms.DecimalField(label=_("Filter By Price"), required=False)
    to_price = forms.DecimalField(label=_("to"), required=False)

    view_by = forms.ChoiceField(choices=VIEW_BY_CHOICES, widget=forms.RadioSelect(), initial="gallery")

    def __init__(self, marketplace, *args, **kwargs):
        super(AdvancedSearchForm, self).__init__(*args, **kwargs)
                
        self.fields.keyOrder = ["q", "categories", "subcategories", 
            "include", "from_price", "to_price", "sort", "view_by"]
        self.marketplace = marketplace
        
    def search(self):
        
        if self.is_valid():
            sqs = sqs = self.searchqueryset.models("inventory.Product")\
                .filter(marketplace_id=self.marketplace.id)

            q = self.cleaned_data.get("q")
            if q:
                sqs = sqs.auto_query(q)
            
            data = self.cleaned_data
            
            params_dict = {} 
            if self.cleaned_data["subcategories"]:
                # only one subcategory may get selected ;)
                params_dict.update({"subcategory_id": self.cleaned_data["subcategories"].id})

            # if we are going to filter by subcategory then filtering by category is
            # superfluous. so we check this first
            if not self.cleaned_data["subcategories"] and self.cleaned_data["categories"]: 
                # only one category may get selected too
                params_dict.update({"category_id": self.cleaned_data["categories"]})

            if self.cleaned_data["from_price"]:
                params_dict.update({"price__gte": self.cleaned_data["from_price"]})

            if self.cleaned_data["to_price"]:
                params_dict.update({"price__lte": self.cleaned_data["to_price"]})

            if params_dict:
                sqs = sqs.filter(**params_dict)

            # decide how to sort results
            sort_field = self.cleaned_data["sort"]
            if sort_field:
                if sort_field != "relevance":
                    sqs = sqs.order_by(sort_field)

            return sqs

        return EmptySearchQuerySet()


    def clean(self):
        super(AdvancedSearchForm, self).clean()
        
        data = self.cleaned_data
        
        if data.get("subcategories") and not data.get("categories"):
            raise forms.ValidationError(_("You must choose a category"))

        return data

    def _as_tuple_list(self):
        param_tuples = []
        
        if not self.cleaned_data:
            return []

        for field, value in self.cleaned_data.iteritems():
            if not value:
                continue
        
            if isinstance(value, (list, QuerySet)):
                for item in value:
                    if isinstance(item, Model):
                        param_tuples.append((field, item.pk))
                    else:
                        param_tuples.append((field, item))
            else:
                if isinstance(value, Model):
                    param_tuples.append((field, value.pk))
                else:
                    param_tuples.append((field, value))

        return param_tuples
                
    def get_qs(self):
        """
        Return the field names and values encoded in a querystring 
        so we may give the user a link to go back from results page
        to the original search form in order to refine his search
        """
        return "&".join(["%s=%s" % tuple for tuple in self._as_tuple_list()])
