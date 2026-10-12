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
CSS=open('build_html.py').read().split("CSS='''")[1].split("'''")[0]+'#three{height:520px}.legend{font-size:13px;color:#9fc3e3}.crumb{font-size:13px}'
JSsort=open('build_html.py').read().split("JS=r'''")[1].split("'''")[0]
nav=lambda cur:'<h1><a href="index.html" style="padding:0;color:#fff">Humanoid Design v1</a></h1>'+f'<a href="index.html"{" class=active" if cur=="index" else ""}>Overview (assembled)</a>'+''.join(f'<a href="{k}.html"{" class=active" if cur==k else ""}>{html.escape(t)}</a>' for k,t,_,_ in PAGES)+f'<a href="sim.html"{" class=active" if cur=="sim" else ""}>▶ Physics sim (MuJoCo)</a>'
def page(fn,cur,title,inner,focus):
    imp='<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}</script>'
    js='<script type="module">'+open('site/robot.js').read()+'\nmount(document.getElementById("three"), '+json.dumps(focus)+');</script>'
    open('site/'+fn,'w').write(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><style>{CSS}</style>{imp}</head><body><nav>{nav(cur)}</nav><main>{inner}</main><script>{JSsort}</script>{js}</body></html>')
viewer='<div id="viewer"><div id="three"></div><div class="hint">%s</div><div id="tip"></div></div>'
for k,t,joints,body in PAGES:
    inner=f'<p class="crumb"><a href="index.html">← Overview</a></p><h2>{html.escape(t)}</h2>'+viewer%('Drag to rotate · scroll to zoom · hover joints for actuator/torque')+'<p class="legend">Highlighted: this part. Values marked [EST] are design targets.</p>'+M(body).replace('<p>%%SVGHAND%%</p>',SVGHAND).replace('<p>%%SVGPOWER%%</p>',SVGPOWER)
    page(k+'.html',k,t,inner,{'part':k,'focus':joints})
head=md.split('## 1.')[0]
cards=''.join(f'<a class="card" style="display:block" href="{k}.html"><h3>{html.escape(t)}</h3></a>' for k,t,_,_ in PAGES)
idx=M(head)+viewer%('Drag to rotate · hover a joint · <b>click a part to open its page</b>')+'<h2>Parts</h2>'+cards+'<section><h2>'+secs['2'][0]+'</h2>'+M(secs['2'][1])+'</section><section><h2>'+secs['1'][0]+'</h2>'+M(secs['1'][1])+'</section><section><h2>Full joint table</h2>'+M(secs['3'][1])+'</section><section><h2>Sources</h2>'+M(md.split('## Sources')[1])+'</section>'
page('index.html','index','Humanoid Design v1 — Overview',idx,{'part':'index','focus':[]})
print('ok')
# ---- sim page ----
xmlsrc=open('sim/humanoid.xml').read()
open('site/humanoid.xml','w').write(xmlsrc)
simjs=open('site/sim_app.js').read()
inner='''<p class="crumb"><a href="index.html">← Overview</a></p><h2>Physics simulation (MuJoCo WASM)</h2>
<p>This is the design's MJCF model (<a href="humanoid.xml">humanoid.xml</a>, 67.7 kg, 33 actuated body joints, torque limits from the joint table) running live in your browser with the official <code>@mujoco/mujoco</code> 3.14 WebAssembly build. Controller: joint-space PD holding the standing pose, with torques clipped to each actuator's limit. Hands are rigid bodies in this version.</p>
<p><button id="pause">Pause</button> <button id="reset">Reset</button> <button id="push">Push pelvis</button> force <input id="force" type="range" min="-300" max="300" value="100" oninput="fv.textContent=this.value"> <span id="fv">100</span> N for 0.2 s</p>
<div id="viewer"><div id="three"></div><div class="hint">Drag to rotate · scroll to zoom</div></div><p id="simstatus">Loading MuJoCo WASM…</p>
<p class="legend">Offline Python test: stands indefinitely; survives forward pushes up to ~125 N for 0.2 s with plain PD. There is no stepping or balance controller yet, so larger pushes make it fall.</p>
<script type="text/plain" id="mjcf">'''+xmlsrc+'</script>'
imp='<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}</script>'
open('site/sim.html','w').write(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Simulation</title><style>{CSS}</style>{imp}</head><body><nav>{nav("sim")}</nav><main>{inner}</main><script type="module">{simjs}</script></body></html>')
print('sim ok')
