from django.apps import AppConfig


class NewsletterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'newsletter'
    
    def ready(self):
        from .signals import snoozed, schedule_unsnoozing
        from .models import Subscriber
        
        snoozed.connect(schedule_unsnoozing, sender=Subscriber)