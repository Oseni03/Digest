from django.conf import settings
from django.dispatch import Signal
from django_celery_beat.models import PeriodicTask

import datetime

from .tasks import unsnooze

# Sent after email verification is sent, with Subscriber instance
email_verification_sent = Signal()

# Sent after subscription confirmed, with Subscriber instance
subscribed = Signal()

# Sent after unsubscription is successful, with Subscriber instance
unsubscribed = Signal()

# Sent after subscription is snoozed successful, with Subscriber instance
snoozed = Signal()

# Sent after subscription is unsnoozed successfully, with Subscriber instance
unsnoozed = Signal()


def schedule_unsnoozing(sender, instance, **kwargs):
    print("Schedule unsnoozing!")
    
    now = datetime.datetime.now()
    interval = datetime.timedelta(days=settings.NEWSLETTER_SNOOZE_INTERVAL)
    
    PeriodicTask.objects.create(
        name=f"unsnoozing {instance.email_address}", 
        task=unsnooze, 
        start_time=now + interval,
        one_off=True, 
        args=(instance.id,)
    )
