import uuid
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.conf import settings

from ckeditor.fields import RichTextField

from . import signals
from .tasks import send_welcome_email_task
from .utils.send_verification import send_subscription_verification_email
from .querysets import SubscriberQuerySet


# Create your models here.
class Subscriber(models.Model):
    email_address = models.EmailField(unique=True)
    token = models.CharField(max_length=128, unique=True, default=uuid.uuid4)
    verified = models.BooleanField(default=False)
    subscribed = models.BooleanField(default=False)
    snoozed = models.BooleanField(default=False)
    verification_sent_date = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = SubscriberQuerySet.as_manager()

    def __str__(self):
        return self.email_address

    def token_expired(self):
        if not self.verification_sent_date:
            return True

        expiration_date = (
            self.verification_sent_date + timezone.timedelta(
                days=settings.NEWSLETTER_EMAIL_CONFIRMATION_EXPIRE_DAYS
            )
        )
        return expiration_date <= timezone.now()

    def reset_token(self):
        unique_token = str(uuid.uuid4())

        while self.__class__.objects.filter(token=unique_token).exists():
            unique_token = str(uuid.uuid4())

        self.token = unique_token
        self.save()

    def subscribe(self, niche):
        if not settings.NEWSLETTER_SEND_VERIFICATION or not self.token_expired():
            self.verified = True
            self.subscribed = True
            self.save()

            signals.subscribed.send(
                sender=self.__class__, instance=self
            )
            send_welcome_email_task.delay(niche, self.email_address)
            return True
    
    def unsubscribe(self):
        if self.subscribed:
            self.subscribed = False
            self.verified = False
            self.categories.clear()
            self.save()

            signals.unsubscribed.send(
                sender=Subscriber, instance=self
            )

            return True

    def snooze(self):
        if not self.snoozed:
            self.snoozed = True
            self.categories.update(is_active=False)
            self.categories.save()
            self.save()

            signals.snoozed.send(
                sender=self.__class__, instance=self
            )
            return True
    
    def unsnooze(self):
        if self.snoozed:
            self.snoozed = False
            self.categories.filter(is_active=False).update(is_active=True)
            self.categories.save()
            self.save()

            signals.unsnoozed.send(
                sender=self.__class__, instance=self
            )
            return True
    
    def send_verification_email(self, created, niche):
        minutes_before = timezone.now() - timezone.timedelta(minutes=5)
        sent_date = self.verification_sent_date

        # Only send email again if the last sent date is five minutes earlier
        if sent_date and sent_date >= minutes_before:
            return

        if not created:
            self.reset_token()

        self.verification_sent_date = timezone.now()
        self.save()

        send_subscription_verification_email(
            self.get_verification_url(), 
            self.email_address,
            niche
        )
        signals.email_verification_sent.send(
            sender=self.__class__, instance=self
        )

    def get_verification_url(self):
        return reverse(
            'newsletter:newsletter_subscription_confirm',
            kwargs={'token': self.token}
        )


class Category(models.Model):
    name = models.CharField(max_length=150)
    rss_url = models.URLField(null=True, blank=True)
    slug = models.SlugField(null=True, blank=True)
    is_default = models.BooleanField(default=True)
    subscribers = models.ManyToManyField(Subscriber, related_name="categories", through="Subscription")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_absolute_url(self):
        return reverse("newsletter:category-detail", args=(self.slug,))


class Newsletter(models.Model):
    category = models.ForeignKey(Category, related_name="newletters", on_delete=models.SET_NULL, null=True)
    subject = models.CharField(max_length=255)
    content = RichTextField()
    schedule = models.DateTimeField(blank=True, null=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField()
    
    def __str__(self):
        return str(self.subject)
    
    class Meta:
        ordering = ["-created_at"]
    
    def get_absolute_url(self):
        return reverse("newsletter:newsletter-detail", args=(self.category.slug, self.slug,))


class Subscription(models.Model):
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE, related_name="subscriptions")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subscriptions")
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        models.UniqueConstraint(
            name="unique_category_subscriber",
            fields=["subscriber", "category"]
        )