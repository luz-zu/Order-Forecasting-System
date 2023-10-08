from django.db import models

from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    dob = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)

class category(models.Model):
    category_id = models.CharField(max_length=100)
    category = models.CharField(max_length=100)