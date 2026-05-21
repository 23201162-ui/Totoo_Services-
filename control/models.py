from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLES = (
        ('admin', 'Admin'),
        ('developer', 'Developer'),
        ('customer', 'Customer'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLES)
    role_id = models.CharField(max_length=50, unique=True) # e.g., EMP-101 or DEV-202

    def __str__(self):
        return f"{self.user.username} - {self.role}"