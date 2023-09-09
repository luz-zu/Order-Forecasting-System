from django.db import models

from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    dob = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)

