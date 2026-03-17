import os
import django
from django.conf import settings

# Minimal settings for testing
if not settings.configured:
    settings.configure(
        DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}},
        INSTALLED_APPS=['django.contrib.contenttypes', 'django.contrib.auth'],
    )
django.setup()
print("Django setup successful!")
