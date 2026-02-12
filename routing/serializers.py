from rest_framework import serializers


class RouteRequestSerializer(serializers.Serializer):
    start = serializers.CharField(help_text="Start coordinates e.g -119.7554, 41.7585")
    end = serializers.CharField(help_text="End coordinates e.g -85.3866, 31.2217")