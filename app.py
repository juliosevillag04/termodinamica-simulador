"""ChocoLab · Simulador interactivo de gases reales con Streamlit.

Iniciar: streamlit run app.py
Referencias teóricas: Termodinámica, Çengel/Boles/Kanoğlu (9.ª ed.), cap. 3.
"""
from __future__ import annotations

from pathlib import Path
from io import StringIO
import math
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from thermodynamics import (
    GASES, R_U, compute, constants_custom, constants_from_critical,
    conversion_to_molar_volume, report_rows,
)
from plots import (
    pressure_bars, pv_comparison, pv_isotherms,
    compressibility_vs_volume, compressibility_vs_pressure,
)
from ui import CSS, hero_html, molecules_html

ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"

st.set_page_config(
    page_title="ChocoLab | Laboratorio Van der Waals",
    page_icon="🐶", layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About":"ChocoLab · Simulador universitario de Van der Waals. Fuente principal: Çengel, 9.ª edición."},
)
st.markdown(CSS, unsafe_allow_html=True)


def initialize():
    defaults = {
        "gas_id":"N2", "temperature_K":175.0,
        "volume_mode":"specific", "volume_specific":0.00375,
        "volume_molar":0.10505, "volume_total":0.10505,
        "n_kmol":1.0, "show_ideal":True, "show_critical":True,
        "parameter_mode":"textbook", "compare_exp":True,
        "exp_pressure":10000.0, "reference_kind":"book",
    }
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k]=v


def load_example():
    st.session_state.update({
        "gas_id":"N2", "temperature_K":175.0, "volume_mode":"specific",
        "volume_specific":.00375, "volume_molar":.00375*GASES["N2"].molar_mass,
        "volume_total":.00375*GASES["N2"].molar_mass,"n_kmol":1.0,
        "parameter_mode":"textbook","compare_exp":True,"exp_pressure":10000.0,
        "reference_kind":"book",
    })


def load_near_critical():
    gas=GASES["N2"]
    c=constants_from_critical(gas.tc,gas.pc)
    st.session_state.update({
        "gas_id":"N2", "temperature_K":gas.tc,"volume_mode":"molar",
        "volume_molar":c.vc_model,"volume_specific":c.vc_model/gas.molar_mass,
        "volume_total":c.vc_model,"parameter_mode":"critical",
        "compare_exp":False,"reference_kind":"manual",
    })


def load_dilute():
    st.session_state.update({
        "gas_id":"N2", "temperature_K":330.0,"volume_mode":"molar",
        "volume_molar":4.0,"volume_specific":4.0/GASES["N2"].molar_mass,
        "volume_total":4.0,"parameter_mode":"critical",
        "compare_exp":False,"reference_kind":"manual",
    })


def section(title: str, sub: str | None = None):
    st.markdown(f"### {title}")
    if sub:
        st.markdown(f'<div class="section-lede">{sub}</div>', unsafe_allow_html=True)


def readout(v: float, digits: int = 2) -> str:
    if abs(v)>=1e6 or (0<abs(v)<.001):
        return f"{v:.4e}"
    return f"{v:,.{digits}f}"


def plot(fig):
    st.plotly_chart(fig, use_container_width=True,
                    config={"displaylogo":False, "responsive":True,
                            "toImageButtonOptions":{"format":"png","filename":"ChocoLab_grafica", "scale":2}})


initialize()

# --------------------------------------------------------------
# SIDEBAR: datos de entrada (fuente única de cada propiedad)
# --------------------------------------------------------------
with st.sidebar:
    st.markdown("### Panel de experimentación")
    st.caption("Introduce las condiciones y observa los resultados en tiempo real.")
    st.markdown("**Escenarios preparados**")
    st.button("📘 Cargar caso Çengel 3-13", use_container_width=True, on_click=load_example,
              help="N₂, 175 K, v = 0.00375 m³/kg; valor experimental 10 000 kPa.")
    cpre1,cpre2=st.columns(2)
    with cpre1:
        st.button("🎯 Punto crítico",use_container_width=True,on_click=load_near_critical)
    with cpre2:
        st.button("🌤️ Gas diluido",use_container_width=True,on_click=load_dilute)
    st.divider()

    st.markdown("**1. Selección de gas**")
    gas_key=st.selectbox("Sustancia pura", list(GASES.keys()),
        format_func=lambda k: f"{GASES[k].name} ({GASES[k].formula})",key="gas_id")
    gas=GASES[gas_key]
    critical=constants_from_critical(gas.tc,gas.pc)
    st.caption(f"M = {gas.molar_mass:.3f} kg/kmol · Tc = {gas.tc:g} K · Pc = {gas.pc:,.0f} kPa")
    st.markdown("**2. Condiciones termodinámicas**")
    temperature=st.number_input("Temperatura absoluta T (K)",min_value=1.0,max_value=2500.0,
                                step=5.0,format="%.2f",key="temperature_K",
                                help="Usa K.  T [K] = t [°C] + 273.15.")
    st.caption(f"Temperatura equivalente: {temperature-273.15:,.2f} °C")

    mode=st.radio("¿Qué tipo de volumen conoces?",["specific","molar","total"],
                  format_func=lambda x:{"specific":"Específico (m³/kg)",
                                        "molar":"Molar (m³/kmol)",
                                        "total":"Total (m³)"}[x],key="volume_mode",
                  help="La app convierte cada valor a volumen molar antes de aplicar las fórmulas.")
    if mode=="specific":
        entered=st.number_input("Volumen específico v (m³/kg)", min_value=0.0000001,
                                max_value=100000.0, step=.00025, format="%.7f",key="volume_specific")
    elif mode=="molar":
        entered=st.number_input("Volumen molar v̄ (m³/kmol)",min_value=.0000001,
                                max_value=1e7,step=.01,format="%.6f",key="volume_molar")
    else:
        entered=st.number_input("Volumen total V (m³)",min_value=.0000001,
                                max_value=1e7,step=.01,format="%.6f",key="volume_total")
        n_kmol=st.number_input("Cantidad de sustancia n (kmol)",min_value=.000001,
                              max_value=1e8,step=.05,format="%.5f",key="n_kmol")
    amount=st.session_state.get("n_kmol",1.)

    st.divider()
    st.markdown("**3. Parámetros del modelo**")
    param_mode=st.radio("Origen de a y b",["critical","textbook","manual"],
        format_func=lambda x:{"critical":"A partir de Tc y Pc", "textbook":"Redondeo del ejemplo 3-13 (N₂)",
                               "manual":"Personalizadas"}[x],
        key="parameter_mode",
        help="Para reproducir el ejemplo del libro se usan a=0.175 kPa·m⁶/kg² y b=0.00138 m³/kg, convertidas a base molar.")
    if param_mode=="manual":
        a=st.number_input("a [kPa·m⁶/kmol²]",min_value=.000001,
                          value=float(critical.a),step=1.0,format="%.6f",key=f"a_{gas_key}")
        b=st.number_input("b [m³/kmol]",min_value=.0000001,
                          value=float(critical.b),step=.001,format="%.7f",key=f"b_{gas_key}")
        const=constants_custom(a,b)
        st.caption("El punto crítico de las gráficas se recalcula con estas constantes.")
    elif param_mode=="textbook" and gas_key=="N2":
        const=constants_custom(.175*gas.molar_mass**2,.00138*gas.molar_mass)
        st.caption("N₂: se reproducen a y b redondeadas del ejemplo 3-13; se convierten de base másica a molar.")
    else:
        const=critical
        if param_mode=="textbook" and gas_key!="N2":
            st.warning("El redondeo del ejemplo 3-13 solo corresponde al nitrógeno. Se aplican los parámetros de Tc y Pc al gas seleccionado.")
        else:
            st.caption("a y b calculadas con los datos críticos de la tabla A-1 (Çengel, ec. 3-23).")

    with st.expander("Ver constantes y condiciones críticas"):
        st.write(f"**a** = {const.a:.5f} kPa·m⁶/kmol²")
        st.write(f"**b** = {const.b:.6f} m³/kmol")
        st.write(f"**Tc** = {const.tc_model:.2f} K")
        st.write(f"**Pc** = {const.pc_model:.2f} kPa")
        st.write(f"**vc** = {const.vc_model:.6f} m³/kmol")
        st.caption("Valores del modelo; en el modo estándar Tc y Pc provienen de la tabla A-1.")

    st.divider()
    st.markdown("**4. Visualización y referencia**")
    st.checkbox("Mostrar curva de gas ideal",key="show_ideal")
    st.checkbox("Señalar punto crítico del modelo",key="show_critical")
    st.checkbox("Comparar con presión experimental",key="compare_exp")
    exp_pressure=None
    if st.session_state.compare_exp:
        source=st.radio("Procedencia de la referencia",["book","manual"],
            format_func=lambda x:{"book":"Ejemplo Çengel 3-13", "manual":"Mi medición"}[x],
            key="reference_kind",horizontal=True)
        if source=="book":
            exp_pressure=10000.0
            st.caption("P medida = 10 000 kPa, únicamente para N₂, 175 K y v = 0.00375 m³/kg.")
        else:
            exp_pressure=st.number_input("Presión experimental (kPa)",min_value=.001,
                                         max_value=1e9,step=100.0,format="%.2f",key="exp_pressure")
            st.caption("La presión debe corresponder al mismo gas, temperatura y volumen de esta simulación.")

# --------------------------------------------------------------
# VALIDACIONES: nunca calcular con volumen <= b o valores no físicos
# --------------------------------------------------------------
try:
    v_molar=conversion_to_molar_volume(mode,entered,gas,amount)
    result=compute(temperature,v_molar,const)
except (ValueError, OverflowError, ZeroDivisionError) as exc:
    st.markdown(hero_html(ASSETS/"chocolab_logo.png"), unsafe_allow_html=True)
    st.error(f"**No se puede calcular el estado:** {exc}")
    st.info("Corrige los datos en el panel lateral. En Van der Waals es indispensable que v̄ > b y T > 0 K.")
    st.stop()

is_example=(gas_key=="N2" and abs(temperature-175.0)<1e-6 and
            abs(v_molar-0.00375*gas.molar_mass)<1e-7)
reference=exp_pressure
if st.session_state.compare_exp and st.session_state.reference_kind=="book" and not is_example:
    reference=None
    with st.sidebar:
        st.warning("La medición del libro NO corresponde al estado actual; se desactiva el cálculo de errores. Selecciona «Mi medición» para usar una referencia propia.")

st.markdown(hero_html(ASSETS/"chocolab_logo.png"), unsafe_allow_html=True)

# --------------------------------------------------------------
# PANTALLA DE ESTADO: ecuación y condiciones inequívocas
# --------------------------------------------------------------
st.markdown('<div class="section-tag">La ecuación que gobierna el laboratorio</div>',unsafe_allow_html=True)
st.latex(r"\boxed{\left(P+\frac{a}{\bar v^{2}}\right)(\bar v-b)=R_uT}\qquad"
         r"\Longleftrightarrow\qquad P=\frac{R_uT}{\bar v-b}-\frac{a}{\bar v^{2}}")
st.caption("Base molar: P en kPa · T en K · v̄ en m³/kmol · Rᵤ = 8.31447 kPa·m³/(kmol·K). Fuente: Çengel, ec. 3-22.")

c1,c2,c3,c4=st.columns(4)
with c1: st.metric("P ideal", f"{readout(result.p_ideal,1)} kPa")
with c2: st.metric("P Van der Waals", f"{readout(result.p_vdw,1)} kPa")
with c3: st.metric("Diferencia relativa", f"{result.difference_pct_ideal:+.2f} %",help="(PvdW − Pideal) / Pideal × 100. No es error experimental.")
with c4: st.metric("Factor Z", f"{result.z:.4f}")

with st.expander("▸ Ver cómo se sustituyen los datos en las ecuaciones", expanded=False):
    st.write(f"Se utiliza el volumen **v̄ = {result.molar_volume:.7f} m³/kmol**, "+
             (f"convertido desde **{entered:g} m³/kg** y M = {gas.molar_mass:g} kg/kmol." if mode=="specific" else
              f"convertido desde **{entered:g} m³** y n = {amount:g} kmol." if mode=="total" else "introducido directamente."))
    st.latex(r"P_{ideal}=\frac{R_uT}{\bar v}")
    st.latex(rf"P_{{ideal}}=\frac{{({R_U:.5f})({temperature:.4f})}}{{{v_molar:.7f}}}={result.p_ideal:.3f}\ \mathrm{{kPa}}")
    st.latex(r"P_{vdW}=\underbrace{\frac{R_uT}{\bar v-b}}_{\mathrm{correccion\ de\ volumen}}-"
             r"\underbrace{\frac{a}{\bar v^2}}_{\mathrm{atraccion}}")
    st.latex(rf"P_{{vdW}}=\frac{{({R_U:.5f})({temperature:.4f})}}{{{v_molar:.7f}-{const.b:.7f}}}"
             rf"-\frac{{{const.a:.5f}}}{{({v_molar:.7f})^2}}={result.p_vdw:.3f}\ \mathrm{{kPa}}")
    st.latex(rf"Z=\frac{{P_{{vdW}}\bar v}}{{R_uT}}={result.z:.5f}")
    st.markdown("**Cálculo de a y b con las propiedades críticas (modo estándar):**")
    st.latex(r"a=\frac{27 R_u^2 T_c^2}{64 P_c}\qquad b=\frac{R_uT_c}{8P_c}\qquad \bar v_c=3b")
    if param_mode == "textbook" and gas_key == "N2":
        st.latex(r"a_{molar}=a_{masico}M^2\qquad b_{molar}=b_{masico}M")
        st.caption("Modo libro: a = 0.175 kPa·m⁶/kg² y b = 0.00138 m³/kg son los redondeos de Çengel; el programa los convierte a unidades molares.")
    elif param_mode == "manual":
        st.caption("Con a y b personalizados, se deduce el crítico consistente con ese par de valores.")

for msg in result.notes:
    st.warning(msg)

# --------------------------------------------------------------
# TRES MÓDULOS, UNA SOLA CONFIGURACIÓN
# --------------------------------------------------------------
tab1, tab2, tab3=st.tabs(["01 · Comparación de presiones", "02 · Curvas P–v e isotermas", "03 · Factor de compresibilidad Z"])

with tab1:
    section("Gas ideal frente a Van der Waals",
            "Compara el modelo simplificado con uno que contempla la atracción intermolecular y el volumen excluido.")
    left,right=st.columns([1.6,1],gap="large")
    with left:
        fig_bars=pressure_bars(result,reference)
        plot(fig_bars)
    with right:
        st.markdown("#### ¿Qué cambia en la ecuación?")
        st.latex(r"P_{ideal}=\frac{R_uT}{\bar v}")
        st.latex(r"P_{vdW}=\frac{R_uT}{\bar v-b}-\frac{a}{\bar v^2}")
        st.markdown(f"**Corrección por volumen:** +{readout(result.p_excluded-result.p_ideal,2)} kPa")
        st.markdown(f"**Corrección por atracción:** −{readout(result.p_attraction,2)} kPa")
        st.markdown(f"**Diferencia neta:** {readout(result.p_vdw-result.p_ideal,2)} kPa")
        if result.p_vdw<result.p_ideal:
            st.info("En este estado, el modelo ideal predice una presión mayor que Van der Waals: domina el efecto atractivo.")
        elif result.p_vdw>result.p_ideal:
            st.info("En este estado, Van der Waals predice mayor presión: la corrección de volumen excluido supera a la atracción.")
        else:
            st.info("Los dos modelos predicen prácticamente la misma presión en este estado.")
    if reference is not None:
        error_i=abs(result.p_ideal-reference)/reference*100
        error_v=abs(result.p_vdw-reference)/reference*100
        e1,e2,e3=st.columns(3)
        e1.metric("Referencia medida", f"{reference:,.1f} kPa")
        e2.metric("Error ideal vs. medición", f"{error_i:.2f} %")
        e3.metric("Error Van der Waals", f"{error_v:.2f} %")
        if is_example and abs(reference-10000)<1e-6:
            st.caption("Ejemplo 3-13 de Çengel: valor medido 10 000 kPa y predicción publicada ≈ 9 471 kPa con constantes redondeadas. Las pequeñas diferencias se deben al redondeo de constantes y Rᵤ.")
    else:
        st.caption("La diferencia entre modelos no equivale al error físico. Para calcular error experimental introduce una medición válida para este mismo estado.")
    with st.expander("Ver la tabla de resultados y detalles numéricos"):
        table = pd.DataFrame(report_rows(gas,const,result,mode,entered))
        st.dataframe(table,hide_index=True,use_container_width=True)

with tab2:
    section("Diagrama presión–volumen e isotermas",
            "Explora cómo cambia P al modificar el volumen molar. Las curvas se calculan con la ecuación original de Van der Waals.")
    st.markdown("#### A. Comparación P–v a la temperatura seleccionada")
    st.caption(f"Gas: {gas.formula} · T = {temperature:.1f} K · estado señalado: v̄ = {v_molar:.6f} m³/kmol")
    fig_pv=pv_comparison(result,const,st.session_state.show_ideal,st.session_state.show_critical)
    plot(fig_pv)
    st.markdown("#### B. Familia de isotermas alrededor del punto crítico")
    fig_iso=pv_isotherms(result,const,st.session_state.show_ideal,st.session_state.show_critical)
    plot(fig_iso)
    k1,k2,k3=st.columns(3)
    k1.metric("Temperatura crítica",f"{const.tc_model:.2f} K")
    k2.metric("Presión crítica",f"{const.pc_model:,.1f} kPa")
    k3.metric("Volumen crítico (modelo)",f"{const.vc_model:.5f} m³/kmol")
    st.caption("Las gráficas ajustan la ventana vertical para permitir la lectura del estado y del crítico; los valores internos no se recortan. Usa zoom y pasa el cursor para ver coordenadas.")
    st.warning("En isotermas subcríticas puede observarse un bucle no físico (rama inestable). Van der Waals por sí sola no calcula la presión correcta de coexistencia; la construcción de Maxwell y condiciones de equilibrio son necesarias.")
    with st.expander("Representación molecular ilustrativa",expanded=True):
        st.caption("Ilustración complementaria para visualizar de manera intuitiva temperatura y compresión. No reemplaza el diagrama termodinámico.")
        components.html(molecules_html(temperature,v_molar,const.vc_model),height=290,scrolling=False)

with tab3:
    section("Factor de compresibilidad Z",
            "Cuantifica la desviación del estado calculado respecto a la ecuación de gas ideal: Z = 1 en el límite ideal.")
    zcol1,zcol2=st.columns([1,1.4],gap="large")
    with zcol1:
        st.latex(r"Z=\frac{P\bar v}{R_uT}")
        st.metric("Z calculado con Van der Waals", f"{result.z:.5f}")
        st.metric("Distancia porcentual a Z = 1",f"{abs(result.z-1)*100:.2f} %")
        st.markdown(f"**Interpretación:** {result.classification}.")
        if result.z>1:
            st.info("Z > 1: en este estado predominan, en términos relativos, los efectos que elevan la presión (p. ej., volumen excluido).")
        elif result.z<1 and result.z>0:
            st.info("0 < Z < 1: los efectos atractivos tienden a reducir la presión frente al modelo ideal.")
        elif result.z<=0:
            st.error("Z no positivo: presión no física en el estado introducido; cambia las condiciones para interpretarlo como gas.")
        else:
            st.info("Z ≈ 1: predicción próxima al límite de gas ideal.")
    with zcol2:
        st.markdown("#### Z frente al volumen molar")
        fig_z=compressibility_vs_volume(result,const)
        plot(fig_z)
    st.markdown("#### Z frente a presión (rama gaseosa del modelo)")
    st.caption("Se representa únicamente la rama de volumen elevado con presión positiva y pendiente P–v negativa. No equivale a un diagrama completo de equilibrio de fases.")
    fig_zp=compressibility_vs_pressure(result,const)
    plot(fig_zp)
    with st.expander("Criterios de lectura y límites"):
        st.markdown("""
- **Z = 1:** comportamiento ideal en cuanto a la relación P–v–T del estado.
- **0 < Z < 1:** la presión del modelo real es menor que la ideal en las mismas T y v̄.
- **Z > 1:** la presión del modelo real es mayor que la ideal en las mismas T y v̄.
- **Indicador didáctico:** menos de 5 % casi ideal; 5–15 % moderado; 15 % o más, considerable. No son límites de ingeniería normalizados.
- **Atención:** para T < Tc, y especialmente en estados de dos fases, se necesitan condiciones de equilibrio y datos experimentales; esta aplicación no calcula propiedades saturadas.
""")

# --------------------------------------------------------------
# EXPORTACIÓN + FUENTES + ALCANCE
# --------------------------------------------------------------
st.divider()
section("Exportar y revisar resultados", "Descarga los cálculos para usarlos en un informe o conservar las gráficas de la exposición.")
rows=report_rows(gas,const,result,mode,entered)
if reference is not None:
    rows += [
        {"Magnitud":"Presión experimental","Valor":reference,"Unidad":"kPa"},
        {"Magnitud":"Error absoluto gas ideal","Valor":abs(result.p_ideal-reference)/reference*100,"Unidad":"%"},
        {"Magnitud":"Error absoluto Van der Waals","Valor":abs(result.p_vdw-reference)/reference*100,"Unidad":"%"},
    ]
raw_csv=pd.DataFrame(rows).to_csv(index=False,sep=";",decimal=",",float_format="%.9g").encode("utf-8-sig")
html_graph=fig_iso.to_html(full_html=True,include_plotlyjs=True,config={"displaylogo":False,"responsive":True})
ex1,ex2,ex3=st.columns(3)
with ex1:
    st.download_button("⬇ Descargar resultados CSV", data=raw_csv,file_name="ChocoLab_resultados.csv",
                       mime="text/csv",use_container_width=True)
with ex2:
    st.download_button("⬇ Descargar gráfica P–v (HTML)",data=html_graph,file_name="ChocoLab_isotermas.html",
                       mime="text/html",use_container_width=True)
with ex3:
    st.download_button("⬇ Descargar gráfica Z (HTML)",
                       data=fig_z.to_html(full_html=True,include_plotlyjs=True,config={"displaylogo":False}),
                       file_name="ChocoLab_compresibilidad.html",mime="text/html",use_container_width=True)

with st.expander("Fuentes bibliográficas y alcance del modelo"):
    st.markdown("""
**Referencia principal (incluida en el material de la asignatura)**  
Çengel, Y. A., Boles, M. A., & Kanoğlu, M. (2019). *Termodinámica* (9.ª ed.). McGraw-Hill.
- Capítulo 3, sección 3-6: gas ideal (p. 133).
- Capítulo 3, sección 3-7: factor de compresibilidad (p. 136).
- Capítulo 3, sección 3-8: Van der Waals, ecuaciones (3-22) y (3-23) (p. 140).
- Ejemplo resuelto 3-13: comparación para N₂ (p. 143).
- Apéndice: tabla A-1 de masa molar y propiedades críticas (p. 882).

**Alcance científico:** el modelo de Van der Waals es una ecuación de estado aproximada;
no sustituye bases de datos de propiedades reales, tablas de vapor ni modelos de equilibrio líquido-vapor.
En las isotermas inferiores a Tc pueden aparecer estados inestables o no físicos.
La comparación con mediciones solo es válida a iguales condiciones.

**Convención:** internamente se utiliza Rᵤ = 8.31447 kPa·m³/(kmol·K), T [K], P [kPa]
y volumen molar [m³/kmol]. Las unidades de a y b son molares, incluso cuando
el usuario introduzca un volumen específico [m³/kg].
""")

st.markdown('<div class="source-note">ChocoLab · Proyecto académico interactivo · Universidad Americana (UAM) · Grupo 5 · Ecuación de estado de Van der Waals · No utilizar para diseño industrial sin validación.</div>',unsafe_allow_html=True)
