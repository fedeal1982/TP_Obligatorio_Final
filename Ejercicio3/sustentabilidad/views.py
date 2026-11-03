from django.shortcuts import render

from .metricas import obtener_metricas_consumo

HISTORIAL_CONSUMOS = [
    {"planta": "Planta Norte - Bahía Blanca", "consumo_kwh": 45000.0, "factor_emision": 0.4,
     "sector": "Refinería y Polímeros", "fecha": "2026-10-15"},
    {"planta": "Planta Centro - Córdoba", "consumo_kwh": 28500.0, "factor_emision": 0.4,
     "sector": "Ensamblado y Robótica", "fecha": "2026-10-16"},
    {"planta": "Planta Sur - Comodoro Rivadavia", "consumo_kwh": 62000.0, "factor_emision": 0.42,
     "sector": "Extracción y Compresión", "fecha": "2026-10-18"},
    {"planta": "Planta Oeste - Mendoza", "consumo_kwh": 18400.0, "factor_emision": 0.38,
     "sector": "Agroindustria Solar", "fecha": "2026-10-20"},
    {"planta": "Planta Litoral - Rosario", "consumo_kwh": 34100.0, "factor_emision": 0.4,
     "sector": "Bioenergía y Molienda", "fecha": "2026-10-22"},
]


def vista_panel_sustentabilidad(request):
    """Calcula las métricas y renderiza sustentabilidad/panel.html."""
    metricas = obtener_metricas_consumo(HISTORIAL_CONSUMOS)

    contexto = {
        "titulo": "Panel de Control de Sustentabilidad - EcoTech Solutions",
        "total_emisiones": metricas["total_emisiones"],
        "total_consumo_kwh": metricas["total_consumo_kwh"],
        "planta_mayor_consumo": metricas["planta_mayor_consumo"],
        "max_consumo_kwh": metricas["max_consumo_kwh"],
        "registros": metricas["registros_procesados"],
        "resumen_plantas": metricas["resumen_por_planta"],
        "metricas": metricas,
    }
    return render(request, "sustentabilidad/panel.html", contexto)
