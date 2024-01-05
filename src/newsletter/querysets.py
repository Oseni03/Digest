from django.db import models
from django.utils import timezone


class SubscriberQuerySet(models.QuerySet):

    use_for_related_fields = True

    def subscribed(self):
        return self.filter(verified=True, subscribed=True)
