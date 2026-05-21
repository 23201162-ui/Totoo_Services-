from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import ServiceUserProfile

@receiver(post_save, sender=User)
def create_service_user_profile(sender, instance, created, **kwargs):
    if created:
        ServiceUserProfile.objects.create(user=instance)