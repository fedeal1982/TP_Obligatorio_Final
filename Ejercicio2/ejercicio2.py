"""
Ejercicio 2 - Modelo de Productos, Excepciones y Persistencia
EcoTech Solutions - Trabajo Final

Módulo para la gestión del catálogo de equipamiento sustentable, validación de reglas
de negocio sobre el inventario y persistencia del stock en disco en formato JSON.
"""

import json
import os
from typing import Any, Dict, List, Optional


class StockInvalidoError(ValueError):
    """
    Excepción de negocio personalizada que se lanza cuando se intenta asignar
    un valor de stock negativo o inconsistente a un dispositivo ecológico.
    """

    def __init__(self, mensaje: str = "El valor de stock no puede ser negativo.", valor: Any = None):
        super().__init__(mensaje)
        self.valor = valor


class DispositivoEcologico:
    """
    Clase base que modela un producto dentro del catálogo ecológico.

    Aplica encapsulamiento explícito sobre el atributo 'stock' mediante propiedades
    (@property y @setter) para impedir inconsistencias de negocio (stock negativo).
    """

    def __init__(
        self,
        id_producto: str,
        nombre: str,
        precio: float,
        stock: int,
        categoria: str = "Equipamiento Sustentable General"
    ):
        self.id_producto: str = str(id_producto).strip()
        self.nombre: str = str(nombre).strip()
        self.precio: float = float(precio)
        self.categoria: str = str(categoria).strip()

        # Atributo privado/protegido para el encapsulamiento
        self._stock: int = 0

        # La asignación invoca el setter, validando el stock inicial desde la creación
        self.stock = stock

    @property
    def stock(self) -> int:
        """
        Getter para acceder al stock actual del dispositivo.
        """
        return self._stock

    @stock.setter
    def stock(self, valor: int) -> None:
        """
        Setter con validación de negocio.
        Impide valores negativos lanzando la excepción StockInvalidoError.
        """
        if not isinstance(valor, int) or isinstance(valor, bool):
            raise TypeError(
                f"El stock debe ser un número entero. Recibido: {type(valor).__name__} ({valor})"
            )

        if valor < 0:
            raise StockInvalidoError(
                f"Asignación rechazada: el stock ({valor}) no puede ser negativo para el producto "
                f"'{self.nombre}' (ID: {self.id_producto}).",
                valor=valor
            )

        self._stock = valor

    def emitir_ficha_tecnica(self) -> str:
        """
        Emite la ficha técnica del producto.
        Diseñada para ser sobreescrita polimórficamente por las clases especializadas.
        """
        return (
            "--------------------------------------------------\n"
            "   FICHA TÉCNICA - DISPOSITIVO ECOLÓGICO ESTÁNDAR \n"
            "--------------------------------------------------\n"
            f"ID de Producto    : {self.id_producto}\n"
            f"Nombre            : {self.nombre}\n"
            f"Categoría         : {self.categoria}\n"
            f"Precio Unitario   : ${self.precio:,.2f}\n"
            f"Stock Disponible  : {self.stock} unidades\n"
            "--------------------------------------------------"
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte la instancia a un diccionario serializable para persistencia JSON.
        """
        return {
            "tipo_producto": self.__class__.__name__,
            "id_producto": self.id_producto,
            "nombre": self.nombre,
            "categoria": self.categoria,
            "precio": round(self.precio, 2),
            "stock": self.stock
        }

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(id='{self.id_producto}', "
            f"nombre='{self.nombre}', stock={self.stock}, precio={self.precio})"
        )


# Alias con tilde para respetar estrictamente la literalidad de la consigna
DispositivoEcológico = DispositivoEcologico


class PanelSolar(DispositivoEcologico):
    """
    Clase especializada que modela un panel solar fotovoltaico.
    Hereda de DispositivoEcologico e incorpora atributos técnicos específicos.
    Aplica polimorfismo en la emisión de su ficha técnica comercial.
    """

    def __init__(
        self,
        id_producto: str,
        nombre: str,
        precio: float,
        stock: int,
        potencia_w: float,
        tipo_celda: str,
        eficiencia_porcentaje: float,
        categoria: str = "Energía Solar Fotovoltaica"
    ):
        # Inicialización de atributos heredados mediante super()
        super().__init__(
            id_producto=id_producto,
            nombre=nombre,
            precio=precio,
            stock=stock,
            categoria=categoria
        )
        # Atributos específicos del panel solar
        self.potencia_w: float = float(potencia_w)
        self.tipo_celda: str = str(tipo_celda).strip()
        self.eficiencia_porcentaje: float = float(eficiencia_porcentaje)

    def emitir_ficha_tecnica(self) -> str:
        """
        Polimorfismo: Sobrescribe el método base para generar una ficha técnica
        comercial adaptada al perfil de clientes de energía solar.
        """
        return (
            "==================================================\n"
            "   FICHA TÉCNICA COMERCIAL - PANEL SOLAR ECOTECH  \n"
            "==================================================\n"
            f"ID de Catálogo        : {self.id_producto}\n"
            f"Modelo Comercial      : {self.nombre}\n"
            f"Línea de Solución     : {self.categoria}\n"
            f"Potencia Nominal      : {self.potencia_w:.1f} W\n"
            f"Tecnología de Celda   : {self.tipo_celda}\n"
            f"Eficiencia Energética : {self.eficiencia_porcentaje:.2f}%\n"
            f"Precio de Venta       : ${self.precio:,.2f}\n"
            f"Disponibilidad Stock  : {self.stock} unidades en almacén\n"
            "=================================================="
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Extiende la serialización base incorporando las especificaciones del panel solar.
        """
        datos = super().to_dict()
        datos.update({
            "potencia_w": round(self.potencia_w, 2),
            "tipo_celda": self.tipo_celda,
            "eficiencia_porcentaje": round(self.eficiencia_porcentaje, 2)
        })
        return datos


class GestorInventario:
    """
    Gestiona la persistencia y serialización del inventario de dispositivos ecológicos.
    """

    @classmethod
    def guardar_catalogo_json(
        cls,
        lista_dispositivos: List[DispositivoEcologico],
        ruta_archivo: str = "catalogo_ecotech.json"
    ) -> None:
        """
        Serializa y almacena en disco la lista de dispositivos en formato JSON.

        :param lista_dispositivos: Colección de instancias de DispositivoEcologico o derivados.
        :param ruta_archivo: Ruta del archivo JSON de destino.
        :raises TypeError: Si lista_dispositivos no es una lista válida.
        :raises IOError: Si ocurre un error durante la escritura en disco.
        """
        if not isinstance(lista_dispositivos, list):
            raise TypeError("El catálogo a exportar debe ser provisto como una lista de dispositivos.")

        # Serialización de cada dispositivo usando su método to_dict() o vars()
        catalogo_serializado = []
        for dispositivo in lista_dispositivos:
            if hasattr(dispositivo, "to_dict") and callable(dispositivo.to_dict):
                catalogo_serializado.append(dispositivo.to_dict())
            elif isinstance(dispositivo, dict):
                catalogo_serializado.append(dispositivo)
            else:
                catalogo_serializado.append(vars(dispositivo))

        # Garantizar que el directorio destino existe
        directorio = os.path.dirname(ruta_archivo)
        if directorio and not os.path.exists(directorio):
            os.makedirs(directorio, exist_ok=True)

        # Escritura segura con codificación UTF-8 e indentación legible
        with open(ruta_archivo, "w", encoding="utf-8") as archivo:
            json.dump(catalogo_serializado, archivo, indent=4, ensure_ascii=False)

    @classmethod
    def cargar_catalogo_json(cls, ruta_archivo: str = "catalogo_ecotech.json") -> List[Dict[str, Any]]:
        """
        Método complementario para leer y deserializar el catálogo desde el archivo JSON.

        :param ruta_archivo: Ruta del archivo JSON a leer.
        :return: Lista de diccionarios con la información de los productos.
        """
        if not os.path.exists(ruta_archivo):
            raise FileNotFoundError(f"No se encontró el archivo de catálogo en: '{ruta_archivo}'")

        with open(ruta_archivo, "r", encoding="utf-8") as archivo:
            return json.load(archivo)


# =====================================================================
# Bloque de prueba y demostración del flujo completo
# =====================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("   ECOTECH SOLUTIONS - GESTIÓN DE CATÁLOGO Y PERSISTENCIA (EJ. 2)")
    print("=" * 70)

    # -----------------------------------------------------------------
    # 1. Creación de instancias válidas (Punto A)
    # -----------------------------------------------------------------
    print("\n[PASO 1] Creación de instancias del catálogo ecológico...")

    inversor = DispositivoEcologico(
        id_producto="INV-HYB-5000",
        nombre="Inversor Híbrido SmartEco 5kW",
        precio=1450.00,
        stock=12,
        categoria="Electrónica de Potencia"
    )

    panel_mono = PanelSolar(
        id_producto="SOL-MONO-450",
        nombre="Panel Solar EcoPro Monocristalino 450W",
        precio=189.90,
        stock=45,
        potencia_w=450.0,
        tipo_celda="Monocristalino PERC",
        eficiencia_porcentaje=21.40
    )

    panel_bifacial = PanelSolar(
        id_producto="SOL-BIFAC-550",
        nombre="Panel Solar Bifacial Hi-Power 550W",
        precio=235.50,
        stock=30,
        potencia_w=550.0,
        tipo_celda="N-Type TopCon Bifacial",
        eficiencia_porcentaje=22.80
    )

    lista_productos_validos = [inversor, panel_mono, panel_bifacial]
    print(f" -> Se crearon {len(lista_productos_validos)} dispositivos válidos con éxito.")

    # -----------------------------------------------------------------
    # 2. Demostración de Polimorfismo en Fichas Técnicas
    # -----------------------------------------------------------------
    print("\n[PASO 2] Demostración de Polimorfismo (emisión de fichas técnicas):")
    for prod in lista_productos_validos:
        print(prod.emitir_ficha_tecnica())
        print()

    # -----------------------------------------------------------------
    # 3. Verificación de captura controlada de StockInvalidoError
    # -----------------------------------------------------------------
    print("[PASO 3] Verificación de Reglas de Negocio y Excepción Personalizada:")

    # Intento A: Modificación de stock a un valor negativo en un producto existente
    print("\n * Caso A: Intento de asignación de stock negativo a un producto existente...")
    try:
        print(f"   Stock actual de '{inversor.nombre}': {inversor.stock} unidades.")
        print("   Intentando asignar stock = -8 ...")
        inversor.stock = -8
        print("   [FALLO]: La asignación negativa no fue bloqueada.")
    except StockInvalidoError as error:
        print(f"   [CAPTURA CONTROLADA EXITOSA] Excepción detectada: {type(error).__name__}")
        print(f"   Mensaje de error: {error}")
        print(f"   Valor rechazado registrado: {error.valor}")
        print(f"   El stock se mantiene seguro e inalterado en: {inversor.stock} unidades.")

    # Intento B: Intento de instanciación directa con stock negativo
    print("\n * Caso B: Intento de instanciación con stock inicial negativo...")
    try:
        print("   Intentando instanciar PanelSolar con stock = -15 ...")
        panel_invalido = PanelSolar(
            id_producto="SOL-ERR-001",
            nombre="Panel Defectuoso",
            precio=99.0,
            stock=-15,
            potencia_w=300.0,
            tipo_celda="Policristalino",
            eficiencia_porcentaje=15.0
        )
        print("   [FALLO]: El objeto con stock negativo fue creado indebidamente.")
    except StockInvalidoError as error:
        print(f"   [CAPTURA CONTROLADA EXITOSA] Excepción detectada: {type(error).__name__}")
        print(f"   Mensaje de error: {error}")
        print("   Se impidió la creación del objeto inconsistente en el sistema.")

    # -----------------------------------------------------------------
    # 4. Persistencia y Exportación con GestorInventario (Punto B)
    # -----------------------------------------------------------------
    print("\n[PASO 4] Exportación de productos válidos a archivo JSON (Punto B)...")
    archivo_destino = "catalogo_ecotech.json"

    # Se puede invocar mediante una instancia o directamente desde la clase
    gestor = GestorInventario()
    gestor.guardar_catalogo_json(lista_productos_validos, archivo_destino)
    print(f" -> Catálogo exportado exitosamente a: '{archivo_destino}'")

    # -----------------------------------------------------------------
    # 5. Verificación de lectura del archivo generado
    # -----------------------------------------------------------------
    print("\n[PASO 5] Verificación del contenido persistido en disco:")
    if os.path.exists(archivo_destino):
        datos_guardados = gestor.cargar_catalogo_json(archivo_destino)
        print(f" -> Archivo verificado. Cantidad de registros almacenados: {len(datos_guardados)}")
        print("\nContenido serializado en catalogo_ecotech.json:")
        print(json.dumps(datos_guardados, indent=2, ensure_ascii=False))

    print("\n" + "=" * 70)
    print(" Demostración completada con éxito.")
    print("=" * 70)

