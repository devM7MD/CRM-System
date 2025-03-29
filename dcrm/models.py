from django.db import models

# Create your models here.

class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.username
