from celery import shared_task 
from django.core.mail import EmailMessage, get_connection
from django.template.loader import render_to_string

from .utils.send_welcome import send_welcome_email
from .utils.feeds import Feed, get_feeds_summary, get_subject
from .models import Category, Newsletter

from concurrent.futures import ThreadPoolExecutor


@shared_task(name='newsletter.unsnooze')
def unsnooze(subscriber_id: int):
    from .models import Subscriber
    
    subscriber = Subscriber.objects.get(id=subscriber_id)
    subscriber.unsnooze()


@shared_task(name='newsletter.welcome')
def send_welcome_email_task(niche, to_email):
    send_welcome_email(niche, to_email)


def generate_newsletter(category):
    feeds = Feed().read_feeds(category.rss_url)
    subject = get_subject(feeds[:3])
    summary = get_feeds_summary(feeds)
    
    data = {
        "summary": summary,
        "feeds": feeds,
    }
    newsletter_content = render_to_string("newsletter/email/newsletter.html", data)
    
    newsletter = Newsletter(category=category, tldr=summary, content=newsletter_content, subject=subject)
    return newsletter.save()


@shared_task(name="newsletter.generate_content")
def generate_content():
    categories = Category.objects.filter(is_active=True)
    with ThreadPoolExecutor() as executor:
        executor.map(generate_newsletter, categories)