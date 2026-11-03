"""
Pruebas unitarias para el Ejercicio 2
EcoTech Solutions - Trabajo Final
"""

import json
import os
import tempfile
import unittest

from ejercicio2 import (
    DispositivoEcologico,
    DispositivoEcológico,
    PanelSolar,
    StockInvalidoError,
    GestorInventario,
)


class TestEjercicio2(unittest.TestCase):

    def setUp(self):
        self.dispositivo = DispositivoEcologico(
            id_producto="TEST-001",
            nombre="Dispositivo Base Test",
            precio=100.0,
            stock=10,
            categoria="Pruebas"
        )
        self.panel = PanelSolar(
            id_producto="PANEL-001",
            nombre="Panel Test 400W",
            precio=200.0,
            stock=25,
            potencia_w=400.0,
            tipo_celda="Monocristalino",
            eficiencia_porcentaje=20.5
        )

    # -------------------------------------------------------------
    # Pruebas Punto A: Encapsulamiento y Excepciones
    # -------------------------------------------------------------
    def test_stock_valido_asignacion(self):
        """Verifica que se puedan asignar valores válidos (>= 0) de stock."""
        self.assertEqual(self.dispositivo.stock, 10)
        self.dispositivo.stock = 0
        self.assertEqual(self.dispositivo.stock, 0)
        self.dispositivo.stock = 50
        self.assertEqual(self.dispositivo.stock, 50)

    def test_stock_negativo_en_setter_lanza_excepcion(self):
        """Verifica que el setter lance StockInvalidoError ante valores negativos."""
        stock_original = self.dispositivo.stock
        with self.assertRaises(StockInvalidoError) as context:
            self.dispositivo.stock = -5

        # El valor de stock original debe permanecer inalterado
        self.assertEqual(self.dispositivo.stock, stock_original)
        self.assertEqual(context.exception.valor, -5)

    def test_stock_negativo_en_constructor_lanza_excepcion(self):
        """Verifica que no se puedan crear dispositivos con stock negativo."""
        with self.assertRaises(StockInvalidoError):
            DispositivoEcologico(
                id_producto="ERR-001",
                nombre="Producto Inválido",
                precio=50.0,
                stock=-1
            )

    def test_stock_tipo_invalido(self):
        """Verifica que el stock deba ser estrictamente un número entero."""
        with self.assertRaises(TypeError):
            self.dispositivo.stock = "diez"  # type: ignore

        with self.assertRaises(TypeError):
            self.dispositivo.stock = True  # type: ignore

    def test_alias_con_tilde(self):
        """Verifica que DispositivoEcológico funcione como alias de DispositivoEcologico."""
        instancia = DispositivoEcológico(
            id_producto="TILDE-01",
            nombre="Sensor Solar",
            precio=45.0,
            stock=5
        )
        self.assertIsInstance(instancia, DispositivoEcologico)
        self.assertEqual(instancia.stock, 5)

    # -------------------------------------------------------------
    # Pruebas Punto A: Herencia y Polimorfismo en PanelSolar
    # -------------------------------------------------------------
    def test_panel_solar_herencia_y_atributos(self):
        """Verifica que PanelSolar herede de DispositivoEcologico y posea sus atributos específicos."""
        self.assertIsInstance(self.panel, DispositivoEcologico)
        self.assertEqual(self.panel.id_producto, "PANEL-001")
        self.assertEqual(self.panel.potencia_w, 400.0)
        self.assertEqual(self.panel.tipo_celda, "Monocristalino")
        self.assertEqual(self.panel.eficiencia_porcentaje, 20.5)

    def test_panel_solar_regla_stock_heredada(self):
        """Verifica que PanelSolar respete la restricción de stock negativo por herencia."""
        with self.assertRaises(StockInvalidoError):
            PanelSolar(
                id_producto="PANEL-ERR",
                nombre="Panel Inválido",
                precio=150.0,
                stock=-10,
                potencia_w=300.0,
                tipo_celda="Policristalino",
                eficiencia_porcentaje=16.0
            )

        with self.assertRaises(StockInvalidoError):
            self.panel.stock = -1

    def test_polimorfismo_ficha_tecnica(self):
        """
        Verifica que emitir_ficha_tecnica() responda de forma polimórfica según la clase.
        """
        ficha_base = self.dispositivo.emitir_ficha_tecnica()
        ficha_panel = self.panel.emitir_ficha_tecnica()

        # La ficha del panel debe incluir los datos comerciales específicos
        self.assertIn("FICHA TÉCNICA COMERCIAL - PANEL SOLAR ECOTECH", ficha_panel)
        self.assertIn("Potencia Nominal      : 400.0 W", ficha_panel)
        self.assertIn("Tecnología de Celda   : Monocristalino", ficha_panel)
        self.assertIn("Eficiencia Energética : 20.50%", ficha_panel)

        # La ficha base no debe contener campos de panel solar
        self.assertNotIn("Potencia Nominal", ficha_base)
        self.assertIn("FICHA TÉCNICA - DISPOSITIVO ECOLÓGICO ESTÁNDAR", ficha_base)

    # -------------------------------------------------------------
    # Pruebas Punto B: Persistencia con GestorInventario
    # -------------------------------------------------------------
    def test_guardar_y_cargar_catalogo_json(self):
        """Verifica la persistencia y lectura íntegra en formato JSON."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            ruta_test = os.path.join(tmp_dir, "test_catalogo.json")
            catalogo = [self.dispositivo, self.panel]

            # Guardar
            GestorInventario.guardar_catalogo_json(catalogo, ruta_test)
            self.assertTrue(os.path.exists(ruta_test))

            # Verificar que sea un JSON válido y contenga los datos esperados
            with open(ruta_test, "r", encoding="utf-8") as f:
                datos = json.load(f)

            self.assertEqual(len(datos), 2)
            self.assertEqual(datos[0]["id_producto"], "TEST-001")
            self.assertEqual(datos[0]["stock"], 10)
            self.assertEqual(datos[1]["id_producto"], "PANEL-001")
            self.assertEqual(datos[1]["potencia_w"], 400.0)
            self.assertEqual(datos[1]["tipo_celda"], "Monocristalino")

            # Cargar mediante GestorInventario
            cargados = GestorInventario.cargar_catalogo_json(ruta_test)
            self.assertEqual(len(cargados), 2)
            self.assertEqual(cargados[1]["nombre"], "Panel Test 400W")

    def test_guardar_catalogo_tipo_invalido(self):
        """Verifica que se lance TypeError si no se pasa una lista de dispositivos."""
        with self.assertRaises(TypeError):
            GestorInventario.guardar_catalogo_json("no_es_una_lista", "ruta.json")  # type: ignore


if __name__ == "__main__":
    unittest.main()

