from celery import shared_task 


@shared_task(name='newsletter.unsnooze')
def unsnooze(subscriber_id: int):
    from .models import Subscriber
    
    subscriber = Subscriber.objects.get(id=subscriber_id)
    subscriber.unsnooze()
    