from celery import shared_task 

from .utils.send_welcome import send_welcome_email


@shared_task(name='newsletter.unsnooze')
def unsnooze(subscriber_id: int):
    from .models import Subscriber
    
    subscriber = Subscriber.objects.get(id=subscriber_id)
    subscriber.unsnooze()


@shared_task(name='newsletter.welcome')
def send_welcome_email_task(niche, to_email):
    send_welcome_email(niche, to_email)