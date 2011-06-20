import decimal, logging

from django.db import models

from shops.models import Shop
from preferences.models import ShippingItem, ShippingPrice, ShippingWeight, TaxState

class ShippingCalculator():
    
    @classmethod
    def get_charge(cls, cart):
        total_price = cart.total()
        total_weight = cart.total_weight()
        total_items = cart.total_items()
        
        charge_for_price = ShippingPrice.calculate_charge(cart.shop, total_price)
        #logging.debug("Charge for price: %s" % charge_for_price)
        charge_for_weight = ShippingWeight.calculate_charge(cart.shop, total_weight)
        #logging.debug("Charge for weight: %s" % charge_for_weight)
        charge_for_items = ShippingItem.calculate_charge(cart.shop, total_items)
        #logging.debug("Charge for items: %s" % charge_for_items)
        
        #return the largest charge of available shipping methods
        maxim = max([charge_for_items, charge_for_price, charge_for_weight])
        logging.debug("Charge for shipping that will be aplied: %s" % maxim)
        
        try:
            state = cart.shippingdata.state
            tax_rate = TaxState.objects.filter(shop=cart.shop).filter(state=state).get()
            if tax_rate.apply_tax_to_shipping:
                logging.debug("Shop %s applies a tax of %s%% to shippings to %s" % (cart.shop, tax_rate.tax, state))
                tax_for_shipping = maxim * (tax_rate.tax / 100)
                return maxim + tax_for_shipping
            
        except TaxState.DoesNotExist:
            pass
        
        logging.debug("State %s don't apply taxes to shipping for shop %s" % (state, cart.shop))
        return maxim
            
        