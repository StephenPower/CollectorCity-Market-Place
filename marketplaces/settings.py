# Django settings for poc project.
import logging
import os.path
import sys

from os.path import abspath, dirname, join

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ROOT_DIR = abspath(join(dirname(__file__), os.path.pardir))
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

##Add apps to sys.path
sys.path.insert(1, os.path.join(ROOT_DIR, "marketplaces", "apps"))
sys.path.insert(2, os.path.join(ROOT_DIR, "stores", "apps"))
sys.path.insert(3, os.path.join(ROOT_DIR, "libs"))
sys.path.insert(4, ROOT_DIR)


ADMINS = (
    ('Sebastian', 'sebastian@devsar.com'),
    ('Steve', 'stephenpatrickpower@gmail.com')
)

STAFF = (
    ('Steve Admin', 'admin@greatcoins.com'),
    ('Steve Alias', 'steve@greatcoins.com'),
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

#TIME_ZONE = 'US/Eastern'
TIME_ZONE = 'America/Buenos_Aires'

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
SECRET_KEY = 'v9hgn924#r($b!-t&05+4_!w5gu%dmo%o^fh=4wk618ni=3%sy'

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
    'market.middleware.MarketPlaceMiddleware'
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',                               
    'django.core.context_processors.request',                               
    'djangoflash.context_processors.flash',
    'market.context_processors.marketplace',
    'core.context_processors.google_key',    
    'core.context_processors.secure_media',
)


ROOT_URLCONF = 'marketplaces.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_ROOT, "templates/"),
    #os.path.join(ROOT_DIR, "stores", "templates/"),
)

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',    

    #third
    'south',
    'uni_form',
    'haystack',
    'rollyourown.seo',

    #POC
    'auth',
    'auctions',
    'blog_pages',
    'core',
    'lots', 
    'for_sale',
    'market',
    'market_import',
    'market_buy',
    'market_community',
    'market_sell',
    'reports',
    'support',
    'inventory',
    'payments',
    'preferences',
    'reversion',
    'sell',
    'search',
    'subscriptions',
    'shops',
    'themes',
    'users'
)

AUTHENTICATION_BACKENDS = (
    #'django.contrib.auth.backends.ModelBackend',
    'core.emailBackend.ModelBackend',
)

AUTH_PROFILE_MODULE = 'users.Profile'

LOGIN_URL = '/buy/login/'
LOGIN_REDIRECT_URL= '/redirect' 

GOOGLE_KEY = 'ABQIAAAAyzeHb2pW9itVqg6nabu-OxTXCAfJ5xohYoj4xmeFNYA-r64HsxTDZtuI70-4l5S44ZnehIPzKxMNXQ'

DEFAULT_DNS = 'shop.com'


EMAIL_HOST = ""
EMAIL_PORT = 587
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_USE_TLS = True
EMAIL_FROM = ''

# django-haystack settings
HAYSTACK_SITECONF = "search.indexes"
HAYSTACK_SEARCH_ENGINE = "solr"
# url for solr core that will serve and index our project data
HAYSTACK_SOLR_URL = "http://127.0.0.1:8983/solr/poc"
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 16


logging.basicConfig(level=logging.INFO, format='[=%(levelname)s : %(asctime)s] %(message)s',)

THEMES_ROOT = join(ROOT_DIR, "stores", 'media', 'themes') + '/'
DEFAULT_THEME = 'default.zip'
SITE_RUNNING_MODE='marketplaces'

#Testing
SOUTH_TESTS_MIGRATE = False

try:
    from local_settings import *
except ImportError:
    pass