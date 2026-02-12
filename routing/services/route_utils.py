import polyline
from django.contrib.gis.geos import Point

def decode_route(polyline_str):
    coords = polyline.decode(polyline_str)
    return [Point(lon, lat) for lat, lon in coords]