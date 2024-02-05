from django.db import models

from django.contrib.auth.models import AbstractUser

from django.utils import timezone

class SalesData(models.Model):
    month = models.DateTimeField()
    sales = models.FloatField()


class CustomUser(AbstractUser):
    dob = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    userrole = models.CharField(max_length=15, blank=True)
    # added_by = models.IntegerField(null=True, blank=True)
    otp = models.CharField(max_length=50, null=True, blank=True)
    otp_created_at = models.CharField(max_length=50, null=True, blank=True)
    otp_verified = models.CharField(max_length=50, null=True, blank=True)
    # first_login = models.IntegerField(default=1)
    added_by = models.BigIntegerField(null=True, blank=True)

 

class category(models.Model):
    id = models.AutoField(primary_key=True)
    category_id = models.CharField(max_length=50, unique=True, null=True)
    category = models.CharField(max_length=50, null=True)
    updated_on = models.DateTimeField(auto_now=True)
    userid = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, related_name='categories')

    class Meta:
        db_table = 'category_info'
        indexes = [
            models.Index(fields=['userid']),
        ]



class Product(models.Model):
    id = models.AutoField(primary_key=True)
    product_id = models.CharField(max_length=50, unique=True, null=True)
    product_name = models.CharField(max_length=50, null=True)
    product_description = models.CharField(max_length=200, null=True)
    category = models.ForeignKey(category, on_delete=models.CASCADE, related_name='product_info')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    added_on = models.DateTimeField(auto_now_add=True) 
    updated_on = models.DateTimeField(auto_now=False, null=True)
    deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'product_info'
        indexes = [
            models.Index(fields=['user_id']),
            # models.Index(fields=['category_id']),
            # models.Index(fields=['product_name']),
            models.Index(fields=['product_id']),
        ]

    # def __str__(self):
    #     return self.product_name
    
class InventoryDetailsDate(models.Model):
    date = models.DateField()
    quantity = models.CharField(max_length=100)
    quantity_added = models.CharField(max_length =50)
    quantity_deducted = models.CharField(max_length =50)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, db_column='product_id', related_name='inventory_details_dates', to_field='product_id')

    user = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)
    price = models.CharField(max_length=50)

    class Meta:
        db_table = 'inventorydetails_date'
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['user']),
        ]

class InventoryDetails(models.Model):
    id = models.AutoField(primary_key=True) 
    quantity = models.CharField(max_length=50)
    price = models.CharField(max_length=50)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, db_column='product_id', related_name='inventorydetails', to_field='product_id')
    user = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'inventory_details'
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['user']),
        ]

class Order(models.Model):
    order_id = models.CharField(max_length=50, unique=True, null=True)
    quantity = models.CharField(max_length=50, null=True)
    ordered_date = models.DateField(null=True)
    delivery_date = models.DateField(null=True)
    completed_date = models.DateField(null=True)
    price = models.CharField(max_length=50, null=True)
    status = models.CharField(max_length=50, null=True)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, db_column='product_id', related_name='order_info', to_field='product_id')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    total_price = models.CharField(max_length=50, null=True)
    added_on = models.DateTimeField(auto_now_add=True) 
    updated_on = models.DateTimeField(auto_now=False, null=True)
    deleted_on = models.DateTimeField(auto_now=False, null=True)

    class Meta:
        db_table = 'order_info'


class ForecastData(models.Model):
    product_id = models.IntegerField(default=101)
    # user_id = models.IntegerField(default=39)
    quantity = models.IntegerField()
    ordered_date = models.DateField()
    class Meta:
        db_table = 'forecast_data'