"""
Ejercicio 3 - Lógica de negocio de sustentabilidad.

Punto A: calcular_emisiones_carbono (auditada con unittest).
Punto B: obtener_metricas_consumo (usa calcular_emisiones_carbono).
"""
from typing import Any, Dict, List, Union

FACTOR_EMISION_DEFECTO = 0.4


def calcular_emisiones_carbono(
    consumo_kwh: Union[int, float],
    factor_emision: Union[int, float] = FACTOR_EMISION_DEFECTO,
) -> float:
    """
    Calcula las emisiones de CO2 (kg) = consumo_kwh * factor_emision.

    :raises ValueError: si el consumo es negativo (o el factor es negativo).
    :raises TypeError: si algún parámetro no es numérico.
    """
    for nombre, valor in (("consumo_kwh", consumo_kwh), ("factor_emision", factor_emision)):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise TypeError(
                f"{nombre} debe ser numérico (int o float), se recibió {type(valor).__name__}."
            )

    if consumo_kwh < 0:
        raise ValueError(f"El consumo no puede ser negativo ({consumo_kwh} kWh).")
    if factor_emision < 0:
        raise ValueError(f"El factor de emisión no puede ser negativo ({factor_emision}).")

    return round(float(consumo_kwh) * float(factor_emision), 4)


def obtener_metricas_consumo(registros: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Procesa un historial de consumos por planta industrial.

    Cada registro: {"planta": str, "consumo_kwh": número, "factor_emision": número (opcional),
    "sector": str (opcional), "fecha": str (opcional)}.

    :return: dict con total_emisiones, total_consumo_kwh, planta_mayor_consumo,
             max_consumo_kwh, registros_procesados y resumen_por_planta.
    """
    total_emisiones = 0.0
    total_consumo = 0.0
    procesados: List[Dict[str, Any]] = []
    por_planta: Dict[str, Dict[str, float]] = {}

    for idx, reg in enumerate(registros, start=1):
        if "consumo_kwh" not in reg:
            raise ValueError(f"El registro #{idx} no contiene la clave 'consumo_kwh'.")

        planta = str(reg.get("planta", f"Planta #{idx}")).strip()
        consumo = reg["consumo_kwh"]
        factor = reg.get("factor_emision", FACTOR_EMISION_DEFECTO)

        emisiones = calcular_emisiones_carbono(consumo, factor)

        total_emisiones += emisiones
        total_consumo += consumo
        procesados.append({
            "planta": planta,
            "sector": reg.get("sector", "General"),
            "fecha": reg.get("fecha", "N/A"),
            "consumo_kwh": float(consumo),
            "factor_emision": float(factor),
            "emisiones_co2": emisiones,
        })

        acum = por_planta.setdefault(planta, {"consumo_kwh": 0.0, "emisiones_co2": 0.0})
        acum["consumo_kwh"] += consumo
        acum["emisiones_co2"] += emisiones

    planta_mayor = None
    max_consumo = 0.0
    for planta, datos in por_planta.items():
        if planta_mayor is None or datos["consumo_kwh"] > max_consumo:
            planta_mayor = planta
            max_consumo = datos["consumo_kwh"]

    return {
        "total_emisiones": round(total_emisiones, 2),
        "total_consumo_kwh": round(total_consumo, 2),
        "planta_mayor_consumo": planta_mayor,
        "max_consumo_kwh": round(max_consumo, 2),
        "registros_procesados": procesados,
        "resumen_por_planta": por_planta,
    }
