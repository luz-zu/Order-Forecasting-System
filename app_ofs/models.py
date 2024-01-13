from django.db import models

from django.contrib.auth.models import AbstractUser

# models.py

class SalesData(models.Model):
    month = models.DateTimeField()
    sales = models.FloatField()


class CustomUser(AbstractUser):
    dob = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    userrole = models.CharField(max_length=15, blank=True)

class category(models.Model):
    category_id = models.CharField(max_length=100)
    category = models.CharField(max_length=100)


class products(models.Model):
    product_id = models.CharField(max_length=50)
    product_name = models.CharField(max_length=50)
    product_description =  models.CharField(max_length=200)