from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class Subscriber(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    business_name = models.CharField(max_length=255)
    residence_country = models.CharField(max_length=100)
    registration_date = models.DateTimeField(default=timezone.now)
    store_link = models.URLField(blank=True)
    services = models.JSONField(default=list, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscriber_profile', null=True)

    def __str__(self):
        return f"{self.full_name} - {self.business_name}"

    class Meta:
        ordering = ['-registration_date']
        db_table = 'subscribers_subscriber' 