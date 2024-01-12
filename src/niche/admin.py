from django.contrib import admin
from django_tenants.admin import TenantAdminMixin

from .models import Niche

# Register your models here.
@admin.register(Niche)
class NicheAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'created_at')
