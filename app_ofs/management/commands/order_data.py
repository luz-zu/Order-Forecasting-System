from random import randint
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from app_ofs.models import ProductStatistics  # Replace 'yourapp' with the name of your Django app

class Command(BaseCommand):
    help = 'Generate sample data for ProductStatistics model'

    def handle(self, *args, **kwargs):
        product_id = 101
        start_date = date(2023, 1, 1)
        end_date = date(2024, 2, 1)
        min_quantity = 250
        max_quantity = 280

        current_date = start_date
        while current_date <= end_date:
            # Check if data already exists for the current date
            if not ProductStatistics.objects.filter(product_id=product_id, date=current_date).exists():
                order_quantity = randint(min_quantity, max_quantity)
                completed_quantity = randint(min_quantity, max_quantity)
                production_quantity = randint(min_quantity, max_quantity)
                cancelled_quantity = randint(min_quantity, max_quantity)

                ProductStatistics.objects.create(
                    product_id=product_id,
                    order_quantity=order_quantity,
                    completed_quantity=completed_quantity,
                    production_quantity=production_quantity,
                    cancelled_quantity=cancelled_quantity,
                    date=current_date
                )
                self.stdout.write(self.style.SUCCESS(f'Data generated for {current_date}.'))
            else:
                self.stdout.write(self.style.WARNING(f'Data already exists for {current_date}. Skipping...'))

            current_date += timedelta(days=1)

        self.stdout.write(self.style.SUCCESS('Sample data generation completed.'))
