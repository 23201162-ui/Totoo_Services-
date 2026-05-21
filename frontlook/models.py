from django.db import models
from django.contrib.auth.models import User
from worker.models import TaskerProfile  # Importing the Tasker model

class Review(models.Model):
    tasker = models.ForeignKey(TaskerProfile, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], help_text="Rating from 1 to 5")
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # This ensures the newest reviews always show up first
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.rating} Stars by {self.customer.first_name} for {self.tasker.user.first_name}"


class Booking(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_bookings')
    tasker = models.ForeignKey(TaskerProfile, on_delete=models.CASCADE, related_name='received_bookings')

    service_details = models.TextField(help_text="Describe exactly what you need help with")
    booking_date = models.DateField()
    booking_time = models.TimeField()
    address = models.TextField(help_text="Where should the tasker go?")

    # Saves the exact amount the customer paid so your ledger never shows 0.00
    price_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Paid', 'Paid'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def gross_price(self):
        """Uses the locked-in price if paid, otherwise previews the tasker's set price."""
        if self.price_paid:
            return float(self.price_paid)
        elif self.tasker and self.tasker.service_price:
            return float(self.tasker.service_price)
        return 0.00

    @property
    def tasker_earnings(self):
        """Calculates 80% net split."""
        return self.gross_price * 0.80

    def __str__(self):
        return f"Booking by {self.customer.first_name} for {self.tasker.user.first_name} - {self.status}"