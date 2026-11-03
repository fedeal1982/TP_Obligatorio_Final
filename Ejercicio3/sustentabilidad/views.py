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


# Umbrales de alerta: desvío porcentual de las emisiones de una planta
# respecto del promedio de todas las plantas.
UMBRAL_EXCESIVO = 0      # > 0 %  -> excesivo
UMBRAL_MUY_EXCESIVO = 20  # > 20 % -> muy excesivo
FACTOR_REFERENCIA = 0.5   # kg CO2/kWh que representa el 100 % del anillo de intensidad


def _armar_plantas(metricas):
    """Datos por planta para las tarjetas y anillos del panel."""
    resumen = metricas["resumen_por_planta"]
    total_emisiones = sum(d["emisiones_co2"] for d in resumen.values()) or 1
    max_consumo = metricas["max_consumo_kwh"] or 1
    promedio = total_emisiones / len(resumen) if resumen else 1

    plantas = []
    for nombre, datos in resumen.items():
        desvio = (datos["emisiones_co2"] - promedio) / promedio * 100
        if desvio > UMBRAL_MUY_EXCESIVO:
            estado = "grave"
        elif desvio > UMBRAL_EXCESIVO:
            estado = "excesivo"
        else:
            estado = "estandar"
        factor = datos["emisiones_co2"] / datos["consumo_kwh"] if datos["consumo_kwh"] else 0
        plantas.append({
            "nombre": nombre,
            "consumo_kwh": datos["consumo_kwh"],
            "emisiones_co2": round(datos["emisiones_co2"], 2),
            "porcentaje": round(datos["emisiones_co2"] / total_emisiones * 100),
            "pct_consumo": round(datos["consumo_kwh"] / max_consumo * 100),
            "factor": round(factor, 2),
            "pct_factor": round(min(factor / FACTOR_REFERENCIA, 1) * 100),
            "estado": estado,
        })
    mitad = (len(plantas) + 1) // 2
    return plantas, plantas[:mitad], plantas[mitad:]


def vista_panel_sustentabilidad(request):
    """Calcula las métricas y renderiza sustentabilidad/panel.html."""
    metricas = obtener_metricas_consumo(HISTORIAL_CONSUMOS)
    plantas, plantas_izq, plantas_der = _armar_plantas(metricas)
    registros = metricas["registros_procesados"]

    contexto = {
        "titulo": "Panel de Control de Sustentabilidad - EcoTech Solutions",
        "total_emisiones": metricas["total_emisiones"],
        "total_consumo_kwh": metricas["total_consumo_kwh"],
        "planta_mayor_consumo": metricas["planta_mayor_consumo"],
        "max_consumo_kwh": metricas["max_consumo_kwh"],
        "registros": registros,
        "plantas": plantas,
        "plantas_izq": plantas_izq,
        "plantas_der": plantas_der,
        "serie_emisiones": [{"x": r["fecha"], "y": r["emisiones_co2"]} for r in registros],
        "serie_consumo": [{"x": r["fecha"], "y": r["consumo_kwh"]} for r in registros],
        "resumen_plantas": metricas["resumen_por_planta"],
        "metricas": metricas,
    }
    return render(request, "sustentabilidad/panel.html", contexto)
