import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import loadMujoco from 'https://cdn.jsdelivr.net/npm/@mujoco/mujoco@3.14.0/mujoco.js';
const status=document.getElementById('simstatus');
try{
 const mj=await loadMujoco();
 const xml=document.getElementById('mjcf').textContent;
 const m=mj.MjModel.from_xml_string(xml);const d=new mj.MjData(m);mj.mj_forward(m,d);
 const q0=Float64Array.from(d.qpos);
 const nu=m.nu,trn=m.actuator_trnid,qadr=m.jnt_qposadr,dadr=m.jnt_dofadr,cr=m.actuator_ctrlrange;
 const qa=[],va=[],kp=[],kd=[];for(let i=0;i<nu;i++){const j=trn[2*i];qa.push(qadr[j]);va.push(dadr[j]);kp.push(Math.max(50,cr[2*i+1]*4));kd.push(kp[i]*0.05)}
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
  const me=new THREE.Mesh(g,mat);me.matrixAutoUpdate=false;sc.add(me);meshes.push(me)}
 {const gh=new THREE.GridHelper(20,40,0x335577,0x223344);gh.rotation.x=Math.PI/2;sc.add(gh)}
 addEventListener('resize',()=>{const w=el.clientWidth,h=el.clientHeight;r.setSize(w,h);cam.aspect=w/h;cam.updateProjectionMatrix()});
 let paused=false,pushT=-1;
 document.getElementById('reset').onclick=()=>{mj.mj_resetData(m,d);mj.mj_forward(m,d)};
 document.getElementById('pause').onclick=e=>{paused=!paused;e.target.textContent=paused?'Resume':'Pause'};
 document.getElementById('push').onclick=()=>{pushT=d.time};
 const pushF=document.getElementById('force');
 const mtx=new THREE.Matrix4();
 function step(){const q=d.qpos,v=d.qvel,c=d.ctrl,xf=d.xfrc_applied;
  for(let i=0;i<nu;i++){let u=kp[i]*(q0[qa[i]]-q[qa[i]])-kd[i]*v[va[i]];c[i]=Math.min(cr[2*i+1],Math.max(cr[2*i],u))}
  xf[6]=(pushT>=0&&d.time-pushT<0.2)?+pushF.value:0;
  mj.mj_step(m,d)}
 function draw(){const p=d.geom_xpos,R=d.geom_xmat;
  for(let i=0;i<meshes.length;i++){const k=9*i;mtx.set(R[k],R[k+1],R[k+2],p[3*i],R[k+3],R[k+4],R[k+5],p[3*i+1],R[k+6],R[k+7],R[k+8],p[3*i+2],0,0,0,1);meshes[i].matrix.copy(mtx)}
  r.render(sc,cam)}
 let last=performance.now();
 (function loop(now){requestAnimationFrame(loop);if(!paused){const steps=Math.min(50,Math.round((now-last)/1000/m.opt.timestep));for(let i=0;i<steps;i++)step()}last=now;draw();
  status.textContent=`t=${d.time.toFixed(2)} s · pelvis height ${d.qpos[2].toFixed(3)} m · ${d.qpos[2]>0.85?'standing':'FALLEN, press Reset'}`})(performance.now());
 window.__simOK=true;
}catch(e){status.textContent='Simulation failed to load: '+e;console.error(e)}
