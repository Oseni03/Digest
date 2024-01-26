from django_tenants.management.commands import BaseTenantCommand
from django.core.management.base import CommandError

import uuid
import random
from faker import Faker
from django.core.management.base import BaseCommand
from newsletter.models import Subscriber, Category, Newsletter, Subscription

fake = Faker()

class Command(BaseCommand):
    help = 'Generate dummy data for testing the newsletter application'
    COMMAND_NAME = "load_dummy"

    def handle(self, *args, **options):
        self.generate_subscribers(5)
        self.stdout.write(self.style.SUCCESS('Dummy subscribers generated successfully.'))
        
        self.generate_categories(5)
        self.stdout.write(self.style.SUCCESS('Dummy categories generated successfully.'))

        subscribers = Subscriber.objects.all()
        categories = Category.objects.all()

        self.generate_newsletters(20, categories)
        self.stdout.write(self.style.SUCCESS('Dummy newsletters generated successfully.'))
        
        self.generate_subscriptions(30, subscribers, categories)
        self.stdout.write(self.style.SUCCESS('Dummy subscriptions generated successfully.'))

        self.stdout.write(self.style.SUCCESS('Dummy data generated successfully.'))

    def generate_subscribers(self, num_subscribers):
        subscribers = []
        for _ in range(num_subscribers):
            subscriber = Subscriber(
                email_address=fake.email(),
                token=str(uuid.uuid4()),
                verified=True,
                subscribed=True,
                snoozed=False,
                verification_sent_date=fake.date_time_this_decade(),
            )
            subscribers.append(subscriber)
        Subscriber.objects.bulk_create(subscribers)
        return # Clear the internal state of the Faker instance

    def generate_categories(self, num_categories):
        categories = []
        for _ in range(num_categories):
            category = Category(
                name=fake.word(),
                slug=fake.slug(),
                is_default=False,
                is_active=True,
            )
            categories.append(category)
        Category.objects.bulk_create(categories)
        return

    def generate_newsletters(self, num_newsletters, categories):
        newsletters = []
        for _ in range(num_newsletters):
            newsletter = Newsletter(
                category=random.choice(categories),
                subject=fake.sentence(),
                content=fake.paragraph(),
                schedule=fake.date_time_this_decade(),
                sent_at=fake.date_time_this_decade(),
                slug=fake.slug(),
            )
            newsletters.append(newsletter)
        Newsletter.objects.bulk_create(newsletters)
        return

    def generate_subscriptions(self, num_subscriptions, subscribers, categories):
        subscriptions = []
        for _ in range(num_subscriptions):
            subscription = Subscription(
                subscriber=random.choice(subscribers),
                category=random.choice(categories),
                joined_at=fake.date_time_this_decade(),
                is_active=True,
            )
            subscriptions.append(subscription)
        Subscription.objects.bulk_create(subscriptions)
        return