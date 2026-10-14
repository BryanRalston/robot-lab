"""V5 polish concept: v4 render (left) vs 2D cover-shell mockup (front + side). Light geometry only (matplotlib).
Dimensions from modules/model/model_v4.py P. Shell outlines are CONCEPT [EST], not module data."""
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Ellipse, Polygon
from PIL import Image
P=dict(hip_y=130,hip_z=920,knee_z=500,ankle_z=80,pelvis_bot=1126,pelvis_top=1230,torso_top=1610,shoulder_z=1500,shoulder_y=190)
GOLD='#c9b48a'; BLK='#222'; JNT='#555'
fig=plt.figure(figsize=(15,9),dpi=110)
a0=fig.add_axes([0,0.02,0.36,0.9]); im=Image.open('media/progress/2026-10-14_model_v4_full.png').convert('RGB'); a0.imshow(im.crop((140,190,640,940))); a0.axis('off')
a0.set_title('v4 (live): exposed screws, levers, box torso',fontsize=11)
def rb(ax,x0,z0,w,h,c,r=25,a=1):
    ax.add_patch(FancyBboxPatch((x0,z0),w,h,boxstyle=f'round,pad=0,rounding_size={r}',fc=c,ec='k',lw=.8,alpha=a))
def taper(ax,xc,z0,z1,w0,w1,c):
    ax.add_patch(Polygon([(xc-w0/2,z0),(xc+w0/2,z0),(xc+w1/2,z1),(xc-w1/2,z1)],closed=True,fc=c,ec='k',lw=.8,joinstyle='round'))
# FRONT
a=fig.add_axes([0.37,0.04,0.3,0.86]); a.set_aspect('equal'); a.axis('off'); a.set_title('v5 concept — front',fontsize=11)
tt=P['torso_top']
a.add_patch(Ellipse((0,tt+170),150,200,fc=BLK,ec='k'))                       # integrated head, black visor face
a.add_patch(Ellipse((0,tt+185),120,60,fc='#3a5a78',ec='none',alpha=.6))      # visor band (ZED behind)
rb(a,-35,tt,70,70,BLK,10)                                                  # neck sleeve
taper(a,0,1290,tt,250,330,GOLD)                                            # chest: tapered, shoulders inside
taper(a,0,1215,1290,200,250,BLK)                                           # waist bellows band (flex cover)
taper(a,0,1100,1215,300,210,GOLD)                                          # pelvis shell
for s in (1,-1):
    y=P['shoulder_y']*s
    a.add_patch(Ellipse((y,1500),110,110,fc=GOLD,ec='k'))                  # shoulder cap
    taper(a,y+12*s,1220,1450,70,90,GOLD); taper(a,y+16*s,980,1215,62,72,BLK)  # upper arm / forearm
    a.add_patch(Ellipse((y+16*s,930),55,95,fc=BLK,ec='k'))                 # hand
    h=P['hip_y']*s
    a.add_patch(Polygon([(h-45,1100),(h+70*s/abs(s)*0+60,1100),(h+55,980),(h-50,980)],fc=BLK,ec='k'))  # flexible hip skirt
    taper(a,h,560,1000,105,140,GOLD)                                       # thigh fairing hides hip/knee screws
    taper(a,h,60,520,80,115,BLK)                                          # matte shin fairing hides knee+ankle screws
    a.add_patch(Ellipse((h,530),95,70,fc=BLK,ec='k'))                      # knee cap
    rb(a,h-55,0,110,60,GOLD,15)                                            # foot
a.set_xlim(-330,330); a.set_ylim(-20,1900)
# SIDE
b=fig.add_axes([0.68,0.04,0.3,0.86]); b.set_aspect('equal'); b.axis('off'); b.set_title('v5 concept — side',fontsize=11)
b.add_patch(Ellipse((10,tt+170),190,200,fc=BLK,ec='k')); rb(b,-30,tt,60,70,BLK,10)
taper(b,0,1290,tt,180,220,GOLD); taper(b,0,1215,1290,150,180,BLK); taper(b,0,1100,1215,170,150,GOLD)
taper(b,15,560,1000,120,170,GOLD); taper(b,10,60,520,95,140,BLK); b.add_patch(Ellipse((25,530),80,90,fc=BLK,ec='k'))
rb(b,-60,0,250,60,GOLD,15); taper(b,0,1220,1450,70,90,GOLD); taper(b,0,980,1215,62,72,BLK)
b.set_xlim(-330,330); b.set_ylim(-20,1900)
fig.text(0.5,0.955,'Robot Lab v4 → v5 cover-shell concept (CF/GF prepreg on machined moulds, no 3D printing). Mechanisms unchanged; shells sized to v4 envelopes [EST]',ha='center',fontsize=11)
fig.savefig('media/progress/2026-10-14_design_v5_polish_concept.png'); print('ok')
