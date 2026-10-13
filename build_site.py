import markdown, re, html, json
md=open('humanoid_plan_v1.md').read()
secs={}
for s in re.split(r'^## ',md,flags=re.M)[1:]:
    t,_,c=s.partition('\n'); secs[t.split('.')[0]]=(t,c)
M=lambda s: markdown.markdown(s,extensions=['tables'])
def seg(name):
    m=re.search(r'^- \*\*'+re.escape(name)+r'.*$',secs['4'][1],flags=re.M); return m.group(0)+'\n' if m else ''
jt=secs['3'][1]; hdr='\n'.join(jt.split('\n')[jt.split('\n').index([l for l in jt.split('\n') if l.startswith('| # ')][0]):][:2])
def rows(nums): return hdr+'\n'+'\n'.join(l for l in jt.split('\n') if re.match(r'\| (\d+) \|',l) and int(re.match(r'\| (\d+)',l).group(1)) in nums)+'\n'
sensors=secs['6'][1]
def sens(keys): 
    ls=sensors.strip().split('\n'); return '\n'.join(ls[:2]+[l for l in ls[2:] if any(l.startswith('| '+k) for k in keys)])+'\n'
PAGES=[
 ('head','Head & sensors',['head','neck'], '### Joints\n'+rows([15])+'\n### Structure\n'+seg('Head')+'\n### Sensors\n'+sens(['Head','Chest','Pelvis','Skin'])),
 ('torso','Torso, spine, power & compute',['chest','waist'], '### Joints\n'+rows([7,8])+'\n### Structure\n'+seg('Torso')+seg('Spine')+seg('Covers')+seg('Fasteners')+'\n### Compute & electronics\n'+secs['7'][1]+'\n### Power\n%%SVGPOWER%%\n'+secs['8'][1]+'\n### Thermal\n'+secs['9'][1]),
 ('arms','Shoulders & arms',['lsh','rsh','lel','rel','lwr','rwr'], '### Joints\n'+rows([9,10,11,12,13,14])+'\n### Structure\n'+seg('Shoulder girdle')+seg('Upper arm')+'\n### Sensors\n'+sens(['Wrists','Joints','Skin'])),
 ('hands','Hands (2 × 21 DoF)',['lha','rha'], '%%SVGHAND%%\n'+secs['5'][1]),
 ('hips','Hips & pelvis',['lhip','rhip','pel'], '### Joints\n'+rows([1,2,3])+'\n### Structure\n'+seg('Pelvis')+'\n### Sensors\n'+sens(['Pelvis','Joints'])),
 ('legs','Legs & feet',['lkn','rkn','lan','ran','lto','rto'], '### Joints\n'+rows([4,5,6])+'\n### Structure\n'+seg('Thigh')+seg('Shank')+seg('Foot')+'\n### Sensors\n'+sens(['Feet','Joints'])),
 ('control','Control & AI stack',[], secs['10'][1]+'\n### Design risks\n'+secs['11'][1]),
]
SVGHAND='<div class="svgbox"><svg viewBox="0 0 260 260" width="260" height="260"><style>.f{fill:#1f3b57;stroke:#7fb3e0;stroke-width:2}.j{fill:#f5a623}.t{fill:#cfe3f5;font:11px sans-serif}</style><rect class="f" x="70" y="130" width="110" height="100" rx="20"/>'+''.join(f'<rect class="f" x="{x}" y="30" width="20" height="100" rx="9"/><circle class="j" cx="{x+10}" cy="128" r="5"/><circle class="j" cx="{x+10}" cy="90" r="4"/><circle class="j" cx="{x+10}" cy="58" r="4"/>' for x in (75,100,125,150))+'<rect class="f" x="20" y="150" width="60" height="20" rx="9" transform="rotate(-35 50 160)"/><circle class="j" cx="70" cy="175" r="5"/><circle class="j" cx="40" cy="145" r="4"/><text class="t" x="5" y="250">Thumb 5 · fingers 4 each · palm arch 1 = 21 DoF</text></svg></div>'
SVGPOWER='<div class="svgbox"><svg viewBox="0 0 520 140" width="520" height="140"><style>.b{fill:#1f3b57;stroke:#7fb3e0;stroke-width:2}.t{fill:#cfe3f5;font:12px sans-serif}.l{stroke:#f5a623;stroke-width:2}</style><rect class="b" x="10" y="45" width="110" height="50" rx="8"/><text class="t" x="20" y="67">3.0 kWh pack</text><text class="t" x="20" y="84">~88 V, swappable</text><line class="l" x1="120" y1="70" x2="190" y2="70"/><rect class="b" x="190" y="45" width="110" height="50" rx="8"/><text class="t" x="200" y="67">88 V main bus</text><text class="t" x="200" y="84">+ leg supercaps</text><line class="l" x1="300" y1="60" x2="380" y2="25"/><line class="l" x1="300" y1="70" x2="380" y2="70"/><line class="l" x1="300" y1="80" x2="380" y2="115"/><rect class="b" x="380" y="5" width="130" height="36" rx="8"/><text class="t" x="390" y="28">Body actuators 88 V</text><rect class="b" x="380" y="52" width="130" height="36" rx="8"/><text class="t" x="390" y="75">Hands 48 V (GaN)</text><rect class="b" x="380" y="99" width="130" height="36" rx="8"/><text class="t" x="390" y="122">Compute/sensors 12/5 V</text></svg></div>'
CSS=open('build_html.py').read().split("CSS='''")[1].split("'''")[0]+'#three{height:520px}'+'\n.topbar{display:none}\ntable{display:table;width:100%}.tw{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:12px 0}.tw table{margin:0}\n#three{height:min(62vh,520px)}#three canvas{touch-action:none;display:block}\n#tip a{color:#ffd27f;pointer-events:auto}\n.controls{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:10px 0}.controls button{min-height:44px;min-width:88px;font-size:16px;border-radius:8px;border:1px solid #3a6a95;background:#1f3b57;color:#fff;padding:8px 14px}\n.controls input[type=range]{flex:1;min-width:160px;height:32px}\n@media (max-width:820px){\n body{font-size:16px}\n .topbar{display:flex;position:sticky;top:0;z-index:20;background:#101e2b;border-bottom:1px solid #1e3347;align-items:center;gap:10px;padding:8px 12px}\n .topbar button{font-size:22px;background:none;border:1px solid #3a6a95;color:#fff;border-radius:8px;width:44px;height:44px}\n .topbar a{color:#fff;font-weight:600;text-decoration:none;font-size:16px}\n nav{transform:translateX(-100%);transition:transform .2s;z-index:30;width:80vw;max-width:300px;box-shadow:4px 0 20px #000a}\n body.navopen nav{transform:none}\n nav a{padding:10px 8px;font-size:16px}\n main{margin-left:0;padding:12px 14px}\n h2{font-size:20px}main h1{font-size:26px;line-height:1.25}th,td{font-size:13px;padding:6px}\n #three{height:62vh}.svgbox{display:block;overflow-x:auto}.svgbox svg{max-width:100%;height:auto}\n .controls{flex-direction:column;align-items:stretch}.controls button{width:100%}\n}'+'.legend{font-size:13px;color:#9fc3e3}.crumb{font-size:13px}'
JSsort=open('build_html.py').read().split("JS=r'''")[1].split("'''")[0]
nav=lambda cur:'<h1><a href="index.html" style="padding:0;color:#fff">Humanoid Design v1</a></h1>'+f'<a href="index.html"{" class=active" if cur=="index" else ""}>Overview (assembled)</a>'+''.join(f'<a href="{k}.html"{" class=active" if cur==k else ""}>{html.escape(t)}</a>' for k,t,_,_ in PAGES)+f'<a href="sim.html"{" class=active" if cur=="sim" else ""}>▶ Physics sim (MuJoCo)</a>'+'<div style="margin:12px 0 4px;color:#f5a623;font-size:12px;letter-spacing:.08em">V2 · BHL → OPTIMUS-CLASS</div>'+''.join(f'<a href="{f}.html"{" class=active" if cur==f else ""}>{t}</a>' for f,t in [('v2','v2 design'),('v2_checks','v2 engineering checks'),('v2_sim','▶ v2 balance sim'),('v2_cad','v2 CAD + FEA')])+'<div style="margin:12px 0 4px;color:#5ad17a;font-size:12px;letter-spacing:.08em">V3 · HARDENING LOOP</div>'+''.join(f'<a href="{f}.html"{" class=active" if cur==f else ""}>{t}</a>' for f,t in [('v3','v3 dashboard + CAD'),('v3_checks','v3 checks, parts, revisions'),('v3_sim','▶ v3 sim (CAD parts)')])
NAVJS='<script>document.querySelectorAll("nav a").forEach(a=>a.addEventListener("click",()=>document.body.classList.remove("navopen")));document.querySelector("main").addEventListener("click",()=>document.body.classList.remove("navopen"))</script>'
def wrap(h):
    h=h
    i=h.rfind('</body>'); h=h[:i]+NAVJS+h[i:]
    return h.replace('<table>','<div class="tw"><table>').replace('</table>','</table></div>')
def page(fn,cur,title,inner,focus):
    imp='<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}</script>'
    js='<script type="module">'+open('site/robot.js').read()+'\nmount(document.getElementById("three"), '+json.dumps(focus)+');</script>'
    open('site/'+fn,'w').write(wrap(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><style>{CSS}</style>{imp}</head><body><div class="topbar"><button aria-label="Menu" onclick="document.body.classList.toggle(\'navopen\')">☰</button><a href="index.html">Humanoid Design v1</a></div><nav>{nav(cur)}</nav><main>{inner}</main><script>{JSsort}</script>{js}</body></html>'))
viewer='<div id="viewer"><div id="three"></div><div class="hint">%s</div><div id="tip"></div></div>'
for k,t,joints,body in PAGES:
    inner=f'<p class="crumb"><a href="index.html">← Overview</a></p><h2>{html.escape(t)}</h2>'+viewer%('Drag to rotate · pinch/scroll to zoom · hover or tap joints for actuator/torque')+'<p class="legend">Highlighted: this part. Values marked [EST] are design targets.</p>'+M(body).replace('<p>%%SVGHAND%%</p>',SVGHAND).replace('<p>%%SVGPOWER%%</p>',SVGPOWER)
    page(k+'.html',k,t,inner,{'part':k,'focus':joints})
head=md.split('## 1.')[0]
cards=''.join(f'<a class="card" style="display:block" href="{k}.html"><h3>{html.escape(t)}</h3></a>' for k,t,_,_ in PAGES)
idx=M(head)+viewer%('Drag to rotate · pinch/scroll to zoom · <b>click or tap a part to open its page</b>')+'<h2>Parts</h2>'+cards+'<section><h2>'+secs['2'][0]+'</h2>'+M(secs['2'][1])+'</section><section><h2>'+secs['1'][0]+'</h2>'+M(secs['1'][1])+'</section><section><h2>Full joint table</h2>'+M(secs['3'][1])+'</section><section><h2>Sources</h2>'+M(md.split('## Sources')[1])+'</section>'
page('index.html','index','Humanoid Design v1 — Overview',idx,{'part':'index','focus':[]})
print('ok')
# ---- sim page ----
xmlsrc=open('sim/humanoid.xml').read()
open('site/humanoid.xml','w').write(xmlsrc)
simjs=open('site/sim_app.js').read()
inner='''<p class="crumb"><a href="index.html">← Overview</a></p><h2>Physics simulation (MuJoCo WASM)</h2>
<p>This is the design's MJCF model (<a href="humanoid.xml">humanoid.xml</a>, 67.7 kg, 33 actuated body joints, torque limits from the joint table) running live in your browser with the official <code>@mujoco/mujoco</code> 3.14 WebAssembly build. Controller: joint-space PD holding the standing pose, with torques clipped to each actuator's limit. Hands are rigid bodies in this version.</p>
<div class="controls"><button id="pause">Pause</button><button id="reset">Reset</button><button id="push">Push pelvis</button><label>Push force <span id="fv">100</span> N (0.2 s)</label><input id="force" type="range" min="-300" max="300" value="100" oninput="fv.textContent=this.value"></div>
<div id="viewer"><div id="three"></div><div class="hint">Drag to rotate · pinch/scroll to zoom</div></div><p id="simstatus">Loading MuJoCo WASM…</p>
<p class="legend">Offline Python test: stands indefinitely; survives forward pushes up to ~125 N for 0.2 s with plain PD. There is no stepping or balance controller yet, so larger pushes make it fall.</p>
<script type="text/plain" id="mjcf">'''+xmlsrc+'</script>'
imp='<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}</script>'
open('site/sim.html','w').write(wrap(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Simulation</title><style>{CSS}</style>{imp}</head><body><div class="topbar"><button aria-label="Menu" onclick="document.body.classList.toggle(\'navopen\')">☰</button><a href="index.html">Humanoid Design v1</a></div><nav>{nav("sim")}</nav><main>{inner}</main><script type="module">{simjs}</script></body></html>'))
print('sim ok')

# ---- v2 section ----
TOPBAR=r'''<div class="topbar"><button aria-label="Menu" onclick="document.body.classList.toggle(\'navopen\')">☰</button><a href="index.html">Humanoid Design v1</a></div>'''.replace("\\'","'")
def simple(fn,cur,title,inner,extra=''):
    imp='<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}</script>'
    open('site/'+fn,'w').write(wrap(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><style>{CSS}</style>{imp}</head><body>'+TOPBAR+f'<nav>{nav(cur)}</nav><main>{inner}</main><script>{JSsort}</script>{extra}</body></html>'))
v2md=open('v2/DESIGN.md').read()
simple('v2.html','v2','Robot Lab v2 design',M(v2md)+'<p><a href="v2_checks.html">→ Engineering check results</a> · <a href="v2_sim.html">→ Balance sim</a> · <a href="https://github.com/BryanRalston/robot-lab/tree/main/v2">source on GitHub</a></p>')
ck='<h1>v2 engineering checks</h1><p>Generated by <code>v2/analysis/checks.py</code>. <b>Final (v2.1)</b> first, then the <b>initial (v2.0)</b> run whose failures drove the fixes. All inputs are estimates unless sourced.</p>'
ck+='<h2>Final design (v2.1)</h2>'+M(open('v2/analysis/results/checks_final.md').read().split('\n',1)[1])
ck+='<h2>Initial design (v2.0), before fixes</h2>'+M(open('v2/analysis/results/checks_initial.md').read().split('\n',1)[1])
simple('v2_checks.html','v2_checks','v2 engineering checks',ck)
x2=open('sim/v2/humanoid_v2.xml').read();open('site/humanoid_v2.xml','w').write(x2)
inner2='''<h2>v2 balance simulation (MuJoCo WASM)</h2>
<p>The v2 model (<a href="humanoid_v2.xml">humanoid_v2.xml</a>, 64.4 kg, 30 actuators, torque limits = checked actuator capacities) running live. Controller: <b>scripted</b> joint PD + center-of-mass ankle strategy (no RL yet). In offline tests it stands 20 s and recovers from 0.2 s pushes of about 175 N forward and 125 to 175 N sideways. Turn balance OFF to see that plain PD with bent knees falls.</p>
<div class="controls"><button id="bal">Balance: ON</button><button id="pause">Pause</button><button id="reset">Reset</button><button id="push">Push pelvis</button>
<label>Direction <select id="pdir" style="font-size:16px;min-height:36px"><option value="0">forward (+x)</option><option value="1">sideways (+y)</option></select></label>
<label>Push force <span id="fv">150</span> N (0.2 s)</label><input id="force" type="range" min="-300" max="300" value="150" oninput="fv.textContent=this.value"></div>
<div id="viewer"><div id="three"></div><div class="hint">Drag to rotate · pinch/scroll to zoom</div></div><p id="simstatus">Loading MuJoCo WASM…</p>
<script type="text/plain" id="mjcf">'''+x2+'</script>'
simple('v2_sim.html','v2_sim','v2 balance sim',inner2,'<script type="module">'+open('site/sim_v2_app.js').read()+'</script>')
print('v2 ok')

cadmd=open('v2/cad/out/mass.md').read()+'\n\n'+open('v2/cad/out/fea.md').read()+'\n\n'+open('v2/cad/RESULTS.md').read()
innerc=('<h2>v2 parametric CAD (CadQuery)</h2><p id="cadload">loading…</p>'
 '<div id="cadview" style="width:100%;height:min(75vh,640px);border-radius:8px;overflow:hidden;touch-action:none"></div>'
 '<p><button id="cadexp" style="padding:10px 18px;font-size:16px">Explode</button> <span id="cadinfo">Tap a part to see its name, material and mass.</span></p>'
 '<p>Downloads: <a href="https://github.com/BryanRalston/robot-lab/raw/main/v2/cad/export/bhl_v2_assembly.step">STEP assembly</a> · <a href="cad/bhl_v2.glb">GLB</a> · <a href="https://github.com/BryanRalston/robot-lab/tree/main/v2/cad">CAD source</a></p>'+M(cadmd))
simple('v2_cad.html','v2_cad','v2 CAD + FEA',innerc,'<script type="module">'+open('site/cad_app.js').read().replace("await (await fetch","await (await fetch")+'</script>')

# ---- v3 section ----
import os
D3=json.load(open('v3/dashboard.json'))
def badge(st): return {'PASS':'<span style="background:#1e7d43;color:#fff;padding:2px 8px;border-radius:6px">PASS</span>','FAIL':'<span style="background:#b3261e;color:#fff;padding:2px 8px;border-radius:6px">FAIL</span>','OPEN':'<span style="background:#a66b00;color:#fff;padding:2px 8px;border-radius:6px">UNVERIFIED</span>'}[st]
dash='<div class="tw"><table><thead><tr><th>area</th><th>check</th><th>result</th><th>status</th></tr></thead><tbody>'+''.join(f'<tr><td>{html.escape(a)}</td><td>{html.escape(c)}</td><td>{html.escape(r)}</td><td>{badge(s_)}</td></tr>' for a,c,r,s_ in D3['rows'])+'</tbody></table></div>'
cnt={k:sum(1 for x in D3['rows'] if x[3]==k) for k in ('PASS','FAIL','OPEN')}
inner3=(f'<h2>Robot Lab v3: hardening loop</h2><p>{html.escape(D3["summary"])}</p>'
 f'<p><b>{cnt["PASS"]} pass · {cnt["FAIL"]} fail · {cnt["OPEN"]} unverifiable without hardware</b></p>'
 '<p id="cadload">loading CAD…</p><div id="cadview" style="width:100%;height:min(70vh,600px);border-radius:8px;overflow:hidden;touch-action:none"></div>'
 '<p><button id="cadexp" style="padding:10px 18px;font-size:16px;min-height:44px">Explode</button> <span id="cadinfo">Tap a part to see its name, material and mass.</span></p>'
 '<p>Downloads: <a href="https://github.com/BryanRalston/robot-lab/raw/main/v3/cad/export/bhl_v3_assembly.step">STEP assembly</a> · <a href="cad/bhl_v3.glb">GLB</a> · <a href="humanoid_v3.xml">MuJoCo MJCF</a> · <a href="https://github.com/BryanRalston/robot-lab/tree/main/v3">source</a> · <a href="https://github.com/BryanRalston/robot-lab/blob/main/v3/REVISIONS.md">revision log</a> · <a href="https://github.com/BryanRalston/robot-lab/blob/main/v3/PARTS.md">parts table</a></p>'
 '<h2>Pass / fail dashboard</h2>'+dash)
simple('v3.html','v3','Robot Lab v3 dashboard + CAD',inner3,'<script type="module">'+open('site/cad_app_v3.js').read()+'</script>')
ck3=('<h1>v3 checks, parts and revisions</h1><p>Generated by <code>v3/analysis/v3.py</code>, <code>v3/cad/*.py</code> and <code>v3/report.py</code>.</p>'
 +M(open('v3/analysis/results/v3_checks.md').read().split('\n',1)[1])
 +'<h2>CAD interference, cables, mass</h2>'+M(open('v3/cad/out/cables.md').read().split('\n',1)[1])+M(open('v3/cad/out/mass.md').read().split('\n',1)[1])
 +'<h2>FEA</h2>'+M(open('v3/cad/out/fea_v3.md').read().split('\n',1)[1])
 +M(open('v3/PARTS.md').read())+M(open('v3/REVISIONS.md').read())
 +'<h2>Before fixes (v3.0 = v2 with catalog parts)</h2>'+M(open('v3/analysis/results/v3_initial.md').read().split('\n',1)[1]))
simple('v3_checks.html','v3_checks','v3 checks, parts, revisions',ck3)
x3=open('sim/v3/humanoid_v3.xml').read();open('site/humanoid_v3.xml','w').write(x3)
inner4=('<h2>v3 simulation with CAD parts (MuJoCo WASM)</h2>'
 f'<p>MJCF generated from the v3 CAD (<a href="humanoid_v3.xml">humanoid_v3.xml</a>, {D3["sim"]["mass"]:.1f} kg; joint locations, per-segment mass/COM/inertia from the CAD, torque limits = catalog actuator peaks). The 3D view draws the actual CAD parts attached to the simulated bodies; collisions use simple shapes (toggle to see them). Controller: scripted joint PD + COM ankle strategy. {html.escape(D3["sim"]["text"])}</p>'
 '<div class="controls"><button id="bal">Balance: ON</button><button id="pause">Pause</button><button id="reset">Reset</button><button id="push">Push pelvis</button><button id="cadtog" disabled>Show: CAD parts</button>'
 '<label>Direction <select id="pdir" style="font-size:16px;min-height:36px"><option value="0">forward (+x)</option><option value="1">sideways (+y)</option></select></label>'
 '<label>Push force <span id="fv">100</span> N (0.2 s)</label><input id="force" type="range" min="-300" max="300" value="100" oninput="fv.textContent=this.value"></div>'
 '<div id="viewer"><div id="three"></div><div class="hint">Drag to rotate · pinch/scroll to zoom</div></div><p id="simstatus">Loading MuJoCo WASM…</p>'
 '<script type="text/plain" id="mjcf">'+x3+'</script><script type="application/json" id="ids">'+json.dumps(D3['ids'])+'</script>')
simple('v3_sim.html','v3_sim','v3 sim with CAD parts',inner4,'<script type="module">'+open('site/sim_v3_app.js').read()+'</script>')
print('v3 ok')
