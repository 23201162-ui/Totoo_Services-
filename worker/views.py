from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import TaskerProfile


@login_required(login_url='loging')
def worker_profile(request):
    # Get the profile, or create an empty one if a guest somehow got here
    tasker_profile, created = TaskerProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        # 1. Handle updating text info
        tasker_profile.phone_number = request.POST.get('phone_number', tasker_profile.phone_number)
        tasker_profile.address = request.POST.get('address', tasker_profile.address)

        # Capture the new Service Price
        tasker_profile.service_price = request.POST.get('service_price', tasker_profile.service_price)

        if hasattr(tasker_profile, 'service_info'):
            tasker_profile.service_info = request.POST.get('service_info', tasker_profile.service_info)
        if hasattr(tasker_profile, 'payment_receive_info'):
            tasker_profile.payment_receive_info = request.POST.get('payment_info', tasker_profile.payment_receive_info)

        # 2. Handle updating Images
        if 'profile_pic' in request.FILES:
            tasker_profile.profile_pic = request.FILES['profile_pic']

        if 'img1' in request.FILES:
            tasker_profile.info_image_1 = request.FILES['img1']

        if 'img2' in request.FILES:
            tasker_profile.info_image_2 = request.FILES['img2']

        if 'img3' in request.FILES:
            tasker_profile.info_image_3 = request.FILES['img3']

        # 3. Save to database and show message
        tasker_profile.save()
        messages.success(request, "Dashboard updated successfully! ✅")
        return redirect('worker_profile')

    # Pass the tasker context to the HTML
    context = {
        'tasker': tasker_profile,
        'user': request.user
    }

    return render(request, 'worker.html', context)