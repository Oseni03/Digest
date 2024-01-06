"""
Celery config file

https://docs.celeryproject.org/en/stable/django/first-steps-with-django.html

"""
from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings


# This code is a copy of manage.py.
# Set the "celery Django" app's default Django settings module.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# you change the name here -Django Celery
app = Celery("core")

# read configuration from Django settings, creating celery Django with the CELERY namespace
# config keys have the prefix "CELERY" Django Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# load tasks.py in django apps - Django Celery
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.result_backend_transport_options = {
    'retry_policy': {
       'timeout': 5.0
    }
}