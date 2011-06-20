import datetime
import logging
import decimal

from django.core.management.base import BaseCommand, CommandError

from pyExcelerator import parse_xls


from market.models import MarketPlace, MarketCategory, MarketSubCategory
from django.template.defaultfilters import slugify


def clean_subcategory(subcategory):   
    subcategory = subcategory.replace("Colonials - ", "").strip()
    if '-' in subcategory:
        x, y = subcategory.split('-', 1)
        x = x.strip()
        y = y.strip()
        if x == y:
            return x

    return subcategory

class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        from inventory.models import Coin
        marketplace = MarketPlace.objects.get(slug="greatcoins")
        today = datetime.datetime.today()
        spreadsheet = open(args[0], 'r')

        for sheet_name, values in parse_xls(spreadsheet, 'utf8'): #'cp1251'):
            if sheet_name == "Sheet1" or sheet_name == "Sheet2":
                products = [[]]
                property_keys = []
                print ('Parsing Sheet = "%s"' % sheet_name.encode('cp866', 'backslashreplace'))
                for row_idx, col_idx in sorted(values.keys()):
                    if row_idx == 0: 
                        property_keys.append(values[(row_idx, col_idx)])
                        continue
                    v = values[(row_idx, col_idx)]
                    if isinstance(v, unicode): v = v.encode('utf8') #'cp866', 'backslashreplace')
                    else: v = str(v)
                    
                    last_row, last_col = len(products), len(products[-1])
                    while last_row < row_idx:
                        products.extend([[]])
                        last_row = len(products)
                
                    while last_col < col_idx:
                        products[-1].extend([''])
                        last_col = len(products[-1])
                    products[-1].extend([v])
                print (property_keys)
                
                
                sort_order_idx = 14
                sub_category_idx = 2
                category_idx = 1
                subcategories = set()
                categories = set()
                category_tree = {}
                
                category_objs = {}
                subcategory_objs = {}
                
                counter = 0
                for i, product in enumerate(products[1:]):
                    line = i + 3
#                    counter += 1
#                    if counter == 600: break
                    if len(product) < 6:
                        print "Line %d: invalid row" % (line)
                        continue
                    
                    try:
                        pcgs_number = int(decimal.Decimal(product[5]))
                    except ValueError:
                        print "Line %d : invalid PCGS" % (line)
                        continue
                    except Exception,e:
                        print "Line %d, %s. Could not recognize PCGS Number, line will not be saved.\n >> %s" % ((line), e, product)
                        continue
                    
                    if len(product) < sub_category_idx + 1:
                        print "Line %d: sub category is missing" % (line)
                        continue
                    
                    if len(product) < 15:
                        print "Line %d: sort order value don't exist. line will not be saved.\n >> %s" % (line, product)
                        continue
                        
                    category = product[category_idx]
                    subcategory = clean_subcategory(product[sub_category_idx])
                    if category == '':
                        print "Line %d: category is missing" % (line)
                        print product
                        continue

                    if category == "Hawaii": 
                        print "Line %d: Hawaii category found, break." % (line)
                        break
                    
                    category_obj = category_objs.get(category, None)
                    if category_obj is None:
                        try: 
                            category_obj = MarketCategory.objects.get(slug=slugify(category))
                        except MarketCategory.DoesNotExist:
                            category_obj = MarketCategory.objects.get_or_create(marketplace=marketplace, name=category)[0]
                        category_objs[category] = category_obj
                    
                    if subcategory == '':
                        subcategory_obj = None
                    else:
                        subcategory_obj = subcategory_objs.get(category + '_' + subcategory, None)  
                        if subcategory_obj is None:
                            try:
                                subcategory_obj = MarketSubCategory.objects.get(parent=category_obj, slug=slugify(subcategory))
                            except MarketSubCategory.DoesNotExist:
                                subcategory_obj = MarketSubCategory.objects.get_or_create(marketplace=marketplace,
                                                                                          parent=category_obj, 
                                                                                          name=subcategory)[0]
                            subcategory_objs[category + '_' + subcategory] = subcategory_obj
                            category_tree.setdefault(category, set())
                            category_tree[category].add(subcategory)
                    
                    coin, created = Coin.objects.get_or_create(pcgs_number=pcgs_number)
                    
                    if not created: #and today < coin.last_update:
                        #already updated today
                        #print "Line %d: coin already saved. %s" % (line, coin)
                        continue
                    
                    coin.category = category_obj
                    coin.subcategory = subcategory_obj
                    coin.country_code = 'us'
                    coin.pcgs_number = pcgs_number
                    coin.description = product[6]
                    coin.year_issued = product[7]
                    coin.actual_year = product[8]
                    coin.denomination = product[9]
                    coin.major_variety = product[10]
                    coin.die_variety = product[11]
                    coin.prefix = product[12]
                    coin.suffix = product[13]
                    if len(product) > 14:
                        coin.sort_order = product[14]
                    coin.heading = subcategory
                    if len(product) > 16:
                        coin.holder_variety = product[16]
                    if len(product) > 17:
                        coin.holder_variety_2 = product[17]
                    if len(product) > 18:
                        coin.additional_data = product[18]
                    coin.save()
