from django.urls import path

from .views import landing


app_name = "dashboard"

urlpatterns = [
    path("", landing, name="landing"),
]
