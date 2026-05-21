from django.urls import path
from . import views

urlpatterns = [
    path('', views.control_login, name='control_login'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('developer-dashboard/', views.developer_dashboard, name='developer_dashboard'),
]