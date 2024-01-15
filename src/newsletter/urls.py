from django.urls import path 

from . import views

app_name = "newsletter"

urlpatterns = [
    path("", views.SubscribeView.as_view(), name="subscribe"),
    path("unsubscribe/<int:pk>/", views.UnsubscribeView.as_view(), name="unsubscribe"),
    path(
        'subscribe/confirm/<uuid:token>/',
        views.SubscriptionConfirmView.as_view(),
        name='newsletter_subscription_confirm'
    ),
    path("snooze-subscription/", views.SnoozeSubscription.as_view(), name="snooze-subscription"),
    path("thank-you/", views.ThankyouView.as_view(), name="thank-you"),
    path("archive/", views.ArchiveView.as_view(), name="archive"),
    path("archive/<slug:slug>/", views.NewsletterDetailView.as_view(), name="newsletter-detail"),

]