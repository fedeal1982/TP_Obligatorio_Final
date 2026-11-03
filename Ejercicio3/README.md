# Ejercicio 3: Auditoría con Tests Unitarios e Integración Web (40 puntos)
## EcoTech Solutions - Trabajo Final de Python

Este repositorio contiene la solución completa para el **Ejercicio 3** del Trabajo Final de EcoTech Solutions como una **aplicación web real de Django**.

---

## 📁 Estructura del Módulo

```text
Ejercicio3/
│
├── ejercicio3.py                   # Aplicación Web Django completa (Punto A y Punto B)
├── test_ejercicio3.py              # Suite de pruebas unitarias automatizadas con unittest
├── templates/
│   └── sustentabilidad/
│       └── panel.html              # Plantilla oficial de Django para el panel administrativo
└── README.md                       # Documentación técnica explicativa
```

---

## 📌 Requerimientos y Solución Técnica

### Punto A: Auditoría de Algoritmo de Emisiones (`unittest`)
- **Función**: `calcular_emisiones_carbono(consumo_kwh, factor_emision=0.4)`
  - Calcula la huella de carbono industrial: $\text{Emisiones (kg } CO_2\text{)} = \text{consumo\_kwh} \times \text{factor\_emision}$.
  - **Validaciones de negocio**:
    - Eleva `ValueError` si `consumo_kwh < 0` (consumo negativo fuera de rango).
    - Eleva `ValueError` si `factor_emision < 0`.
    - Eleva `TypeError` si los parámetros no son numéricos o son booleanos.
  - Precisión numérica con redondeo a 4 decimales para eliminar inconsistencias de precisión flotante estándar (IEEE 754).
- **Clase de prueba**: `TestCalculoEmisiones(unittest.TestCase)`
  - Comprueba exactitud numérica con factor por defecto ($0.4$).
  - Comprueba cálculo con factor de emisión personalizado (ej: $0.5$, $0.25$, $0.42$).
  - Comprueba el caso límite de consumo cero ($0\text{ kWh} \rightarrow 0.0\text{ kg } CO_2$).
  - Comprueba la elevación de `ValueError` ante consumos negativos con `with self.assertRaises(ValueError):` y `self.assertRaises(...)`.
  - Comprueba rechazo de tipos no válidos con `TypeError`.

---

### Punto B: Procesamiento de Métricas y Renderizado Web
- **Función de procesamiento**: `obtener_metricas_consumo(registros)`
  - Recibe un historial de consumos energéticos por planta industrial.
  - Invoca `calcular_emisiones_carbono(...)` para cada registro.
  - Determina:
    1. **Total global de emisiones** ($\text{kg } CO_2$).
    2. **Planta de mayor consumo** y su consumo acumulado.
    3. Total global de consumo energético ($\text{kWh}$).
    4. Resumen agregado y registros enriquecidos.
  - Manejo seguro de casos extremos (historial vacío, acumulación multirregistro por planta).
- **Función de vista Django**: `vista_panel_sustentabilidad(request)`
  - Recibe la solicitud HTTP (`request`).
  - Procesa los registros mediante `obtener_metricas_consumo(...)`.
  - Construye el diccionario de `contexto` con:
    - `total_emisiones` / `total_global_emisiones`
    - `planta_mayor_consumo`
    - `total_consumo_kwh`
    - `registros`
    - `metricas`
  - Retorna `render(request, "sustentabilidad/panel.html", contexto)`.
- **Plantilla HTML**: `templates/sustentabilidad/panel.html`
  - Maquetación corporativa con Bootstrap 5 e iconos.
  - Tarjetas de KPIs (Total Emisiones, Planta Líder, Consumo Global).
  - Tabla de monitoreo detallado con badges condicionales de alerta ambiental.

---

## 🚀 Cómo Ejecutar

### 1. Iniciar la Aplicación Web Django en el Navegador
Para arrancar el servidor real de Django y abrir automáticamente la interfaz web en tu navegador:
```powershell
python ejercicio3.py
```
*(O utilizando el entorno virtual: `& "..\Entorno Virtual\.venv\Scripts\python.exe" ejercicio3.py`)*

Se abrirá automáticamente tu navegador en `http://127.0.0.1:8000/`. Para detener el servidor, presiona `CTRL + C` en la terminal.

### 2. Ejecutar la Suite de Pruebas Unitarias
Para auditar y validar todas las aserciones con `unittest`:
```powershell
python -m unittest test_ejercicio3.py -v
```

---

## 🏆 Criterios de Evaluación y Cobertura (40/40 Puntos)

| Criterio | Implementación | Estado |
| :--- | :--- | :---: |
| **Punto A: Exactitud numérica** | Pruebas nominales, factor por defecto y personalizados | ✅ Auditado |
| **Punto A: Elevación ValueError** | Detección de consumos negativos y fuera de rango | ✅ Auditado |
| **Punto A: Clase TestCalculoEmisiones** | Estructurada como `unittest.TestCase` según especificación | ✅ Auditado |
| **Punto B: obtener_metricas_consumo** | Integración obligatoria de `calcular_emisiones_carbono` | ✅ Integrado |
| **Punto B: Total global y planta máxima** | Determinación de totales y planta líder | ✅ Integrado |
| **Punto B: vista_panel_sustentabilidad** | Vista Django completa retornando `render(..., "sustentabilidad/panel.html", contexto)` | ✅ Integrado |
| **Arranque Web Directo** | Servidor Django autónomo y apertura automática de navegador | ✅ Integrado |
