import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import loadMujoco from 'https://cdn.jsdelivr.net/npm/@mujoco/mujoco@3.14.0/mujoco.js';
const status=document.getElementById('simstatus');
try{
 const mj=await loadMujoco();
 const xml=document.getElementById('mjcf').textContent;
 const m=mj.MjModel.from_xml_string(xml);const d=new mj.MjData(m);mj.mj_forward(m,d);
 const IDS={"jq": {"root": 0, "l_hip_yaw": 7, "l_hip_roll": 8, "l_hip_pitch": 9, "l_knee": 10, "l_ankle_pitch": 11, "l_ankle_roll": 12, "r_hip_yaw": 13, "r_hip_roll": 14, "r_hip_pitch": 15, "r_knee": 16, "r_ankle_pitch": 17, "r_ankle_roll": 18, "waist_yaw": 19, "waist_pitch": 20, "l_shoulder_pitch": 21, "l_shoulder_roll": 22, "l_shoulder_yaw": 23, "l_elbow": 24, "l_wrist_roll": 25, "l_wrist_pitch": 26, "l_wrist_yaw": 27, "r_shoulder_pitch": 28, "r_shoulder_roll": 29, "r_shoulder_yaw": 30, "r_elbow": 31, "r_wrist_roll": 32, "r_wrist_pitch": 33, "r_wrist_yaw": 34, "neck_yaw": 35, "neck_pitch": 36}, "g": {"l_foot": 4, "r_foot": 7}, "a": {"l_hip_yaw": 0, "l_hip_roll": 1, "l_hip_pitch": 2, "l_knee": 3, "l_ankle_pitch": 4, "l_ankle_roll": 5, "r_hip_yaw": 6, "r_hip_roll": 7, "r_hip_pitch": 8, "r_knee": 9, "r_ankle_pitch": 10, "r_ankle_roll": 11, "waist_yaw": 12, "waist_pitch": 13, "l_shoulder_pitch": 14, "l_shoulder_roll": 15, "l_shoulder_yaw": 16, "l_elbow": 17, "l_wrist_roll": 18, "l_wrist_pitch": 19, "l_wrist_yaw": 20, "r_shoulder_pitch": 21, "r_shoulder_roll": 22, "r_shoulder_yaw": 23, "r_elbow": 24, "r_wrist_roll": 25, "r_wrist_pitch": 26, "r_wrist_yaw": 27, "neck_yaw": 28, "neck_pitch": 29}};const jq=n=>IDS.jq[n];
 function nominal(){mj.mj_resetData(m,d);for(const s of ['l','r']){d.qpos[jq(s+'_hip_pitch')]=-0.25;d.qpos[jq(s+'_knee')]=0.5;d.qpos[jq(s+'_ankle_pitch')]=-0.25;d.qpos[jq(s+'_elbow')]=-0.3}
  mj.mj_forward(m,d);let lo=1e9;for(const g of [gl,gr]){lo=Math.min(lo,d.geom_xpos[3*g+2]-0.02)}d.qpos[2]-=lo-0.0005;mj.mj_forward(m,d)}
 const gid=n=>IDS.g[n];const gl=gid('l_foot'),gr=gid('r_foot');
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
  const me=new THREE.Mesh(g,mat);me.matrixAutoUpdate=false;sc.add(me);meshes.push(me)}
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
  r.render(sc,cam)}
 let last=performance.now();
 (function loop(now){requestAnimationFrame(loop);if(!paused){const steps=Math.min(50,Math.round((now-last)/1000/m.opt.timestep));for(let i=0;i<steps;i++)step()}last=now;draw();
  status.textContent=`t=${d.time.toFixed(2)} s · pelvis height ${d.qpos[2].toFixed(3)} m · ${d.qpos[2]>0.8?'standing':'FALLEN, press Reset'}`})(performance.now());
 window.__simOK=true;
}catch(e){status.textContent='Simulation failed to load: '+e;console.error(e)}
