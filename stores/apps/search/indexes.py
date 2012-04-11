# -*- coding: utf-8 -*-
from datetime import datetime

from haystack.indexes import (RealTimeSearchIndex, CharField, IntegerField,
    FloatField, DateTimeField, EdgeNgramField, DecimalField)
from haystack import site

# import models to be indexed...
from for_sale.models import Item
from auctions.models import AuctionSession
from lots.models import Lot
from inventory.models import Product
from sell.models import CartItem


class ItemIndex(RealTimeSearchIndex):
    """
    Indexes for_sale.models.Item instances
    """

    # remember to respect haystack primary field convention name!
    # by default, stored and indexed parameters are True
    summary = CharField(document=True, use_template=True)

    title = CharField(model_attr="title")
    description = CharField(model_attr="description", indexed=False, null=True)
    price = FloatField(model_attr="price", indexed=False)
#    price = DecimalField(model_attr="price", indexed=False)
    added_at = DateTimeField(model_attr="date_time", stored=False)

    shop_id = IntegerField(model_attr="shop__id", stored=False)
    shop_name = CharField(model_attr="shop__name")

    category = CharField(model_attr="category")
    subcategory = CharField(model_attr="subcategory", null=True)

    # order by:
    # * relevance == score function?
    # * added_at ASC / DESC
    # * price ASC / DESC
    # * title ASC / DESC

#    def get_queryset(self):
    def index_queryset(self):
        return Item.objects.filter(qty__gt=0)

site.register(Item, ItemIndex)

class CartItemIndex(RealTimeSearchIndex):
    summary = EdgeNgramField(model_attr='product__title', document=True)
    shop_id = IntegerField(model_attr="cart__shop__id", stored=False)
    cart_id = IntegerField(model_attr="cart__id")
    category_id = CharField(model_attr="product__category_id")
    subcategory_id = CharField(model_attr="product__subcategory_id", null=True)
    
site.register(CartItem, CartItemIndex)

class AuctionSessionIndex(RealTimeSearchIndex):
    """
    Indexes auctions.models.AuctionSession instances
    """
    # remember to respect haystack primary field convention name!
    # by default, stored and indexed parameters are True
    summary = CharField(document=True, use_template=True)

    title = CharField(model_attr="title")
    description = CharField(model_attr="description", indexed=False, null=True)

    shop_id = IntegerField(model_attr="shop__id", stored=False)
    shop_name = CharField(model_attr="shop__name")

    starts_at = DateTimeField(model_attr="start", stored=False)
    ends_at = DateTimeField(model_attr="end", stored=False)

#    def get_queryset(self):
    def index_queryset(self):
        return AuctionSession.objects.filter(start__lte=datetime.now(), end__gt=datetime.now())

site.register(AuctionSession, AuctionSessionIndex)

class LotIndex(RealTimeSearchIndex):
    """
    Indexes lots.models.Lot instances
    """

    # remember to respect haystack primary field convention name!
    # by default, stored and indexed parameters are True
    summary = CharField(document=True, use_template=True)

    title = CharField(model_attr="title")
    description = CharField(model_attr="description", indexed=False, null=True)
    state = CharField(model_attr="get_state_display")

    shop_id = IntegerField(model_attr="shop__id", stored=False)
    shop_name = CharField(model_attr="shop__name")

    category = CharField(model_attr="category")
    subcategory = CharField(model_attr="subcategory", null=True)

    added_at = DateTimeField(model_attr="date_time", stored=False)

#    def get_queryset(self):
    def index_queryset(self):
        # allow to search only active lots
        return Lot.objects.filter(state="A")

site.register(Lot, LotIndex)

class ProductIndex(RealTimeSearchIndex):
    """
    Index for inventory.models.Product
    """

    # summary template will include title, description, category name and
    # subcategory name in order to make it easy to search
    summary = CharField(document=True, use_template=True, stored=False)

    title = CharField(model_attr="title")
    description = CharField(model_attr="description", indexed=False, null=True)

    product_id = IntegerField(model_attr="id")
    category = CharField(model_attr="category__name")#, faceted=True)
    category_id = IntegerField(model_attr="category__id")
    subcategory = CharField(model_attr="subcategory__name", null=True)#, faceted=True, null=True)
    subcategory_id = IntegerField(model_attr="subcategory__id", null=True)
    price = FloatField()
#    price = DecimalField()
    image_url = CharField(null=True, indexed=True)

    marketplace_id = IntegerField(model_attr="shop__marketplace__id")

    shop_id = IntegerField(model_attr="shop__id")
    shop_name = CharField(model_attr="shop__name", indexed=False)
    shop_default_dns = CharField(model_attr="shop__default_dns", indexed=False)
    shop_currency = CharField(indexed=False)

    added_at = DateTimeField(model_attr="date_time")

    def prepare_price(self, obj):
        price = obj.child().price

        # the price of a Lot is an instance method
        if callable(price):
            return price()

        # the .price of an Item is an instance attribute
        return price

    def prepare_image_url(self, obj):
        image = obj.child().image()
        if image:
            return image.image.url_100x100
        return None

    def prepare_shop_currency(self, obj):
        return obj.shop.preference().checkout_currency

site.register(Product, ProductIndex)
