import hashlib
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.contrib.gis.geos import Point
from routing.serializers import RouteRequestSerializer
from routing.services.route_service import RouteService
from routing.services.fuel_optimizer import (
    FuelOptimizer
)
from django.core.cache import cache
from routing.services.route_utils import decode_route

class OptimizeFuelRoute(APIView):
    @extend_schema(
            request=RouteRequestSerializer,
            responses={
                200: {
                    "type": "object",
                    "properties": {
                        "distance_miles": {"type": "number"},
                        "fuel_stops": {"type": "array"},
                        "total_cost": {"type": "number"},
                    },
                }
            },
            description="Returns the optimal fuel stops and total fuel cost for a given route.",
        )
    def post(self, request):
        serializer = RouteRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        start = serializer.validated_data["start"].replace(' ', '')
        end = serializer.validated_data["end"].replace(' ', '')

        try:
            # Expecting "longitude, latitude" strings from serializer
            start_coords = [float(coord ) for coord in start.split(',')]
            end_coords = [float(coord ) for coord in end.split(',')]
        except Exception:
            return self.response({'error': 'Invalid coordinates format. Expected "lon, lat"'}, status=status.HTTP_400_BAD_REQUEST)

        # Currently using memcache but Redis or RabbitMQ are my choices
        cache_key = build_cache_key(start, end)
        result = cache.get(cache_key)
        if result:
            return self.response(result)

        route_service = RouteService()
        route = route_service.get_route(start_coords, end_coords)
        
        if not route:
            return self.response({'error': 'Could not calculate route'}, status=status.HTTP_400_BAD_REQUEST)

        route_points = decode_route(route["polyline"])
        total_miles = route["distance_meters"] / 1609.34
        try:
            total_miles = round(total_miles, 2)
            optimizer = FuelOptimizer(polyline=route_points, start_coords=start_coords, total_distance_miles=total_miles)
            total_cost, breakdown = optimizer.optimize()        
        except Exception as e:
            return self.response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        result = {
            "distance_miles": round(total_miles, 2),
            "fuel_stops": breakdown,
            "total_cost": round(total_cost, 2),
        }
        cache.set(cache_key, result, timeout=60 * 60 * 24)
        return self.response(result)
    
    def response(self,*args, **kwargs):
        return Response(*args, **kwargs)
    


def build_cache_key(start, end):
    raw_key = f"{start}-{end}"
    hashed = hashlib.md5(raw_key.encode()).hexdigest()
    return f"routing_result_{hashed}"
        
