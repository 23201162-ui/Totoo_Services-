from django.db import models
from django.contrib.auth.models import User


class TaskerProfile(models.Model):
    # Link to User
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tasker_profile')

    # Custom ID generated on save
    totooid = models.CharField(max_length=20, unique=True, blank=True)

    # Professional Details
    category = models.CharField(max_length=100, blank=True, help_text="e.g., Plumber, Electrician, Designer")
    service_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Starting price for your service (Money Demand)"
    )
    service_info = models.TextField(blank=True, help_text="Work Bio / Service Description")

    # Contact & Location
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)

    # Profile & Verification Images
    profile_pic = models.ImageField(upload_to='worker_profiles/', blank=True, null=True)
    info_image_1 = models.ImageField(upload_to='worker_docs/', blank=True, null=True)
    info_image_2 = models.ImageField(upload_to='worker_docs/', blank=True, null=True)
    info_image_3 = models.ImageField(upload_to='worker_docs/', blank=True, null=True)

    # Status & Payment
    is_approved = models.BooleanField(default=False)
    payment_receive_info = models.CharField(max_length=100, blank=True)

    def save(self, *args, **kwargs):
        # Auto-generate Totoo ID if it doesn't exist
        if not self.totooid and self.user_id:
            self.totooid = f"TOTO-W-{self.user_id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.totooid} | {self.user.username} | {self.category}"

    # --- PROPERTY METHODS FOR RATINGS & REVIEWS ---

    @property
    def average_rating(self):
        """Calculates average stars from linked reviews."""
        if hasattr(self, 'reviews'):
            reviews = self.reviews.all()
            if reviews.exists():
                avg = sum(review.rating for review in reviews) / reviews.count()
                return round(avg, 1)
        return 0.0

    @property
    def review_count(self):
        """Returns total number of reviews."""
        if hasattr(self, 'reviews'):
            return self.reviews.count()
        return 0

    @property
    def recent_review(self):
        """Returns the most recent review comment."""
        if hasattr(self, 'reviews'):
            recent = self.reviews.first()
            if recent and recent.comment:
                return recent.comment
        return None