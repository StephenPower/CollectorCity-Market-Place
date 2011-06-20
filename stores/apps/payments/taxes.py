import decimal, logging

from django.db import models

from shops.models import Shop
from preferences.models import Preference, TaxState

class TaxCalculator():
    
    @classmethod
    def get_tax(cls, shop, state, city=None):
        try: 
            tax_rate = TaxState.objects.filter(shop=shop).filter(state=state).get()
            logging.debug("Shop %s have a tax rate of %s%% for state %s" % (shop, tax_rate.tax, state))
            return tax_rate.tax / 100
        except TaxState.DoesNotExist:
            logging.debug("No tax specified for state %s on shop %s" % (state, shop))
            return decimal.Decimal("0.0")