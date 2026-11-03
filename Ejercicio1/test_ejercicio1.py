"""
Pruebas unitarias para Ejercicio 1
"""

import unittest
from ejercicio1 import limpiar_registro_sensor, generar_resumen_sensores


class TestEjercicio1(unittest.TestCase):

    def test_limpiar_registro_sensor_estandar(self):
        crudo = {"sensor_id": " SENSOR-001 ", "temperatura": "24.5C", "ubicacion": "Planta Norte"}
        limpio = limpiar_registro_sensor(crudo)

        self.assertEqual(limpio["sensor_id"], "SENSOR-001")
        self.assertIsInstance(limpio["temperatura"], float)
        self.assertEqual(limpio["temperatura"], 24.5)
        self.assertEqual(limpio["ubicacion"], "Planta Norte")

    def test_inmutabilidad_diccionario_original(self):
        crudo = {"sensor_id": " SENSOR-001 ", "temperatura": "24.5C", "ubicacion": "Planta Norte"}
        _ = limpiar_registro_sensor(crudo)
        # El diccionario original no debe ser modificado
        self.assertEqual(crudo["sensor_id"], " SENSOR-001 ")

    def test_variaciones_temperatura(self):
        # Con grados centígrados con símbolo
        self.assertEqual(limpiar_registro_sensor({"sensor_id": "S1", "temperatura": "28.7°C"})["temperatura"], 28.7)
        # Con espacios intermedios
        self.assertEqual(limpiar_registro_sensor({"sensor_id": "S1", "temperatura": " 31.2 C "})["temperatura"], 31.2)
        # Número sin unidad
        self.assertEqual(limpiar_registro_sensor({"sensor_id": "S1", "temperatura": "19.8"})["temperatura"], 19.8)
        # Negativos
        self.assertEqual(limpiar_registro_sensor({"sensor_id": "S1", "temperatura": "-5.5C"})["temperatura"], -5.5)
        # Tipo numérico directo
        self.assertEqual(limpiar_registro_sensor({"sensor_id": "S1", "temperatura": 22.4})["temperatura"], 22.4)

    def test_ubicacion_por_defecto(self):
        # Sin clave ubicacion
        r1 = limpiar_registro_sensor({"sensor_id": "S1", "temperatura": "20C"})
        self.assertEqual(r1["ubicacion"], "No especificada")

        # Clave vacía
        r2 = limpiar_registro_sensor({"sensor_id": "S2", "temperatura": "20C", "ubicacion": ""})
        self.assertEqual(r2["ubicacion"], "No especificada")

        # Solo espacios
        r3 = limpiar_registro_sensor({"sensor_id": "S3", "temperatura": "20C", "ubicacion": "   "})
        self.assertEqual(r3["ubicacion"], "No especificada")

    def test_generar_resumen_sensores(self):
        sensores = [
            {"sensor_id": "S1", "temperatura": 20.0, "ubicacion": "A"},
            {"sensor_id": "S2", "temperatura": 30.0, "ubicacion": "B"},
            {"sensor_id": "S3", "temperatura": 25.0, "ubicacion": "C"}
        ]
        alertas, promedio = generar_resumen_sensores(sensores, 24.0)

        self.assertEqual(alertas, ["S2", "S3"])
        self.assertEqual(promedio, 25.0)

    def test_generar_resumen_sensores_lista_vacia(self):
        alertas, promedio = generar_resumen_sensores([], 25.0)
        self.assertEqual(alertas, [])
        self.assertEqual(promedio, 0.0)


if __name__ == "__main__":
    unittest.main()

