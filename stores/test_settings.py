import os

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_ROOT, 'test_poc.db'),
        'USER': '',
        'PASSWORD': '',
        'OPTIONS': {}
    }
}
