# -*- coding: utf-8 -*-
import logging
from django import forms
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _

from haystack.forms import SearchForm
from haystack.query import SearchQuerySet

from for_sale.models import Item
from lots.models import Lot

class BidForm(forms.Form):
    amount = forms.DecimalField(required=True)

    def __init__(self, lot=None, *args, **kwargs):
        self.lot = lot
        super(BidForm, self).__init__(*args, **kwargs)

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount < self.lot.next_bid_from():
            raise forms.ValidationError(_("Enter US $%s or more" % str(self.lot.next_bid_from())))
        return amount


class BiddingSearchForm(SearchForm):
    """
    Bidding search form made easy for using at views
    """
    
    # redefine q field so label is empty and it has an initial value :P
    q = forms.CharField(required=False, label="", initial=_("search..."))

    MODEL_LIST = [("%s.%s" % (model._meta.app_label, model._meta.module_name)) 
        for model in (Lot, Item)] 

    def __init__(self, shop=None, *args, **kwargs):
        super(BiddingSearchForm, self).__init__(*args, **kwargs)
        self.shop = shop

    def get_query(self):
        return self.cleaned_data["q"]

    def search(self):
        from inventory.models import Product

        sqs = SearchQuerySet().models(Product).load_all()
        sqs = sqs.filter(shop_id=self.shop.id)
        
        if self.get_query():
            sqs = sqs.filter(summary=self.get_query())
        
        return sqs
        
    def all_results(self):
        from inventory.models import Product
        
        sqs = SearchQuerySet().load_all().models(Product)
        sqs = sqs.filter(shop_id=self.shop.id)
        
        return sqs
        
        
        