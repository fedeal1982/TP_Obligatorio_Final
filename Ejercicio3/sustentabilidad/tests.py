"""
Pruebas del Ejercicio 3 (EcoTech Solutions).
Ejecutar desde la carpeta Ejercicio3:  python manage.py test
"""
import unittest

from django.test import TestCase

from .metricas import calcular_emisiones_carbono, obtener_metricas_consumo


class TestCalculoEmisiones(unittest.TestCase):
    """
    Punto A: Auditoría del Algoritmo de Emisiones mediante 'unittest'.

    Valida la exactitud numérica ante valores nominales, el uso de factores
    por defecto y personalizados, los casos límite y la correcta elevación
    de excepciones ante valores fuera de rango o tipos incompatibles.
    """

    # -------------------------------------------------------------
    # 1. Exactitud numérica ante valores nominales
    # -------------------------------------------------------------
    def test_calculo_nominal_factor_por_defecto(self):
        """
        Verifica el cálculo exacto utilizando el factor de emisión por defecto (0.4 kg CO2/kWh).
        Fórmula: Emisiones = consumo * 0.4
        """
        # 100 kWh * 0.4 = 40.0 kg CO2
        self.assertEqual(calcular_emisiones_carbono(100), 40.0)

        # 2500 kWh * 0.4 = 1000.0 kg CO2
        self.assertEqual(calcular_emisiones_carbono(2500), 1000.0)

        # 1500.5 kWh * 0.4 = 600.2 kg CO2
        self.assertAlmostEqual(calcular_emisiones_carbono(1500.5), 600.2, places=2)

        # Tipo de dato retornado debe ser float
        self.assertIsInstance(calcular_emisiones_carbono(100), float)

    def test_calculo_nominal_factor_personalizado(self):
        """
        Verifica que se aplique correctamente un factor de emisión explícito.
        """
        # 100 kWh con factor 0.5 = 50.0 kg CO2
        self.assertEqual(calcular_emisiones_carbono(100, factor_emision=0.5), 50.0)

        # 200 kWh con factor 0.25 = 50.0 kg CO2
        self.assertEqual(calcular_emisiones_carbono(200, factor_emision=0.25), 50.0)

        # 50000 kWh con factor 0.42 (intensidad alta) = 21000.0 kg CO2
        self.assertEqual(calcular_emisiones_carbono(50000, factor_emision=0.42), 21000.0)

    def test_consumo_cero_caso_limite(self):
        """
        Verifica que un consumo de 0 kWh resulte en exactamente 0.0 kg CO2.
        """
        self.assertEqual(calcular_emisiones_carbono(0), 0.0)
        self.assertEqual(calcular_emisiones_carbono(0.0), 0.0)
        self.assertEqual(calcular_emisiones_carbono(0, factor_emision=0.75), 0.0)

    def test_precision_decimal_alta(self):
        """
        Verifica la precisión numérica con valores decimales fraccionarios.
        """
        # 123.456 kWh * 0.4 = 49.3824 kg CO2
        resultado = calcular_emisiones_carbono(123.456, factor_emision=0.4)
        self.assertAlmostEqual(resultado, 49.3824, places=4)

    # -------------------------------------------------------------
    # 2. Validación de excepciones ante valores fuera de rango
    # -------------------------------------------------------------
    def test_consumo_negativo_eleva_value_error(self):
        """
        Verifica que un consumo estrictamente negativo eleve ValueError con un mensaje descriptivo.
        """
        # Caso 1: Entero negativo
        with self.assertRaises(ValueError) as context:
            calcular_emisiones_carbono(-1)
        self.assertIn("negativo", str(context.exception).lower())

        # Caso 2: Decimal negativo cercano a cero
        with self.assertRaises(ValueError):
            calcular_emisiones_carbono(-0.001)

        # Caso 3: Gran magnitud negativa
        with self.assertRaises(ValueError):
            calcular_emisiones_carbono(-15000)

        # Verificación alternativa con assertRaises directo (patrón visto en el curso)
        self.assertRaises(ValueError, calcular_emisiones_carbono, -100)

    def test_factor_emision_negativo_eleva_value_error(self):
        """
        Verifica que un factor de emisión negativo también sea rechazado con ValueError.
        """
        with self.assertRaises(ValueError) as context:
            calcular_emisiones_carbono(100, factor_emision=-0.4)
        self.assertIn("negativo", str(context.exception).lower())

    def test_tipos_datos_invalidos_elevan_type_error(self):
        """
        Verifica que valores no numéricos o tipos incompatibles eleven TypeError.
        """
        # String en lugar de numérico
        with self.assertRaises(TypeError):
            calcular_emisiones_carbono("100")  # type: ignore

        # None como consumo
        with self.assertRaises(TypeError):
            calcular_emisiones_carbono(None)  # type: ignore

        # Booleano (evitar que True sea interpretado como 1)
        with self.assertRaises(TypeError):
            calcular_emisiones_carbono(True)  # type: ignore

        # Factor de emisión con tipo incorrecto
        with self.assertRaises(TypeError):
            calcular_emisiones_carbono(100, factor_emision="alto")  # type: ignore


class TestMetricasConsumo(unittest.TestCase):
    """
    Punto B: Pruebas unitarias para 'obtener_metricas_consumo(registros)'.
    """

    def setUp(self):
        self.historial_nominal = [
            {"planta": "Planta Norte", "consumo_kwh": 10000.0, "factor_emision": 0.4},  # 4000.0 CO2
            {"planta": "Planta Sur", "consumo_kwh": 25000.0, "factor_emision": 0.4},    # 10000.0 CO2
            {"planta": "Planta Este", "consumo_kwh": 15000.0, "factor_emision": 0.4},   # 6000.0 CO2
        ]

    def test_total_global_emisiones_y_planta_mayor_consumo(self):
        """
        Valida que se determine correctamente el total global de emisiones
        y la planta industrial con mayor consumo.
        """
        metricas = obtener_metricas_consumo(self.historial_nominal)

        # Total emisiones: 4000 + 10000 + 6000 = 20000.0 kg CO2
        self.assertEqual(metricas["total_emisiones"], 20000.0)

        # Total consumo: 10000 + 25000 + 15000 = 50000.0 kWh
        self.assertEqual(metricas["total_consumo_kwh"], 50000.0)

        # Planta de mayor consumo: Planta Sur (25000 kWh)
        self.assertEqual(metricas["planta_mayor_consumo"], "Planta Sur")
        self.assertEqual(metricas["max_consumo_kwh"], 25000.0)

    def test_acumulacion_multiples_registros_misma_planta(self):
        """
        Verifica que si una misma planta tiene múltiples registros en el historial,
        su consumo total sea sumado para determinar a la planta líder.
        """
        historial = [
            {"planta": "Planta A", "consumo_kwh": 10000.0, "factor_emision": 0.4},
            {"planta": "Planta B", "consumo_kwh": 18000.0, "factor_emision": 0.4},
            {"planta": "Planta A", "consumo_kwh": 12000.0, "factor_emision": 0.4},  # Planta A total = 22000 kWh
        ]
        metricas = obtener_metricas_consumo(historial)

        # Planta A supera a Planta B en el acumulado total
        self.assertEqual(metricas["planta_mayor_consumo"], "Planta A")
        self.assertEqual(metricas["max_consumo_kwh"], 22000.0)
        # Total emisiones: (10000+18000+12000) * 0.4 = 16000.0 kg CO2
        self.assertEqual(metricas["total_emisiones"], 16000.0)

    def test_historial_vacio(self):
        """
        Verifica el comportamiento seguro ante un historial vacío.
        """
        metricas = obtener_metricas_consumo([])
        self.assertEqual(metricas["total_emisiones"], 0.0)
        self.assertEqual(metricas["total_consumo_kwh"], 0.0)
        self.assertIsNone(metricas["planta_mayor_consumo"])
        self.assertEqual(metricas["registros_procesados"], [])

    def test_propagacion_value_error_en_consumo_negativo(self):
        """
        Verifica que si un registro tiene consumo negativo, al invocar
        calcular_emisiones_carbono se eleve ValueError.
        """
        historial_invalido = [
            {"planta": "Planta Norte", "consumo_kwh": 5000.0},
            {"planta": "Planta Defectuosa", "consumo_kwh": -200.0},
        ]
        with self.assertRaises(ValueError):
            obtener_metricas_consumo(historial_invalido)

    def test_registro_sin_clave_consumo(self):
        """
        Verifica que se detecte y eleve ValueError si un registro carece de 'consumo_kwh'.
        """
        historial_incompleto = [
            {"planta": "Planta Incompleta"}  # Falta 'consumo_kwh'
        ]
        with self.assertRaises(ValueError):
            obtener_metricas_consumo(historial_incompleto)


class TestVistaPanelSustentabilidad(TestCase):
    """Punto B: vista Django vista_panel_sustentabilidad."""

    def test_vista_renderiza_plantilla_y_contexto(self):
        respuesta = self.client.get("/")
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, "sustentabilidad/panel.html")

        for clave in ("total_emisiones", "planta_mayor_consumo", "total_consumo_kwh", "registros"):
            self.assertIn(clave, respuesta.context)

        self.assertGreater(respuesta.context["total_emisiones"], 0)
        self.assertEqual(respuesta.context["planta_mayor_consumo"], "Planta Sur - Comodoro Rivadavia")
        self.assertContains(respuesta, "Planta Sur - Comodoro Rivadavia")
