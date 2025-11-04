from django.apps import AppConfig
from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'
