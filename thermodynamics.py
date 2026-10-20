"""ChocoLab | Modelo termodinámico consistente para gases puros.

Referencia: Çengel, Boles y Kanoğlu, Termodinámica, 9.ª ed.,
cap. 3, sec. 3-8, ec. (3-22) y (3-23), ejemplo 3-13, tabla A-1.

Convención de UNIDADES INTERNA:
T [K], P [kPa], v_bar [m^3/kmol], R_u [kPa*m^3/(kmol*K)],
a [kPa*m^6/kmol^2], b [m^3/kmol], M [kg/kmol].
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Dict

import numpy as np

R_U = 8.31447


@dataclass(frozen=True)
class Gas:
    key: str
    name: str
    formula: str
    molar_mass: float  # kg/kmol
    tc: float          # K
    pc: float          # kPa


# Datos reproducidos de la TABLA A-1 de la edición española de Çengel (2019).
GASES: Dict[str, Gas] = {
    "N2": Gas("N2", "Nitrógeno", "N₂", 28.013, 126.2, 3390.0),
    "CO2": Gas("CO2", "Dióxido de carbono", "CO₂", 44.010, 304.2, 7390.0),
    "O2": Gas("O2", "Oxígeno", "O₂", 31.999, 154.8, 5080.0),
    "CH4": Gas("CH4", "Metano", "CH₄", 16.043, 191.1, 4640.0),
    "C3H8": Gas("C3H8", "Propano", "C₃H₈", 44.097, 370.0, 4260.0),
    "NH3": Gas("NH3", "Amoniaco", "NH₃", 17.030, 405.5, 11280.0),
    "H2O": Gas("H2O", "Agua / vapor", "H₂O", 18.015, 647.1, 22060.0),
    "Ar": Gas("Ar", "Argón", "Ar", 39.948, 151.0, 4860.0),
}


@dataclass(frozen=True)
class Constants:
    a: float
    b: float
    tc_model: float
    pc_model: float
    vc_model: float


@dataclass(frozen=True)
class Result:
    temperature: float
    molar_volume: float
    p_ideal: float
    p_excluded: float
    p_attraction: float
    p_vdw: float
    z: float
    difference_pct_ideal: float
    dPdv: float
    reduced_temperature: float
    reduced_pressure: float
    reduced_volume: float
    classification: str
    notes: tuple[str, ...]


def constants_from_critical(tc: float, pc: float) -> Constants:
    """Parámetros a y b por condición crítica de Van der Waals."""
    if not all(map(isfinite, (tc, pc))) or tc <= 0 or pc <= 0:
        raise ValueError("La temperatura y presión críticas deben ser positivas y finitas.")
    a = 27.0 * R_U**2 * tc**2 / (64.0 * pc)
    b = R_U * tc / (8.0 * pc)
    return Constants(a, b, tc, pc, 3.0 * b)


def constants_custom(a: float, b: float) -> Constants:
    """Obtiene el crítico del MODELO para los coeficientes personalizados."""
    if not all(map(isfinite, (a, b))) or a <= 0 or b <= 0:
        raise ValueError("Las constantes personalizadas a y b deben ser positivas y finitas.")
    tc = 8.0 * a / (27.0 * R_U * b)
    pc = a / (27.0 * b**2)
    return Constants(a, b, tc, pc, 3.0 * b)


def pressure_ideal(t: float, v: float | np.ndarray):
    return R_U * t / np.asarray(v)


def pressure_vdw(t: float, v: float | np.ndarray, const: Constants):
    v = np.asarray(v, dtype=float)
    return R_U * t / (v - const.b) - const.a / v**2


def dpdv_vdw(t: float, v: float | np.ndarray, const: Constants):
    v = np.asarray(v, dtype=float)
    return -R_U * t / (v - const.b)**2 + 2.0 * const.a / v**3


def classify_z(z: float) -> str:
    """Umbrales didácticos: NO criterios universales de ingeniería."""
    deviation = abs(z - 1.0)
    if deviation < 0.05:
        return "Casi ideal (umbral didáctico: < 5 %)"
    if deviation < 0.15:
        return "Desviación moderada (5–15 %)"
    return "Desviación considerable (≥ 15 %)"


def compute(t: float, v: float, const: Constants) -> Result:
    if not all(map(isfinite, (t, v))) or t <= 0:
        raise ValueError("Ingrese temperatura y volumen positivos y finitos.")
    if v <= const.b:
        raise ValueError(f"El volumen molar debe superar b = {const.b:.6f} m³/kmol.")
    p_i = float(pressure_ideal(t, v))
    p_e = R_U * t / (v - const.b)
    p_a = const.a / v**2
    p_v = p_e - p_a
    z = p_v * v / (R_U * t)
    slope = float(dpdv_vdw(t, v, const))
    notes: list[str] = []
    if p_v <= 0:
        notes.append("La ecuación devuelve una presión absoluta no positiva: no representa un estado gaseoso físico válido.")
    if t < const.tc_model:
        notes.append("T < Tc: puede haber coexistencia líquido-vapor; la isoterma cruda no sustituye al equilibrio de fases ni a la construcción de Maxwell.")
    if slope > 0:
        notes.append("Pendiente (∂P/∂v)T > 0: esta rama es mecánicamente inestable; no debe interpretarse como estado homogéneo estable.")
    if abs(p_v) > 200000:
        notes.append("Presión de magnitud muy elevada: la aproximación de Van der Waals puede ser poco fiable.")
    return Result(
        temperature=t,
        molar_volume=v,
        p_ideal=p_i,
        p_excluded=p_e,
        p_attraction=p_a,
        p_vdw=p_v,
        z=z,
        difference_pct_ideal=100.0 * (p_v - p_i) / p_i,
        dPdv=slope,
        reduced_temperature=t / const.tc_model,
        reduced_pressure=p_v / const.pc_model,
        reduced_volume=v / const.vc_model,
        classification=classify_z(z),
        notes=tuple(notes),
    )


def conversion_to_molar_volume(mode: str, value: float, gas: Gas, n_kmol: float = 1.0) -> float:
    if not isfinite(value) or value <= 0:
        raise ValueError("El volumen debe ser positivo y finito.")
    if mode == "specific":
        return value * gas.molar_mass
    if mode == "molar":
        return value
    if mode == "total":
        if not isfinite(n_kmol) or n_kmol <= 0:
            raise ValueError("La cantidad de sustancia debe ser positiva (kmol).")
        return value / n_kmol
    raise ValueError("Modo de volumen desconocido.")


def report_rows(gas: Gas, const: Constants, res: Result, mode: str, entered: float) -> list[dict[str, object]]:
    rows = [
        ("Sustancia", f"{gas.name} ({gas.formula})", ""),
        ("Modelo", "Van der Waals / gas ideal", ""),
        ("Temperatura", res.temperature, "K"),
        ("Volumen introducido", entered, {"specific":"m³/kg", "molar":"m³/kmol", "total":"m³"}[mode]),
        ("Volumen molar utilizado", res.molar_volume, "m³/kmol"),
        ("Constante a", const.a, "kPa·m^6/kmol²"),
        ("Constante b", const.b, "m³/kmol"),
        ("Presión gas ideal", res.p_ideal, "kPa"),
        ("Presión solo corrección de volumen", res.p_excluded, "kPa"),
        ("Corrección por atracción", res.p_attraction, "kPa"),
        ("Presión Van der Waals", res.p_vdw, "kPa"),
        ("Diferencia respecto al ideal", res.difference_pct_ideal, "%"),
        ("Factor de compresibilidad Z", res.z, "adimensional"),
        ("Temperatura reducida", res.reduced_temperature, "adimensional"),
    ]
    return [{"Magnitud":key,"Valor":value,"Unidad":unit} for key,value,unit in rows]
