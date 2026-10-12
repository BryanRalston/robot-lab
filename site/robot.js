import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
// joint: [x,y,z,label,DoF,actuator,torque,part]
export const J={
 neck:[0,1.55,0,'Neck yaw/pitch',2,'Strain-wave','10 N·m','head'],
 waist:[0,1.02,0,'Waist yaw/pitch/roll',3,'Cycloidal + 2 roller screws','250/400/250 N·m','torso'],
 lsh:[0.21,1.42,0,'L shoulder',3,'Strain-wave','180/150/80 N·m','arms'],rsh:[-0.21,1.42,0,'R shoulder',3,'Strain-wave','180/150/80 N·m','arms'],
 lel:[0.23,1.13,0,'L elbow',1,'Planetary roller screw','150 N·m','arms'],rel:[-0.23,1.13,0,'R elbow',1,'Planetary roller screw','150 N·m','arms'],
 lwr:[0.24,0.86,0,'L wrist',3,'Strain-wave roll + 2 linear','25/30 N·m','arms'],rwr:[-0.24,0.86,0,'R wrist',3,'Strain-wave roll + 2 linear','25/30 N·m','arms'],
 lha:[0.25,0.76,0,'L hand',21,'Tendon, forearm motors','300 N grasp','hands'],rha:[-0.25,0.76,0,'R hand',21,'Tendon, forearm motors','300 N grasp','hands'],
 lhip:[0.1,0.92,0,'L hip yaw/roll/pitch',3,'QDD planetary','150/300/400 N·m','hips'],rhip:[-0.1,0.92,0,'R hip yaw/roll/pitch',3,'QDD planetary','150/300/400 N·m','hips'],
 lkn:[0.1,0.5,0,'L knee',1,'Roller screw + linkage','450 N·m','legs'],rkn:[-0.1,0.5,0,'R knee',1,'Roller screw + linkage','450 N·m','legs'],
 lan:[0.1,0.08,0,'L ankle pitch/roll',2,'2× parallel linear','250/120 N·m','legs'],ran:[-0.1,0.08,0,'R ankle pitch/roll',2,'2× parallel linear','250/120 N·m','legs'],
 lto:[0.1,0.02,0.14,'L toe',1,'QDD + belt','40 N·m','legs'],rto:[-0.1,0.02,0.14,'R toe',1,'QDD + belt','40 N·m','legs'],
};
const P={head:[0,1.68,0,'head'],chest:[0,1.42,0,'torso'],pel:[0,0.92,0,'hips']};
const pos=k=>new THREE.Vector3(...(J[k]||P[k]).slice(0,3));
const partOf=k=>(J[k]||P[k])[J[k]?7:3];
const L=[['head','neck','head'],['neck','chest','head'],['chest','lsh','arms'],['chest','rsh','arms'],['lsh','lel','arms'],['lel','lwr','arms'],['lwr','lha','hands'],['rsh','rel','arms'],['rel','rwr','arms'],['rwr','rha','hands'],['chest','waist','torso'],['waist','pel','torso'],['pel','lhip','hips'],['pel','rhip','hips'],['lhip','lkn','legs'],['lkn','lan','legs'],['lan','lto','legs'],['rhip','rkn','legs'],['rkn','ran','legs'],['ran','rto','legs']];
export function mount(el,{part,focus}){
 if(!el)return;const W=el.clientWidth||800,H=el.clientHeight||520;
 const r=new THREE.WebGLRenderer({antialias:true});r.setSize(W,H);r.setPixelRatio(devicePixelRatio);el.appendChild(r.domElement);
 const sc=new THREE.Scene();sc.background=new THREE.Color(0x0e1a26);
 const cam=new THREE.PerspectiveCamera(40,W/H,0.01,50);
 const oc=new OrbitControls(cam,r.domElement);
 sc.add(new THREE.HemisphereLight(0xffffff,0x334455,1.2));const dl=new THREE.DirectionalLight(0xffffff,1);dl.position.set(2,4,3);sc.add(dl);
 sc.add(new THREE.GridHelper(4,20,0x335577,0x223344));
 const isIdx=part==='index'||part==='control';
 const on=p=>isIdx||p===part;
 const mat=p=>new THREE.MeshStandardMaterial({color:on(p)?0x7fb3e0:0x3a4a5a,metalness:.3,roughness:.5,transparent:!on(p),opacity:on(p)?1:.25});
 const clickable=[];
 const add=(m,p)=>{m.userData.part=p;sc.add(m);clickable.push(m)};
 L.forEach(([a,b,p])=>{const A=pos(a),B=pos(b);const m=new THREE.Mesh(new THREE.CylinderGeometry(p==='legs'||p==='hips'?0.045:0.035,0.035,A.distanceTo(B),14),mat(p));m.position.copy(A).add(B).multiplyScalar(.5);m.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),B.clone().sub(A).normalize());add(m,p)});
 const hd=new THREE.Mesh(new THREE.SphereGeometry(0.1,24,16),mat('head'));hd.position.copy(pos('head'));add(hd,'head');
 const to=new THREE.Mesh(new THREE.BoxGeometry(0.36,0.44,0.22),mat('torso'));to.position.set(0,1.2,0);add(to,'torso');
 const pv=new THREE.Mesh(new THREE.BoxGeometry(0.3,0.1,0.18),mat('hips'));pv.position.copy(pos('pel'));add(pv,'hips');
 ['l','r'].forEach(s=>{const f=new THREE.Mesh(new THREE.BoxGeometry(0.1,0.04,0.26),mat('legs'));f.position.set(s==='l'?0.1:-0.1,0.02,0.05);add(f,'legs');
   const h=new THREE.Mesh(new THREE.BoxGeometry(0.08,0.1,0.04),mat('hands'));h.position.copy(pos(s+'ha'));h.position.y-=0.05;add(h,'hands')});
 const joints=[];
 Object.entries(J).forEach(([k,d])=>{const hot=on(d[7]);const m=new THREE.Mesh(new THREE.SphereGeometry(0.03+Math.min(d[4],6)*0.006,20,14),new THREE.MeshStandardMaterial({color:hot?(d[4]>=21?0x4cd964:0xf5a623):0x665533,emissive:hot?0x331a00:0,transparent:!hot,opacity:hot?1:.35}));m.position.copy(pos(k));m.userData={part:d[7],j:d};sc.add(m);joints.push(m);clickable.push(m)});
 // camera focus
 let tgt=new THREE.Vector3(0,0.9,0),dist=3.2;
 if(focus&&focus.length&&!isIdx){const b=new THREE.Box3();focus.forEach(k=>b.expandByPoint(pos(k)));b.getCenter(tgt);dist=Math.max(0.9,b.getSize(new THREE.Vector3()).length()*2.2)}
 oc.target.copy(tgt);cam.position.copy(tgt).add(new THREE.Vector3(dist*.65,dist*.3,dist*.7));oc.update();
 const ray=new THREE.Raycaster(),mp=new THREE.Vector2(),tip=document.getElementById('tip');
 const hit=e=>{const b=r.domElement.getBoundingClientRect();mp.x=(e.clientX-b.left)/b.width*2-1;mp.y=-(e.clientY-b.top)/b.height*2+1;ray.setFromCamera(mp,cam);return [ray.intersectObjects(clickable)[0],b]};
 r.domElement.addEventListener('pointermove',e=>{const [h,b]=hit(e);if(!tip)return;if(h){const u=h.object.userData;tip.style.display='block';tip.style.left=(e.clientX-b.left+12)+'px';tip.style.top=(e.clientY-b.top+12)+'px';tip.innerHTML=u.j?`<b>${u.j[3]}</b><br>${u.j[4]} DoF · ${u.j[5]}<br>Peak: ${u.j[6]} [EST]`+(part==='index'?'<br><i>click to open</i>':''):`<b>${u.part}</b>`+(part==='index'?' (click to open)':'');r.domElement.style.cursor=part==='index'?'pointer':'default'}else{tip.style.display='none';r.domElement.style.cursor='grab'}});
 let down;r.domElement.addEventListener('pointerdown',e=>down=[e.clientX,e.clientY]);
 r.domElement.addEventListener('pointerup',e=>{if(part!=='index'||!down||Math.hypot(e.clientX-down[0],e.clientY-down[1])>4)return;const [h]=hit(e);if(h)location.href=h.object.userData.part+'.html'});
 addEventListener('resize',()=>{const w=el.clientWidth;r.setSize(w,H);cam.aspect=w/H;cam.updateProjectionMatrix()});
 (function loop(){requestAnimationFrame(loop);r.render(sc,cam)})();
 window.__threeOK=true;
}
