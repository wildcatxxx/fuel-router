import csv
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from django.db import transaction

from routing.models import TruckStop


class Command(BaseCommand):
    help = "Load fuel data from CSV into TruckStop model"

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file",
            type=str,
            help="Path to the fuel CSV file",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        csv_file_path = options["csv_file"]

        self.stdout.write(self.style.NOTICE("Loading fuel data..."))

        if TruckStop.objects.exists():
            self.stdout.write(
                self.style.WARNING("TruckStop data already exists. Skipping load.")
            )
            return

        truckstops = []
        row_count = 0

        with open(csv_file_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)

            for index, row in enumerate(reader):
                if index == 0:
                    continue  # skip header

                try:
                    lon = float(row[7])
                    lat = float(row[6])

                    truckstops.append(
                        TruckStop(
                            opis_id=row[0],
                            name=row[1],
                            address=row[2],
                            city=row[3],
                            state=row[4],
                            rack_id=row[8],
                            retail_price=Decimal(row[9]),
                            location=Point(lon, lat, srid=4326),
                        )
                    )

                    row_count += 1

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Skipping row {index}: {e}")
                    )

        TruckStop.objects.bulk_create(truckstops, batch_size=1000)

        self.stdout.write(
            self.style.SUCCESS(f"Successfully loaded {row_count} truck stops.")
        )