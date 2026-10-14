"""Builds site/v4.html (viewer + joint audit table) from JOINT_AUDIT.json, parts_v4.json, joints_v4.json. Reuses the v3 page style/nav."""
import json,os,re,html
import model_v4 as M
R=M.ROOT; A=json.load(open(os.path.join(M.HERE,'JOINT_AUDIT.json')))
v3=open(os.path.join(R,'site/v3.html')).read()
head=v3[:v3.index('<main>')]
head=head.replace('<title>Robot Lab v3 dashboard + CAD</title>','<title>Robot Lab v4 joint-fidelity model</title>').replace(' class=active','')
head=head.replace('<a href="v3_sim.html">▶ v3 sim (CAD parts)</a></nav>','<a href="v3_sim.html">▶ v3 sim (CAD parts)</a><div style="margin:12px 0 4px;color:#e0559a;font-size:12px;letter-spacing:.08em">V4 · JOINT FIDELITY</div><a href="v4.html" class=active>v4 model + joint audit</a></nav>')
head=head.replace('</style>','.st{padding:2px 8px;border-radius:6px;color:#fff;white-space:nowrap}.BUILDABLE{background:#1e7d43}.PLACEHOLDER{background:#b8641c}.FAIL{background:#b3261e}.jb{min-height:40px;margin:3px;border-radius:8px;border:1px solid #3a6a95;background:#1f3b57;color:#fff;padding:6px 10px;font-size:14px}.jb.on{outline:2px solid #ff3fd0}#lbl{position:absolute;inset:0;pointer-events:none;overflow:hidden}#lbl span{position:absolute;transform:translate(-50%,-120%);font-size:11px;padding:1px 5px;border-radius:5px;color:#fff;white-space:nowrap;opacity:.92}.sw{display:inline-block;width:12px;height:12px;border-radius:3px;margin:0 4px 0 10px;vertical-align:-1px}</style>')
c=A['counts']; J=A['joints']
PP=os.path.join(M.HERE,'JOINT_AUDIT_pending.json'); Pc=json.load(open(PP))['counts'] if os.path.exists(PP) else None
M.build(); JT=[]
for j in J:
    k=j['joint']
    for pre in (('L_','R_') if ('L_'+k) in M.JOINTS else ('',)):
        if (pre+k) not in M.JOINTS: continue
        p=M.JOINTS[pre+k]['pt']; JT.append(dict(name=pre+k,joint=k,status=j['status'],p=[p[0]/1000,p[2]/1000,-p[1]/1000],parts=j['model_parts'],mech=j['bearing']+' · '+j['actuation']))
json.dump(JT,open(os.path.join(R,'site/cad/joints_v4.json'),'w'))
def st(s): return f'<span class="st {s}">{s}</span>'
rows=''.join(f"<tr id='j_{j['joint']}'><td><b>{html.escape(j['joint'])}</b></td><td>{st(j['status'])}</td><td>{html.escape(j['bearing'])}</td><td>{html.escape(j['axis'])}</td><td>{html.escape(j['actuation'])}</td><td>{html.escape(j['attachment'])}</td><td>{html.escape(j['hard_stop'])}</td><td>{j.get('sim_range','')}</td><td>{j.get('swept_clear','not swept')}</td><td>{html.escape(j['notes'])}</td></tr>" for j in J)
fails=[j for j in J if j['status']=='FAIL']
stand=A['standing']
body=f'''<main><h2>Robot Lab v4: every joint gets a real mechanism</h2>
<p>Bryan looked at the v3 model and said some joints couldn't work in the real world. He was right: v3 was a simplified parametric model that had fallen behind the engineered design. v4 rebuilds the legs from the module parts: the Actuators STEP solids (hip yaw/roll housings, twin RV12 roller-screw bodies, hip lever with needle hub, knee lever r47.5), the Legs linkage geometry, the ankle instep pins at r73, the ±18° ankle-roll stop, the femur tongue with the IKO TLA3520 needle pivot and the bonded thigh clamp. Every joint now shows its bearing, its actuator attachment points and its hard stop. Upper-body joints are strain-wave + crossed-roller <b>placeholders</b> (orange), since no module has engineered them yet. Their dimensions are estimates.</p>
<p><b>Update 14 Oct (Actuators D59-D62):</b> the knee now uses one twin housing with a shared centre web. The ankle screws now have an axial GE 12 C top eye in a shank clevis and a QA1 MGF12T-class PTFE rod end at the bottom (27°). The hip-body clearance is now measured, not typed in. Legs L37-L40 (15c602d) add the matching leg side: ankle clevises at trunnion z 450, the instep lug moved 5 mm outboard on an outrigger, and hip yaw/roll PU bumper stops (yaw -35/+45, roll -12/+15). Still estimated: the trunnion bracket plates and the hip yoke brackets. Ankle pitch -60° clashes, but that is outside the ±45/+40 range used in simulation.</p>
<p><b>{c.get("BUILDABLE",0)} buildable · {c.get("PLACEHOLDER",0)} placeholder · {c.get("FAIL",0)} fail</b> (joints per side; 15 finger joints per hand). Standing pose: {len(stand["clashes"])} interferences, {len(stand["floating"])} floating parts.</p>
{''.join(f"<blockquote><b>FAIL · {html.escape(j['joint'])}</b>: {html.escape(j['notes'].replace('FAIL: ',''))}</blockquote>" for j in fails)}
<div id="viewer"><div id="cadview" style="width:100%;height:min(70vh,620px);touch-action:none"></div><div id="lbl"></div></div>
<p class="legend"><span class="sw" style="background:#4670c8"></span>module actuator<span class="sw" style="background:#e1aa28"></span>bearing / pin<span class="sw" style="background:#3caaaa"></span>lever / linkage<span class="sw" style="background:#dc2828"></span>hard stop<span class="sw" style="background:#b9bec6"></span>module structure<span class="sw" style="background:#f08c3c"></span>PLACEHOLDER / estimate<span class="sw" style="background:#ff3fd0"></span>selected joint</p>
<p><button class="jb" id="labels">Joint labels: on</button> <span id="cadinfo">Tap a part, or pick a joint below to highlight it.</span></p>
<div id="jbtns"></div>
<p>Downloads: <a href="cad/bhl_v4.glb">GLB</a> · <a href="https://github.com/BryanRalston/robot-lab/blob/main/modules/model/JOINT_AUDIT.md">JOINT_AUDIT.md</a> · <a href="https://github.com/BryanRalston/robot-lab/tree/main/modules/model">source (model_v4.py, clash_v4.py, audit_v4.py)</a></p>
<h2>Joint audit</h2><p>Left side listed; the right side is the mirror. "Clash-free" is the range swept with no interference between moving and fixed parts (5-15° steps). A hand touching the thigh with the arm hanging is counted separately, as a control/pose issue rather than a mechanism fault.</p>
<div class="tw"><table><thead><tr><th>joint</th><th>status</th><th>bearing / pivot</th><th>axis</th><th>actuation</th><th>attachment points</th><th>hard stop</th><th>sim range °</th><th>clash-free °</th><th>notes</th></tr></thead><tbody>{rows}</tbody></table></div>
</main>'''
js=open(os.path.join(M.HERE,'v4_viewer.js')).read()
tail=v3[v3.index('</main>')+7:]
tail=tail[:tail.index('<script type="module">')]
out=head+body+tail+'<script type="module">'+js+'</script><script>document.querySelectorAll("nav a").forEach(a=>a.addEventListener("click",()=>document.body.classList.remove("navopen")));document.querySelector("main").addEventListener("click",()=>document.body.classList.remove("navopen"))</script></body></html>'
open(os.path.join(R,'site/v4.html'),'w').write(out); print('ok',len(out))
