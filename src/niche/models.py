from django.db import models
from django_tenants.models import TenantMixin, DomainMixin

# Create your models here.
class Niche(TenantMixin):
    name = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)


class Domain(DomainMixin):
    pass