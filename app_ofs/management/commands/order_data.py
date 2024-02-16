# import random
# from datetime import date, timedelta
# from django.core.management.base import BaseCommand
# from app_ofs.models import ProductStatistics

# class Command(BaseCommand):
#     help = 'Generate dataset for product_id 101 in product_statistics table'

#     def handle(self, *args, **options):
#         product_id = 101
#         start_date = date(2023, 1, 1)
#         end_date = date.today()
        
#         while start_date <= end_date:
#             order_quantity = random.randint(300, 330)
#             completed_quantity = random.randint(200, 230)
#             cancelled_quantity = random.randint(20, 30)
#             production_quantity = random.randint(330, 345)
            
#             ProductStatistics.objects.create(
#                 product_id=product_id,
#                 date=start_date,
#                 order_quantity=order_quantity,
#                 completed_quantity=completed_quantity,
#                 cancelled_quantity=cancelled_quantity,
#                 production_quantity=production_quantity
#             )
            
#             start_date += timedelta(days=1)

# import random
# from datetime import date, timedelta
# from django.core.management.base import BaseCommand
# from app_ofs.models import ProductStatistics

# class Command(BaseCommand):
#     help = 'Generate dataset for product_id 101'

#     def handle(self, *args, **options):
#         product_id = 101
#         current_date = date(2023, 1, 1)
#         end_date = date.today()

#         # Initial order quantity and other quantities
#         initial_order_quantity = random.randint(200, 220)
#         order_quantity = initial_order_quantity
#         completed_order = str(int(float(order_quantity) * random.uniform(0.7, 0.8)))
#         cancelled_quantity = str(int(float(order_quantity) * 0.1))
#         production_quantity = str(int(float(order_quantity) * random.uniform(0.9, 1.1)))

#         while current_date <= end_date:
#             ProductStatistics.objects.create(
#                 product_id=product_id,
#                 date=current_date,
#                 order_quantity=str(order_quantity),
#                 completed_quantity=completed_order,
#                 cancelled_quantity=cancelled_quantity,
#                 production_quantity=production_quantity
#             )

#             # Increase order_quantity for the next day by a certain percentage
#             order_quantity = int(order_quantity * random.uniform(1.005, 1.01))  # Increase by 0.5% to 1%
#             completed_order = str(int(float(order_quantity) * random.uniform(0.7, 0.8)))
#             cancelled_quantity = str(int(float(order_quantity) * 0.1))
#             production_quantity = str(int(float(order_quantity) * random.uniform(0.9, 1.1)))

#             # Move to the next day
#             current_date += timedelta(days=1)


from django.core.management.base import BaseCommand
from app_ofs.models import ProductStatistics
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Generate dataset for product_id 102 with seasonal trends and patterns'

    def handle(self, *args, **options):
        product_id = 102
        current_date = date(2023, 1, 1)
        end_date = date.today()

        while current_date <= end_date:
            # Initial order quantity
            order_quantity = random.randint(200, 220)

            # Generate seasonal trends and patterns
            seasonal_factor = 1 + 0.1 * (current_date.month in [6, 7, 8])  # Increase by 10% in summer months
            order_quantity = int(order_quantity * seasonal_factor)

            # Generate increasing/decreasing quantities
            if current_date.month in [1, 2, 3]:  # Decrease by 5% in winter months
                order_quantity = int(order_quantity * 0.95)
            elif current_date.month in [9, 10, 11]:  # Increase by 5% in autumn months
                order_quantity = int(order_quantity * 1.05)

            # Generate completed, cancelled, and production quantities
            completed_order = int(order_quantity * random.uniform(0.7, 0.8))
            cancelled_quantity = int(order_quantity * 0.1)
            production_quantity = int(order_quantity * random.uniform(0.9, 1.1))

            # Save data to ProductStatistics model
            ProductStatistics.objects.create(
                product_id=product_id,
                date=current_date,
                order_quantity=str(order_quantity),
                completed_quantity=str(completed_order),
                cancelled_quantity=str(cancelled_quantity),
                production_quantity=str(production_quantity)
            )

            # Move to the next day
            current_date += timedelta(days=1)



