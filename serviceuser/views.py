from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import ServiceUserProfile
from payment.models import Payment
from frontlook.models import Booking


@login_required
def profile(request):
    user_profile = request.user.service_profile

    if request.method == 'POST':
        user_profile.phone_number = request.POST.get('phone')
        user_profile.address = request.POST.get('address')
        user_profile.work_info = request.POST.get('work_info')

        # Handling Image Uploads
        if request.FILES.get('profile_pic'):
            user_profile.profile_pic = request.FILES['profile_pic']

        if request.FILES.get('img1'):
            user_profile.info_image_1 = request.FILES['img1']

        if request.FILES.get('img2'):
            user_profile.info_image_2 = request.FILES['img2']

        if request.FILES.get('img3'):
            user_profile.info_image_3 = request.FILES['img3']

        user_profile.save()
        return redirect('profile')

    # DYNAMIC QUERY: Replaced static arrays with real history records matching this customer context
    real_payment_history = Payment.objects.filter(booking__customer=request.user).order_by('-id')

    # DYNAMIC QUERY: Pulls real tasker service requests assigned to this user
    real_service_history = Booking.objects.filter(customer=request.user).order_by('-id')

    context = {
        'profile': user_profile,
        'payments': real_payment_history,
        'services': real_service_history
    }
    return render(request, 'profile.html', context)