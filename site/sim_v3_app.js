import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import loadMujoco from 'https://cdn.jsdelivr.net/npm/@mujoco/mujoco@3.14.0/mujoco.js';
const status=document.getElementById('simstatus');
try{
 const mj=await loadMujoco();
 const xml=document.getElementById('mjcf').textContent;
 const m=mj.MjModel.from_xml_string(xml);const d=new mj.MjData(m);mj.mj_forward(m,d);
 const IDS=JSON.parse(document.getElementById("ids").textContent);const jq=n=>IDS.jq[n];
 function nominal(){mj.mj_resetData(m,d);for(const s of ['l','r']){d.qpos[jq(s+'_hip_pitch')]=-0.25;d.qpos[jq(s+'_knee')]=0.5;d.qpos[jq(s+'_ankle_pitch')]=-0.25;d.qpos[jq(s+'_elbow')]=-0.3}
  mj.mj_forward(m,d);let lo=1e9;for(const g of [gl,gr]){lo=Math.min(lo,d.geom_xpos[3*g+2]-0.02)}d.qpos[2]-=lo-0.0005;mj.mj_forward(m,d)}
 const gid=n=>IDS.g[n];const gl=gid('l_foot'),gr=gid('r_foot');
 mj.mj_resetData(m,d);mj.mj_forward(m,d);const xpos0=Float64Array.from(d.xpos);
 nominal();const q0=Float64Array.from(d.qpos);
 const aid=n=>IDS.a[n];const ankP=['l','r'].map(s=>aid(s+'_ankle_pitch')),ankR=['l','r'].map(s=>aid(s+'_ankle_roll'));
 const Mtot=m.body_subtreemass[1];let balance=true;
 const nu=m.nu,trn=m.actuator_trnid,qadr=m.jnt_qposadr,dadr=m.jnt_dofadr,cr=m.actuator_ctrlrange;
 const qa=[],va=[],kp=[],kd=[];for(let i=0;i<nu;i++){const j=trn[2*i];qa.push(qadr[j]);va.push(dadr[j]);kp.push(Math.min(600,Math.max(30,cr[2*i+1]*3)));kd.push(kp[i]*0.04)}
 const el=document.getElementById('three');const W=el.clientWidth,H=el.clientHeight;
 const r=new THREE.WebGLRenderer({antialias:true});r.setSize(W,H);r.setPixelRatio(Math.min(2,devicePixelRatio));el.appendChild(r.domElement);
 const sc=new THREE.Scene();sc.background=new THREE.Color(0x0e1a26);
 const cam=new THREE.PerspectiveCamera(40,W/H,0.01,50);cam.up.set(0,0,1);cam.position.set(2.5,2.0,1.4);
 const oc=new OrbitControls(cam,r.domElement);oc.target.set(0,0,0.9);oc.update();
 sc.add(new THREE.HemisphereLight(0xffffff,0x334455,1.3));const dl=new THREE.DirectionalLight(0xffffff,1);dl.position.set(2,3,4);sc.add(dl);
 const gs=m.geom_size,gt=m.geom_type,meshes=[];
 for(let i=0;i<m.ngeom;i++){const t=gt[i],s=[gs[3*i],gs[3*i+1],gs[3*i+2]];let g;
  if(t===0){g=new THREE.PlaneGeometry(20,20)}else if(t===2){g=new THREE.SphereGeometry(s[0],24,16)}
  else if(t===3){g=new THREE.CapsuleGeometry(s[0],2*s[1],8,16);g.rotateX(Math.PI/2)}
  else if(t===6){g=new THREE.BoxGeometry(2*s[0],2*s[1],2*s[2])}else{g=new THREE.SphereGeometry(0.02)}
  const mat=t===0?new THREE.MeshStandardMaterial({color:0x1a2a38}):new THREE.MeshStandardMaterial({color:0x7fb3e0,metalness:.3,roughness:.5});
  const me=new THREE.Mesh(g,mat);me.matrixAutoUpdate=false;me.userData.prim=t!==0;sc.add(me);meshes.push(me)}
 // CAD parts (v3 GLB) attached to their MuJoCo bodies: M = Body(t) * T(-body_rest) * R^T(glTF->CAD)
 const cad=[];let showCad=true;const Rt=new THREE.Matrix4().set(0,0,1,0, 1,0,0,0, 0,1,0,0, 0,0,0,1);
 const meta=await (await fetch('cad/parts_v3.json')).json();const byId={};meta.forEach(x=>byId[x.id]=x);
 new GLTFLoader().load('cad/bhl_v3.glb',g=>{g.scene.updateMatrixWorld(true);const todo=[];g.scene.traverse(o=>{if(o.isMesh)todo.push(o)});
  for(const o of todo){const x=byId[o.name]||byId[o.parent&&o.parent.name];if(!x)continue;let bn=x.seg;if(/^[LR]_pelvis$/.test(bn))bn='pelvis';const b=IDS.b[bn];if(b===undefined)continue;
   const geo=o.geometry.clone().applyMatrix4(o.matrixWorld);geo.computeVertexNormals();
   const col=/battery/.test(x.name)?0x2a5aa0:/motor|Harmonic|drive/.test(x.name)?0xb87333:({'CFRP':0x3a3d44,'PA12':0xe6e6e1,'steel':0x8a8e96}[x.material]??0xb0b8c4);
   const me=new THREE.Mesh(geo,new THREE.MeshStandardMaterial({color:col,metalness:.3,roughness:.55}));me.matrixAutoUpdate=false;
   me.userData.b=b;me.userData.off=new THREE.Matrix4().makeTranslation(-xpos0[3*b],-xpos0[3*b+1],-xpos0[3*b+2]).multiply(Rt);sc.add(me);cad.push(me)}
  for(const me of meshes)if(me.userData.prim)me.visible=!showCad;document.getElementById('cadtog').disabled=false;});
 document.getElementById('cadtog').onclick=e=>{showCad=!showCad;e.target.textContent=showCad?'Show: CAD parts':'Show: collision shapes';for(const me of cad)me.visible=showCad;for(const me of meshes)if(me.userData.prim)me.visible=!showCad};
 const bm=new THREE.Matrix4();
 {const gh=new THREE.GridHelper(20,40,0x335577,0x223344);gh.rotation.x=Math.PI/2;sc.add(gh)}
 addEventListener('resize',()=>{const w=el.clientWidth,h=el.clientHeight;r.setSize(w,h);cam.aspect=w/h;cam.updateProjectionMatrix()});
 let paused=false,pushT=-1;
 document.getElementById('reset').onclick=()=>{nominal()};document.getElementById('bal').onclick=e=>{balance=!balance;e.target.textContent='Balance: '+(balance?'ON':'OFF')};
 document.getElementById('pause').onclick=e=>{paused=!paused;e.target.textContent=paused?'Resume':'Pause'};
 document.getElementById('push').onclick=()=>{pushT=d.time};
 const pushF=document.getElementById('force');
 const mtx=new THREE.Matrix4();
 function step(){const q=d.qpos,v=d.qvel,c=d.ctrl,xf=d.xfrc_applied;
  const tau=new Float64Array(nu);for(let i=0;i<nu;i++)tau[i]=kp[i]*(q0[qa[i]]-q[qa[i]])-kd[i]*v[va[i]];
  if(balance){const sc=d.subtree_com,gx=d.geom_xpos;const ex=sc[3]-0.5*(gx[3*gl]+gx[3*gr]),ey=sc[4]-0.5*(gx[3*gl+1]+gx[3*gr+1]);
   const ax=Mtot*9.81*ex+20*v[0],ay=Mtot*9.81*ey+20*v[1];for(const i of ankP)tau[i]+=ax;for(const i of ankR)tau[i]-=ay}
  for(let i=0;i<nu;i++)c[i]=Math.min(cr[2*i+1],Math.max(cr[2*i],tau[i]));
  const on=(pushT>=0&&d.time-pushT<0.2);const dir=document.getElementById('pdir').value|0;xf[6]=on&&dir===0?+pushF.value:0;xf[7]=on&&dir===1?+pushF.value:0;
  mj.mj_step(m,d)}
 function draw(){const p=d.geom_xpos,R=d.geom_xmat;
  for(let i=0;i<meshes.length;i++){const k=9*i;mtx.set(R[k],R[k+1],R[k+2],p[3*i],R[k+3],R[k+4],R[k+5],p[3*i+1],R[k+6],R[k+7],R[k+8],p[3*i+2],0,0,0,1);meshes[i].matrix.copy(mtx)}
  const X=d.xpos,XM=d.xmat;for(const me of cad){const b=me.userData.b,k=9*b;bm.set(XM[k],XM[k+1],XM[k+2],X[3*b],XM[k+3],XM[k+4],XM[k+5],X[3*b+1],XM[k+6],XM[k+7],XM[k+8],X[3*b+2],0,0,0,1);me.matrix.multiplyMatrices(bm,me.userData.off)}
  r.render(sc,cam)}
 let last=performance.now();
 (function loop(now){requestAnimationFrame(loop);if(!paused){const steps=Math.min(50,Math.round((now-last)/1000/m.opt.timestep));for(let i=0;i<steps;i++)step()}last=now;draw();
  status.textContent=`t=${d.time.toFixed(2)} s · pelvis height ${d.qpos[2].toFixed(3)} m · ${d.qpos[2]>0.9?'standing':'FALLEN, press Reset'}`})(performance.now());
 window.__simOK=true;
}catch(e){status.textContent='Simulation failed to load: '+e;console.error(e)}
