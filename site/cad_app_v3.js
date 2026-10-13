import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
const box=document.getElementById('cadview'), info=document.getElementById('cadinfo');
const r=new THREE.WebGLRenderer({antialias:true}); r.setPixelRatio(Math.min(devicePixelRatio,2)); box.appendChild(r.domElement);
const sc=new THREE.Scene(); sc.background=new THREE.Color(0x15181d);
const cam=new THREE.PerspectiveCamera(35,1,0.01,50); cam.position.set(1.5,1.3,3.0);
const ctl=new OrbitControls(cam,r.domElement); ctl.target.set(0,0.85,0); ctl.update();
sc.add(new THREE.HemisphereLight(0xffffff,0x333344,1.2)); const dl=new THREE.DirectionalLight(0xffffff,1.6); dl.position.set(2,3,2); sc.add(dl);
const grid=new THREE.GridHelper(2,20,0x444444,0x2a2a2a); sc.add(grid);
function size(){const w=box.clientWidth,h=box.clientHeight; r.setSize(w,h); cam.aspect=w/h; cam.updateProjectionMatrix();}
addEventListener('resize',size); size();
const meta=await (await fetch('cad/parts_v3.json')).json(); const byId={}; meta.forEach(m=>byId[m.id]=m);
const parts=[]; let ex=0, exT=0, sel=null;
new GLTFLoader().load('cad/bhl_v3.glb',g=>{
  sc.add(g.scene);
  g.scene.traverse(o=>{ if(o.isMesh){ const m=byId[o.name]||byId[o.parent&&o.parent.name]; if(!m) return;
     const n=m.name, col=/battery/.test(n)?0x2a5aa0:/compute/.test(n)?0x1e8c5a:/motor|Harmonic|drive/.test(n)?0xb87333:/bearing|bolts/.test(n)?0x5a6068:/tendon|drum/.test(n)?0xf0c83c:({'7075-T6':0xb0b8c4,'CFRP':0x3a3d44,'steel':0x8a8e96,'Ti-6Al-4V':0x9a8c80,'PA12':0xe6e6e1}[m.material]??0x999999);
     o.geometry.computeVertexNormals(); o.material=new THREE.MeshStandardMaterial({color:col,metalness:.3,roughness:.5});
     // explode direction: outward from the body's centre, segment-weighted
     const c=new THREE.Vector3(...m.c), d=c.clone().sub(new THREE.Vector3(0,0.9,0)); d.y*=0.6;
     const seg=m.seg.replace(/^[LR]_/,''); const k={foot:1.4,shank:1.2,thigh:1.0,hipR:.8,hipY:.7,pelvis:.6,head:1.2,hand:1.5,forearm:1.3,upper_arm:1.1,shoulderP:.9}[seg]||.5;
     o.userData={m,base:o.position.clone(),dir:d.multiplyScalar(k)}; parts.push(o);} });
  document.getElementById('cadload').textContent=`${meta.length} parts · CAD mass ${meta.reduce((a,b)=>a+b.mass_kg,0).toFixed(1)} kg`;
});
document.getElementById('cadexp').onclick=e=>{exT=exT?0:1; e.target.textContent=exT?'Assemble':'Explode';};
const ray=new THREE.Raycaster(), pt=new THREE.Vector2(); let down=null;
r.domElement.addEventListener('pointerdown',e=>down=[e.clientX,e.clientY]);
r.domElement.addEventListener('pointerup',e=>{ if(!down||Math.hypot(e.clientX-down[0],e.clientY-down[1])>6) return;
  const b=r.domElement.getBoundingClientRect(); pt.set((e.clientX-b.left)/b.width*2-1,-(e.clientY-b.top)/b.height*2+1);
  ray.setFromCamera(pt,cam); const h=ray.intersectObjects(parts,false)[0];
  if(sel){sel.material.emissive.setHex(0);} sel=h?h.object:null;
  if(sel){sel.material.emissive.setHex(0x553300); const m=sel.userData.m;
    info.innerHTML=`<b>${m.name}</b><br>segment: ${m.seg}<br>material: ${m.material}<br>mass: ${(m.mass_kg*1000).toFixed(0)} g <span style="color:#999">(${m.mass_src})</span>`;}
  else info.textContent='Tap a part to see its name, material and mass.';});
(function loop(){ requestAnimationFrame(loop); ex+=(exT-ex)*0.12;
  for(const o of parts){o.position.copy(o.userData.base).addScaledVector(o.userData.dir,ex*0.6);} r.render(sc,cam); })();
