"""Gráficos científicos ChocoLab (Plotly, unidades molares SI)."""
from __future__ import annotations
import numpy as np
import plotly.graph_objects as go
from thermodynamics import Constants, Result, R_U, pressure_ideal, pressure_vdw

COL = {
    "cocoa": "#51352A",
    "espresso": "#2E201B",
    "caramel": "#B97845",
    "gold": "#D6A15E",
    "sage": "#6D8063",
    "lavender": "#9983A2",
    "cream": "#FFF9F2",
    "text": "#39281F",
    "grid": "#E9DCCF",
    "muted": "#857468",
}


def style(fig: go.Figure, height: int = 415, x_label: str = "", y_label: str = "") -> go.Figure:
    fig.update_layout(
        height=height, margin=dict(l=28, r=24, b=40, t=50),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial, sans-serif", size=12, color=COL["text"]),
        legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="left", x=0,
                    bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
        hovermode="closest",
        xaxis=dict(title=x_label, gridcolor=COL["grid"], zeroline=False,
                   linecolor=COL["grid"], ticks="outside"),
        yaxis=dict(title=y_label, gridcolor=COL["grid"], zeroline=False,
                   linecolor=COL["grid"], ticks="outside"),
    )
    return fig


def pressure_bars(result: Result, reference: float | None = None) -> go.Figure:
    names = ["Gas ideal", "Van der Waals"]
    values = [result.p_ideal, result.p_vdw]
    colors = [COL["caramel"], COL["cocoa"]]
    if reference is not None:
        names.append("Experimental")
        values.append(reference)
        colors.append(COL["sage"])
    fig = go.Figure(go.Bar(
        x=names, y=values, marker_color=colors, width=.53,
        text=[f"{v:,.1f}" for v in values], textposition="outside",
        customdata=[["kPa"]]*len(values), hovertemplate="%{x}<br>%{y:,.2f} kPa<extra></extra>"
    ))
    style(fig, 370, "", "Presión (kPa)")
    lo = min(0, min(values)*1.2)
    hi = max(values)*1.25 if max(values)>0 else 10
    fig.update_yaxes(range=[lo, hi])
    fig.update_layout(showlegend=False, bargap=.36)
    return fig


def plot_range(t: float, v: float, c: Constants) -> np.ndarray:
    # Vista alejada de singularidad; presión sigue sin recortarse matemáticamente.
    left=max(c.b*1.06, min(v*.42, c.vc_model*.56))
    right=max(v*2.6, c.vc_model*8.0, left*4.0)
    return np.geomspace(left, right, 480)


def _focus_y(fig: go.Figure, res: Result, c: Constants) -> None:
    # Solo limita ventana visual: los datos subyacentes permanecen completos.
    m = max(c.pc_model, abs(res.p_ideal), abs(res.p_vdw), 10)
    upper=max(2.8*c.pc_model, 1.4*max(res.p_ideal, res.p_vdw, 0), 10)
    lower=min(-1.25*c.pc_model, 1.45*min(res.p_vdw, 0))
    if upper-lower < .5*m: upper+=m
    fig.update_yaxes(range=[lower, upper])


def pv_comparison(res: Result, c: Constants, show_ideal: bool=True, mark_critical: bool=True) -> go.Figure:
    vv=plot_range(res.temperature,res.molar_volume,c)
    fig=go.Figure()
    if show_ideal:
        fig.add_trace(go.Scatter(x=vv, y=pressure_ideal(res.temperature,vv), mode="lines", name="Gas ideal",
                                 line=dict(color=COL["gold"],width=2.6,dash="dash"),
                                 hovertemplate="v̄ = %{x:.5f} m³/kmol<br>P ideal = %{y:,.1f} kPa<extra></extra>"))
    fig.add_trace(go.Scatter(x=vv, y=pressure_vdw(res.temperature,vv,c), mode="lines", name="Van der Waals",
                             line=dict(color=COL["cocoa"],width=3.3),
                             hovertemplate="v̄ = %{x:.5f} m³/kmol<br>P vdW = %{y:,.1f} kPa<extra></extra>"))
    fig.add_trace(go.Scatter(x=[res.molar_volume],y=[res.p_vdw],mode="markers",name="Estado elegido",
                             marker=dict(size=13,color=COL["sage"],line=dict(color="white",width=2)),
                             hovertemplate="Estado actual<br>v̄ = %{x:.5f}<br>P = %{y:,.1f} kPa<extra></extra>"))
    if mark_critical:
        fig.add_trace(go.Scatter(x=[c.vc_model],y=[c.pc_model],mode="markers",name="Crítico (modelo)",
                                 marker=dict(size=11,symbol="diamond",color=COL["lavender"]),
                                 hovertemplate="Punto crítico (modelo)<br>v̄c=%{x:.5f}<br>Pc=%{y:,.1f}<extra></extra>"))
    style(fig,460,"Volumen molar v̄ (m³/kmol)","Presión P (kPa)")
    _focus_y(fig,res,c)
    return fig


def pv_isotherms(res: Result, c: Constants, show_ideal: bool, mark_critical: bool,
                 reference_temp: float | None = None) -> go.Figure:
    vv=plot_range(res.temperature,res.molar_volume,c)
    iso_t=[(.80*c.tc_model,"0,80 Tc",COL["lavender"]),
           (c.tc_model,"Tc",COL["sage"]),
           (1.20*c.tc_model,"1,20 Tc",COL["caramel"])]
    # Mostrar la temperatura del usuario sin duplicar casi exactamente otras curvas.
    if all(abs(res.temperature-t)>0.02*c.tc_model for t,_,_ in iso_t):
        iso_t.append((res.temperature,"T seleccionada",COL["espresso"]))
    fig=go.Figure()
    for t,label,color in iso_t:
        p=pressure_vdw(t,vv,c)
        fig.add_trace(go.Scatter(x=vv,y=p,mode="lines",name=f"{label} ({t:.1f} K)",
                                 line=dict(color=color,width=3 if label=="T seleccionada" else 2.3),
                                 hovertemplate=f"{label}<br>v̄=%{{x:.5f}}<br>P=%{{y:,.1f}} kPa<extra></extra>"))
    if show_ideal:
        fig.add_trace(go.Scatter(x=vv,y=pressure_ideal(res.temperature,vv),mode="lines",
                                 name="Gas ideal (T actual)",line=dict(color=COL["gold"],width=2,dash="dot")))
    fig.add_trace(go.Scatter(x=[res.molar_volume],y=[res.p_vdw],mode="markers",name="Estado actual",
                             marker=dict(size=13,color=COL["espresso"],line=dict(width=2,color="white"))))
    if mark_critical:
        fig.add_trace(go.Scatter(x=[c.vc_model],y=[c.pc_model],mode="markers",name="Crítico (modelo)",
                                 marker=dict(size=13,symbol="diamond",color=COL["sage"],line=dict(width=1,color="white"))))
    style(fig,500,"Volumen molar v̄ (m³/kmol)","Presión P (kPa)")
    _focus_y(fig,res,c)
    return fig


def compressibility_vs_volume(res: Result, c: Constants) -> go.Figure:
    vv=plot_range(res.temperature,res.molar_volume,c)
    pp=pressure_vdw(res.temperature,vv,c)
    zz=pp*vv/(R_U*res.temperature)
    fig=go.Figure()
    fig.add_hline(y=1.0,line_dash="dash",line_color=COL["gold"],annotation_text="Ideal: Z = 1",
                  annotation_position="bottom right")
    fig.add_trace(go.Scatter(x=vv,y=zz,mode="lines",name="Z de Van der Waals",
                             line=dict(color=COL["cocoa"],width=3.0),
                             hovertemplate="v̄=%{x:.5f} m³/kmol<br>Z=%{y:.4f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=[res.molar_volume],y=[res.z],mode="markers",name="Estado elegido",
                             marker=dict(size=14,color=COL["sage"],line=dict(color="white",width=2)),
                             hovertemplate="Z del estado = %{y:.4f}<extra></extra>"))
    style(fig,430,"Volumen molar v̄ (m³/kmol)","Factor Z (adimensional)")
    margin=max(.9, abs(res.z)*.3)
    fig.update_yaxes(range=[min(-.5,res.z-margin), max(2.5,res.z+margin)])
    return fig


def compressibility_vs_pressure(res: Result, c: Constants) -> go.Figure:
    # Muestra sólo la rama gaseosa monotónica del modelo.
    vv=np.geomspace(max(3*c.b,c.vc_model,res.molar_volume*0.4),
                    max(100*c.b,res.molar_volume*7,c.vc_model*15),500)
    p=pressure_vdw(res.temperature,vv,c)
    deriv= -R_U*res.temperature/(vv-c.b)**2+2*c.a/vv**3
    mask=(p>0) & (deriv<0) & np.isfinite(p)
    fig=go.Figure()
    fig.add_vline(x=0,line_color=COL["grid"])
    fig.add_hline(y=1.0,line_dash="dash",line_color=COL["gold"])
    fig.add_trace(go.Scatter(x=p[mask],y=(p[mask]*vv[mask]/(R_U*res.temperature)),mode="lines",
                             name="Rama gaseosa del modelo",line=dict(color=COL["cocoa"],width=3),
                             hovertemplate="P = %{x:,.1f} kPa<br>Z = %{y:.4f}<extra></extra>"))
    if res.p_vdw>0 and res.dPdv<0 and res.molar_volume>=c.vc_model:
        fig.add_trace(go.Scatter(x=[res.p_vdw],y=[res.z],mode="markers",name="Estado actual",
                                 marker=dict(size=13,color=COL["sage"])))
    style(fig,430,"Presión P (kPa)","Factor Z (adimensional)")
    return fig
