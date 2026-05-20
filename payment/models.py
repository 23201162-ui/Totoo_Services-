from django.db import models
from decimal import Decimal
from frontlook.models import Booking


class Payment(models.Model):
    # Relational target link
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment_detail')

    # Identifiers (Requested strings)
    service_user_role_id = models.CharField(max_length=50, verbose_name="Service User Role ID")
    tasker_toto_id = models.CharField(max_length=50, verbose_name="Tasker Totoo ID")

    # Dual Financial Tracks
    money_amount_sent = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Amount Sent by User")
    money_amount_given = models.DecimalField(max_digits=10, decimal_places=2, editable=False,
                                             verbose_name="Amount Given to Tasker (80%)")
    platform_retained = models.DecimalField(max_digits=10, decimal_places=2, editable=False,
                                            verbose_name="Totoo Platform Cut (20%)")

    # Dual Transaction IDs
    user_transaction_id = models.CharField(max_length=100, unique=True, verbose_name="User TrxID")
    tasker_transaction_id = models.CharField(max_length=100, unique=True, verbose_name="Tasker TrxID")

    payment_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payments_info'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

    def save(self, *args, **kwargs):
        if self.money_amount_sent:
            sent_decimal = Decimal(str(self.money_amount_sent))
            # Perform clean 80/20 split calculations
            self.platform_retained = (sent_decimal * Decimal('0.20')).quantize(Decimal('0.01'))
            self.money_amount_given = (sent_decimal - self.platform_retained).quantize(Decimal('0.01'))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"User Trx: {self.user_transaction_id} -> Tasker Trx: {self.tasker_transaction_id}"