"""
Ejercicio 3 - Auditoría con Tests Unitarios e Integración Web
EcoTech Solutions - Trabajo Final

Aplicación web real de Django con:
1. Punto A: Algoritmo de cálculo de huella de carbono industrial ('calcular_emisiones_carbono')
   con rigurosa validación de tipos y rangos numéricos.
2. Punto B: Procesamiento consolidado de métricas industriales ('obtener_metricas_consumo')
   e integración con la capa web administrativa mediante una vista Django ('vista_panel_sustentabilidad')
   que renderiza en 'sustentabilidad/panel.html'.
3. Servidor Web Django: Ejecutable directamente con 'python ejercicio3.py' para abrir
   el panel administrativo en el navegador web.
"""

from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Union

# Registrar el módulo en sys.modules como 'ejercicio3'
sys.modules["ejercicio3"] = sys.modules[__name__]

BASE_DIR = Path(__file__).resolve().parent

# =====================================================================
# Detección e Importación de Django
# =====================================================================
try:
    import django
    from django.conf import settings
    from django.core.management import execute_from_command_line
    from django.http import HttpRequest, HttpResponse
    from django.shortcuts import render
    from django.urls import path

    DJANGO_INSTALADO = True

    if not settings.configured:
        settings.configure(
            DEBUG=True,
            SECRET_KEY="ecotech-solutions-secret-key-evaluacion-final-2026",
            ROOT_URLCONF="ejercicio3",
            ALLOWED_HOSTS=["*"],
            INSTALLED_APPS=[
                "django.contrib.contenttypes",
                "django.contrib.auth",
            ],
            TEMPLATES=[
                {
                    "BACKEND": "django.template.backends.django.DjangoTemplates",
                    "DIRS": [BASE_DIR / "templates"],
                    "APP_DIRS": False,
                    "OPTIONS": {
                        "context_processors": [
                            "django.template.context_processors.debug",
                            "django.template.context_processors.request",
                        ],
                    },
                }
            ],
        )
        django.setup()

except ImportError:
    DJANGO_INSTALADO = False

    class HttpRequest:  # type: ignore
        """Emulación de HttpRequest de Django cuando no está instalado."""
        def __init__(self, method: str = "GET"):
            self.method = method
            self.GET: Dict[str, Any] = {}
            self.POST: Dict[str, Any] = {}


    class HttpResponse:  # type: ignore
        """Emulación de HttpResponse de Django cuando no está instalado."""
        def __init__(self, content: bytes, status_code: int = 200, content_type: str = "text/html"):
            self.content = content
            self.status_code = status_code
            self.content_type = content_type
            self.template_name = ""
            self.context_data: Dict[str, Any] = {}


    def render(request: Any, template_name: str, context: Optional[Dict[str, Any]] = None) -> HttpResponse:
        """
        Renderizador compatible que emula django.shortcuts.render
        cuando Django no se encuentra en el entorno activo.
        """
        ruta_tpl = BASE_DIR / "templates" / template_name
        ctx = context or {}
        if ruta_tpl.exists():
            html = ruta_tpl.read_text(encoding="utf-8")
            # Sustitución básica de variables principales para emulación
            total_emi = f"{ctx.get('total_emisiones', 0.0):,.2f}"
            total_con = f"{ctx.get('total_consumo_kwh', 0.0):,.2f}"
            planta_lider = str(ctx.get("planta_mayor_consumo", "N/A"))
            max_con = f"{ctx.get('max_consumo_kwh', 0.0):,.1f}"

            html = html.replace('{{ titulo|default:"EcoTech Solutions - Panel de Sustentabilidad" }}', ctx.get("titulo", "EcoTech Solutions"))
            html = html.replace("{{ total_emisiones|floatformat:2 }}", total_emi)
            html = html.replace('{{ planta_mayor_consumo|default:"N/A" }}', planta_lider)
            html = html.replace("{{ total_consumo_kwh|floatformat:2 }}", total_con)
            html = html.replace("{{ max_consumo_kwh|floatformat:1 }}", max_con)
            contenido_bytes = html.encode("utf-8")
        else:
            contenido_bytes = f"<html><body>Template {template_name} no encontrada.</body></html>".encode("utf-8")

        res = HttpResponse(contenido_bytes, status_code=200)
        res.template_name = template_name
        res.context_data = ctx
        return res


# =====================================================================
# PUNTO A: Algoritmo de Cálculo de Emisiones de Carbono
# =====================================================================

def calcular_emisiones_carbono(
    consumo_kwh: Union[int, float],
    factor_emision: Union[int, float] = 0.4
) -> float:
    """
    Calcula la huella de carbono industrial generada a partir del consumo eléctrico.

    Fórmula:
        Emisiones (kg CO2) = Consumo (kWh) * Factor de emisión (kg CO2 / kWh)

    :param consumo_kwh: Consumo de energía eléctrica expresado en kilovatios-hora (kWh).
                        Debe ser un valor numérico (int o float) mayor o igual a 0.
    :param factor_emision: Factor de intensidad de carbono en kg CO2 por kWh.
                           Valor por defecto: 0.4 kg CO2/kWh.
    :return: Total de emisiones de carbono estimadas en kg CO2 (float).
    :raises TypeError: Si consumo_kwh o factor_emision no son numéricos o son booleanos.
    :raises ValueError: Si consumo_kwh es estrictamente negativo (< 0),
                        o si factor_emision es negativo (< 0).
    """
    # 1. Validación de tipos estrictos
    if isinstance(consumo_kwh, bool) or not isinstance(consumo_kwh, (int, float)):
        raise TypeError(
            f"El consumo energético debe ser un número (int o float). "
            f"Tipo recibido: {type(consumo_kwh).__name__}."
        )

    if isinstance(factor_emision, bool) or not isinstance(factor_emision, (int, float)):
        raise TypeError(
            f"El factor de emisión debe ser un número (int o float). "
            f"Tipo recibido: {type(factor_emision).__name__}."
        )

    # 2. Validación de rango de negocio: El consumo no puede ser negativo
    if consumo_kwh < 0:
        raise ValueError(
            f"Consumo fuera de rango: el consumo energético no puede ser negativo ({consumo_kwh} kWh)."
        )

    # Validación adicional de robustez: el factor de emisión no puede ser negativo
    if factor_emision < 0:
        raise ValueError(
            f"Factor de emisión inválido: no puede ser un valor negativo ({factor_emision} kg CO2/kWh)."
        )

    # 3. Cálculo matemático preciso
    emisiones = float(consumo_kwh) * float(factor_emision)

    # Retorna con redondeo a 4 decimales para eliminar imprecisiones de coma flotante (IEEE 754)
    return round(emisiones, 4)


# =====================================================================
# PUNTO B: Procesamiento de Métricas de Consumo e Integración Web
# =====================================================================

def obtener_metricas_consumo(
    registros: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Procesa un historial de consumos energéticos por planta industrial para determinar:
      1. El total global de emisiones de carbono (utilizando calcular_emisiones_carbono).
      2. La planta de mayor consumo registrado.
      3. Métricas agregadas por planta y resumen consolidado para el panel de control.

    :param registros: Lista de diccionarios con el historial de mediciones de consumo.
    :return: Diccionario con las métricas consolidadas.
    :raises TypeError: Si registros no es una lista de diccionarios.
    :raises ValueError: Si algún registro contiene valores de consumo inválidos.
    """
    if not isinstance(registros, list):
        raise TypeError(f"Se esperaba una lista de registros, pero se recibió: {type(registros).__name__}")

    # Caso base: Historial vacío
    if not registros:
        return {
            "total_emisiones": 0.0,
            "total_global_emisiones": 0.0,
            "total_consumo_kwh": 0.0,
            "planta_mayor_consumo": None,
            "max_consumo_kwh": 0.0,
            "registros_procesados": [],
            "resumen_por_planta": {}
        }

    total_consumo_global: float = 0.0
    total_emisiones_global: float = 0.0
    registros_procesados: List[Dict[str, Any]] = []

    # Diccionario para acumular consumos y emisiones por planta
    acumulado_por_planta: Dict[str, Dict[str, float]] = {}

    for idx, reg in enumerate(registros):
        if not isinstance(reg, dict):
            raise TypeError(f"El registro en el índice {idx} no es un diccionario: {reg}")

        nombre_planta = str(reg.get("planta", f"Planta Desconocida #{idx + 1}")).strip()
        consumo = reg.get("consumo_kwh")

        if consumo is None:
            raise ValueError(f"El registro #{idx + 1} de '{nombre_planta}' no contiene la clave requerida 'consumo_kwh'.")

        # Factor de emisión opcional por registro (si no está, toma el default de 0.4)
        factor = reg.get("factor_emision", 0.4)

        # Invocación obligatoria de la función del Punto A
        emisiones_calculadas = calcular_emisiones_carbono(
            consumo_kwh=consumo,
            factor_emision=factor
        )

        consumo_float = float(consumo)
        total_consumo_global += consumo_float
        total_emisiones_global += emisiones_calculadas

        # Agregar al historial procesado manteniendo inmutabilidad del registro de entrada
        item_procesado = {
            "planta": nombre_planta,
            "consumo_kwh": consumo_float,
            "factor_emision": float(factor),
            "emisiones_co2": emisiones_calculadas,
            "fecha": reg.get("fecha", "N/A"),
            "sector": reg.get("sector", "General")
        }
        registros_procesados.append(item_procesado)

        # Acumular métricas por planta industrial
        if nombre_planta not in acumulado_por_planta:
            acumulado_por_planta[nombre_planta] = {
                "consumo_acumulado_kwh": 0.0,
                "emisiones_acumuladas_co2": 0.0,
                "cantidad_registros": 0
            }

        acumulado_por_planta[nombre_planta]["consumo_acumulado_kwh"] += consumo_float
        acumulado_por_planta[nombre_planta]["emisiones_acumuladas_co2"] += emisiones_calculadas
        acumulado_por_planta[nombre_planta]["cantidad_registros"] += 1

    # Determinar la planta de mayor consumo total acumulado
    planta_mayor_consumo: Optional[str] = None
    max_consumo: float = -1.0

    for planta, datos in acumulado_por_planta.items():
        if datos["consumo_acumulado_kwh"] > max_consumo:
            max_consumo = datos["consumo_acumulado_kwh"]
            planta_mayor_consumo = planta

    # Redondeo final para reportes ejecutivos limpios
    total_emisiones_redondeado = round(total_emisiones_global, 2)
    total_consumo_redondeado = round(total_consumo_global, 2)
    max_consumo_redondeado = round(max_consumo, 2) if max_consumo >= 0 else 0.0

    return {
        "total_emisiones": total_emisiones_redondeado,
        "total_global_emisiones": total_emisiones_redondeado,
        "total_consumo_kwh": total_consumo_redondeado,
        "planta_mayor_consumo": planta_mayor_consumo,
        "max_consumo_kwh": max_consumo_redondeado,
        "registros_procesados": registros_procesados,
        "resumen_por_planta": acumulado_por_planta
    }


def vista_panel_sustentabilidad(request: HttpRequest) -> HttpResponse:
    """
    Vista basada en funciones de Django para el panel administrativo de sustentabilidad.

    Flujo de la vista:
      1. Obtiene o define el historial de consumos industriales de EcoTech Solutions.
      2. Invoca 'obtener_metricas_consumo' para calcular el total global de emisiones
         y determinar la planta de mayor consumo.
      3. Ensambla el diccionario de contexto con toda la información requerida.
      4. Renderiza la plantilla 'sustentabilidad/panel.html' con dicho contexto.

    :param request: Objeto HttpRequest de Django.
    :return: Objeto HttpResponse de Django.
    """
    # Dataset predeterminado representativo de alta fidelidad
    historial_consumos: List[Dict[str, Any]] = [
        {
            "planta": "Planta Norte - Bahía Blanca",
            "consumo_kwh": 45000.0,
            "factor_emision": 0.4,
            "sector": "Refinería y Polímeros",
            "fecha": "2026-10-15"
        },
        {
            "planta": "Planta Centro - Córdoba",
            "consumo_kwh": 28500.0,
            "factor_emision": 0.4,
            "sector": "Ensamblado y Robótica",
            "fecha": "2026-10-16"
        },
        {
            "planta": "Planta Sur - Comodoro Rivadavia",
            "consumo_kwh": 62000.0,
            "factor_emision": 0.42,
            "sector": "Extracción y Compresión",
            "fecha": "2026-10-18"
        },
        {
            "planta": "Planta Oeste - Mendoza",
            "consumo_kwh": 18400.0,
            "factor_emision": 0.38,
            "sector": "Agroindustria Solar",
            "fecha": "2026-10-20"
        },
        {
            "planta": "Planta Litoral - Rosario",
            "consumo_kwh": 34100.0,
            "factor_emision": 0.4,
            "sector": "Bioenergía y Molienda",
            "fecha": "2026-10-22"
        }
    ]

    # Permitir inyección de registros dinámicos si se envían en el request
    if hasattr(request, "registros_custom") and isinstance(request.registros_custom, list):
        historial_consumos = request.registros_custom

    # 2. Invocación del procesamiento de métricas
    metricas = obtener_metricas_consumo(historial_consumos)

    # 3. Configuración del diccionario de contexto para la plantilla
    contexto = {
        "titulo": "Panel de Control de Sustentabilidad - EcoTech Solutions",
        "empresa": "EcoTech Solutions",
        "total_emisiones": metricas["total_emisiones"],
        "total_global_emisiones": metricas["total_global_emisiones"],
        "total_consumo_kwh": metricas["total_consumo_kwh"],
        "planta_mayor_consumo": metricas["planta_mayor_consumo"],
        "max_consumo_kwh": metricas["max_consumo_kwh"],
        "registros": metricas["registros_procesados"],
        "resumen_plantas": metricas["resumen_por_planta"],
        "metricas": metricas
    }

    # 4. Renderizado oficial de Django
    respuesta = render(request, "sustentabilidad/panel.html", contexto)

    # Atributos adicionales para facilitar la inspección en pruebas unitarias
    respuesta.context_data = contexto
    respuesta.template_name = "sustentabilidad/panel.html"

    return respuesta


# =====================================================================
# Definición de URLs de la Aplicación Web Django
# =====================================================================
if DJANGO_INSTALADO:
    urlpatterns = [
        path("", vista_panel_sustentabilidad, name="panel_sustentabilidad"),
        path("sustentabilidad/", vista_panel_sustentabilidad, name="panel_sustentabilidad_alt"),
    ]


# =====================================================================
# Bloque de Ejecución: Arranque del Servidor Web en el Navegador
# =====================================================================
if __name__ == "__main__":
    import threading
    import time
    import webbrowser

    PUERTO = "8000"
    HOST = "127.0.0.1"
    URL_SITIO = f"http://{HOST}:{PUERTO}/"

    print("=" * 75)
    print(" ECOTECH SOLUTIONS - APLICACIÓN WEB DE SUSTENTABILIDAD (EJERCICIO 3)")
    print("=" * 75)

    # 1. Demostración y validación en consola de Punto A y Punto B
    datos_demo = [
        {"planta": "Planta Norte", "consumo_kwh": 12000.0, "factor_emision": 0.4},
        {"planta": "Planta Sur", "consumo_kwh": 35000.0, "factor_emision": 0.4},
        {"planta": "Planta Este", "consumo_kwh": 18500.0, "factor_emision": 0.4},
    ]
    resumen = obtener_metricas_consumo(datos_demo)
    print(f" • Total global de emisiones calculadas : {resumen['total_emisiones']:,.2f} kg CO2")
    print(f" • Total de consumo industrial          : {resumen['total_consumo_kwh']:,.2f} kWh")
    print(f" • Planta industrial de mayor consumo   : {resumen['planta_mayor_consumo']} ({resumen['max_consumo_kwh']:,.2f} kWh)")
    print("-" * 75)
    print(f" • Servidor iniciado en                 : {URL_SITIO}")
    print(f" • Plantilla oficial renderizada        : sustentabilidad/panel.html")
    print(f" • Abriendo automáticamente en tu navegador web...")
    print(" • Presiona CTRL + C en esta terminal para detener el servidor.")
    print("=" * 75 + "\n")

    # Función para abrir automáticamente el navegador tras iniciar el servidor
    def abrir_en_navegador():
        time.sleep(1.2)
        webbrowser.open(URL_SITIO)

    threading.Thread(target=abrir_en_navegador, daemon=True).start()

    if DJANGO_INSTALADO:
        if len(sys.argv) > 1 and sys.argv[1] != "runserver":
            execute_from_command_line(sys.argv)
        else:
            execute_from_command_line([sys.argv[0], "runserver", f"{HOST}:{PUERTO}", "--noreload"])
    else:
        # Servidor web HTTP autónomo en caso de que Django no esté instalado en el intérprete activo
        from http.server import HTTPServer, BaseHTTPRequestHandler

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                req = HttpRequest(method="GET")
                resp = vista_panel_sustentabilidad(req)
                self.send_response(resp.status_code)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(resp.content)

            def log_message(self, format, *args):
                return

        httpd = HTTPServer((HOST, int(PUERTO)), Handler)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.server_close()
