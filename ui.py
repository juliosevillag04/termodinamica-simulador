"""Presentación y microvisualización ChocoLab."""
from __future__ import annotations
import base64
from pathlib import Path

CSS = r"""
<style>
:root { --coffee:#3B271F; --brown:#6E4632; --accent:#AA6D41; --caramel:#C79462;
  --cream:#FFF9F2; --sand:#F1E7DA; --muted:#776658; --line:#E8DBCB; }
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header[data-testid="stHeader"] {background:transparent;}
.stApp, section.main, .block-container {background-color:#FCF8F3; color:var(--coffee);}
.block-container {padding-top:1.3rem; max-width:1210px; padding-bottom:4rem;}
section[data-testid="stSidebar"] {background:#F3E8DB; border-right:1px solid #DDCBB8;}
section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p {color:#524035;}
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {gap:.55rem;}
h1,h2,h3,h4,h5,h6 {color:#3B271F !important; letter-spacing:-.025em;}
h1 {font-weight:800!important;}
p, li, label, span {letter-spacing:0;}
[data-testid="stMetric"] {background:#FFFFFF; border:1px solid #EADCCC; border-radius:14px;
  padding:15px 17px; box-shadow:0 3px 13px rgba(61,39,31,.025);}
[data-testid="stMetricLabel"] p {color:#786452!important; font-weight:650!important;}
[data-testid="stMetricValue"] div {color:#3D291F!important; font-size:1.65rem;}
[data-testid="stMetricDelta"] {font-size:.84rem;}
div.stButton > button[kind="primary"],div.stDownloadButton > button[kind="primary"] {
  background:#75432C;border:1px solid #75432C;color:#FFF7ED;
  border-radius:9px;font-weight:650;}
div.stButton > button[kind="secondary"],div.stDownloadButton > button[kind="secondary"] {
  background:#FFF9F2;border:1px solid #CDB7A2;color:#583C2D;
  border-radius:9px;font-weight:600;}
div.stButton button:hover,div.stDownloadButton button:hover {border-color:#B97845;color:#A2643B;}
button[data-baseweb="tab"] {font-weight:650; font-size:.97rem; color:#614536;}
button[data-baseweb="tab"][aria-selected="true"] {color:#874B30!important;}
.stTabs [data-baseweb="tab-highlight"] {background:#874B30!important;}
div[data-testid="stExpander"] {background:#FFFDF9;border:1px solid #E8DACC; border-radius:13px;}
[data-testid="stAlert"] {border-radius:12px;}
[data-testid="stPlotlyChart"] {background:#FFFCF8;border:1px solid #EBDDCD;border-radius:15px;padding:4px;}
[data-testid="stDataFrame"] {border-radius:14px;overflow:hidden;}
[data-testid="stMarkdownContainer"] .katex {font-size:1.12em;}
.choco-hero {display:flex;justify-content:space-between;align-items:center;gap:22px;
  padding:18px 26px;border-radius:22px;background:linear-gradient(120deg,#FFF9F2 0%,#F0DECC 100%);
  border:1px solid #E5D4C0; box-shadow:0 6px 20px rgba(67,43,28,.045);margin-bottom:20px;}
.choco-hero .brand {width:260px; min-width:190px; max-width:46%;height:auto;object-fit:contain;}
.choco-hero .right {text-align:right;max-width:54%;}
.choco-hero .eyebrow {font-size:11px;font-weight:800;letter-spacing:.13em;color:#9B6C4F;text-transform:uppercase;}
.choco-hero h1 {font-size:clamp(22px,2.8vw,34px);margin:6px 0!important;line-height:1.08;}
.choco-hero p {margin:5px 0 0;font-size:.88rem;color:#715B4B;}
.section-lede {border-left:4px solid #BD8354;padding:7px 0 7px 15px;margin:12px 0 20px;color:#574133;background:#F7EDE2;border-radius:0 10px 10px 0;font-size:.96rem;}
.section-tag {font-size:.72rem;letter-spacing:.10em;text-transform:uppercase;font-weight:800;color:#976B4B;margin-top:14px;}
.formula-panel {border-radius:14px;border:1px solid #E4D0BA;background:#FFFDF8;padding:12px 16px;margin:12px 0;}
.explain {background:#F1E8DC;padding:13px 16px;border-radius:13px;border:1px solid #E6D5C4;color:#5B4537;font-size:.93rem;}
.source-note {font-size:12px;color:#857264;padding:13px 16px;border-top:1px solid #E9D8C9;margin-top:19px;}
.stat-line {padding:9px 0;border-bottom:1px solid #EBDFD0;font-size:.95rem;}
@media(max-width:680px){.block-container{padding-top:1.1rem}.choco-hero{padding:16px;flex-direction:column;align-items:flex-start;gap:4px}
.choco-hero .brand{width:210px;max-width:100%}.choco-hero .right{text-align:left;max-width:100%}.choco-hero h1{font-size:24px}}
</style>
"""


def hero_html(logo_path: Path) -> str:
    img=base64.b64encode(logo_path.read_bytes()).decode("ascii")
    return f'''<div class="choco-hero"><img class="brand" src="data:image/png;base64,{img}" alt="ChocoLab, perro café con gafas"/><div class="right"><div class="eyebrow">Termodinámica · Laboratorio interactivo</div><h1>Gases reales, datos claros.</h1><p>Ecuación de Van der Waals · comparación · isotermas · factor Z</p></div></div>'''


def molecules_html(t: float, molar_volume: float, critical_volume: float) -> str:
    # Interpretación cualitativa, no simulación microscópica ni solución cinética.
    dense = max(.08, min(1., critical_volume/max(molar_volume,1e-12)))
    count=round(9+20*dense)
    speed=max(.33,min(2.4,(t/300.0)**.5))
    template = '''<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"/><style>
body{margin:0;font-family:Arial,sans-serif;background:#FFFCF8;color:#4D3326;}
.wrap{padding:12px;border:1px solid #E8DAC9;border-radius:13px;}
.top{display:flex;justify-content:space-between;align-items:center;gap:12px;font-size:13px;padding:0 0 9px;}
button{background:#75432C;color:white;border:0;border-radius:8px;padding:7px 12px;cursor:pointer;}
canvas{width:100%;height:192px;display:block;background:#F6EDE2;border-radius:10px;}
.small{font-size:11px;color:#816A58;margin-top:9px;line-height:1.35;}
</style></head><body><div class="wrap"><div class="top"><strong>Movimiento molecular · ilustración cualitativa</strong><button id="toggle">Pausar</button></div><canvas id="scene"></canvas>
<div class="small">La cantidad aparente de partículas representa cualitativamente la compresión; la rapidez aumenta con T. No es dinámica molecular ni calcula fuerzas reales.</div></div><script>
const cnv=document.getElementById('scene'),ctx=cnv.getContext('2d');let active=true;
let nodes=[];const N=__COUNT__, SPEED=__SPEED__;
function reset(){let w=cnv.width= Math.max(330,Math.floor(cnv.clientWidth*devicePixelRatio));let h=cnv.height=Math.floor(192*devicePixelRatio);nodes=[];
for(let i=0;i<N;i++){let r=7*devicePixelRatio, angle=(i*2.39996)%(2*Math.PI);nodes.push({x:r+22*devicePixelRatio+Math.random()*(w-2*r-44*devicePixelRatio),y:r+Math.random()*(h-2*r),vx:Math.cos(angle)*SPEED*devicePixelRatio*.6,vy:Math.sin(angle)*SPEED*devicePixelRatio*.6,r:r});}}
function draw(){let w=cnv.width,h=cnv.height;ctx.clearRect(0,0,w,h);ctx.fillStyle='#F6EDE2';ctx.fillRect(0,0,w,h);
for(let i=0;i<nodes.length;i++){let p=nodes[i];if(active){p.x+=p.vx;p.y+=p.vy;if(p.x<p.r||p.x>w-p.r)p.vx*=-1;if(p.y<p.r||p.y>h-p.r)p.vy*=-1;p.x=Math.max(p.r,Math.min(w-p.r,p.x));p.y=Math.max(p.r,Math.min(h-p.r,p.y));}
for(let j=i+1;j<nodes.length;j++){let q=nodes[j],d=Math.hypot(p.x-q.x,p.y-q.y);if(d<50*devicePixelRatio){ctx.beginPath();ctx.setLineDash([3*devicePixelRatio,4*devicePixelRatio]);ctx.strokeStyle='rgba(168,105,63,'+(.26*(1-d/(50*devicePixelRatio)))+')';ctx.moveTo(p.x,p.y);ctx.lineTo(q.x,q.y);ctx.stroke();ctx.setLineDash([]);}}
let grad=ctx.createRadialGradient(p.x-p.r*.4,p.y-p.r*.4,p.r*.2,p.x,p.y,p.r);grad.addColorStop(0,'#F7CF9A');grad.addColorStop(.65,'#A66E4C');grad.addColorStop(1,'#573525');ctx.beginPath();ctx.fillStyle=grad;ctx.arc(p.x,p.y,p.r,0,Math.PI*2);ctx.fill();}
requestAnimationFrame(draw);}
document.getElementById('toggle').onclick=()=>{active=!active;document.getElementById('toggle').textContent=active?'Pausar':'Reanudar';};
window.addEventListener('resize',reset);reset();draw();
</script></body></html>'''
    return template.replace("__COUNT__",str(count)).replace("__SPEED__",str(speed))
