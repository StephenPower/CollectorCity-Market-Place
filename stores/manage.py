#!/usr/bin/env python
# Django settings for poc project.

import os.path
from os.path import abspath, dirname, join
import sys


ROOT_DIR = abspath(join(dirname(__file__), os.path.pardir))
PROJECT_ROOT = abspath(dirname(__file__))

ZIPS_DIR = os.path.join(ROOT_DIR, "zip-packages")


for zip in os.listdir(ZIPS_DIR):
    if (os.path.splitext(zip)[1] == '.zip'):
        sys.path.insert(2, os.path.join(ZIPS_DIR, zip))

from django.core.management import execute_manager
try:
    import settings # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

if __name__ == "__main__":
    execute_manager(settings)
