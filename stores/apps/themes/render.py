import logging
from django.conf import settings
from jinja2 import Environment
from jinja2.loaders import BaseLoader

from models import Asset 

class AssetLoader(BaseLoader):

#    def __init__(self, shop):
#        self.shop = shop

    def __init__(self, shop, is_secure=False):
        self.shop = shop
        self.is_secure = is_secure 


    def get_source(self, environment, text):
        source = text
        path = "%s/%s" % (self.shop.name, 'asset')
        return source, path, lambda: False
    
#    def asset_url(self, name_file):
#        try:
#            asset = Asset.objects.filter(theme__shop=self.shop, name=name_file)[0]
#            return asset.file.url
#        except IndexError:
#            raise Exception("The file %s does not exist." % name_file)

    def asset_url(self, name_file):
        try:
            asset = Asset.objects.filter(theme__shop=self.shop, name=name_file)[0]
            if asset.is_editable():
                if self.is_secure:
                    return settings.SECURE_ASSET_URL + asset.assetrendering.file.name
                else:
                    return asset.assetrendering.file.url
            else:
                if self.is_secure:
                    return settings.SECURE_ASSET_URL + asset.file.name
                else:
                    return asset.file.url
        except:
            logging.error("Asset(%s) object not found" % name_file)
            return ''
        
        
def render_asset(text, shop, is_secure=False):
    env = Environment(loader=AssetLoader(shop, is_secure))
    env.filters['asset_url'] = env.loader.asset_url

#        template = env.get_template(str(self.id))
    template = env.get_template(text)
    result = template.render()

    return result