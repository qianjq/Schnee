"""
WSGI config for schnee project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os, sys
from django.core.wsgi import get_wsgi_application
from os.path import join, dirname, abspath

PROJECT_DIR = dirname(dirname(abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "schnee.settings")
application = get_wsgi_application()
