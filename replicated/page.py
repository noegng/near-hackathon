"""Render docs/index.html: one static, self-contained page (inline SVG, no dependencies, no network).

Reads the thesis snapshot and recomputes everything, so the page cannot drift from the build.
"""
from __future__ import annotations

import html
import json
import math
from pathlib import Path

from . import build, checks, compare, history, metrics

ROOT = Path(__file__).resolve().parent.parent
E = html.escape
REPO_URL = "https://github.com/noegng/proof-of-numbers"  # empty makes the page link relatively

CSS = """
:root{color-scheme:dark;--sans:"Space Grotesk",system-ui,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;--mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;
--surface:#020202;--panel:rgba(11,11,12,.9);--panel2:#141415;--line:#1c1c1f;--text:#fff;--text2:#a4a8bd;--muted:#777b91;--grid:#26262a;
--s1:#6a8cff;--s2:#ff7a45;--good:#00ec97;--warn:#f5c443;--crit:#ff5a5f;--blue:#3c50e0}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--surface);color:var(--text);font:16px/1.6 var(--sans);-webkit-font-smoothing:antialiased;overflow-x:hidden}
main{max-width:1120px;margin:0 auto;padding:0 28px 72px}
nav.toc{position:sticky;top:0;z-index:5;display:flex;align-items:center;gap:6px 22px;flex-wrap:wrap;margin:0 calc(50% - 50vw);padding:14px max(28px,calc(50vw - 532px));background:rgba(2,2,2,.72);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);border-bottom:1px solid var(--line);font:500 .74rem/1.4 var(--sans);letter-spacing:.02em;text-transform:uppercase}
nav.toc .brand{font:600 1.05rem/1 var(--sans);text-transform:none;letter-spacing:-.02em;margin-right:auto;text-decoration:none;color:var(--text)}nav.toc .brand span{color:var(--good)}
nav.toc a{text-decoration:none;color:var(--text2)}nav.toc a:hover{color:var(--text)}
nav.toc a.btn{background:var(--panel2);color:var(--text);padding:9px 14px;border-radius:10px}nav.toc a.btn:hover{background:var(--good);color:#020202}
.hero{position:relative;min-height:min(86vh,820px);display:flex;flex-direction:column;justify-content:flex-end;padding:120px 0 40px;isolation:isolate}
.aura{position:absolute;z-index:-1;top:-70px;bottom:0;left:50%;width:100vw;transform:translateX(-50%);overflow:hidden;pointer-events:none;background-color:var(--surface);
background-image:radial-gradient(38% 55% at 30% 52%,rgba(0,236,151,.72),transparent 70%),radial-gradient(34% 60% at 62% 30%,rgba(60,80,224,.85),transparent 70%),radial-gradient(30% 40% at 80% 70%,rgba(0,190,210,.45),transparent 72%),radial-gradient(25% 30% at 48% 40%,rgba(230,255,245,.35),transparent 70%)}
.aura svg{position:absolute;inset:0;width:100%;height:100%;mix-blend-mode:overlay;opacity:.9}
.aura::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(2,2,2,0) 55%,var(--surface) 98%)}
h1{font:500 clamp(2.8rem,8vw,6.2rem)/.98 var(--sans);letter-spacing:-.04em;margin:0 0 30px;max-width:11.5em;text-shadow:0 2px 40px rgba(0,0,0,.35)}
h1 em{font-style:normal;display:block;padding-left:1em}
.lede{font-size:1.2rem;line-height:1.5;max-width:34em;margin:0;color:#e9eaf0}
.meta{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:14px 28px;margin-top:56px;font:.82rem/1.4 var(--sans);color:var(--text2)}
.meta b{display:block;color:var(--text);font-weight:600;text-transform:uppercase;letter-spacing:-.01em;font-size:.95rem;margin-top:4px}
p{margin:10px 0;max-width:40em;color:var(--text2)}p b{color:var(--text)}.note{font-size:.82rem;line-height:1.55;color:var(--muted);max-width:62em}
a{color:inherit;text-decoration-color:var(--muted);text-decoration-thickness:1px;text-underline-offset:3px}a:hover{text-decoration-color:var(--good);color:var(--text)}
code{font:.82em var(--mono);background:var(--panel2);padding:2px 6px;border-radius:5px;white-space:nowrap;color:var(--text)}
section,header{scroll-margin-top:64px}section{margin-top:120px}
.kicker{font:500 .72rem/1 var(--mono);letter-spacing:.04em;text-transform:uppercase;color:var(--good);margin:0}
h2{font:500 clamp(2rem,4.4vw,3.2rem)/1.06 var(--sans);letter-spacing:-.035em;margin:14px 0 18px;max-width:18em}
h3{font:600 .98rem/1.3 var(--sans);letter-spacing:-.01em;margin:0 0 4px}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,380px),1fr));gap:20px;margin-top:20px}
.grid2>figure,.grid2>div{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:22px 24px;margin:0}
figure{margin:26px 0 0}figcaption{font:.84rem/1.45 var(--sans);color:var(--text2);margin-bottom:12px;max-width:46em}
svg{display:block;width:100%;height:auto;overflow:visible}svg text{fill:var(--text2);font:12px var(--sans);font-variant-numeric:tabular-nums}
svg .strong{fill:var(--text);font-weight:600}svg .axl{paint-order:stroke;stroke:var(--panel);stroke-width:4px;font-size:11px}.gridl{stroke:var(--grid);stroke-width:1}.hit{fill:transparent;cursor:crosshair}
.dot{opacity:0;pointer-events:none}.hit:hover+.dot{opacity:1}
.legend{display:flex;gap:8px 20px;flex-wrap:wrap;font:.8rem/1.3 var(--sans);color:var(--text2);margin:12px 0 10px}.legend i{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:7px}
.legend i.dia{border-radius:0;transform:rotate(45deg)}
table{border-collapse:collapse;width:100%;font:.84rem/1.45 var(--sans);font-variant-numeric:tabular-nums;margin-top:18px;color:var(--text2)}
th,td{text-align:left;padding:10px 16px 10px 0;border-bottom:1px solid var(--line);vertical-align:top}th:last-child,td:last-child{padding-right:0}
th{font:500 .68rem/1.3 var(--mono);letter-spacing:.03em;text-transform:uppercase;color:var(--muted);border-bottom-color:var(--grid);white-space:nowrap}
td.n,th.n{text-align:right;white-space:nowrap}td:first-child{white-space:nowrap;color:var(--text)}
details{margin:16px 0;border-top:1px solid var(--line);padding-top:14px}summary{cursor:pointer;font:600 .88rem/1.3 var(--sans)}summary:hover{color:var(--good)}
.st{font-weight:600;white-space:nowrap}.st.ok::before{content:"\\2713  ";color:var(--good)}.st.bad::before{content:"\\2717  ";color:var(--crit)}.st.wait::before{content:"\\25CB  ";color:var(--muted)}
.scroll{overflow-x:auto}
.mx td,.mx th{padding-right:12px}.mx td{white-space:nowrap}.mx td:first-child{white-space:normal;min-width:15em}.mx tfoot td{border-top:1px solid var(--grid);border-bottom:0;font-weight:600;color:var(--text)}.mx th{white-space:normal;vertical-align:bottom}
.m{display:inline-block;width:11px;height:11px;margin:0 3px 0 0;border-radius:50%;vertical-align:-1px;text-decoration:none}
.m.same{background:var(--good)}.m.close{background:var(--warn);border-radius:2px}
.m.miss{width:auto;height:auto;font:700 14px/11px var(--sans);color:var(--crit);vertical-align:0}.m:hover{outline:2px solid var(--text);outline-offset:1px}
.live{margin:28px 0 0;padding:14px 18px;background:var(--panel);border:1px solid var(--line);border-radius:12px;font:.84rem/1.55 var(--sans);color:var(--text2);max-width:none}.live b{color:var(--text)}.live .st{margin-right:2px;color:var(--text)}
footer{margin-top:120px;border-top:1px solid var(--line);padding-top:24px;display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:20px 40px;font:.82rem/1.6 var(--sans);color:var(--text2)}
footer b{display:block;font:500 .7rem/1 var(--mono);letter-spacing:.04em;text-transform:uppercase;color:var(--good);margin-bottom:8px}footer p{margin:0}
.tldr{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr));gap:16px;margin:8px 0 0}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:22px 24px}
.lab{font:500 .7rem/1 var(--mono);letter-spacing:.04em;text-transform:uppercase;color:var(--muted)}
.big{display:block;font:500 3.2rem/1 var(--sans);letter-spacing:-.05em;margin:16px 0 10px;font-variant-numeric:tabular-nums;color:var(--good)}.big small{font-size:.45em;color:var(--muted);letter-spacing:-.02em}
.card:nth-child(2) .big{color:var(--s1)}.card:nth-child(3) .big{color:var(--text)}
.card p{font:.9rem/1.5 var(--sans);color:var(--text2);margin:0}
.term{border-bottom:1px dotted var(--muted);cursor:help;color:var(--text)}
.glance{display:grid;grid-template-columns:minmax(0,11fr) minmax(0,8fr);gap:16px;margin-top:16px;align-items:stretch}
.glance>*{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:22px 24px;margin:0}.glance figcaption{margin:12px 0 0}
@media (max-width:820px){.glance{grid-template-columns:1fr}}
.steps{list-style:none;padding:0;margin:14px 0 0;display:grid;gap:18px;counter-reset:s}
.steps li{display:grid;grid-template-columns:34px 1fr;gap:12px;font:.87rem/1.45 var(--sans);color:var(--text2)}
.steps li::before{counter-increment:s;content:"0" counter(s);width:30px;height:30px;border-radius:8px;background:var(--panel2);color:var(--good);display:grid;place-items:center;font:500 .75rem var(--mono)}
.steps b{color:var(--text);display:block}
.finding{display:grid;grid-template-columns:minmax(0,5fr) minmax(0,6fr);gap:24px 44px;align-items:center;padding:40px 0;border-top:1px solid var(--line)}
.finding:first-of-type{border-top:0}.finding>figure{margin:0;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:22px 24px}.finding p{font-size:.98rem}
@media (max-width:820px){.finding{grid-template-columns:1fr}}
.fh{font:500 1.6rem/1.15 var(--sans);letter-spacing:-.035em;margin:12px 0 12px;display:flex;gap:12px;align-items:baseline}
.num{flex:none;font:500 .78rem/1 var(--mono);color:var(--good);background:var(--panel2);border-radius:8px;width:30px;height:30px;display:inline-grid;place-items:center;transform:translateY(-4px)}
.takeaway{border-left:2px solid var(--good);padding:2px 0 2px 14px;font:500 .92rem/1.5 var(--sans);color:var(--text);margin-top:16px}
.tag{display:inline-block;font:500 .66rem/1 var(--mono);letter-spacing:.04em;text-transform:uppercase;padding:6px 9px;border-radius:100px;border:1px solid}
.tag.ok{color:var(--good)}.tag.warn{color:var(--warn)}.tag.bad{color:var(--crit)}
svg .node{fill:var(--panel2);stroke:var(--grid)}svg .node.ok{fill:color-mix(in srgb,var(--good) 12%,var(--panel));stroke:var(--good)}svg .cap{font:500 10.5px var(--mono);letter-spacing:.04em;text-transform:uppercase;fill:var(--muted)}
.proscons ul{margin:10px 0 0;padding-left:18px;font:.9rem/1.5 var(--sans);color:var(--text2)}.proscons li{margin:0 0 10px}.proscons li b{color:var(--text)}
h3.pro{color:var(--good)}h3.con{color:var(--crit)}
.chks{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,300px),1fr));gap:14px;margin-top:16px}
.chk{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px 18px}.chk.ok{border-color:color-mix(in srgb,var(--good) 35%,var(--line))}.chk.bad{border-color:var(--crit)}
.chk-h{display:flex;justify-content:space-between;font:.86rem var(--sans)}.chk-h b{font:500 .8rem var(--mono);color:var(--muted)}.chk p{font:.88rem/1.45 var(--sans);margin:8px 0 0;color:var(--text)}.chk .chk-v{color:var(--muted);font-size:.8rem}.chk .chk-v b{color:var(--text)}
.gwrap{margin:30px 0 34px}.cap{font:500 .7rem/1 var(--mono);letter-spacing:.04em;text-transform:uppercase;color:var(--muted);margin:0 0 12px}
.gauge{display:flex;height:56px;border-radius:12px;overflow:hidden;background:var(--panel2);font:600 1rem/1 var(--sans)}
.gauge>div{display:flex;align-items:center;white-space:nowrap}.g-i{background:var(--good);color:#020202;padding-left:14px}.g-b{background:var(--warn)}.g-r{flex:1;padding-left:16px;color:var(--text);font-weight:500;overflow:hidden}
.g-leg{display:flex;flex-wrap:wrap;gap:6px 22px;font:.8rem/1.4 var(--sans);color:var(--text2);margin-top:12px}.g-leg i{display:inline-block;width:9px;height:9px;margin-right:7px;border-radius:2px}.g-gap{margin-left:auto}.g-leg b{color:var(--text)}
#bg{position:fixed;inset:0;width:100vw;height:100vh;z-index:-1;pointer-events:none}.gl .aura{display:none}
#tip{position:fixed;pointer-events:none;background:var(--text);color:var(--surface);padding:7px 10px;border-radius:8px;font:.78rem/1.35 var(--sans);display:none;z-index:9;max-width:280px}
@media (max-width:560px){body{font-size:15px}main{padding:0 18px 56px}nav.toc{padding:12px 18px;flex-wrap:nowrap;overflow-x:auto;white-space:nowrap}nav.toc .brand{margin-right:12px}
.hero{min-height:0;padding:80px 0 30px}h1 em{padding-left:0}section{margin-top:80px}.g-r{font-size:.78rem}.g-gap{margin-left:0}.big{font-size:2.6rem}}
"""


JS = """
const tip=document.getElementById('tip');
document.addEventListener('mousemove',e=>{const t=e.target.closest('[data-tip]');if(!t){tip.style.display='none';return}
tip.textContent=t.dataset.tip;tip.style.display='block';const w=tip.offsetWidth;
tip.style.left=Math.min(e.clientX+14,innerWidth-w-8)+'px';tip.style.top=(e.clientY+14)+'px'});
// Background: a slow green WebGL gradient behind the whole page. Full strength behind the hero; further down it dims
// and darkens the centre column, so text always sits on near-black. Without WebGL the static CSS gradient stays.
(()=>{const cv=document.createElement('canvas');cv.id='bg';const gl=cv.getContext('webgl',{antialias:false,alpha:false});if(!gl)return;
const VS='attribute vec2 a;void main(){gl_Position=vec4(a,0.,1.);}';
const FS=`precision mediump float;uniform vec2 R;uniform float T,K,C;
float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float n(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(h(i),h(i+vec2(1,0)),f.x),mix(h(i+vec2(0,1)),h(i+1.),f.x),f.y);}
float fbm(vec2 p){float v=0.,a=.5;for(int i=0;i<4;i++){v+=a*n(p);p=p*2.03+7.1;a*=.5;}return v;}
void main(){vec2 uv=gl_FragCoord.xy/R;uv.y=1.-uv.y;vec2 p=uv*vec2(R.x/R.y,1.)*1.3;float s=T*.012;
vec2 q=vec2(fbm(p+s),fbm(p+vec2(5.2,1.3)-s));float f=fbm(p+2.2*q+vec2(1.7,9.2)+.6*s);
float y=.30+.30*uv.x+.10*sin(uv.x*2.6+s*3.)+.12*(q.x-.5);float d=uv.y-y;
float band=exp(-d*d*16.),core=exp(-d*d*120.);
vec3 deep=vec3(.0,.13,.09),green=vec3(0.,.93,.59),mint=vec3(.75,1.,.9),blue=vec3(.20,.28,.85);
vec3 col=deep*smoothstep(.15,.75,f)*1.4;
col+=green*band*(.45+.55*f);col+=mint*core*.22*f;col+=blue*exp(-pow(uv.y-y+.22,2.)*20.)*.35*q.y;
float side=mix(1.,.18+.82*smoothstep(.16,.48,abs(uv.x-.5)),C);
col*=K*side;col+=(h(gl_FragCoord.xy+fract(T*7.))-.5)*.05*(.4+K);
gl_FragColor=vec4(max(col,0.),1.);}`;
const sh=(t,src)=>{const o=gl.createShader(t);gl.shaderSource(o,src);gl.compileShader(o);return gl.getShaderParameter(o,gl.COMPILE_STATUS)?o:null};
const v=sh(gl.VERTEX_SHADER,VS),f=sh(gl.FRAGMENT_SHADER,FS);if(!v||!f)return;
const pr=gl.createProgram();gl.attachShader(pr,v);gl.attachShader(pr,f);gl.linkProgram(pr);if(!gl.getProgramParameter(pr,gl.LINK_STATUS))return;
gl.useProgram(pr);gl.bindBuffer(gl.ARRAY_BUFFER,gl.createBuffer());gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,3,-1,-1,3]),gl.STATIC_DRAW);
const al=gl.getAttribLocation(pr,'a');gl.enableVertexAttribArray(al);gl.vertexAttribPointer(al,2,gl.FLOAT,false,0,0);
const U=k=>gl.getUniformLocation(pr,k),uR=U('R'),uT=U('T'),uK=U('K'),uC=U('C');
document.body.prepend(cv);document.documentElement.classList.add('gl');
const hero=document.querySelector('.hero'),still=matchMedia('(prefers-reduced-motion:reduce)').matches,S=.5;
let last=0,raf=0;
function size(){cv.width=Math.ceil(innerWidth*S);cv.height=Math.ceil(innerHeight*S);gl.viewport(0,0,cv.width,cv.height)}
function draw(ms){const m=Math.min(1,Math.max(0,scrollY/((hero?hero.offsetHeight:innerHeight)*.8)));
gl.uniform2f(uR,cv.width,cv.height);gl.uniform1f(uT,still?12.:ms/1000);gl.uniform1f(uK,.78-.42*m);gl.uniform1f(uC,.4+.6*m);gl.drawArrays(gl.TRIANGLES,0,3)}
function loop(ms){raf=requestAnimationFrame(loop);if(ms-last<33)return;last=ms;draw(ms)}
size();addEventListener('resize',()=>{size();draw(performance.now())});
if(still){draw(0);addEventListener('scroll',()=>draw(0),{passive:true})}else raf=requestAnimationFrame(loop)})();
"""


def money(v: float) -> str:
    a = abs(v)
    return f"${v / 1e9:.1f}B" if a >= 1e9 else f"${v / 1e6:.0f}M" if a >= 1e6 else f"${v / 1e3:.0f}K" if a >= 1e3 else f"${v:.0f}"


def count(v: float) -> str:
    a = abs(v)
    return f"{v / 1e6:.1f}M" if a >= 1e6 else f"{v / 1e3:.0f}K" if a >= 1e3 else f"{v:.0f}"


def nice_max(v: float) -> float:
    """Axis top at or above v whose quarters are round, so the four tick labels need no rounding."""
    import math
    if v <= 0:
        return 1.0
    mag = 10 ** math.floor(math.log10(v))
    for step in (1.2, 1.6, 2, 2.4, 3.2, 4, 4.8, 6, 8, 12):
        if v <= step * mag * (1 + 1e-9):
            return step * mag
    return 12 * mag


def spread(ys: list[float], gap: float) -> list[float]:
    """Move label positions apart until neighbours are at least `gap` apart, keeping their order and centre."""
    order = sorted(range(len(ys)), key=lambda i: ys[i])
    out = list(ys)
    for a, b in zip(order, order[1:]):
        if out[b] - out[a] < gap:
            out[b] = out[a] + gap
    shift = (math.fsum(out) - math.fsum(ys)) / len(ys)
    return [y - shift for y in out]


def place(xs: list[float], gap: float, lo: float, hi: float) -> list[float]:
    """Label positions in [lo, hi], at least `gap` apart, each as close to its own x as that allows."""
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    out = list(xs)
    prev = lo - gap
    for i in order:
        out[i] = prev = max(out[i], prev + gap)
    nxt = hi + gap
    for i in reversed(order):
        out[i] = nxt = min(out[i], nxt - gap)
    return out


MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def day_label(day: str) -> str:
    """'2026-11-08' -> '8 Nov'."""
    return f"{int(day[8:])} {MONTHS[int(day[5:7]) - 1]}"


def month_label(day: str) -> str:
    """'2026-11-11' -> 'Nov 26'."""
    return f"{MONTHS[int(day[5:7]) - 1]} {day[2:4]}"


def line_chart(xlabels: list[str], series: list[tuple[str, str, list[float]]], fmt, w=460, h=230) -> str:
    """series: (name, css color var, values). One shared y axis from zero."""
    L, R, T, B = 48, 96 if len(series) > 1 else 16, 12, 26
    top = nice_max(max(max(v) for _, _, v in series))
    n = len(xlabels)
    X = lambda i: L + (w - L - R) * i / (n - 1)
    Y = lambda v: T + (h - T - B) * (1 - v / top)
    o = [f'<svg viewBox="0 0 {w} {h}" role="img">']
    for k in range(5):
        v = top * k / 4
        o.append(f'<line class="gridl" x1="{L}" x2="{w - R}" y1="{Y(v):.1f}" y2="{Y(v):.1f}"/><text x="{L - 6}" y="{Y(v) + 4:.1f}" text-anchor="end">{fmt(v)}</text>')
    for i in (0, n // 2, n - 1):
        o.append(f'<text x="{X(i):.1f}" y="{h - 6}" text-anchor="{"start" if i == 0 else "end" if i == n - 1 else "middle"}">{E(xlabels[i])}</text>')
    ends = spread([Y(v[-1]) for _, _, v in series], 15)
    for (name, col, vals), ly in zip(series, ends):
        pts = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(vals))
        o.append(f'<polyline points="{pts}" fill="none" stroke="var({col})" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>')
        if len(series) > 1:
            o.append(f'<text class="strong" x="{X(n - 1) + 8:.1f}" y="{ly + 4:.1f}">{E(name)}</text>')
    for name, col, vals in series:
        for i, v in enumerate(vals):
            o.append(f'<circle class="hit" cx="{X(i):.1f}" cy="{Y(v):.1f}" r="{max(4, min(10, (w - L - R) / n / 2)):.1f}" data-tip="{E(name)}, {E(xlabels[i])}: {fmt(v)}"/>'
                     f'<circle class="dot" cx="{X(i):.1f}" cy="{Y(v):.1f}" r="4" fill="var({col})" stroke="var(--surface)" stroke-width="2"/>')
    return "".join(o) + "</svg>"


def bar_chart(labels: list[str], vals: list[float], fmt, w=940, h=240) -> str:
    L, R, T, B = 44, 8, 18, 26
    top = nice_max(max(vals))
    n = len(vals)
    slot = (w - L - R) / n
    bw = min(40, slot - 2)
    Y = lambda v: T + (h - T - B) * (1 - v / top)
    o = [f'<svg viewBox="0 0 {w} {h}" role="img">']
    for k in range(5):
        v = top * k / 4
        o.append(f'<line class="gridl" x1="{L}" x2="{w - R}" y1="{Y(v):.1f}" y2="{Y(v):.1f}"/><text x="{L - 6}" y="{Y(v) + 4:.1f}" text-anchor="end">{fmt(v)}</text>')
    hi = max(range(n), key=lambda i: vals[i])
    for i, v in enumerate(vals):
        x = L + slot * i + (slot - bw) / 2
        y, r = Y(v), min(4, max(0, (Y(0) - Y(v)) / 2))
        o.append(f'<path d="M{x:.1f},{Y(0):.1f}V{y + r:.1f}q0,-{r} {r},-{r}h{bw - 2 * r:.1f}q{r},0 {r},{r}V{Y(0):.1f}z" fill="var(--s1)" data-tip="{E(labels[i])}: {fmt(v)}"/>')
        if i in (hi, n - 1):
            o.append(f'<text class="strong" x="{x + bw / 2:.1f}" y="{y - 5:.1f}" text-anchor="middle">{fmt(v)}</text>')
        if i % 2 == (n - 1) % 2:
            o.append(f'<text x="{x + bw / 2:.1f}" y="{h - 6}" text-anchor="middle">{E(labels[i])}</text>')
    return "".join(o) + "</svg>"


def strip(rows: list[dict], w=940) -> str:
    """One row per quantity, each on its own scale from zero: team numbers as circles, ours as diamonds."""
    L, R, rh = 270, 60, 58
    h = rh * len(rows) + 8
    o = [f'<svg viewBox="0 0 {w} {h}" role="img">']
    for k, r in enumerate(rows):
        y = rh * k + 34
        top = nice_max(max(r["teams"] + [v for _, v in r["ours"]]))
        X = lambda v: L + (w - L - R) * v / top
        o.append(f'<text class="strong" x="0" y="{y - 4}">{E(r["label"])}</text><text x="0" y="{y + 11}">{len(r["teams"])} team numbers</text>')
        o.append(f'<line class="gridl" x1="{L}" x2="{w - R}" y1="{y}" y2="{y}"/><text x="{L - 8}" y="{y + 4}" text-anchor="end">0</text><text x="{w - R + 8}" y="{y + 4}">{r["fmt"](top)}</text>')
        last_x, level = None, 0
        for v, who in sorted(zip(r["teams"], r["who"])):
            # numbers closer than a dot's width stack upwards, so three teams quoting one figure show as three dots
            level = level + 1 if last_x is not None and X(v) - last_x < 9 else 0
            if level == 0:
                last_x = X(v)
            o.append(f'<circle cx="{last_x:.1f}" cy="{y - 7 - 11 * level}" r="6" fill="var(--s1)" stroke="var(--surface)" stroke-width="2" data-tip="{E(who)}: {r["fmt"](v)}"/>')
        for name, v in r["ours"]:
            x = X(v)
            o.append(f'<path d="M{x:.1f},{y}l7,7l-7,7l-7,-7z" fill="var(--s2)" stroke="var(--surface)" stroke-width="2" data-tip="Ours, {E(name)}: {r["fmt"](v)}"/>')
    return "".join(o) + "</svg>"


# Column of the team-by-metric matrix -> prefixes of the claim families it gathers.
GROUPS = (
    ("Intents volume", ("intents_volume", "intents_share")),
    ("Intents fees", ("intents_fees", "intents_take_rate")),
    ("Captured revenue", ("intents_capture", "intents_revenue", "revenue_yield", "mcap_over")),
    ("Issuance offset", ("issuance_cover", "burn_cover", "breakeven", "net_inflation")),
    ("Transactions", ("tx_",)),
    ("Accounts", ("active_accounts", "new_accounts")),
    ("L1 fees", ("l1_fees", "fees_over_l1", "revenue_over_l1")),
    ("Price", ("price_",)),
    ("Staking", ("staked", "validators")),
)


def group_of(family: str) -> str:
    for name, prefixes in GROUPS:
        if family.startswith(prefixes):
            return name
    raise KeyError(family)


def mark_class(c: dict) -> str:
    return {"reproduced": "same", "close": "close"}.get(c["at_publication"]["status"], "miss")


def compared_on(p: dict) -> str:
    return f'on {p["asof"]}' if p["dated"] else f'on our snapshot day {p["asof"]}'



def matrix(claims: list[dict]) -> str:
    """One row per team, one column per group of metrics, one mark per published number."""
    by = {}
    for c in claims:
        by.setdefault(c["project"], []).append(c)
    ok = lambda cs: sum(c["at_publication"]["status"] == "reproduced" for c in cs)
    head = "<th>Team</th>" + "".join(f"<th>{E(g)}</th>" for g, _ in GROUPS) + '<th class="n">Within 5%</th>'
    body = []
    for project, cs in sorted(by.items(), key=lambda kv: (-len(kv[1]), kv[0].lower())):
        repo = cs[0]["url"].split("/-/blob/")[0].split("/blob/")[0]
        cells = []
        for g, _ in GROUPS:
            marks = []
            for c in sorted((c for c in cs if group_of(c["family"]) == g), key=lambda c: c["id"]):
                b, cls = c["at_publication"], mark_class(c)
                tip = (f'{c["family"]}: {compare.fmt(c["claimed"], c["unit"])} published {c["published"][:10]}, '
                       f'ours {compare.fmt(b["ours"], c["unit"])} {compared_on(b)} ({b["gap"]:.1%} apart)')
                marks.append(f'<a class="m {cls}" href="{E(c["url"])}" data-tip="{E(tip)}" aria-label="{E(tip)}">{"&times;" if cls == "miss" else ""}</a>')
            cells.append(f"<td>{''.join(marks)}</td>")
        body.append(f'<tr><td><a href="{E(repo)}">{E(project)}</a></td>{"".join(cells)}<td class="n">{ok(cs)} of {len(cs)}</td></tr>')
    foot = "<td>All teams</td>" + "".join(
        f"<td>{ok(g_cs)} of {len(g_cs)}</td>" for g_cs in ([c for c in claims if group_of(c["family"]) == g] for g, _ in GROUPS)
    ) + f'<td class="n">{ok(claims)} of {len(claims)}</td>'
    return f'<div class="scroll"><table class="mx"><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody><tfoot><tr>{foot}</tr></tfoot></table></div>'


def table(head: list[str], rows: list[list[str]], num_cols=()) -> str:
    th = "".join(f'<th class="{"n" if i in num_cols else ""}">{E(h)}</th>' for i, h in enumerate(head))
    body = "".join("<tr>" + "".join(f'<td class="{"n" if i in num_cols else ""}">{c}</td>' for i, c in enumerate(r)) + "</tr>" for r in rows)
    return f'<div class="scroll"><table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'


STATUS_COLOR = {"reproduced": "--good", "close": "--warn", "not reproduced": "--crit"}


def waffle(claims: list[dict], per_row=20, cell=22, gap=4) -> str:
    """One square per published number, coloured by how close our recomputation is."""
    order = {"reproduced": 0, "close": 1, "not reproduced": 2}
    cs = sorted(claims, key=lambda c: (order[c["at_publication"]["status"]], c["family"], c["id"]))
    rows = math.ceil(len(cs) / per_row)
    w, h = per_row * (cell + gap) - gap, rows * (cell + gap) - gap
    o = [f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{len(cs)} published numbers by replication result">']
    for i, c in enumerate(cs):
        b = c["at_publication"]
        x, y = (i % per_row) * (cell + gap), (i // per_row) * (cell + gap)
        tip = (f'{c["project"]}, {c["family"]}: published {compare.fmt(c["claimed"], c["unit"])}, '
               f'ours {compare.fmt(b["ours"], c["unit"])} ({b["gap"]:.1%} apart)')
        o.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="var({STATUS_COLOR[b["status"]]})" data-tip="{E(tip)}"/>')
    return "".join(o) + "</svg>"


def box(x, y, w, h, lines, cls="node") -> str:
    o = [f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="6"/>']
    top = y + h / 2 - (len(lines) - 1) * 7.5 + 4
    for k, (t, strong) in enumerate(lines):
        c = ' class="strong"' if strong else ""
        o.append(f'<text{c} x="{x + w / 2:.1f}" y="{top + 15 * k:.1f}" text-anchor="middle">{E(t)}</text>')
    return "".join(o)


def arrow(x1, y1, x2, y2, dashed=False) -> str:
    dash = ' stroke-dasharray="4 4"' if dashed else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2 - 7}" y2="{y2}" stroke="var(--muted)" stroke-width="1.5"{dash}/>'
            f'<path d="M{x2},{y2}l-8,-4.5v9z" fill="var(--muted)"/>')


def source_diagram(n_teams: int, lo: float, hi: float, w=520, h=250) -> str:
    """Top route: one upstream dataset fans out to every team. Bottom route: our independent on-chain reading."""
    o = [f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="Where the Intents numbers come from">']
    o.append('<text class="cap" x="0" y="12">Route the teams used</text>')
    o.append(box(0, 30, 120, 50, [("NEAR datasets", True), ("on Dune", False)]))
    o.append(arrow(120, 55, 160, 55))
    o.append(box(160, 30, 110, 50, [("DefiLlama", True), ("adapter", False)]))
    cols, rws = 5, math.ceil(n_teams / 5)
    for i in range(n_teams):
        cx, cy = 340 + (i % cols) * 30, 30 + (i // cols) * (50 / max(1, rws - 1))
        o.append(f'<line x1="270" y1="55" x2="{cx - 8}" y2="{cy:.1f}" stroke="var(--grid)" stroke-width="1"/>')
    for i in range(n_teams):
        cx, cy = 340 + (i % cols) * 30, 30 + (i // cols) * (50 / max(1, rws - 1))
        o.append(f'<circle cx="{cx}" cy="{cy:.1f}" r="8" fill="var(--s1)" stroke="var(--surface)" stroke-width="2"/>')
    o.append(f'<text class="strong" x="400" y="{30 + 50 + 28}" text-anchor="middle">{n_teams} teams, one number</text>')
    o.append('<line x1="0" x2="520" y1="128" y2="128" class="gridl"/>')
    o.append('<text class="cap" x="0" y="150">Route we added, independent of DefiLlama</text>')
    o.append(box(0, 168, 120, 50, [("3 revenue wallets", True), ("on NEAR", False)]))
    o.append(arrow(120, 193, 160, 193))
    o.append(box(160, 168, 110, 50, [("Archival node", True), ("past balances", False)]))
    o.append(arrow(270, 193, 310, 193))
    o.append(box(310, 168, 210, 50, [(f"{lo:.2f}–{hi:.2f}× of reported", True), ("revenue ✓ they agree", False)], cls="node ok"))
    return "".join(o) + "</svg>"


def number_line(teams: list[tuple[str, float]], ours: list[tuple[str, float]], fmt, w=520, h=190) -> str:
    """Published values above the axis, our definitions below, labels pushed apart so they never overlap."""
    L, R, y = 10, 10, 95
    top = nice_max(max(v for _, v in teams + ours))
    X = lambda v: L + (w - L - R) * v / top
    o = [f'<svg viewBox="0 0 {w} {h}" role="img">', f'<line x1="{L}" x2="{w - R}" y1="{y}" y2="{y}" stroke="var(--muted)"/>']
    for k in range(5):
        v = top * k / 4
        o.append(f'<line x1="{X(v):.1f}" x2="{X(v):.1f}" y1="{y - 3}" y2="{y + 3}" stroke="var(--muted)"/>'
                 f'<text x="{X(v):.1f}" y="{y + 4}" dx="{-14 if k == 4 else 0}" text-anchor="{"end" if k == 4 else "start" if k == 0 else "middle"}" class="axl">{fmt(v)}</text>')
    for pts, sign, col in ((teams, -1, "--s1"), (ours, 1, "--s2")):
        lx = place([X(v) for _, v in pts], 150, L + 70, w - R - 70)
        for (name, v), tx in zip(pts, lx):
            x, my = X(v), y + sign * 13
            if sign < 0:
                o.append(f'<line x1="{x:.1f}" y1="{my - 7}" x2="{tx:.1f}" y2="{y - 44}" stroke="var(--grid)"/>'
                         f'<circle cx="{x:.1f}" cy="{my}" r="7" fill="var({col})" stroke="var(--surface)" stroke-width="2" data-tip="{E(name)}: {fmt(v)}"/>'
                         f'<text class="strong" x="{tx:.1f}" y="{y - 64}" text-anchor="middle">{fmt(v)}</text><text x="{tx:.1f}" y="{y - 49}" text-anchor="middle">{E(name)}</text>')
            else:
                o.append(f'<line x1="{x:.1f}" y1="{my + 8}" x2="{tx:.1f}" y2="{y + 44}" stroke="var(--grid)"/>'
                         f'<path d="M{x:.1f},{my - 8}l8,8l-8,8l-8,-8z" fill="var({col})" stroke="var(--surface)" stroke-width="2" data-tip="{E(name)}: {fmt(v)}"/>'
                         f'<text class="strong" x="{tx:.1f}" y="{y + 58}" text-anchor="middle">{fmt(v)}</text><text x="{tx:.1f}" y="{y + 73}" text-anchor="middle">{E(name)}</text>')
    return "".join(o) + "</svg>"


def fee_windows(days: list[str], ours: list[float], target: float, claims: list[dict], w=520, h=250) -> str:
    """Our 30-day fee total for each end day, a 5% band around the unexplained figure, and every team's 30-day fee claim."""
    L, R, T, B = 52, 12, 14, 26
    vals = ours + [target * 0.95] + [c["claimed"] for c in claims]
    lo = math.floor(min(vals) / 2e5) * 2e5
    hi = math.ceil(max(vals) / 2e5) * 2e5
    n = len(days)
    X = lambda i: L + (w - L - R) * i / (n - 1)
    Y = lambda v: T + (h - T - B) * (1 - (v - lo) / (hi - lo))
    o = [f'<svg viewBox="0 0 {w} {h}" role="img">']
    k = lo
    while k <= hi + 1:
        o.append(f'<line class="gridl" x1="{L}" x2="{w - R}" y1="{Y(k):.1f}" y2="{Y(k):.1f}"/><text x="{L - 6}" y="{Y(k) + 4:.1f}" text-anchor="end">${k / 1e6:.1f}M</text>')
        k += 4e5
    o.append(f'<rect x="{L}" y="{Y(target * 1.05):.1f}" width="{w - L - R}" height="{Y(target * 0.95) - Y(target * 1.05):.1f}" fill="var(--crit)" opacity=".13"/>'
             f'<line x1="{L}" x2="{w - R}" y1="{Y(target):.1f}" y2="{Y(target):.1f}" stroke="var(--crit)" stroke-dasharray="5 4"/>'
             f'<text x="{L + 6}" y="{Y(target * 0.95) - 6:.1f}" fill="var(--crit)" style="fill:var(--crit)">${target:,.0f} ± 5%</text>')
    for i in (0, n // 2, n - 1):
        o.append(f'<text x="{X(i):.1f}" y="{h - 6}" text-anchor="{"start" if i == 0 else "end" if i == n - 1 else "middle"}">{E(days[i][5:])}</text>')
    pts = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(ours))
    o.append(f'<polyline points="{pts}" fill="none" stroke="var(--s1)" stroke-width="2.2" stroke-linejoin="round"/>')
    for i, v in enumerate(ours):
        o.append(f'<circle class="hit" cx="{X(i):.1f}" cy="{Y(v):.1f}" r="6" data-tip="Our 30-day fees ending {E(days[i])}: {money(v)}"/>'
                 f'<circle class="dot" cx="{X(i):.1f}" cy="{Y(v):.1f}" r="4" fill="var(--s1)" stroke="var(--surface)" stroke-width="2"/>')
    stack = {}
    for c in sorted(claims, key=lambda c: c["claimed"]):
        b = c["at_publication"]
        if b["asof"] not in days:
            continue
        i = days.index(b["asof"])
        k = stack[i] = stack.get(i, -1) + 1
        o.append(f'<circle cx="{X(i) - 10 * k:.1f}" cy="{Y(c["claimed"]):.1f}" r="6" fill="var({STATUS_COLOR[b["status"]]})" stroke="var(--surface)" stroke-width="2" '
                 f'data-tip="{E(c["project"])}: {compare.fmt(c["claimed"], c["unit"])} for the 30 days to {E(b["asof"])}; ours {compare.fmt(b["ours"], c["unit"])}"/>')
    return "".join(o) + "</svg>"


def offset_gauge(intents: float, burn: float) -> str:
    """100% = NEAR created over 90 days. How much of it is offset, and by what. HTML, so its text stays legible on a phone."""
    rest = 100 - intents - burn
    return (f'<p class="cap">All NEAR created in the last 90 days = 100%</p>'
            f'<div class="gauge"><div class="g-i" style="width:{intents:.2f}%" data-tip="Offset by captured Intents revenue: {intents:.1f}%">{intents:.0f}%</div>'
            f'<div class="g-b" style="width:{burn:.2f}%" data-tip="Offset by base-layer fee burn: {burn:.1f}%"></div>'
            f'<div class="g-r" data-tip="Not offset: {rest:.1f}%">{rest:.0f}% not offset: holders are diluted</div></div>'
            f'<div class="g-leg"><span><i style="background:var(--good)"></i>Intents revenue, held on chain ({intents:.1f}%)</span>'
            f'<span><i style="background:var(--warn)"></i>Base-layer fee burn ({burn:.1f}%)</span>'
            f'<span class="g-gap">Gap to close: revenue must grow about <b>{100 / intents:.1f}&times;</b></span></div>')


def render(snapshot: str) -> str:
    raw = build.load_raw(snapshot)
    res = metrics.compute(raw)
    m = {k: v["value"] for k, v in res["metrics"].items()}
    rep = compare.run(snapshot)
    chk = checks.evaluate(res)
    reg = json.loads((ROOT / "claims" / "claims.json").read_text())
    s, fam = rep["summary"], {}
    for c in rep["claims"]:
        fam.setdefault(c["family"], []).append(c)
    pct = lambda v: f"{v:.1f}%"
    mult = lambda v: f"{v:.1f}x"
    ap = s["at_publication"]

    def fam_row(f, label, fmt, ours):
        return {"label": label, "fmt": fmt, "teams": [c["claimed"] for c in fam[f]], "who": [c["project"] for c in fam[f]],
                "ours": [(n, m[i]) for n, i in ours]}

    strips = [
        fam_row("issuance_cover", "Issuance offset by Intents revenue", pct,
                [("360 days, on chain", "wallet_growth_cover_of_net_issuance_pct_360d"), ("30 days, on chain", "wallet_growth_cover_of_net_issuance_pct_30d"), ("90 days, on chain", "wallet_growth_cover_of_net_issuance_pct_90d")]),
        fam_row("burn_cover", "Issuance offset by fee burn", lambda v: f"{v:.2f}%",
                [("30 days", "burn_cover_of_net_issuance_pct_30d"), ("90 days", "burn_cover_of_net_issuance_pct_90d"), ("365 days", "burn_cover_of_net_issuance_pct_365d")]),
        fam_row("breakeven_multiple", "Growth needed to offset issuance", mult,
                [("90 days", "breakeven_multiple_90d"), ("30 days", "breakeven_multiple_30d"), ("365 days", "breakeven_multiple_365d")]),
        fam_row("intents_fees_30d", "Intents gross fees, 30 days", lambda v: f"${v / 1e6:.2f}M", [("snapshot day", "intents_fees_30d")]),
        fam_row("intents_revenue_annualized", "Captured revenue, annualized", lambda v: f"${v / 1e6:.1f}M",
                [("90 days", "intents_revenue_annualized_90d"), ("30 days", "intents_revenue_annualized_30d")]),
        fam_row("price_yoy", "NEAR price change over a year", lambda v: f"+{v:.0f}%", [("day to day", "price_yoy"), ("30-day means", "price_yoy_30d_avg")]),
    ]
    wk = res["series"]["weekly_30d_means"]
    wv = res["series"]["wallets_vs_reported"]
    steps = res["series"]["wallet_cover_steps"]
    near = lambda v: f"{v / 1e6:.1f}M"

    # Finding 1: who reads the single upstream source, and our on-chain cross-check.
    intents_src = {c["source"] for c in reg["claims"] if c["family"].startswith("intents_")}
    via_llama = sum("defillama" in reg["sources"][x]["mentions"] for x in intents_src)
    ratios = [m[f"wallet_growth_over_defillama_revenue_{n}d"] for n in (30, 90, 360)]
    # Finding 2: one quantity, two definitions.
    price_teams = [(c["project"].replace("NEAR ", "").replace(" Thesis", ""), c["claimed"]) for c in sorted(fam["price_yoy"], key=lambda c: c["claimed"])]
    price_ours = [("ours, day vs day", m["price_yoy"]), ("ours, 30-day means", m["price_yoy_30d_avg"])]
    l1 = sorted(c["claimed"] for c in fam["l1_fees_usd_yoy"])
    # Finding 3: the 30-day fee total that matches no window.
    fees = metrics.llama_series(raw["llama_intents_fees"])
    fee_claims = fam["intents_fees_30d"]
    target = max(set(c["claimed"] for c in fee_claims), key=lambda v: sum(c["claimed"] == v for c in fee_claims))
    n_target = sum(abs(c["claimed"] - target) / target < 0.01 for c in fee_claims)
    last = metrics.day_of(res["asof"] + "T00:00:00Z")
    first = min(metrics.day_of(c["at_publication"]["asof"] + "T00:00:00Z") for c in fee_claims) - 4 * metrics.DAY
    fdays = list(range(first, last + 1, metrics.DAY))
    fee_iso = [metrics.datetime.fromtimestamp(d, metrics.timezone.utc).strftime("%Y-%m-%d") for d in fdays]
    fee_vals = [metrics.wsum(fees, d, 30) for d in fdays]
    t_day = next(c["at_publication"]["asof"] for c in fee_claims if c["claimed"] == target)
    t_ours = fee_vals[fee_iso.index(t_day)]
    best = min(range(len(fdays)), key=lambda i: abs(fee_vals[i] - target))
    others_ok = sum(c["at_publication"]["status"] == "reproduced" for c in fee_claims)

    status_cls = {"HOLDS": "ok", "HIT": "ok", "FAILS": "bad", "MISS": "bad", "PENDING": "wait"}
    unit = lambda c: {"%": "%", "x": "x"}.get(res["metrics"][c["metric"]]["unit"], "")
    check_rows = [[E(c["id"]), E(c["statement"]), E(c.get("due", "now")), f'{c["value"]:.3g}{unit(c)}',
                   f'<span class="st {status_cls[c["status"]]}">{c["status"].capitalize()}</span>'] for c in chk]
    claim_rows = [[E(c["family"]), E(c["project"]), compare.fmt(c["claimed"], c["unit"]), E(c["published"][:10]), E(c["at_publication"]["asof"]),
                   compare.fmt(c["at_publication"]["ours"], c["unit"]), f'{c["at_publication"]["gap"]:.1%}', E(c["at_publication"]["status"]),
                   f'<a href="{E(c["url"])}">quote</a>']
                  for c in sorted(rep["claims"], key=lambda c: (c["family"], c["claimed"]))]
    lo, hi = m["wallet_growth_cover_of_net_issuance_pct_360d"], m["wallet_growth_cover_of_net_issuance_pct_90d"]

    hist = history.run()
    newest = hist["snapshots"][-1]
    res_new = res if newest["snapshot"] == snapshot else metrics.compute(build.load_raw(newest["snapshot"]))
    chk_new = {c["id"]: c for c in checks.evaluate(res_new)}
    for row, c in zip(check_rows, chk):
        n = chk_new[c["id"]]
        row += [f'{n["value"]:.3g}{unit(n)}', f'<span class="st {status_cls[n["status"]]}">{n["status"].capitalize()}</span>']
    kills = [c for c in chk_new.values() if c["id"].startswith("K")]
    failed = [c["id"] for c in kills if c["status"] == "FAILS"]
    restated_new = [x for x in hist["restatements"] if x["newer"] == newest["snapshot"]]
    changed = sum(x["days_changed"] for x in restated_new)
    hist_url = REPO_URL + "/blob/main/out/history.md" if REPO_URL else "../out/history.md"
    live = (f'<b>Re-checked every day.</b> Newest snapshot {E(newest["snapshot"])} (data to {E(newest["asof"])}, {len(hist["snapshots"])} snapshots so far): '
            + (f'<span class="st ok">all {len(kills)} kill conditions hold</span>' if not failed else f'<span class="st bad">{E(", ".join(failed))} fails</span>')
            + f'; 90-day on-chain cover of net issuance {res_new["metrics"]["wallet_growth_cover_of_net_issuance_pct_90d"]["value"]:.1f}%'
            + (f'; past days changed by DefiLlama since the snapshot before: {changed}' if restated_new else "")
            + f'. <a href="{hist_url}">Every snapshot side by side</a>.')

    def threshold(c):
        t = c["threshold"]
        if c["op"] == "between":
            return f"between {t[0]:g}{unit(c)} and {t[1]:g}{unit(c)}"
        if isinstance(t, str):
            return f'above the earlier half-year ({m[t]:.3g}{unit(c)})'
        return f'{"above" if c["op"] == ">" else "at least"} {t:g}{unit(c)}'

    def check_card(c):
        n = chk_new[c["id"]]
        st = status_cls[n["status"]]
        word = {"ok": "Holds" if c["id"].startswith("K") else "Hit", "bad": "Fails" if c["id"].startswith("K") else "Missed", "wait": "Pending"}[st]
        due = f' &middot; due {E(c["due"])}' if "due" in c else ""
        return (f'<div class="chk {st}"><div class="chk-h"><b>{E(c["id"])}</b><span class="st {st}">{word}</span></div>'
                f'<p>{E(c["statement"])}</p><p class="chk-v">Today <b>{n["value"]:.3g}{unit(n)}</b> &middot; must be {threshold(c)}{due}</p></div>')

    kill_cards = "".join(check_card(c) for c in chk if c["id"].startswith("K"))
    pred_cards = "".join(check_card(c) for c in chk if c["id"].startswith("P"))
    cover90, burn90 = m["wallet_growth_cover_of_net_issuance_pct_90d"], m["burn_cover_of_net_issuance_pct_90d"]

    repo = f'<a href="{REPO_URL}">{E(REPO_URL.split("//")[-1])}</a>' if REPO_URL else "the repository"
    thesis = REPO_URL + "/blob/main/THESIS.md" if REPO_URL else "../THESIS.md"
    term = lambda word, tip: f'<span class="term" data-tip="{E(tip)}">{word}</span>'
    INTENTS = term("NEAR Intents", "NEAR's cross-chain swap and settlement product. Users trade, NEAR takes a fee.")
    ISSUANCE = term("new supply", "NEAR creates new tokens every epoch to pay validators (about 2.5% a year). Each new token dilutes existing holders.")
    CAPTURED = term("captured revenue", "The part of Intents fees that NEAR keeps. It arrives as NEAR in three public wallets.")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Proof of Numbers: NEAR, recomputed</title><meta name="description" content="{s['claims']} published NEAR numbers recomputed from raw data, and the investment thesis that survives."><style>{CSS}</style></head><body><main>
<nav class="toc"><a class="brand" href="#summary"><span>&#10035;</span> Proof of Numbers</a><a href="#findings">Findings</a><a href="#thesis">Thesis</a><a href="#tests">Kill switches</a><a href="#teams">Teams</a><a href="#data">Data</a><a class="btn" href="{REPO_URL or '..'}">Code &#8599;</a></nav>

<header id="summary">
<div class="hero"><div class="aura"><svg aria-hidden="true"><filter id="grain"><feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="3" stitchTiles="stitch"/><feColorMatrix type="saturate" values="0"/></filter><rect width="100%" height="100%" filter="url(#grain)"/></svg></div>
<h1>About thirty teams measured NEAR. <em>Do their numbers agree?</em></h1>
<p class="lede">We took {s['claims']} numbers published by {s['sources']} teams in this track, recomputed every one from raw public data, and built an investment thesis using only the numbers that hold up.</p>
<div class="meta"><span>Track<b>Investment Thesis</b></span><span>Teams checked<b>{s['sources']}</b></span><span>Numbers recomputed<b>{s['claims']}</b></span><span>Data to<b>{E(res['asof'])}</b></span></div>
</div>

<div class="tldr">
<div class="card"><span class="lab">What we checked</span><b class="big">{ap['reproduced']}<small> / {s['claims']}</small></b>
<p>published numbers are reproduced within 5% from raw data. {ap['close']} more are within 15%; {ap['not reproduced']} are further apart.</p></div>
<div class="card"><span class="lab">What no single team saw</span><b class="big">{via_llama}&nbsp;&rarr;&nbsp;1</b>
<p>{via_llama} teams publish {INTENTS} figures, and all {via_llama} read them from the same source. We added an independent on-chain check. It agrees.</p></div>
<div class="card"><span class="lab">The investment thesis</span><b class="big">{lo:.0f}&ndash;{hi:.0f}%</b>
<p>of NEAR's {ISSUANCE} is offset by {CAPTURED}. Owning NEAR is a bet that this revenue grows about {m['growth_multiple_to_offset_issuance_90d']:.1f}&times;, not a claim that the token is cheap.</p></div>
</div>

<div class="glance">
<figure><h3>Every square is one number a team published</h3>
<div class="legend"><span><i style="background:var(--good)"></i>Within 5% of ours: {ap['reproduced']}</span><span><i style="background:var(--warn)"></i>Within 15%: {ap['close']}</span><span><i style="background:var(--crit)"></i>Further apart: {ap['not reproduced']}</span></div>
{waffle(rep["claims"])}
<figcaption>Hover a square for the team, the published value and ours. Each number is compared on the day it was published.</figcaption></figure>
<div><h3>How it works</h3><ol class="steps">
<li><span><b>Collect</b>{s['claims']} numbers from {s['sources']} public repositories, each with its exact sentence and the commit that wrote it.</span></li>
<li><span><b>Download</b>Raw data from DefiLlama, NearBlocks and a NEAR archival node, saved byte for byte with SHA-256 hashes.</span></li>
<li><span><b>Recompute</b>Every number for the day it was published, under each standard definition (30, 90 or 365 days&hellip;).</span></li>
<li><span><b>Build and test</b>A thesis from what replicates. Its {len([c for c in chk if c['id'].startswith('K')])} kill conditions run as code and are re-checked every day.</span></li>
</ol></div>
</div>
<p class="live">{live}</p>
</header>

<section id="findings"><p class="kicker">Three findings</p>
<h2>What comparing {s['sources']} teams shows that no single thesis can</h2>

<div class="finding"><div><span class="tag ok">Confirmed independently</span>
<h3 class="fh"><span class="num">1</span>The teams agree because they read one source</h3>
<p>All {via_llama} teams that publish NEAR Intents volume, fees or revenue cite DefiLlama, which reads datasets NEAR itself uploads to Dune. Their agreement is one measurement read {via_llama} times, not {via_llama} confirmations.</p>
<p>So we measured revenue a second way. It arrives as NEAR in three public wallets, and an archival node can read their balances at past blocks. Their growth is <b>{min(ratios):.2f}&ndash;{max(ratios):.2f}&times;</b> the reported revenue over 30, 90 and 360 days.</p>
<p class="takeaway">The revenue figure behind every Intents thesis is real, and it can be checked on chain without trusting anyone.</p></div>
<figure>{source_diagram(via_llama, min(ratios), max(ratios))}</figure></div>

<div class="finding"><div><span class="tag warn">Explained</span>
<h3 class="fh"><span class="num">2</span>Where the numbers differ, the definition differs, not the data</h3>
<p>Three teams publish NEAR's price change over a year: +{price_teams[0][1]:.0f}%, +{price_teams[1][1]:.0f}% and +{price_teams[2][1]:.0f}%. All three are right. Comparing two single days gives +{m['price_yoy']:.0f}%; comparing two 30-day averages gives +{m['price_yoy_30d_avg']:.0f}%, because the price jumped in early November 2025.</p>
<p>The same holds for base-layer fees in dollars ({l1[0]:.0f}%, {l1[1]:.0f}% or {l1[2]:.0f}% in a year): each number is reproduced within 5% once the window and the end day match.</p>
<p class="takeaway">A single number without its definition means little. The spread between teams is the honest error bar.</p></div>
<figure><h3>NEAR price change over one year</h3>
<div class="legend"><span><i style="background:var(--s1)"></i>Published by a team</span><span><i class="dia" style="background:var(--s2)"></i>Our recomputation, per definition</span></div>
{number_line(price_teams, price_ours, lambda v: f"+{v:.0f}%")}</figure></div>

<div class="finding"><div><span class="tag bad">Unexplained</span>
<h3 class="fh"><span class="num">3</span>One figure does not replicate, and we say so</h3>
<p>{n_target} teams print 30-day Intents fees of <b>${target:,.0f}</b> (or a rounded version), all committed the same day. Our total for the day before is <b>${t_ours / 1e6:.2f}M</b>, {abs(t_ours - target) / target:.0%} higher. No 30-day window in the chart comes within 5%: the closest is ${fee_vals[best] / 1e6:.2f}M, for the window ending {E(day_label(fee_iso[best]))}.</p>
<p>Meanwhile {others_ok} other teams' fee totals land exactly on our line on their own publication days. Nor did the source rewrite its history: two snapshots a day apart agree on every past day.</p>
<p class="takeaway">We publish what we cannot explain instead of tuning it away.</p></div>
<figure><h3>Intents fees over 30 days, by the day the window ends</h3>
<div class="legend"><span><i style="background:var(--s1)"></i>Ours</span><span><i style="background:var(--good)"></i>Team, within 5%</span><span><i style="background:var(--warn)"></i>Team, 5 to 15% off</span></div>
{fee_windows(fee_iso, fee_vals, target, fee_claims)}</figure></div>
</section>

<section id="thesis"><p class="kicker">The investment thesis</p>
<h2>NEAR is a growth bet on Intents revenue, not a bargain</h2>
<p>NEAR creates about {m['net_inflation_annual_pct_90d']:.1f}% new tokens a year. Revenue from NEAR Intents now offsets part of that dilution, and the base layer offsets almost none. The thesis holds as long as that revenue keeps growing and stays in the wallets.</p>
<div class="gwrap">{offset_gauge(cover90, burn90)}</div>
<div class="grid2 proscons">
<div><h3 class="pro">Evidence for</h3><ul>
<li><b>Demand moved to Intents and grows:</b> {money(m['intents_volume_365d'])} settled in a year; the 30-day average is +{m['intents_volume_yoy_30d']:.0f}% on a year ago.</li>
<li><b>NEAR keeps a rising share of fees:</b> {m['intents_capture_share_365d']:.0f}% over a year, {m['intents_capture_share_30d']:.0f}% over the last 30 days.</li>
<li><b>The revenue is verifiable:</b> the wallets hold {m['revenue_wallets_near'] / 1e6:.2f}M NEAR and their total has never fallen.</li>
<li><b>The offset is rising:</b> {m['wallet_cover_pct_first_180d']:.1f}% of new supply in the first half of the year, {m['wallet_cover_pct_last_180d']:.1f}% in the second.</li></ul></div>
<div><h3 class="con">Evidence against</h3><ul>
<li><b>The base layer collapsed:</b> transactions {m['tx_yoy_30d']:.0f}%, new accounts {m['new_accounts_yoy_30d']:.0f}% in a year.</li>
<li><b>Holders are still diluted:</b> {100 - cover90 - burn90:.0f}% of new supply is offset by nothing.</li>
<li><b>The yield is thin:</b> captured revenue is {m['revenue_yield_on_mcap_pct_30d']:.2f}% of a {money(m['market_cap_usd'])} market cap a year; the market pays {m['mcap_over_intents_revenue_annualized_30d']:.0f}&times; revenue.</li>
<li><b>The captured NEAR is held, not burned:</b> it could be spent. The thesis depends on it not being spent.</li></ul></div>
</div>
<p class="note">Full argument, with every figure tied to the metric that produced it (a test fails if they disagree): <a href="{thesis}">THESIS.md</a>.</p></section>

<section id="tests"><p class="kicker">Falsification</p>
<h2>Five kill switches, checked automatically every day</h2>
<p>If any of these fails on new data, we drop the thesis: <code>python3 -m replicated.checks</code> exits with an error. A scheduled job downloads fresh data every day at 15:00 UTC and re-runs them.</p>
<div class="chks">{kill_cards}</div>
<h3 style="margin-top:30px">Four dated predictions, written on 2026-11-11</h3>
<div class="chks">{pred_cards}</div>
<details><summary>Same conditions as a table, thesis snapshot next to the newest one</summary>
{table(["Id", "Condition", "Due", f"Thesis snapshot {snapshot}", "Status", f"Newest snapshot {newest['snapshot']}", "Status"], check_rows, num_cols=(3, 5))}</details></section>

<section id="teams"><p class="kicker">Go deeper &middot; Team by team</p>
<h2>{s['sources']} teams, {s['claims']} published numbers, one recomputation</h2>
<p>Each mark is one number a team published, placed under the kind of quantity it measures. Hover for both values; click for the sentence it was read from, at a pinned commit.</p>
<div class="legend"><span><i class="m same"></i>Within 5%</span><span><i class="m close"></i>Within 15%</span><span><i class="m miss">&times;</i>Not reproduced</span></div>
{matrix(rep["claims"])}
<p class="note">Each number is compared on one day: the end day its sentence states, otherwise the last complete day before the commit that wrote it. There is no search over days. Where a family has several standard definitions (30, 90 or 365 days; net or gross issuance), the closest is used and named in the data tables below, so a match shows that a standard definition gives the number, not that the team computed it that way. Validators and stake ({s['undated']} numbers) are compared on our snapshot day, the only day the snapshot holds. On our snapshot day instead of each publication day, {s['at_snapshot']['reproduced']} of {s['claims']} are within 5%: a correct 30-day number drifts as the window moves on.</p></section>

<section><p class="kicker">Go deeper &middot; Definitions</p>
<h2>Six quantities, the teams' numbers next to ours</h2>
<p>Each row has its own scale starting at zero. Circles are numbers published by other teams; diamonds are our recomputation under different, equally defensible definitions. The circles spread about as widely as the diamonds do.</p>
<div class="legend"><span><i style="background:var(--s1)"></i>Published by a team</span><span><i class="dia" style="background:var(--s2)"></i>Our recomputation, per definition</span></div>
<figure>{strip(strips)}</figure></section>

<section><p class="kicker">Go deeper &middot; Revenue</p>
<h2>The revenue is on chain, and it is all still there</h2>
<p>Reported revenue does not have to be taken on trust. It arrives as NEAR in three wallets, and their balances at past block heights can be read from any archival node.</p>
<div class="grid2">
<figure><h3>Revenue wallets against reported revenue</h3><figcaption>NEAR held by the three wallets at 30-day block samples, next to DefiLlama's reported revenue accumulated from the first sample.</figcaption>
{line_chart([x['day'] for x in wv], [("On chain", "--s1", [x['wallets_near'] for x in wv]), ("Reported", "--s2", [x['defillama_cumulative_near'] for x in wv])], near)}</figure>
<figure><h3>Share of new supply offset, per 30-day step</h3><figcaption>Growth of the wallets divided by growth of total supply, both from block data. Lumpy, which is why a single 30-day reading misleads.</figcaption>
{bar_chart([month_label(x['to']) for x in steps], [x['cover_pct'] for x in steps], lambda v: f"{v:.0f}%", w=460, h=262)}</figure>
</div></section>

<section><p class="kicker">Go deeper &middot; Usage</p>
<h2>Usage left the base layer and went to Intents</h2>
<p>Two charts, two scales: transactions and dollars are not comparable on one axis. Intents volume and fees come from one upstream source (finding 1), so agreement between teams on these is not independent confirmation.</p>
<div class="grid2">
<figure><h3>Base-layer transactions per day</h3><figcaption>30-day mean, weekly samples. Now {count(m['tx_per_day_30d'])}, {m['tx_yoy_30d']:.0f}% in a year.</figcaption>
{line_chart([x['day'] for x in wk], [("Transactions per day", "--s1", [x['tx_per_day'] for x in wk])], count)}</figure>
<figure><h3>NEAR Intents volume per day</h3><figcaption>30-day mean, weekly samples. Now {money(m['intents_volume_avg_30d'])}, +{m['intents_volume_yoy_30d']:.0f}% in a year.</figcaption>
{line_chart([x['day'] for x in wk], [("Intents volume per day", "--s1", [x['intents_volume_usd_per_day'] for x in wk])], money)}</figure>
</div></section>

<section id="data"><p class="kicker">Go deeper &middot; Data</p>
<h2>Every claim we checked</h2>
<p class="note">"Commit date" is when the sentence quoting the number was committed. "Ours" is the closest standard definition on the day in "Compared on". A match means a standard definition gives the published number, not that the team computed it that way. Snapshot {E(snapshot)}; every figure on this page is generated by <code>python3 -m replicated.page</code> from raw data committed with its hashes.</p>
<details><summary>All {s['claims']} claims from {s['sources']} repositories</summary>
{table(["Metric", "Project", "Published", "Commit date", "Compared on", "Ours", "Gap", "Result", "Source"], claim_rows, num_cols=(2, 5, 6))}</details>
<details><summary>Data behind the charts</summary>
{table(["Sample", "Wallets, NEAR", "Reported cumulative, NEAR"], [[x['day'], f"{x['wallets_near']:,.0f}", f"{x['defillama_cumulative_near']:,.0f}"] for x in wv], num_cols=(1, 2))}
{table(["Step ending", "Wallet growth, NEAR", "Net issuance, NEAR", "Offset"], [[x['to'], f"{x['wallet_growth_near']:,.0f}", f"{x['net_issuance_near']:,.0f}", f"{x['cover_pct']:.1f}%"] for x in steps], num_cols=(1, 2, 3))}
</details></section>

<footer>
<div><b>Reproduce</b><p>Python 3.9+, standard library only. Clone {repo}, then <code>python3 -m replicated.build</code>. Runs offline from the committed snapshot.</p></div>
<div><b>Sources</b><p>DefiLlama (Intents volume, fees, revenue), NearBlocks (daily charts), a public archival RPC node (supply, wallet balances, validators). No API key.</p></div>
<div><b>Credit</b><p>The numbers under test belong to the teams quoted in the claims table, each linked to its source. Not investment advice. MIT license.</p></div>
</footer>
</main><div id="tip"></div><script>{JS}</script></body></html>
"""


def main() -> int:
    snap = build.thesis_snapshot()
    out = ROOT / "docs"
    out.mkdir(exist_ok=True)
    (out / "index.html").write_text(render(snap))
    print(f"docs/index.html written from snapshot {snap}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
