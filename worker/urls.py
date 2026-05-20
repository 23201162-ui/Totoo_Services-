# worker/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # This will be accessed via /worker/dashboard/
    path('dashboard/', views.worker_profile, name='worker_profile'),
]