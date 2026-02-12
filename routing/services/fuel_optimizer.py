import csv
from decimal import Decimal
import math
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from routing.models import TruckStop
from django.contrib.gis.geos import Point

class FuelOptimizer:
    MAX_RANGE_MILES = 500
    MPG = 10

    def __init__(self, polyline, start_coords, total_distance_miles):
        self.polyline = polyline
        self.start_point = Point(start_coords, srid=4326)
        self.total_distance_miles = total_distance_miles
    
    def get_stops_near_route(self):
        qs = TruckStop.objects.none()

        for point in self.polyline[::20]:  # sample every ~20 points
            nearby = TruckStop.objects.filter(
                location__distance_lte=(point, D(mi=5))
            )

            qs = qs | nearby
        stops = (
            qs.distinct()
            .annotate(dist_from_start=Distance("location", self.start_point))
            .order_by("dist_from_start")
        )

        return list(stops)

    def segment_route(self):
        segments = []
        remaining = self.total_distance_miles

        while remaining > 0:
            segment = min(remaining, self.MAX_RANGE_MILES)
            segments.append(segment)
            remaining -= segment

        return segments

    def optimize(self):
        stops = self.get_stops_near_route()

        chosen_stops = []
        total_cost = Decimal("0.00")

        current_position = 0  # miles from start

        while current_position < self.total_distance_miles:

            # max_reach = current_position + self.MAX_RANGE_MILES
            if self.total_distance_miles - current_position < self.MAX_RANGE_MILES:
                max_reach = self.total_distance_miles
            else:
                max_reach = current_position + self.MAX_RANGE_MILES

            search_range = current_position + (max_reach-current_position)*0.5
            
            reachable = [
                s for s in stops
                if  search_range < s.dist_from_start.mi <= max_reach
            ]

            if not reachable:
                raise ValueError('No reachable fuel stops')

            # Choose cheapest among reachable
            cheapest = min(reachable, key=lambda x: x.retail_price)

            distance_to_stop = cheapest.dist_from_start.mi - current_position

            gallons_used = Decimal(distance_to_stop / self.MPG)
            cost = gallons_used * Decimal(cheapest.retail_price)

            total_cost += cost

            chosen_stops.append({
                "opis_id": cheapest.opis_id,
                "name": cheapest.name,
                "city": cheapest.city,
                "state": cheapest.state,
                "price": float(cheapest.retail_price),
                "distance_from_start": round(cheapest.dist_from_start.mi, 2),
                "gallons": round(gallons_used, 2),
                "cost": round(cost, 2),
            })

            current_position = cheapest.dist_from_start.mi

        return float(round(total_cost, 2)), chosen_stops
