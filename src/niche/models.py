from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.contrib.sites.models import Site
from django_tenants.models import TenantMixin, DomainMixin

# Create your models here.
class Niche(TenantMixin):
    class ScheduleChoices(models.TextChoices):
        WEEKLY = "WEEKLY", _('WEEKLY')
        DAILY = "DAILY", _('DAILY')
        MONTHLY = "MONTHLY", _('MONTHLY')
        
    name = models.CharField(max_length=150)
    schedule = models.CharField(max_length=25, choices=ScheduleChoices.choices, default=ScheduleChoices.DAILY)
    description = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=False)
    
    def get_absolute_url(self):
        url = f'{settings.HTTP_PROTOCOL}://'
        url += str(self.schema_name) + '.'
        url += Site.objects.get_current().domain
        return url


class Domain(DomainMixin):
    pass