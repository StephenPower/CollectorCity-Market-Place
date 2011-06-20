# Django settings for poc project.

import os.path
from os.path import abspath, dirname, join
import sys



DEBUG = False
TEMPLATE_DEBUG = DEBUG

ROOT_DIR = abspath(join(dirname(__file__), os.path.pardir))
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

##Add apps to sys.path
sys.path.insert(1, os.path.join(PROJECT_ROOT, "apps"))
sys.path.insert(2, os.path.join(ROOT_DIR, "libs"))
sys.path.insert(3, os.path.join(ROOT_DIR, 'marketplaces', "apps"))

ADMINS = (
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = os.path.join(PROJECT_ROOT, 'dev_poc.db')             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.

TIME_ZONE = 'US/Eastern'
#TIME_ZONE = 'America/Buenos_Aires'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'auth.middleware.AuthenticationMiddleware',
    'djangoflash.middleware.FlashMiddleware',
    'core.middleware.SubdomainMiddleware',
    'market.middleware.MarketPlaceMiddleware',
    'shops.middleware.CartMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'reversion.middleware.RevisionMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',                               
    'django.core.context_processors.request',                               
    'djangoflash.context_processors.flash',
    'core.context_processors.shop',    
    'core.context_processors.default_dns',    
    'core.context_processors.google_key',    
    'bidding.context_processors.search',
)


ROOT_URLCONF = 'stores.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_ROOT, "templates/"),
)

STORE_TEMPLATES = os.path.join(PROJECT_ROOT, "templates/") 

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',    

    #third
    'south',
    'uni_form',
    'haystack',
    'reversion',

    #POC
    'auth',
    'auctions',
    'blog_pages',
    'bidding',
    'category',
    'core',
    'for_sale',
    'invoices',
    'inventory',
    'lots',
    'market',
    'my_shopping',
    'payments',
    'preferences',
    'search',
    'sell',
    'shops',
    'subscriptions',
    'store_admin',
    'themes',
    'users',
    'market_buy',
    'market_community',
    'inventory',
    'store_admin'
)

AUTHENTICATION_BACKENDS = (
    #'django.contrib.auth.backends.ModelBackend',
    'core.emailBackend.ModelBackend',
)

AUTH_PROFILE_MODULE = 'users.Profile'

LOGIN_REDIRECT_URL= '/redirect' 
LOGIN_URL = '/login/'

GOOGLE_CHECKOUT_SANDBOX = False
GOOGLE_KEY = ''
GOOGLE_MARKETPLACE_KEY = ''

DEFAULT_DNS = ''


EMAIL_HOST = ""
EMAIL_PORT = 
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_USE_TLS = True
EMAIL_FROM = ''

# django-haystack settings
HAYSTACK_SITECONF = "search.indexes"
HAYSTACK_SEARCH_ENGINE = "solr"
# url for solr core that will serve and index our project data
HAYSTACK_SOLR_URL = "http://127.0.0.1:8983/solr/poc"
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 6


MERCHANT_ID=''
PUBLIC_KEY=''
PRIVATE_KEY=''

TMP_DIR = '/tmp/'

THEMES_ROOT = "%s%s" % (MEDIA_ROOT, '/themes/')
DEFAULT_THEME = 'default.zip'
SITE_RUNNING_MODE='stores'

import logging

logging.basicConfig(level=logging.DEBUG, format='[=%(levelname)s : %(asctime)s] %(message)s',)

#import sys
#logging.basicConfig(stream=sys.stdout)


#Testing
SOUTH_TESTS_MIGRATE = False


COVERAGE_MODULES = [
  'auctions.feeds',  'auctions.forms',  'auctions.models',  'auctions.views',  
  'auth.models', 'auth.views', 
  'bidding.context_processors',  'bidding.forms',  'bidding.models',  'bidding.views',
  'blog_pages.feeds', 'blog_pages.forms',  'blog_pages.models', 'blog_pages.views',
  'category.forms', 'category.models', 
  'core.context_processors', 'core.decorators', 'core.middleware', 'core.thumbs', 'core.views',
  'for_sale.feeds', 'for_sale.forms', 'for_sale.views',  
  'invoices.models', 'invoices.views',  
  'my_shopping.views',
  'preferences.forms', 'preferences.models', 'preferences.views',  
  'sell.forms', 'sell.models', 'sell.views',
  'store_admin.models', 'store_admin.views',
  'themes.forms', 'themes.models', 'themes.render', 'themes.views',
  'users.forms',  'users.models',  'users.views',
  'inventory.models', 'inventory.views',
  'lots.models',  'lots.views',
  'payments.forms', 'payments.models',  'payments.views',
  'payments.gateways.braintreegw',  'payments.gateways.googlecheckout',  'payments.gateways.paypal',
  'search.models',  'search.views',
  'shops.forms',  'shops.models',  'shops.middleware',  'shops.views',
  'subscriptions.forms', 'subscriptions.models', 'subscriptions.views',
]

TEST_RUNNER='stores.test_coverage.test_runner_with_coverage'

try:
    from local_settings import *
except ImportError:
    pass
