from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from frontlook.models import Booking
from worker.models import TaskerProfile
from .models import Payment
import uuid


@login_required(login_url='loging')
def process_totoo_payment(request, booking_id):
    # Fetch target booking object matching active user context
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
    tasker = booking.tasker

    # Prevent processing unless status is explicitly marked 'Accepted' or 'Pending'
    if booking.status != 'Accepted' and booking.status != 'Pending':
        # If already paid, send them back to profile safely
        if booking.status == 'Paid':
            messages.info(request, "This booking has already been paid for.")
            return redirect('profile')

        messages.error(request, "Payment cannot be processed. Tasker must accept the request first.")
        return redirect('profile')

    # Dynamically extract fallback price from the tasker profile layout
    # Uses a fallback of 1500.00 if the field is empty, null, or set to 0.00
    amount_to_pay = tasker.service_price if tasker.service_price else 1500.00

    if request.method == "POST":
        inputted_tasker_id = request.POST.get('verification_tasker_id', '').strip()

        # EXTRACT THE EDITED PRICE VALUE FROM THE USER'S HTML INPUT
        custom_amount_input = request.POST.get('money_amount_sent', '').strip()

        if custom_amount_input:
            try:
                amount_to_pay = float(custom_amount_input)
            except ValueError:
                # Protects database integrity if string conversion fails
                pass

        # Security Verification: Cross-match form inputs against target dataset
        if inputted_tasker_id != tasker.totooid:
            messages.error(request,
                           "Verification Failed: Inputted Tasker ID does not match this job's assigned Tasker.")
            return render(request, 'payment/payment.html', {
                'booking': booking,
                'tasker': tasker,
                'amount_to_pay': amount_to_pay
            })

        # Generate separate tracking strings for the platform and worker ledgers
        generated_user_trx = f"TX-USER-{uuid.uuid4().hex[:8].upper()}"
        generated_tasker_trx = f"TX-TSKR-{uuid.uuid4().hex[:8].upper()}"

        # Initialize and save the payment transaction ledger record instance
        Payment.objects.create(
            booking=booking,
            service_user_role_id=request.user.profile.role_id,
            tasker_toto_id=tasker.totooid,
            money_amount_sent=amount_to_pay,
            user_transaction_id=generated_user_trx,
            tasker_transaction_id=generated_tasker_trx,
            payment_date=timezone.now() if hasattr(Payment, 'payment_date') else None
        )

        # 🚨 CRITICAL FIX: Save the actual amount to the booking model!
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