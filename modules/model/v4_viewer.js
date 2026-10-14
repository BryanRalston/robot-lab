import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
const box=document.getElementById('cadview'), info=document.getElementById('cadinfo'), lbl=document.getElementById('lbl');
const r=new THREE.WebGLRenderer({antialias:true}); r.setPixelRatio(Math.min(devicePixelRatio,2)); box.appendChild(r.domElement);
const sc=new THREE.Scene(); sc.background=new THREE.Color(0x15181d);
const cam=new THREE.PerspectiveCamera(35,1,0.01,50); cam.position.set(1.6,1.2,2.4);
const ctl=new OrbitControls(cam,r.domElement); ctl.target.set(0,0.8,0); ctl.update();
sc.add(new THREE.HemisphereLight(0xffffff,0x333344,1.3)); const dl=new THREE.DirectionalLight(0xffffff,1.5); dl.position.set(2,3,2); sc.add(dl);
sc.add(new THREE.GridHelper(2,20,0x444444,0x2a2a2a));
function size(){const w=box.clientWidth,h=box.clientHeight; r.setSize(w,h); cam.aspect=w/h; cam.updateProjectionMatrix();}
addEventListener('resize',size); size();
const meta=await (await fetch('cad/parts_v4.json')).json(); const byNode={}; meta.forEach(m=>byNode[m.node]=m);
const JT=await (await fetch('cad/joints_v4.json')).json();
const SC={BUILDABLE:'#1e7d43',PLACEHOLDER:'#b8641c',FAIL:'#b3261e'};
const parts=[]; let sel=null, selJ=null, showL=true;
new GLTFLoader().load('cad/bhl_v4.glb',g=>{ sc.add(g.scene);
  g.scene.traverse(o=>{ if(!o.isMesh) return; const m=byNode[o.name]||byNode[o.parent&&o.parent.name]; if(!m) return;
    const c=o.material.color?o.material.color.clone():new THREE.Color(0x999999);
    o.geometry.computeVertexNormals(); o.material=new THREE.MeshStandardMaterial({color:c,metalness:.25,roughness:.55,vertexColors:!!o.geometry.attributes.color});
    o.userData={m}; parts.push(o); });
});
// joint labels
const L=JT.map(j=>{const s=document.createElement('span'); s.textContent=j.name; s.style.background=SC[j.status]; lbl.appendChild(s); return [j,s];});
document.getElementById('labels').onclick=e=>{showL=!showL; e.target.textContent='Joint labels: '+(showL?'on':'off'); lbl.style.display=showL?'':'none';};
// joint buttons
const jb=document.getElementById('jbtns'); const AU={}; JT.forEach(j=>AU[j.name]=j);
[...new Set(JT.map(j=>j.joint))].forEach(k=>{const j=JT.find(x=>x.joint===k); const b=document.createElement('button'); b.className='jb'; b.textContent=k; b.style.borderColor=SC[j.status]; b.onclick=()=>pickJoint(k,b); jb.appendChild(b);});
function paint(){ for(const o of parts){ const hit=selJ&&o.userData.m.jparts; o.material.emissive.setHex(0);} }
function pickJoint(k,b){ document.querySelectorAll('.jb').forEach(x=>x.classList.remove('on')); if(selJ===k){selJ=null; for(const o of parts)o.material.emissive.setHex(0); info.textContent='Tap a part, or pick a joint below to highlight it.'; return;}
  selJ=k; b.classList.add('on'); const j=JT.find(x=>x.joint===k); const names=new Set(j.parts);
  for(const o of parts){ const m=o.userData.m; const on=names.has(m.name.replace(/^R_/,'L_'))||names.has(m.name); o.material.emissive.setHex(on?0xff00c8:0); o.material.emissiveIntensity=on?0.8:0; }
  info.innerHTML=`<b>${k}</b> <span class="st ${j.status}">${j.status}</span><br>${j.mech}<br><a href="#j_${k}">audit row ↓</a>`; }
const ray=new THREE.Raycaster(), pt=new THREE.Vector2(); let down=null;
r.domElement.addEventListener('pointerdown',e=>down=[e.clientX,e.clientY]);
r.domElement.addEventListener('pointerup',e=>{ if(!down||Math.hypot(e.clientX-down[0],e.clientY-down[1])>6) return;
  const b=r.domElement.getBoundingClientRect(); pt.set((e.clientX-b.left)/b.width*2-1,-(e.clientY-b.top)/b.height*2+1);
  ray.setFromCamera(pt,cam); const h=ray.intersectObjects(parts,false)[0];
  if(h){ const m=h.object.userData.m; info.innerHTML=`<b>${m.name}</b><br>segment ${m.seg} · ${m.group}${m.est?' · <span class="st PLACEHOLDER">estimate</span>':''}<br>moves with: ${m.joints.join(', ')||'pelvis (fixed)'}`; }});
const v=new THREE.Vector3();
(function loop(){ requestAnimationFrame(loop); r.render(sc,cam);
  if(showL){ const w=box.clientWidth,h=box.clientHeight; for(const [j,s] of L){ v.set(j.p[0],j.p[1],j.p[2]).project(cam); const vis=v.z<1&&Math.abs(v.x)<1.05&&Math.abs(v.y)<1.05; s.style.display=vis?'':'none'; s.style.left=((v.x+1)/2*w)+'px'; s.style.top=((1-v.y)/2*h)+'px'; s.style.outline=(selJ===j.joint)?'2px solid #ff3fd0':''; } }
})();
