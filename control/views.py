from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import UserProfile
from worker.models import TaskerProfile
from payment.models import Payment  # Imports the tracking table safely

def control_login(request):
    if request.method == "POST":
        u_name = request.POST.get("username")
        p_word = request.POST.get("password")
        role = request.POST.get("role")
        role_id = request.POST.get("role_id")

        user = authenticate(request, username=u_name, password=p_word)

        if user is not None:
            user_prof = getattr(user, 'profile', None)
            if user_prof and user_prof.role == role and user_prof.role_id == role_id:
                login(request, user)
                if role == "admin":
                    return redirect("admin_dashboard")
                elif role == "developer":
                    return redirect("developer_dashboard")
                else:
                    return redirect("home")  # Redirecting customer to frontlook home
            else:
                return render(request, "control/login.html", {"error": "Invalid Role or Role ID"})
        else:
            return render(request, "control/login.html", {"error": "Invalid Credentials"})

    return render(request, "control/login.html")


def admin_dashboard(request):
    # Security Verification Check
    if not request.user.is_authenticated:
        return redirect('control_login')
    try:
        if request.user.profile.role != 'admin':
            return redirect('control_login')
    except AttributeError:
        return redirect('control_login')

    # Pull datasets dynamically, including cleanly sorted transaction records
    context = {
        'service_users': UserProfile.objects.filter(role='customer'),
        'developers': UserProfile.objects.filter(role='developer'),
        'admins': UserProfile.objects.filter(role='admin'),
        'taskers': TaskerProfile.objects.all().select_related('user'),

        # Extract transaction data history sorted from newest to oldest
        'payments_info': Payment.objects.all().order_by('-payment_date')
    }
    return render(request, 'control/admin_dashboard.html', context)


def developer_dashboard(request):
    # Security Verification Check
    if not request.user.is_authenticated:
        return redirect('control_login')
    try:
        if request.user.profile.role != 'developer':
            return redirect('control_login')
    except AttributeError:
        return redirect('control_login')

    return render(request, 'control/developer_dashboard.html', {'user': request.user})