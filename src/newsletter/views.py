from django.conf import settings
from django.shortcuts import render
from django.contrib import messages
from django.views.generic import DetailView, FormView, TemplateView, View, ListView
from django.views.generic.detail import SingleObjectMixin

from .forms import SubscriberEmailForm
from .models import Subscriber, Category, Newsletter
from .utils.email_validator import email_is_valid


# Create your views here.
class SubscribeView(FormView):
    form_class = SubscriberEmailForm
    template_name = "newsletter/newsletter_subscribe.html"
    success_url = settings.NEWSLETTER_SUBSCRIPTION_REDIRECT_URL
    
    def get_context_data(self):
        context = super().get_context_data()
        context["niche"] = self.request.tenant.name
        context["latest"] = Newsletter.objects.first()
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
            if settings.NEWSLETTER_SEND_VERIFICATION:
                subscriber.send_verification_email(created, self.request.tenant.schema_name)
            else:
                # if email_is_valid(subscriber.email_address):
                    subscriber.subscribe(self.request.tenant.schema_name)
                    default_category = Category.objects.object.filter(is_default=True)
                    if default_category.exists():
                        subscriber.categories.add(default_category.first())
                        subscriber.save()
                    self.request.session["subscriber_email"] = subscriber.email_address
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
        subscribed = self.object.subscribe(request.tenant.schema_name)
        
        context = self.get_context_data(
            object=self.object, subscribed=subscribed
        )
        if subscribed:
            request.session["subscriber_email"] = self.object.email_address
        return self.render_to_response(context)


class ThankyouView(TemplateView):
    template_name = "newsletter/thank-you.html"
    
    def get_context_data(self):
        context = super().get_context_data()
        context["send_verification"] = settings.NEWSLETTER_SEND_VERIFICATION
        return context


class SnoozeSubscription(View):
    def post(self, request, *args, **kwargs):
        email_address = request.POST.get("email")
        subscriber = Subscriber.objects.filter(email_address=email_address)
        if subscriber.exists():
            subscriber.first().snooze()
        return render(request, "newsletter/unsubscribe_successful.html", {"source": "snooze"})


class CategoriesView(ListView):
    template_name = "newsletter/categories.html"
    model = Category
    context_object_name = "categories"
    
    def get_queryset(self):
        return Category.objects.filter(is_active=True)


class CategoryDetailView(SingleObjectMixin, ListView):
    model = Newsletter
    template_name = "newsletter/category_detail.html"
    slug_url_kwarg = 'slug'
    slug_field = 'slug'
    paginate_by = 15
    context_object_name = "newsletters"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(
            queryset=Category.objects.filter(is_active=True)
        )
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.object
        context["breadcrumb"] = True
        return context

    def get_queryset(self):
        return self.object.newletters.all()


class NewsletterDetailView(DetailView):
    model = Newsletter 
    template_name = "newsletter/newsletter_detail.html"
    slug_url_kwarg = 'slug'
    slug_field = 'slug'
    context_object_name = "newsletter"
    
    def get_context_data(self):
        context = super().get_context_data()
        context["breadcrumb"] = True
        return context_object_name