from django.db import models
from django.contrib.auth.models import User
import uuid


# --- SERVICE USER TABLE ---
class ServiceUserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='service_profile')
    toto_id = models.CharField(max_length=20, unique=True, editable=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True)

    # --- NEW FIELDS ADDED HERE ---
    work_info = models.TextField(blank=True, null=True)
    profile_pic = models.ImageField(upload_to='service_users/', blank=True, null=True)
    info_image_1 = models.ImageField(upload_to='service_docs/', blank=True, null=True)
    info_image_2 = models.ImageField(upload_to='service_docs/', blank=True, null=True)
    info_image_3 = models.ImageField(upload_to='service_docs/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.toto_id:
            self.toto_id = f"TOTO-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)


# --- DEVELOPER TABLE ---
class DeveloperProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='developer_profile')
    github_link = models.URLField(blank=True)
    specialization = models.CharField(max_length=100, blank=True, null=True, help_text="Frontend/Backend")
    is_active_dev = models.BooleanField(default=True)


# --- ADMIN TABLE (For custom Admin details) ---
class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    employee_id = models.CharField(max_length=10, unique=True)
    access_level = models.IntegerField(default=1)  # 1 for moderator, 2 for super-admin