"""Pruebas de verificación de la física y de la construcción de gráficos."""
import math
import numpy as np
import pytest

from thermodynamics import (
    GASES, R_U, compute, constants_custom, constants_from_critical,
    conversion_to_molar_volume, pressure_vdw, report_rows,
)
from plots import (pressure_bars, pv_comparison,pv_isotherms,compressibility_vs_volume,
                   compressibility_vs_pressure)


def test_ideal_nitrogen_book_value():
    gas=GASES["N2"]
    result=compute(175,.00375*gas.molar_mass,constants_from_critical(gas.tc,gas.pc))
    assert result.p_ideal == pytest.approx(13851, rel=.001)


def test_rounding_book_vdw_matches_printed_solution():
    gas=GASES["N2"]
    c=constants_custom(.175*gas.molar_mass**2, .00138*gas.molar_mass)
    result=compute(175,.00375*gas.molar_mass,c)
    assert result.p_vdw == pytest.approx(9471, abs=3)
    assert abs(result.p_vdw -10000)/10000*100 == pytest.approx(5.3,abs=.1)


def test_critical_point_conditions_and_flat_inflexion():
    for gas in GASES.values():
        c=constants_from_critical(gas.tc,gas.pc)
        r=compute(gas.tc,3*c.b,c)
        assert r.p_vdw == pytest.approx(gas.pc,rel=1e-10)
        assert r.dPdv == pytest.approx(0,abs=1e-6)
        assert r.z == pytest.approx(3/8,rel=1e-10)


def test_three_volume_input_modes_consistent():
    gas=GASES["N2"]
    vsp=.00375
    mol=conversion_to_molar_volume('specific',vsp,gas)
    assert mol == pytest.approx(vsp*gas.molar_mass)
    assert conversion_to_molar_volume('molar',mol,gas) == pytest.approx(mol)
    assert conversion_to_molar_volume('total',mol*2.5,gas,n_kmol=2.5) == pytest.approx(mol)


def test_forbid_unphysical_input():
    c=constants_from_critical(126.2,3390)
    for v in [c.b,c.b*.9,0]:
        with pytest.raises(ValueError):compute(175,v,c)
    with pytest.raises(ValueError):compute(0,c.vc_model*2,c)
    with pytest.raises(ValueError):constants_custom(1,0)
    with pytest.raises(ValueError):conversion_to_molar_volume('total',1,GASES['N2'],0)


def test_high_volume_low_pressure_ideal_limit():
    c=constants_from_critical(GASES['N2'].tc,GASES['N2'].pc)
    r=compute(350,500,c)
    assert abs(r.z-1)<.001


def test_both_corrections_have_expected_signs():
    g=GASES['N2'];c=constants_from_critical(g.tc,g.pc)
    r=compute(180,.25,c)
    assert r.p_excluded>r.p_ideal
    assert r.p_attraction>0
    assert r.p_vdw==pytest.approx(r.p_excluded-r.p_attraction)


def test_subcritical_instability_notice():
    c=constants_from_critical(126.2,3390)
    r=compute(.8*c.tc_model,c.vc_model,c)
    assert r.dPdv>0
    assert any('inestable' in note.lower() for note in r.notes)
    assert any('Maxwell' in note for note in r.notes)


def test_all_plotly_figures_generate_without_errors():
    gas=GASES['N2'];c=constants_from_critical(gas.tc,gas.pc)
    r=compute(175,.00375*gas.molar_mass,c)
    figures=[pressure_bars(r,10000),pv_comparison(r,c),pv_isotherms(r,c,True,True),
             compressibility_vs_volume(r,c),compressibility_vs_pressure(r,c)]
    assert all(len(fig.data)>0 for fig in figures)
    for fig in figures:
        assert fig.to_json().startswith('{')


def test_csv_rows_are_named_and_unit_tagged():
    gas=GASES['CO2'];c=constants_from_critical(gas.tc,gas.pc)
    r=compute(350,.5,c)
    rows=report_rows(gas,c,r,'molar',.5)
    assert any(row['Magnitud']=='Factor de compresibilidad Z' for row in rows)
    assert any(row['Magnitud']=='Presión Van der Waals' and row['Unidad']=='kPa' for row in rows)
