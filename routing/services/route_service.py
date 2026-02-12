import requests
from django.conf import settings

class RouteService:
    BASE_URL = 'https://api.openrouteservice.org/v2/directions/driving-car'

    def get_route(self, start_coords, end_coords):

        body = {"coordinates":[start_coords, end_coords]}

        headers = {
            'Authorization': settings.OPENROUTE_API_KEY,
            'Content-Type': 'application/json'
        }

        response = requests.post(self.BASE_URL, json=body, headers=headers)
        try:
            response.raise_for_status()
            data = response.json()
            return {
                "polyline": data["routes"][0]["geometry"],
                "distance_meters": data["routes"][0]["summary"]["distance"],
            }
        
        except Exception as e: 
            print(str(e))
            return None

