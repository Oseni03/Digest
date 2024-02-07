from celery import shared_task 
from django.core.mail import EmailMessage, get_connection
from django.template.loader import render_to_string

from .utils.send_welcome import send_welcome_email
from .utils.feeds import Feed, get_summary, get_subject
from .models import Category, Newsletter, Subscriber

from concurrent.futures import ThreadPoolExecutor
from newspaper import Article

import datetime


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
    for feed in feeds:
        article = Article(feed["link"])
        article.download()
        article.nlp()
        feed["article_summary"] = article.summary
    
    subject = get_subject(feeds[:3])
    summary = get_summary([feed["summary"] for feed in feeds])
    
    data = {
        "summary": summary,
        "feeds": feeds,
    }
    newsletter_content = render_to_string("newsletter/email/newsletter.html", data)
    
    newsletter = Newsletter(category=category, tldr=summary, content=newsletter_content, subject=subject)
    return newsletter.save()


@shared_task(name="newsletter.generate_newsletters")
def generate_newsletters():
    categories = Category.objects.filter(is_active=True)
    with ThreadPoolExecutor() as executor:
        executor.map(generate_newsletter, categories)


@shared_task(name="newsletter.send_newsletter")
def send_newsletter():
    emails = ()
    for category in Category.objects.filter(is_active=True):
        newsletter = Newsletter.objects.filter(category=category, schedule__date=datetime.date.today()).first()
        recipient_list = [subscriber.email_address for subscriber in category.newsletters.all()]
        emails.append((newsletter.subject, newsletter.content, settings.FROM_EMAIL, recipient_list))
    return send_mass_mail(emails, fail_silently=False)