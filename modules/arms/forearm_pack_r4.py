"""RL Arms A42: forearm hand-drive packing in the UNCHANGED Ø66 x 177 mm bore (model_v4), two mixed tiers, 1 mm gaps.
Diameters: DCX22S+GPX22HP Ø22, DCX16S+GPX16LN Ø16 (+1 mm gap each -> Ø23 / Ø17). Lengths D68 (+1 mm tol) + spool 10 mm [EST].
Tier A: 4 flexors at R 21.5 (90 deg) + 1 small at centre. Tier B: 2 flexors at R 21.5 (0/180) + 4 small at R 24.5 (±60, ±120)."""
import numpy as np,json,os,itertools,matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
H=os.path.dirname(os.path.abspath(__file__)); BORE=33.0
def ring(n,R,d,a0=0): return [(R*np.cos(a0+2*np.pi*k/n),R*np.sin(a0+2*np.pi*k/n),d) for k in range(n)]
A=ring(4,21.5,23,np.pi/4)+[(0,0,17)]
B=[(21.5,0,23),(-21.5,0,23)]+[(24.5*np.cos(np.radians(a)),24.5*np.sin(np.radians(a)),17) for a in (60,120,240,300)]
def check(T):
    inside=min(BORE-(np.hypot(x,y)+d/2) for x,y,d in T)
    pair=min(np.hypot(a[0]-b[0],a[1]-b[1])-(a[2]+b[2])/2 for a,b in itertools.combinations(T,2))
    return round(inside,2),round(pair,2)
LA=70.9+1+10; LB=70.9+1+10   # both tiers carry a flexor -> flexor length governs
out=dict(tierA=dict(parts='4 flexor + 1 small',min_wall_clear_mm=check(A)[0],min_pair_clear_mm=check(A)[1],length_mm=LA),
         tierB=dict(parts='2 flexor + 4 small',min_wall_clear_mm=check(B)[0],min_pair_clear_mm=check(B)[1],length_mm=LB),
         total_mm=LA+LB,bore_len_mm=177,spare_mm=round(177-LA-LB,1),
         tendon_pass='tier A tendons pass tier B through 4 gaps/centre (tier B centre free Ø ~20); 11 x Ø2.5 sheaths',
         wrist_drives='none in forearm (D70 rotary at wrist); hand node + 2x RP40 in torso shoulder bay')
json.dump(out,open(os.path.join(H,'forearm_pack_r4.json'),'w'),indent=1); print(out)
fig,ax=plt.subplots(1,3,figsize=(15,5))
for a,T,t in ((ax[0],A,'Tier A (4 flexor DCX22 + 1 DCX16)'),(ax[1],B,'Tier B (2 flexor + 4 DCX16)')):
    a.add_patch(plt.Circle((0,0),BORE,fill=False,lw=2))
    for x,y,d in T: a.add_patch(plt.Circle((x,y),d/2-0.5,color='#d95f02' if d>20 else '#1b9e77',alpha=.7))
    a.set_xlim(-36,36);a.set_ylim(-36,36);a.set_aspect('equal');a.set_title(t+f'\nwall {check(T)[0]} / pair {check(T)[1]} mm',fontsize=9)
b=ax[2]; th=np.linspace(0,2*np.pi,200)
b.plot(24.5*np.cos(th),24.5*np.sin(th),'b--',label='fork/cross envelope r 24.5'); b.plot(27*np.cos(th),27*np.sin(th),'r-',label='palm min radius 27 (top dropped 12 mm)')
b.add_patch(plt.Rectangle((-16,-117),32,90,fill=False,ec='r')); b.add_patch(plt.Rectangle((-10,-10),20,20,fill=True,alpha=.3))
b.set_aspect('equal'); b.set_xlim(-60,60); b.set_ylim(-120,40); b.legend(fontsize=8); b.set_title('Wrist sphere rule: clash-free for any pitch/yaw\n(sampled P-026 min gap 4.91 mm)',fontsize=9)
fig.suptitle('2026-10-14 RL Arms A42: forearm two-tier pack (Ø66 x 177 unchanged) + wrist fork fix'); fig.tight_layout()
for p in (os.path.join(H,'A42_forearm_wrist_r4.png'),'/workspace/2026-10-14_arms_A42_forearm_wrist.png',os.path.join(H,'../../media/progress/2026-10-14_arms_A42_forearm_wrist.png')): fig.savefig(p,dpi=100)
