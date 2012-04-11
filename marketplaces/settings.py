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
#    ('name', 'email'),
)

STAFF = (
#	('name', 'email'),
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

MEDIA_URL_OUT_S3 = '/media_out_s3/'
MEDIA_ROOT_OUT_S3 = os.path.join(PROJECT_ROOT, 'media_out_s3')

STATIC_URL = '/public/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/public/admin/'


STATIC_ROOT = os.path.join(PROJECT_ROOT, 'public')

STATICFILES_DIRS = (
                   os.path.join(PROJECT_ROOT, 'static'),   
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'compressor.finders.CompressorFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware', # cache
    'django.middleware.common.CommonMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware', # cache
    'django.contrib.sessions.middleware.SessionMiddleware',
    'auth.middleware.AuthenticationMiddleware',
    'djangoflash.middleware.FlashMiddleware',
    'market.middleware.MarketPlaceMiddleware',
    'flatpages.middleware.FlatpageFallbackMiddleware',
    'pagination.middleware.PaginationMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',   
    'django.core.context_processors.static',                               
    'django.core.context_processors.request',                               
    'djangoflash.context_processors.flash',
    'market.context_processors.marketplace',
    'core.context_processors.google_key',    
    'core.context_processors.secure_media',
    'core.context_processors.media_url_ous_s3',
    'social_auth.context_processors.social_auth_by_type_backends',
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
    'django.contrib.staticfiles',
    'django.contrib.admin',    
    'django.contrib.markup', 
    'django.contrib.humanize',    

    #third
    'south',
    'uni_form',
    'haystack',
    'rollyourown.seo',
    'tinymce',
    'captcha',
    #'pipeline',
    'compressor',
    'pagination',

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
    'users',
    'flatpages',
    
    'social_auth',
)

AUTHENTICATION_BACKENDS = (
    'social_auth.backends.twitter.TwitterBackend',
    'social_auth.backends.facebook.FacebookBackend',
#    'social_auth.backends.google.GoogleOAuthBackend',
    'social_auth.backends.google.GoogleOAuth2Backend',
    'social_auth.backends.google.GoogleBackend',
    #'django.contrib.auth.backends.ModelBackend',
    'core.emailBackend.ModelBackend',
)

AUTH_PROFILE_MODULE = 'users.Profile'

LOGIN_URL = '/buy/login/'
LOGIN_REDIRECT_URL= '/redirect' 

GOOGLE_KEY = ''

DEFAULT_DNS = 'shop.com'


EMAIL_HOST = ''
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = True
EMAIL_FROM = ''

# django-haystack settings
HAYSTACK_SITECONF = "search.indexes"
HAYSTACK_SEARCH_ENGINE = "solr"
# url for solr core that will serve and index our project data
HAYSTACK_SOLR_URL = "http://127.0.0.1:8983/solr/poc"
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 16

CAPTCHA_CHALLENGE_FUNCT = 'market.captcha_generators.category_captcha'

logging.basicConfig(level=logging.INFO, format='[=%(levelname)s : %(asctime)s] %(message)s',)

THEMES_ROOT = join(ROOT_DIR, "stores", 'media', 'themes') + '/'
DEFAULT_THEME = 'default.zip'
SITE_RUNNING_MODE='marketplaces'

#Testing
SOUTH_TESTS_MIGRATE = False

LANGUAGES = (
    ('en', 'English'),
)

TINYMCE_DEFAULT_CONFIG = {
    'spellchecker_languages' : "+English=en,"
}

TINYMCE_SPELLCHECKER = True

# Bitly settings
BITLY_USERNAME = ''
BITLY_API_KEY = ''

# django-social-auth settings
TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET = ''

FACEBOOK_APP_ID = ''
FACEBOOK_API_SECRET = ''

GOOGLE_CONSUMER_KEY = ''
GOOGLE_CONSUMER_SECRET = ''

GOOGLE_OAUTH2_CLIENT_ID = ''
GOOGLE_OAUTH2_CLIENT_SECRET = ''

#LOGIN_URL = '/buy/login/'
LOGIN_REDIRECT_URL = '/'
LOGIN_ERROR_URL = '/buy/'

SOCIAL_AUTH_BACKEND_ERROR_URL = LOGIN_URL

SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/buy/profile/'

SOCIAL_AUTH_COMPLETE_URL_NAME  = 'socialauth_complete'
SOCIAL_AUTH_ASSOCIATE_URL_NAME = 'socialauth_associate_complete'

# django-social-auth: Not mandatory, but recommended
SOCIAL_AUTH_DEFAULT_USERNAME = 'new_social_auth_user'
SOCIAL_AUTH_UUID_LENGTH = 3

SOCIAL_AUTH_EXTRA_DATA = True

SOCIAL_AUTH_EXPIRATION = 'expires'

SOCIAL_AUTH_USER_MODEL = 'auth.User'

SOCIAL_AUTH_CREATE_USERS = True
SOCIAL_AUTH_ASSOCIATE_BY_MAIL = True
#SOCIAL_AUTH_SANITIZE_REDIRECTS = False

SOCIAL_AUTH_RAISE_EXCEPTIONS = DEBUG

SOCIAL_AUTH_PIPELINE = (
    'social_auth.backends.pipeline.social.social_auth_user',
    'social_auth.backends.pipeline.associate.associate_by_email',
    'social_auth.backends.pipeline.user.get_username',
    'social_auth.backends.pipeline.user.create_user',
    'social_auth.backends.pipeline.social.associate_user',
    'social_auth.backends.pipeline.social.load_extra_data',
    'social_auth.backends.pipeline.user.update_user_details',

    'market_buy.auth_pipelines.pipeline.update_user_details',
)


PAGINATION_DEFAULT_PAGINATION = 10
PAGINATION_DEFAULT_WINDOW = 5

#CACHES = {
#    'default': {
#        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#        'LOCATION': '127.0.0.1:11211',
#        'TIMEOUT': 300,
#        'KEY_PREFIX': 'dev.numismatichq.com',
#    }
#}

#CACHE_MIDDLEWARE_ALIAS = 'default'
#CACHE_MIDDLEWARE_SECONDS = 300
#CACHE_MIDDLEWARE_KEY_PREFIX = ''
#CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

try:
    from local_settings import *
except ImportError:
    pass
