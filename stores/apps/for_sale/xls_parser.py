# -*- coding: utf-8 -*-
import logging

from pyExcelerator import parse_xls

from for_sale.models import Item

class CoinInventoryParser():
    
    def __init__(self):
        pass
    
    def parse_xls(self, xls_file):
        for sheet_name, values in parse_xls(xls_file, 'utf8'): #'cp1251'):
            if sheet_name == "Products":
                products = [[]]
                property_keys = []
                logging.debug('Parsing Sheet = "%s"' % sheet_name.encode('cp866', 'backslashreplace'))
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
                
                return (property_keys, products)

                    