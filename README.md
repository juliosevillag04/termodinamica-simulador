# ChocoLab — Laboratorio interactivo de Van der Waals 🐶

**Proyecto académico | Termodinámica | Grupo 5 | Universidad Americana (UAM)**

Aplicación web local en **Python + Streamlit** para comparar gases ideales y reales mediante la ecuación de estado de **Van der Waals**. Incluye cálculos detallados, tres módulos de gráficas interactivas, representaciones moleculares ilustrativas y exportación de resultados.

## 1. Requisitos

- Python **3.10 o superior**.
- Windows 10/11, macOS o Linux.
- Navegador moderno.
- Conexión a internet **solo para instalar las dependencias la primera vez** (si ya están instaladas, el simulador funciona localmente). No requiere cuentas ni servicios externos.

## 2. Inicio rápido en Windows

1. Extrae **todo** el ZIP a una carpeta, sin separar los archivos ni modificar la estructura.
2. Instala Python desde su sitio oficial si aún no está en el equipo. Durante la instalación activa **Add Python to PATH**.
3. Haz doble clic en `INICIAR_CHOCOLAB.bat`.
4. La primera ejecución instalará las bibliotecas en `.venv` (puede tardar algunos minutos); después se abrirá el navegador en **http://localhost:8501**.
5. Para cerrar, vuelve a la consola y presiona **Ctrl+C**. No cierres la consola mientras estés exponiendo.

> Si Windows no encuentra Python, abre la terminal en la carpeta del proyecto y utiliza el procedimiento manual. Instala dependencias en una red confiable antes de la presentación.

## 3. Inicio manual (Windows, Mac o Linux)

Abre una terminal en la carpeta del proyecto y ejecuta:

```bash
python -m venv .venv
```

**Windows (PowerShell o CMD):**

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py
```

**Linux/macOS:**

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

Si Python en tu Mac/Linux se llama `python3`, usa `python3 -m venv .venv`. También puedes ejecutar `./iniciar_chocolab.sh`.

## 4. Qué muestra el simulador

**Barra lateral:**
- Escenarios rápidos: **Çengel ejemplo 3-13**, **punto crítico** y **gas diluido**.
- Sustancias preconfiguradas: nitrógeno, dióxido de carbono, oxígeno, metano, propano, amoniaco, agua/vapor y argón.
- Temperatura en **K** con equivalente calculado en °C.
- Tres formas de ingresar volumen: específico (m³/kg), molar (m³/kmol) o total (m³), con n en kmol.
- Tres orígenes de a y b: derivados de Tc y Pc, constantes redondeadas del ejemplo 3-13 **solo para N₂**, o entrada personalizada.
- Posibilidad de contrastar con presión experimental medida al mismo estado.

**Módulo 1 — Comparación:**
- P ideal, P Van der Waals, diferencia relativa **entre modelos** y Z.
- Gráfica de barras, desglose de las correcciones, sustitución de fórmulas.
- Si existe un dato experimental válido, error porcentual de cada modelo respecto a esa medición.

**Módulo 2 — P–v e isotermas:**
- Curva gas ideal vs. Van der Waals a T dada.
- Isotermas a 0,80 Tc, Tc y 1,20 Tc (y T seleccionada si es distinta).
- Marcador del estado y punto crítico **del modelo**.
- Animación molecular **didáctica, no dinámica molecular calculada**.
- Advertencias sobre ramas inestables y coexistencia de fases.

**Módulo 3 — Factor Z:**
- Z, |Z−1| y descripción del grado de desviación según **umbrales didácticos**.
- Gráfica Z vs. volumen molar y Z vs. presión en la rama de gas seleccionada.

**Exportación:** CSV y gráficos Plotly en HTML independiente con JavaScript incluido (se pueden abrir sin internet).

## 5. Caso de demostración del libro

Pulse **«📘 Cargar caso Çengel 3-13»**:

| Propiedad | Valor |
|---|---:|
| Sustancia | N₂ |
| T | 175 K |
| v específico | 0.00375 m³/kg |
| Masa molar | 28.013 kg/kmol |
| Volumen molar v̄ | 0.10504875 m³/kmol |
| Presión experimental | 10 000 kPa |
| a en base másica (redondeada en el libro) | 0.175 kPa·m⁶/kg² |
| b en base másica (redondeada en el libro) | 0.00138 m³/kg |

El libro informa **P ideal ≈ 13 851 kPa** y **P Van der Waals ≈ 9 471 kPa**. ChocoLab ofrece valores muy próximos a esas cifras; la última unidad puede variar levemente al utilizar Rᵤ y la masa molar con más decimales.

**Atención:** si cambias T, volumen o gas, la medición experimental del libro se oculta del cálculo de errores, porque ya no corresponde a ese estado. Puedes introducir tu propia presión medida desde el panel.

## 6. Convención matemática y unidades

Ecuaciones en **base molar**:

```text
P_ideal = R_u * T / v_molar
P_vdw   = R_u * T / (v_molar - b) - a / v_molar²
Z       = P_vdw * v_molar / (R_u * T)
a       = 27 * R_u² * Tc² / (64 * Pc)
b       = R_u * Tc / (8 * Pc)
vc      = 3b
```

| Símbolo | Unidad |
|---|---|
| T | K |
| P | kPa |
| v̄ | m³/kmol |
| Rᵤ | 8.31447 kPa·m³/(kmol·K) |
| a | kPa·m⁶/kmol² |
| b | m³/kmol |
| M | kg/kmol |
| n | kmol |

La app convierte `v específico × M = v molar` o `V total / n = v molar`. No mezcles constantes a y b en base másica con ecuaciones en base molar.

## 7. Limitaciones físicas del modelo

- **T > 0 K** y **v̄ > b** son obligatorias para evaluar la expresión.
- Si el modelo entrega presión absoluta no positiva, se identifica como resultado **no físico** para un gas.
- Para temperaturas inferiores a Tc, algunas ramas de la isoterma de Van der Waals son **inestables**. El simulador muestra la forma algebraica, no un cálculo riguroso de coexistencia líquido-vapor.
- El factor Z puede obtenerse como salida algebraica aunque el estado sea inestable; en tal caso no debe tratarse como medida experimental de un gas real estable.
- Los indicadores de 5 % y 15 % para calificar la desviación son **rangos didácticos**, no límites oficiales.
- Las predicciones pueden diferir de mediciones reales: Van der Waals es una aproximación con dos constantes.
- La familia de isotermas usa una ventana visual enfocada para mostrar con claridad el estado y el punto crítico. Al hacer zoom, Plotly permite explorar otros rangos.
- El simulador **no debe usarse para diseño de equipos industriales** sin datos de propiedades de calidad ingenieril.

## 8. Fuentes

Çengel, Y. A., Boles, M. A., & Kanoğlu, M. (2019). *Termodinámica* (9.ª ed.). McGraw-Hill.

- Capítulo 3, §3-6 (gas ideal): p. 133.
- Capítulo 3, §3-7 (Z): p. 136.
- Capítulo 3, §3-8, ecs. (3-22) y (3-23) (Van der Waals): p. 140.
- Ejemplo resuelto 3-13 (N₂): p. 143.
- Tabla A-1 (propiedades críticas y M): p. 882.

El paquete **no incorpora copias de libros protegidos por derechos de autor**.

## 9. Estructura del proyecto

```text
ChocoLab_Streamlit/
├── app.py                     # Interfaz y controles Streamlit
├── thermodynamics.py          # Ecuaciones, unidades, controles físicos
├── plots.py                   # Gráficas interactivas Plotly
├── ui.py                      # Paleta, estilos, logo y partículas
├── assets/
│   ├── chocolab_logo.png      # Logo recortado para la cabecera
│   └── chocolab_original.png  # Logo original entregado
├── tests/
│   └── test_thermodynamics.py # Pruebas de cálculo y gráficos
├── .streamlit/config.toml     # Tema café y crema
├── .gitignore
├── requirements.txt
├── INICIAR_CHOCOLAB.bat       # Windows
├── iniciar_chocolab.sh       # macOS/Linux
└── README.md
```

## 10. Pruebas

Con las bibliotecas instaladas:

```bash
python -m pip install pytest
python -m pytest -q
```

**Recomendación para la exposición:** carga el caso del libro, verifica los valores, cambia a «Punto crítico» y luego a «Gas diluido» para visualizar condiciones diferentes; ensaya la demostración antes de presentarla. Abre la aplicación con antelación y deja la consola iniciada.
