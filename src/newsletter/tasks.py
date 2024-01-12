from celery import shared_task 
from django.core.mail import EmailMessage, get_connection
from django.template.loader import render_to_string

from .utils.send_welcome import send_welcome_email
from .utils.feeds import Feed


@shared_task(name='newsletter.unsnooze')
def unsnooze(subscriber_id: int):
    from .models import Subscriber
    
    subscriber = Subscriber.objects.get(id=subscriber_id)
    subscriber.unsnooze()


@shared_task(name='newsletter.welcome')
def send_welcome_email_task(niche, to_email):
    send_welcome_email(niche, to_email)


@shared_task(name="newsletter.generate_content")
def generate_content(rss_url, email_template):
    feeds = Feed().read_feeds(rss_url)
    html_content = render_to_string(email_template, {"feeds": feeds})
    # Get the category with the rss_url and 
    # create a newsletter object for the category with the html content 