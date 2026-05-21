from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('loging/', views.loging, name='loging'),
    path('singup/', views.singup, name='singup'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('tasker/', views.tasker, name='tasker'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.user_logout, name='logout'),
    path('worker/', include('worker.urls')),
    path('services/<str:category_name>/', views.tasker_list, name='tasker_list'),
    path('book/<int:tasker_id>/', views.book_tasker, name='book_tasker'),
    path('booking/accept/<int:booking_id>/', views.accept_booking, name='accept_booking'),
    path('booking/cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('booking/complete/<int:booking_id>/', views.complete_booking, name='complete_booking'),

    # REGISTERED THE MISSING ROUTE HERE:
    path('booking/pay/<int:booking_id>/', views.payment_page, name='payment_page'),
    path('tasker/review/<int:tasker_id>/', views.leave_review, name='leave_review'),
    path('taskers/', views.tasker_list, name='tasker_list'),
]