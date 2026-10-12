import markdown, re, html
md=open('humanoid_plan_v1.md').read()
# split by h2
parts=re.split(r'^## ', md, flags=re.M)
head=parts[0]; secs=parts[1:]
def slug(s): return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
nav=[]; body=[]
segs=[]
for s in secs:
    title,_,content=s.partition('\n')
    sid=slug(title)
    nav.append(f'<a href="#{sid}">{html.escape(title)}</a>')
    if title.startswith('4.'):
        # break segment bullets into cards
        bullets=re.findall(r'^- \*\*(.+?)\*\*(.*)$',content,flags=re.M)
        rest=re.sub(r'^- \*\*.+$\n?','',content,flags=re.M)
        cards=[]
        for name,txt in bullets:
            nm=name.rstrip(':').split('(')[0].strip(); cid='seg-'+slug(nm)
            segs.append((cid,nm))
            cards.append(f'<div class="card" id="{cid}"><h3>{html.escape(nm)}</h3>{markdown.markdown("**"+name+"**"+txt)}</div>')
        h='<div class="svgbox">%%SVGBODY%%</div>'+''.join(cards)+markdown.markdown(rest,extensions=['tables'])
    else:
        h=markdown.markdown(content,extensions=['tables'])
        if title.startswith('5.'): h='<div class="svgbox">%%SVGHAND%%</div>'+h
        if title.startswith('8.'): h='<div class="svgbox">%%SVGPOWER%%</div>'+h
        if title.startswith('3.'): h='<div id="viewer"><div id="three"></div><div class="hint">Drag to rotate · scroll to zoom · hover a joint</div><div id="tip"></div></div>'+h
    body.append(f'<section id="{sid}"><h2>{html.escape(title)}</h2>{h}</section>')
segnav=''.join(f'<a class="sub" href="#{c}">{html.escape(n)}</a>' for c,n in segs)
navhtml=[]
for a in nav:
    navhtml.append(a)
    if '4.-mechanical' in a or 'mechanical-design' in a: navhtml.append(segnav)
intro=markdown.markdown(head,extensions=['tables'])
SVGBODY='''<svg viewBox="0 0 300 420" width="300" height="420" aria-label="Body segment diagram">
<style>.s{fill:#1f3b57;stroke:#7fb3e0;stroke-width:2}.j{fill:#f5a623}.t{fill:#cfe3f5;font:11px sans-serif}</style>
<rect class="s" x="125" y="10" width="50" height="55" rx="18"/><text class="t" x="185" y="35">Head</text>
<rect class="s" x="105" y="80" width="90" height="110" rx="12"/><text class="t" x="200" y="120">Torso/battery</text>
<rect class="s" x="115" y="195" width="70" height="35" rx="8"/><text class="t" x="190" y="215">Pelvis</text>
<rect class="s" x="65" y="85" width="30" height="100" rx="10"/><rect class="s" x="205" y="85" width="30" height="100" rx="10"/>
<rect class="s" x="60" y="190" width="28" height="90" rx="10"/><rect class="s" x="212" y="190" width="28" height="90" rx="10"/><text class="t" x="245" y="240">Forearm/hand</text>
<rect class="s" x="118" y="235" width="28" height="80" rx="10"/><rect class="s" x="154" y="235" width="28" height="80" rx="10"/><text class="t" x="190" y="280">Thigh</text>
<rect class="s" x="118" y="320" width="28" height="70" rx="10"/><rect class="s" x="154" y="320" width="28" height="70" rx="10"/><text class="t" x="190" y="360">Shank</text>
<rect class="s" x="108" y="395" width="40" height="14" rx="4"/><rect class="s" x="152" y="395" width="40" height="14" rx="4"/><text class="t" x="200" y="407">Foot</text>
<g class="j"><circle cx="150" cy="72" r="5"/><circle cx="80" cy="85" r="5"/><circle cx="220" cy="85" r="5"/><circle cx="74" cy="187" r="5"/><circle cx="226" cy="187" r="5"/><circle cx="132" cy="232" r="5"/><circle cx="168" cy="232" r="5"/><circle cx="132" cy="317" r="5"/><circle cx="168" cy="317" r="5"/><circle cx="132" cy="392" r="5"/><circle cx="168" cy="392" r="5"/><circle cx="150" cy="192" r="5"/></g>
<text class="t" x="5" y="415">● joint groups (see 3D view in §3)</text></svg>'''
SVGHAND='''<svg viewBox="0 0 260 260" width="260" height="260" aria-label="Hand DoF diagram"><style>.f{fill:#1f3b57;stroke:#7fb3e0;stroke-width:2}.j{fill:#f5a623}.t{fill:#cfe3f5;font:11px sans-serif}</style>
<rect class="f" x="70" y="130" width="110" height="100" rx="20"/>
<g>''' + ''.join(f'<rect class="f" x="{x}" y="30" width="20" height="100" rx="9"/><circle class="j" cx="{x+10}" cy="128" r="5"/><circle class="j" cx="{x+10}" cy="90" r="4"/><circle class="j" cx="{x+10}" cy="58" r="4"/>' for x in (75,100,125,150)) + '''</g>
<rect class="f" x="20" y="150" width="60" height="20" rx="9" transform="rotate(-35 50 160)"/><circle class="j" cx="70" cy="175" r="5"/><circle class="j" cx="40" cy="145" r="4"/>
<text class="t" x="5" y="250">Thumb 5 · fingers 4 each · palm arch 1 = 21 DoF</text></svg>'''
SVGPOWER='''<svg viewBox="0 0 520 140" width="520" height="140" aria-label="Power architecture"><style>.b{fill:#1f3b57;stroke:#7fb3e0;stroke-width:2}.t{fill:#cfe3f5;font:12px sans-serif}.l{stroke:#f5a623;stroke-width:2;marker-end:url(#a)}</style>
<defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8z" fill="#f5a623"/></marker></defs>
<rect class="b" x="10" y="45" width="110" height="50" rx="8"/><text class="t" x="20" y="67">3.0 kWh pack</text><text class="t" x="20" y="84">~88 V, swappable</text>
<line class="l" x1="120" y1="70" x2="190" y2="70"/>
<rect class="b" x="190" y="45" width="110" height="50" rx="8"/><text class="t" x="200" y="67">88 V main bus</text><text class="t" x="200" y="84">+ leg supercaps</text>
<line class="l" x1="300" y1="60" x2="380" y2="25"/><line class="l" x1="300" y1="70" x2="380" y2="70"/><line class="l" x1="300" y1="80" x2="380" y2="115"/>
<rect class="b" x="380" y="5" width="130" height="36" rx="8"/><text class="t" x="390" y="28">Body actuators 88 V</text>
<rect class="b" x="380" y="52" width="130" height="36" rx="8"/><text class="t" x="390" y="75">Hands 48 V (GaN)</text>
<rect class="b" x="380" y="99" width="130" height="36" rx="8"/><text class="t" x="390" y="122">Compute/sensors 12/5 V</text></svg>'''
content=''.join(body).replace('%%SVGBODY%%',SVGBODY).replace('%%SVGHAND%%',SVGHAND).replace('%%SVGPOWER%%',SVGPOWER)
JS=r'''
// sortable tables
document.querySelectorAll('table').forEach(t=>{const ths=t.querySelectorAll('th');ths.forEach((th,i)=>{th.title='Click to sort';th.addEventListener('click',()=>{const tb=t.tBodies[0];const rows=[...tb.rows];const asc=th.dataset.dir!=='asc';ths.forEach(h=>{delete h.dataset.dir});th.dataset.dir=asc?'asc':'desc';const num=s=>{const m=s.replace(/,/g,'').match(/-?\d+(\.\d+)?/);return m?parseFloat(m[0]):NaN};rows.sort((a,b)=>{const x=a.cells[i].innerText.trim(),y=b.cells[i].innerText.trim();const nx=num(x),ny=num(y);let r=(!isNaN(nx)&&!isNaN(ny))?nx-ny:x.localeCompare(y);return asc?r:-r});rows.forEach(r=>tb.appendChild(r))})})});
// active nav
const links=[...document.querySelectorAll('nav a')];const obs=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){links.forEach(l=>l.classList.toggle('active',l.getAttribute('href')==='#'+e.target.id))}}),{rootMargin:'-20% 0px -70% 0px'});document.querySelectorAll('section,.card').forEach(s=>obs.observe(s));
'''
THREE=r'''
<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}</script>
<script type="module">
import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
const el=document.getElementById('three'); if(el){
const W=el.clientWidth||600,H=480;
const r=new THREE.WebGLRenderer({antialias:true});r.setSize(W,H);r.setPixelRatio(devicePixelRatio);el.appendChild(r.domElement);
const sc=new THREE.Scene();sc.background=new THREE.Color(0x0e1a26);
const cam=new THREE.PerspectiveCamera(40,W/H,0.01,50);cam.position.set(2.2,1.2,2.2);
const oc=new OrbitControls(cam,r.domElement);oc.target.set(0,0.9,0);oc.update();
sc.add(new THREE.HemisphereLight(0xffffff,0x334455,1.2));const dl=new THREE.DirectionalLight(0xffffff,1);dl.position.set(2,4,3);sc.add(dl);
sc.add(new THREE.GridHelper(4,20,0x335577,0x223344));
// joint positions (m), name, DoF, actuator, torque
const J={
 neck:[0,1.55,0,'Neck yaw/pitch',2,'Strain-wave','10 N·m'],
 waist:[0,1.02,0,'Waist yaw/pitch/roll',3,'Cycloidal + 2 roller screws','250/400/250 N·m'],
 lsh:[0.21,1.42,0,'L shoulder (3)',3,'Strain-wave','180/150/80 N·m'],rsh:[-0.21,1.42,0,'R shoulder (3)',3,'Strain-wave','180/150/80 N·m'],
 lel:[0.23,1.13,0,'L elbow',1,'Roller screw','150 N·m'],rel:[-0.23,1.13,0,'R elbow',1,'Roller screw','150 N·m'],
 lwr:[0.24,0.86,0,'L wrist (3)',3,'Strain-wave + 2 linear','25/30 N·m'],rwr:[-0.24,0.86,0,'R wrist (3)',3,'Strain-wave + 2 linear','25/30 N·m'],
 lha:[0.25,0.76,0,'L hand',21,'Tendon, forearm motors','300 N grasp'],rha:[-0.25,0.76,0,'R hand',21,'Tendon, forearm motors','300 N grasp'],
 lhip:[0.1,0.92,0,'L hip (3)',3,'QDD planetary','150/300/400 N·m'],rhip:[-0.1,0.92,0,'R hip (3)',3,'QDD planetary','150/300/400 N·m'],
 lkn:[0.1,0.5,0,'L knee',1,'Roller screw','450 N·m'],rkn:[-0.1,0.5,0,'R knee',1,'Roller screw','450 N·m'],
 lan:[0.1,0.08,0,'L ankle (2)',2,'2× parallel linear','250/120 N·m'],ran:[-0.1,0.08,0,'R ankle (2)',2,'2× parallel linear','250/120 N·m'],
 lto:[0.1,0.02,0.14,'L toe',1,'QDD + belt','40 N·m'],rto:[-0.1,0.02,0.14,'R toe',1,'QDD + belt','40 N·m'],
 head:[0,1.68,0,null],chest:[0,1.42,0,null],pel:[0,0.92,0,null]};
const links=[['head','neck'],['neck','chest'],['chest','lsh'],['chest','rsh'],['lsh','lel'],['lel','lwr'],['lwr','lha'],['rsh','rel'],['rel','rwr'],['rwr','rha'],['chest','waist'],['waist','pel'],['pel','lhip'],['pel','rhip'],['lhip','lkn'],['lkn','lan'],['lan','lto'],['rhip','rkn'],['rkn','ran'],['ran','rto']];
const v=k=>new THREE.Vector3(...J[k].slice(0,3));
const lm=new THREE.MeshStandardMaterial({color:0x7fb3e0,metalness:.3,roughness:.5});
links.forEach(([a,b])=>{const A=v(a),B=v(b);const len=A.distanceTo(B);const g=new THREE.CylinderGeometry(0.025,0.025,len,12);const m=new THREE.Mesh(g,lm);m.position.copy(A).add(B).multiplyScalar(.5);m.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),B.clone().sub(A).normalize());sc.add(m)});
const head=new THREE.Mesh(new THREE.SphereGeometry(0.1,24,16),lm);head.position.copy(v('head'));sc.add(head);
const torso=new THREE.Mesh(new THREE.BoxGeometry(0.34,0.42,0.2),new THREE.MeshStandardMaterial({color:0x1f3b57,transparent:true,opacity:.6}));torso.position.set(0,1.2,0);sc.add(torso);
const pick=[];Object.entries(J).forEach(([k,d])=>{if(!d[3])return;const rad=0.03+Math.min(d[4],21)*0.004;const m=new THREE.Mesh(new THREE.SphereGeometry(rad,20,14),new THREE.MeshStandardMaterial({color:d[4]>=21?0x4cd964:0xf5a623,emissive:0x221100}));m.position.copy(v(k));m.userData=d;sc.add(m);pick.push(m)});
const ray=new THREE.Raycaster(),mp=new THREE.Vector2(),tip=document.getElementById('tip');
r.domElement.addEventListener('pointermove',e=>{const b=r.domElement.getBoundingClientRect();mp.x=(e.clientX-b.left)/b.width*2-1;mp.y=-(e.clientY-b.top)/b.height*2+1;ray.setFromCamera(mp,cam);const h=ray.intersectObjects(pick)[0];if(h){const d=h.object.userData;tip.style.display='block';tip.style.left=(e.clientX-b.left+12)+'px';tip.style.top=(e.clientY-b.top+12)+'px';tip.innerHTML=`<b>${d[3]}</b><br>${d[4]} DoF · ${d[5]}<br>Peak: ${d[6]} [EST]`}else tip.style.display='none'});
(function loop(){requestAnimationFrame(loop);r.render(sc,cam)})();
window.__threeOK=true;}
</script>'''
CSS='''*{box-sizing:border-box}body{margin:0;font:15px/1.55 system-ui,sans-serif;background:#0b141d;color:#dbe7f2}
nav{position:fixed;top:0;left:0;bottom:0;width:260px;overflow:auto;background:#101e2b;padding:16px;border-right:1px solid #1e3347}
nav h1{font-size:16px;margin:0 0 12px;color:#fff}nav a{display:block;color:#9fc3e3;text-decoration:none;padding:4px 6px;border-radius:4px;font-size:14px}
nav a.sub{padding-left:20px;font-size:13px;color:#7ea4c6}nav a.active,nav a:hover{background:#1f3b57;color:#fff}
main{margin-left:260px;padding:24px 40px;max-width:1200px}section{margin-bottom:40px;scroll-margin-top:10px}h2{border-bottom:2px solid #f5a623;padding-bottom:4px}
table{border-collapse:collapse;width:100%;font-size:13px;margin:12px 0;display:block;overflow-x:auto}th,td{border:1px solid #24405a;padding:6px 8px;vertical-align:top}
th{background:#16293b;cursor:pointer;user-select:none;position:sticky;top:0}th[data-dir=asc]:after{content:" ▲"}th[data-dir=desc]:after{content:" ▼"}tr:nth-child(even) td{background:#0f1c28}
a{color:#7fc4ff}.card{background:#101e2b;border:1px solid #1e3347;border-radius:8px;padding:10px 16px;margin:12px 0;scroll-margin-top:10px}.card h3{margin:4px 0;color:#f5a623}
.svgbox{background:#0e1a26;border:1px solid #1e3347;border-radius:8px;padding:10px;display:inline-block;margin:8px 0}
#viewer{position:relative;border:1px solid #1e3347;border-radius:8px;overflow:hidden;margin:10px 0}#three{width:100%;height:480px}
.hint{position:absolute;top:8px;left:10px;font-size:12px;color:#9fc3e3}#tip{position:absolute;display:none;background:#000c;padding:6px 8px;border-radius:6px;font-size:12px;pointer-events:none}
blockquote{border-left:4px solid #f5a623;margin:0;padding:4px 12px;background:#101e2b}'''
out=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Humanoid Design Spec v1</title><style>{CSS}</style></head>
<body><nav><h1>Humanoid Design v1</h1>{"".join(navhtml)}</nav><main><header>{intro}</header>{content}</main><script>{JS}</script>{THREE}</body></html>'''
open('humanoid_design.html','w').write(out)
print(len(out), [n for _,n in segs])
