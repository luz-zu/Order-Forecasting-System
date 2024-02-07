import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from app_ofs.models import ForecastData

class Command(BaseCommand):
    help = 'Import data from CSV into ForecastData model'

    def handle(self, *args, **options):
        file_path = 'app_ofs/data/Electric_Production.csv'  # Replace with the actual path to your CSV file

        with open(file_path, 'r') as csvfile:
            reader = csv.reader(csvfile)

            # Skip the header row
            next(reader)

            for row in reader:
                try:
                    DATE, IPG2211A2N = row
                    print(DATE)
                    print(IPG2211A2N)

                    ForecastData.objects.create(
                        product_id=101,  # Assuming a default value for product_id
                        # user_id=39,      # Assuming a default value for user_id
                        quantity=float(IPG2211A2N),
                        ordered_date=datetime.strptime(DATE, '%m/%d/%Y').date()
                    )
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error importing data: {e}'))

        self.stdout.write(self.style.SUCCESS('Data imported successfully.'))


# import csv
# from datetime import datetime
# from django.core.management.base import BaseCommand
# from app_ofs.models import ForecastData
# class Command(BaseCommand):
#     help = 'Import data from CSV into ForecastData model'

#     def handle(self, *args, **options):
#         file_path = 'app_ofs/data/Electric_Production_copy.csv'  # Replace with the actual path to your CSV file

#         with open(file_path, 'r') as csvfile:
#             reader = csv.reader(csvfile)

#             # Skip the header row
#             next(reader)

#             for row in reader:
#                 try:
#                     Date, Sales = row
#                     # Convert date format from 'YYYY-MM-DD' to 'MM/DD/YYYY'
#                     Date = datetime.strptime(Date, '%Y-%m-%d').strftime('%m/%d/%Y')
#                     print(Date)
#                     print(Sales)

#                     ForecastData.objects.create(
#                         product_id=101,  # Assuming a default value for product_id
#                         # user_id=39,      # Assuming a default value for user_id
#                         quantity=float(Sales),
#                         ordered_date=datetime.strptime(Date, '%m/%d/%Y').date()
#                     )
#                 except Exception as e:
#                     self.stdout.write(self.style.ERROR(f'Error importing data: {e}'))

#         self.stdout.write(self.style.SUCCESS('Data imported successfully.'))
# from django.core.management.base import BaseCommand
# from app_ofs.models import ForecastData
# from datetime import timedelta

# class Command(BaseCommand):
#     help = 'Shift the ordered_date column by 10 years'

#     def handle(self, *args, **options):
#         # Get all instances of ForecastData
#         forecast_data_instances = ForecastData.objects.all()

#         # Update ordered_date for each instance by adding 10 years
#         for instance in forecast_data_instances:
#             instance.ordered_date += timedelta(days=365 * 6)  # Add 10 years (365 days * 10)
#             instance.save()

#         self.stdout.write(self.style.SUCCESS('ordered_date shifted by 10 years for all instances.'))


# from django.core.management.base import BaseCommand
# from app_ofs.models import ForecastData
# from datetime import timedelta

# class Command(BaseCommand):
#     help = 'Shift the ordered_date column by 10 years'

#     def handle(self, *args, **options):
#         # Get all instances of ForecastData
#         forecast_data_instances = ForecastData.objects.all()

#         # Update ordered_date for each instance by adding 10 years
#         for instance in forecast_data_instances:
#             try:
#                 # Add 10 years to the ordered_date
#                 instance.ordered_date += timedelta(days=365 * 10)
#                 instance.save()
#                 self.stdout.write(self.style.SUCCESS(f'Instance updated: {instance.id}, ordered_date: {instance.ordered_date}'))
#             except Exception as e:
#                 self.stdout.write(self.style.ERROR(f'Error updating instance {instance.id}: {e}'))

#         self.stdout.write(self.style.SUCCESS('ordered_date shifted by 10 years for all instances.'))

