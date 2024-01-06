# init.py - django redis
# Let's keep modifying django_celery_example/__init__.py

from __future__ import absolute_import, unicode_literals

# The application will always be imported as a result of this.
#Django launches so that shared taskS can use this application.- django redis

from .celery import app as celery_app

__all__ = ('celery_app',)