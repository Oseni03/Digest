from django.conf import settings
from django.shortcuts import render
from django.contrib import messages
from django.views.generic import DetailView, FormView, TemplateView, View

from .forms import SubscriberEmailForm
from .models import Subscriber


# Create your views here.
class SubscribeView(FormView):
    form_class = SubscriberEmailForm
    template_name = "newsletter/newsletter_subscribe.html"
    success_url = settings.NEWSLETTER_SUBSCRIPTION_REDIRECT_URL
    
    def get_context_data(self):
        context = super().get_context_data()
        context["niche"] = self.request.tenant.name
        return context
    
    def form_invalid(self, form):
        response = super().form_invalid(form)
        for error in form.errors.values():
            messages.error(self.request, error)
        return response
    
    def form_valid(self, form):
        email_address = form.cleaned_data.get('email_address')

        subscriber, created = Subscriber.objects.get_or_create(
            email_address=email_address
        )

        if not created and subscriber.subscribed:
            pass
            # messages.success(self.request, 'You have already subscribed to the newsletter.')
        else:
            subscriber.send_verification_email(created)
        return super().form_valid(form)


class UnsubscribeView(DetailView):
    model = Subscriber
    template_name = "newsletter/newsletter_unsubscribe.html"
    context_object_name = "subscriber"
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        context = self.get_context_data(
            object=self.object, form=SubscriberEmailForm()
        )
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = SubscriberEmailForm(request.POST)
        if form.is_valid():
            email_address = form.cleaned_data.get('email_address')
            
            subscriber = Subscriber.objects.filter(
                subscribed=True,
                email_address=email_address
            ).first()
            
            if subscriber:
                subscriber.unsubscribe()
            return render(request, "newsletter/unsubscribe_successful.html", {"source": "unsubscribe"})
        context = {
            "form": form,
            "subscriber": self.get_object()
        }
        return render(request, self.template_name, context)


class SubscriptionConfirmView(DetailView):
    template_name = "newsletter/newsletter_subscription_confirm.html"
    model = Subscriber
    slug_url_kwarg = 'token'
    slug_field = 'token'

    def get_queryset(self):
        return super().get_queryset().filter(verified=False)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        subscribed = self.object.subscribe()
        
        context = self.get_context_data(
            object=self.object, subscribed=subscribed
        )
        return self.render_to_response(context)


class ThankyouView(TemplateView):
    template_name = "newsletter/thank-you.html"


class SnoozeSubscription(View):
    def post(self, request, *args, **kwargs):
        email_address = request.POST.get("email")
        subscriber = Subscriber.objects.filter(email_address=email_address)
        if subscriber.exists():
            subscriber.first().snooze()
        return render(request, "newsletter/unsubscribe_successful.html", {"source": "snooze"})