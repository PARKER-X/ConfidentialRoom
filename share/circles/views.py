from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin



from .models import Circle


# Create your views here.

class CircleCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Circle
    fields = [
        "name",
        "photo",
    ]


    
