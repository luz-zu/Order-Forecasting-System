from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from app_ofs.models import Order, Product
from django.db.models import Count

class Command(BaseCommand):
    help = 'Update product statistics for the last week'

    def handle(self, *args, **kwargs):
        # Calculate the start and end dates for the last week
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=7)

        # Get the highest ordered product for the last week
        highest_ordered_product = Order.objects.filter(ordered_date__gte=start_date, ordered_date__lte=end_date).values('product_id').annotate(total_orders=Count('product_id')).order_by('-total_orders').first()

        if highest_ordered_product:
            highest_ordered_product_id = highest_ordered_product['product_id']
            product = Product.objects.get(product_id=highest_ordered_product_id)
            product.highest_ordered_last_week = highest_ordered_product['total_orders']
            
            product.start_date_last_week = start_date
            product.end_date_last_week = end_date
            product.save()