import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from app_ofs.models import ForecastData

class Command(BaseCommand):
    help = 'Import data from CSV into ForecastData model'

    def handle(self, *args, **options):
        file_path = '/home/lujana/Order-Forecasting-System/app_ofs/data/Electric_Production.csv'  # Replace with the actual path to your CSV file

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
