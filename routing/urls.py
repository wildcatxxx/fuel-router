from django.urls import path
from routing.views import OptimizeFuelRoute

urlpatterns = [
    path("optimize-fuel", OptimizeFuelRoute.as_view()),
]