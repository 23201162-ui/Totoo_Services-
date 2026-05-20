from django.urls import path
from . import views

urlpatterns = [
    # This matches the route signature required by your profile template tag
    path('checkout/<int:booking_id>/', views.process_totoo_payment, name='process_totoo_payment'),
]