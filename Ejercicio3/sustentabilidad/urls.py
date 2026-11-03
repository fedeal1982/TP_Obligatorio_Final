from django.urls import path

from . import views

app_name = "sustentabilidad"

urlpatterns = [
    path("", views.vista_panel_sustentabilidad, name="panel"),
    path("sustentabilidad/", views.vista_panel_sustentabilidad, name="panel_alt"),
]
