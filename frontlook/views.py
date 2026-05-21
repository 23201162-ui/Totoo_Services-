import uuid
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Avg, Count

from control.models import UserProfile
from serviceuser.models import ServiceUserProfile
from worker.models import TaskerProfile
from payment.models import Payment
from .models import Booking, Review


def home(request):
    return render(request, 'home.html')


def loging(request):
    # If they are already logged in and visit the login page
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.is_staff:
            return redirect('/admin/')

        if TaskerProfile.objects.filter(user=request.user).exists():
            return redirect('worker_profile')

        return redirect('profile')

    if request.method == "POST":
        u_name = request.POST.get('username')
        p_word = request.POST.get('password')

        if not User.objects.filter(username=u_name).exists():
            messages.warning(request, "Account not found. Please sign up first!")
            return redirect('singup')

        user = authenticate(request, username=u_name, password=p_word)

        if user is not None:
            # ✨ FIXED: Explicitly define the backend to resolve the allauth conflict
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            if user.is_superuser or user.is_staff:
                messages.success(request, "Welcome Admin!")
                return redirect('/admin/')

            elif TaskerProfile.objects.filter(user=user).exists():
                return redirect('worker_profile')

            else:
                return redirect('profile')
        else:
            messages.error(request, "Incorrect password. Please try again.")
            return redirect('loging')

    return render(request, 'loging.html')


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('loging')

    if request.user.is_superuser or request.user.is_staff:
        return redirect('/admin/')

    try:
        if TaskerProfile.objects.filter(user=request.user).exists():
            return redirect('worker_profile')
    except Exception:
        pass

    return redirect('profile')


def singup(request):
    if request.method == "POST":
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role', 'customer')

        tasker_category = request.POST.get('category', '')

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, 'singup.html')

        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=full_name
            )

            role_id_gen = f"{role[:3].upper()}-{user.pk}"
            UserProfile.objects.get_or_create(
                user=user,
                defaults={'role': role, 'role_id': role_id_gen}
            )

            if role == 'customer':
                ServiceUserProfile.objects.get_or_create(user=user)
            elif role == 'tasker':
                TaskerProfile.objects.get_or_create(
                    user=user,
                    defaults={'category': tasker_category}
                )
            elif role == 'admin':
                user.is_staff = True
                user.save()

            # ✨ FIXED: Added the backend argument here as well!
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            if role == 'tasker':
                messages.success(request, "Welcome! Let's complete your Tasker Dashboard.")
                return redirect('worker_profile')
            else:
                messages.success(request, "Welcome! Your account has been created.")
                return redirect('profile')

        except Exception as e:
            messages.error(request, f"Error: {e}")
            return render(request, 'singup.html')

    return render(request, 'singup.html')


def tasker(request):
    return render(request, 'tasker.html')


@login_required(login_url='loging')
def profile(request):
    if request.user.is_superuser or request.user.is_staff:
        return redirect('/admin/')

    try:
        is_tasker = TaskerProfile.objects.filter(user=request.user).exists()
    except Exception:
        is_tasker = False

    if is_tasker:
        return redirect('worker_profile')

    try:
        service_profile = ServiceUserProfile.objects.get(user=request.user)
    except ObjectDoesNotExist:
        service_profile = None

    my_bookings = Booking.objects.filter(customer=request.user).order_by('-id')

    context = {
        'profile': service_profile,
        'user': request.user,
        'bookings': my_bookings,
    }
    return render(request, 'profile.html', context)


def services(request):
    return render(request, 'services.html')


# ✅ UPDATED: Supports URL parameters as well as dynamic query string filtering (?q=...)
def tasker_list(request, category_name=None):
    # Check if a search term was submitted via the search bar query parameter 'q'
    search_query = request.GET.get('q')
    if search_query:
        category_name = search_query

    # Filter with case-insensitive containment matching if any search criteria exists
    if category_name:
        raw_taskers = TaskerProfile.objects.filter(category__icontains=category_name)[:5]
    else:
        raw_taskers = TaskerProfile.objects.all()[:5]
        category_name = "All Services"

    taskers_with_reviews = []

    for tasker in raw_taskers:
        tasker_reviews = tasker.reviews.all()
        count_val = tasker_reviews.count()

        avg_val = tasker_reviews.aggregate(Avg('rating'))['rating__avg']
        avg_rating = round(avg_val, 1) if avg_val else "0.0"

        # Exclude blank comments so we only fetch a review if they actually typed something
        latest_review_obj = tasker_reviews.exclude(comment__exact='').first()
        recent_comment = latest_review_obj.comment if latest_review_obj else None

        taskers_with_reviews.append({
            'object': tasker,
            'review_count': count_val,
            'average_rating': avg_rating,
            'recent_review': recent_comment
        })

    context = {
        'taskers_data': taskers_with_reviews,
        'category': category_name
    }
    return render(request, 'tasker_list.html', context)


@login_required(login_url='loging')
def book_tasker(request, tasker_id):
    tasker = get_object_or_404(TaskerProfile, id=tasker_id)

    # Fetch review stats for the booking page
    reviews = tasker.reviews.all()
    review_count = reviews.count()
    avg_val = reviews.aggregate(Avg('rating'))['rating__avg']
    average_rating = round(avg_val, 1) if avg_val else "0.0"

    if request.method == 'POST':
        service_details = request.POST.get('service_details')
        booking_date = request.POST.get('booking_date')
        booking_time = request.POST.get('booking_time')
        address = request.POST.get('address')

        Booking.objects.create(
            customer=request.user,
            tasker=tasker,
            service_details=service_details,
            booking_date=booking_date,
            booking_time=booking_time,
            address=address
        )

        messages.success(request, f"Your booking request has been sent to {tasker.user.first_name}!")
        return redirect('services')

    context = {
        'tasker': tasker,
        'reviews': reviews[:5],  # Show only the 5 most recent reviews
        'review_count': review_count,
        'average_rating': average_rating
    }
    return render(request, 'book_tasker.html', context)


def about(request):
    return render(request, 'about.html')


def user_logout(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('loging')


@login_required(login_url='loging')
def accept_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if booking.tasker.user == request.user:
        booking.status = 'Accepted'
        booking.save()
        messages.success(request, "Job accepted! Get ready to work.")
    return redirect('worker_profile')


@login_required(login_url='loging')
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if booking.tasker.user == request.user:
        booking.status = 'Cancelled'
        booking.save()
        messages.warning(request, "Job request declined.")
    return redirect('worker_profile')


@login_required(login_url='loging')
def complete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if booking.tasker.user == request.user:
        booking.status = 'Completed'
        booking.save()
        messages.success(request, "Job marked as completed! Great work.")
    return redirect('worker_profile')


@login_required(login_url='loging')
def payment_page(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    tasker = booking.tasker

    amount_to_pay = tasker.service_price if tasker.service_price else 1500.00

    if request.method == 'POST':
        custom_amount_input = request.POST.get('money_amount_sent', '').strip()
        if custom_amount_input:
            try:
                amount_to_pay = float(custom_amount_input)
            except ValueError:
                pass

        generated_user_trx = f"TX-USER-{uuid.uuid4().hex[:8].upper()}"
        generated_tasker_trx = f"TX-TSKR-{uuid.uuid4().hex[:8].upper()}"

        Payment.objects.create(
            booking=booking,
            service_user_role_id=request.user.profile.role_id,
            tasker_toto_id=tasker.totooid,
            money_amount_sent=amount_to_pay,
            user_transaction_id=generated_user_trx,
            tasker_transaction_id=generated_tasker_trx,
            payment_date=timezone.now()
        )

        booking.price_paid = amount_to_pay
        booking.status = 'Paid'
        booking.save()

        messages.success(request, f"Payment Verified Successfully! TrxID: {generated_user_trx}")
        return redirect('profile')

    return render(request, 'payment/payment.html', {
        'booking': booking,
        'tasker': tasker,
        'amount_to_pay': amount_to_pay
    })


@login_required(login_url='loging')
def leave_review(request, tasker_id):
    tasker = get_object_or_404(TaskerProfile, id=tasker_id)

    # Fetch review stats so users can see what others said before writing theirs
    reviews = tasker.reviews.all()
    review_count = reviews.count()
    avg_val = reviews.aggregate(Avg('rating'))['rating__avg']
    average_rating = round(avg_val, 1) if avg_val else "0.0"

    if request.method == 'POST':
        rating_score = request.POST.get('rating')
        text_feedback = request.POST.get('comment', '').strip()

        if not rating_score:
            messages.error(request, "Please choose a rating level using the stars.")
            return render(request, 'leave_review.html', {
                'tasker': tasker, 'reviews': reviews[:5],
                'review_count': review_count, 'average_rating': average_rating
            })

        Review.objects.create(
            tasker=tasker,
            customer=request.user,
            rating=int(rating_score),
            comment=text_feedback
        )

        messages.success(request, f"Review submitted for {tasker.user.first_name}!")
        return redirect('tasker_list', category_name=tasker.category)

    context = {
        'tasker': tasker,
        'reviews': reviews[:5],
        'review_count': review_count,
        'average_rating': average_rating
    }
    return render(request, 'leave_review.html', context)