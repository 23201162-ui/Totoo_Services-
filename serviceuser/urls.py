from django.urls import path
from . import views

urlpatterns = [
    # This matches the 'user/' path from the main config
    path('profile/', views.profile, name='profile'),
]