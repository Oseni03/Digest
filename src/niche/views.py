from django.shortcuts import render
from django.views.generic import ListView

from .models import Niche

# Create your views here.
class HomeView(ListView):
    model = Niche
    context_object_name = "niches"
    template_name="niche/home.html"
    
    def get_queryset(self):
        return super().get_queryset().filter(is_public=False)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["home"] = True
        return context 