"""
Ejercicio 1 - Sanitización y Análisis Estadístico de Sensores
EcoTech Solutions - Trabajo Final
"""

import re
from typing import Any, Dict, List, Tuple


def limpiar_registro_sensor(
    registro_raw: Dict[str, Any],
    ubicacion_default: str = "No especificada"
) -> Dict[str, Any]:
    """
    Normaliza y sanitiza un registro individual de sensor.

    Punto A:
    - Identificador (sensor_id): Se eliminan espacios en blanco sobrantes.
    - Temperatura: Se remueven sufijos de unidad ('C', '°C', etc.) y se convierte a float.
    - Ubicación: Asigna un valor seguro por defecto si no fue registrada o está vacía.

    :param registro_raw: Diccionario con datos crudos del sensor.
    :param ubicacion_default: Texto por defecto para la ubicación ('No especificada').
    :return: Nuevo diccionario estandarizado.
    """
    # 1. Normalización de 'sensor_id'
    raw_id = registro_raw.get("sensor_id", "")
    sensor_id_limpio = str(raw_id).strip() if raw_id is not None else "DESCONOCIDO"

    # 2. Normalización de 'temperatura'
    raw_temp = registro_raw.get("temperatura")
    if raw_temp is None:
        temp_float = 0.0
    elif isinstance(raw_temp, (int, float)):
        temp_float = float(raw_temp)
    else:
        # Limpieza de caracteres de unidad y espacios
        temp_str = str(raw_temp).strip()
        # Expresión regular para capturar números enteros, decimales y signos (+/-)
        match = re.search(r"[-+]?(?:\d+\.?\d*|\.\d+)", temp_str)
        if match:
            temp_float = float(match.group())
        else:
            raise ValueError(f"No se pudo extraer un valor numérico de temperatura: '{raw_temp}'")

    # 3. Normalización de 'ubicacion' con valor por defecto seguro
    raw_ubicacion = registro_raw.get("ubicacion")
    if raw_ubicacion is None or not str(raw_ubicacion).strip():
        ubicacion_limpia = ubicacion_default
    else:
        ubicacion_limpia = str(raw_ubicacion).strip()

    # Retorna un nuevo diccionario garantizando inmutabilidad del original
    return {
        "sensor_id": sensor_id_limpio,
        "temperatura": temp_float,
        "ubicacion": ubicacion_limpia
    }


def generar_resumen_sensores(
    lista_sensores_limpios: List[Dict[str, Any]],
    umbral_temperatura: float
) -> Tuple[List[str], float]:
    """
    Monitorea y genera métricas estadísticas a partir de registros sanitizados.

    Punto B:
    - Retorna una tupla: (lista_sensores_alerta, promedio_temperatura)
    - lista_sensores_alerta: IDs de dispositivos cuya temperatura supera el umbral estipulado.
    - promedio_temperatura: Promedio térmico global de la planta.

    :param lista_sensores_limpios: Colección de diccionarios sanitizados con Punto A.
    :param umbral_temperatura: Valor límite de temperatura para disparar alertas.
    :return: Tupla (sensores_en_alerta, promedio_general).
    """
    if not lista_sensores_limpios:
        return ([], 0.0)

    # Filtrar IDs que superan el umbral térmico
    lista_sensores_alerta = [
        sensor["sensor_id"]
        for sensor in lista_sensores_limpios
        if sensor["temperatura"] > umbral_temperatura
    ]

    # Calcular promedio térmico global
    suma_temperaturas = sum(sensor["temperatura"] for sensor in lista_sensores_limpios)
    promedio_temperatura = suma_temperaturas / len(lista_sensores_limpios)

    return (lista_sensores_alerta, round(promedio_temperatura, 2))


# =====================================================================
# Bloque de ejecución: Demostración del flujo completo
# =====================================================================
if __name__ == "__main__":
    print("=" * 70)
    print(" ECOTECH SOLUTIONS - SISTEMA DE MONITOREO TÉRMICO ")
    print("=" * 70)

    # 1. Dataset de prueba con datos crudos y heterogéneos
    registros_crudos = [
        {"sensor_id": " SENSOR-001 ", "temperatura": "24.5C", "ubicacion": "Planta Norte"},
        {"sensor_id": "SENSOR-002  ", "temperatura": "28.7°C", "ubicacion": "Planta Sur"},
        {"sensor_id": "  SENSOR-003", "temperatura": " 31.2 C ", "ubicacion": "Sector Calderas"},
        {"sensor_id": "SENSOR-004", "temperatura": "19.8", "ubicacion": ""},          # Ubicación vacía
        {"sensor_id": " SENSOR-005 ", "temperatura": "33.0C"},                         # Sin clave 'ubicacion'
        {"sensor_id": " SENSOR-006 ", "temperatura": "26.1 C", "ubicacion": "   "},   # Solo espacios en ubicación
        {"sensor_id": "SENSOR-007", "temperatura": 22.4, "ubicacion": "Laboratorio"}  # Temperatura ya float
    ]

    print("\n--- 1. REGISTROS CRUDOS TRANSMITIDOS ---")
    for r in registros_crudos:
        print(f"  [RAW] {r}")

    # 2. Sanitización de los registros (Punto A)
    sensores_limpios = [limpiar_registro_sensor(registro) for registro in registros_crudos]

    print("\n--- 2. REGISTROS SANITIZADOS Y NORMALIZADOS (Punto A) ---")
    for r in sensores_limpios:
        print(f"  [OK]  ID: '{r['sensor_id']:<10}' | Temp: {r['temperatura']:>5.1f} °C | Ubicación: '{r['ubicacion']}'")

    # 3. Monitoreo y Mapeo Estadístico (Punto B)
    UMBRAL_LIMITE = 27.0
    sensores_alerta, promedio_global = generar_resumen_sensores(sensores_limpios, UMBRAL_LIMITE)

    # 4. Impresión formateada del reporte consolidado
    print("\n" + "=" * 70)
    print(f" REPORTE CONSOLIDADO DE PLANTA (Umbral de Alerta: {UMBRAL_LIMITE:.1f} °C)")
    print("=" * 70)
    print(f"• Total de sensores procesados : {len(sensores_limpios)}")
    print(f"• Promedio térmico global      : {promedio_global:.2f} °C")
    print(f"• Dispositivos en ALERTA (> {UMBRAL_LIMITE:.1f} °C): {len(sensores_alerta)}")

    if sensores_alerta:
        print("  Sensores que superan el límite:")
        for sensor_id in sensores_alerta:
            # Buscar el registro para mostrar detalle
            info = next(s for s in sensores_limpios if s["sensor_id"] == sensor_id)
            print(f"    - ALERTA: {sensor_id} con {info['temperatura']} °C en '{info['ubicacion']}'")
    else:
        print("  Todos los sensores se encuentran en rangos térmicos normales.")

    print(f"\nTupla devuelta por generar_resumen_sensores:")
    print(f"  (lista_sensores_alerta, promedio_temperatura) = { (sensores_alerta, promedio_global) }")
    print("=" * 70)

