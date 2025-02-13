from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.conf import settings
from django.apps import apps  # ✅ Lazy import
import random, string
from .models import CustomUser

def generate_random_password(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

@receiver(post_save, sender=CustomUser)  # ✅ Initially set sender=None
def send_dashboard_email(sender, instance, created, **kwargs):
    
    if created:  # ✅ Ensure this runs only when a user is created
        
        if instance.role and instance.role.role_name == "Shop_Owner":
            
            temp_password = generate_random_password()
            instance.password = make_password(temp_password)
            instance.save()

            dashboard_link = f"http://127.0.0.1:8000/dashboard/shop-owner/{instance.username}/change-password/"
            

            subject = "Your Shop Owner Dashboard Access"
            message = f"""
            Dear {instance.username},

            Your Shop Owner account has been created successfully!

            🌐 Dashboard Link: {dashboard_link}
            🔑 Username: {instance.username}
            🔒 Temporary Password: {temp_password}

            Please log in and change your password as soon as possible.

            Regards,
            Your Company
            """

            send_mail(subject, message, settings.EMAIL_HOST_USER, [instance.email], fail_silently=False)
            