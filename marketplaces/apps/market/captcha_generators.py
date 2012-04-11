from models import MarketCategory

def category_captcha():
    return MarketCategory.generate_captcha()
