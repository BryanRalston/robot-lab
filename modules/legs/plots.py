"""PNG plots for each scenario (left leg torque/speed/power vs time, foot loads) and the envelope vs v3 contract."""
import sys,json,numpy as np,matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from gait_lib import LEG,HERE
import os
OUT=os.path.join(HERE,'results'); PL=os.path.join(HERE,'plots'); os.makedirs(PL,exist_ok=True)
def scen(name):
    d=np.load(f'{OUT}/{name}.npz'); t=d['t']; T=d['TAU']; V=d['V']; va=d['va']; Q=d['Q']; qa=d['qa']
    fig,ax=plt.subplots(5,1,figsize=(11,13),sharex=True)
    for i,j in enumerate(LEG):
        for side,off,ls in (('L',0,'-'),('R',6,'--')):
            c=f'C{i}'
            ax[0].plot(t,T[:,va[i+off]],ls,color=c,lw=1,label=f'{j}' if side=='L' else None)
            ax[1].plot(t,V[:,va[i+off]],ls,color=c,lw=1)
            ax[2].plot(t,T[:,va[i+off]]*V[:,va[i+off]],ls,color=c,lw=1)
            ax[3].plot(t,np.degrees(Q[:,qa[i+off]]),ls,color=c,lw=1)
    ax[4].plot(t,d['FZ'][:,0],label='Fz left'); ax[4].plot(t,d['FZ'][:,1],'--',label='Fz right')
    for a,l in zip(ax,['torque N·m','speed rad/s','power W','angle deg','vertical GRF N']): a.set_ylabel(l); a.grid(alpha=.3)
    ax[0].legend(ncol=6,fontsize=8); ax[4].legend(); ax[4].set_xlabel('time s (solid = left, dashed = right)')
    ax[0].set_title(f'{name}: inverse dynamics on sim/v3 model (63.8 kg)')
    fig.tight_layout(); fig.savefig(f'{PL}/{name}.png',dpi=80); plt.close(fig)
def envelope(env,contract):
    fig,ax=plt.subplots(1,3,figsize=(15,4.5)); x=np.arange(len(LEG))
    for k,(key,lab) in enumerate([('peak_Nm','peak torque N·m'),('peak_rads','peak speed rad/s'),('peak_W','peak power W')]):
        ax[k].bar(x-0.2,[env[j][key]['value'] for j in LEG],0.4,label='gait-ID envelope')
        if key in('peak_Nm','peak_rads'):
            ax[k].bar(x+0.2,[contract[j]['req' if key=='peak_Nm' else 'speed'] for j in LEG],0.4,label='v3 req (need/1.5)' if key=='peak_Nm' else 'v3 need speed [EST v2]')
            ax[k].plot(x+0.2,[contract[j]['avail' if key=='peak_Nm' else 'avail_speed'] for j in LEG],'k_',ms=20,mew=2,label='v3 available')
        ax[k].set_xticks(x); ax[k].set_xticklabels(LEG,rotation=30,fontsize=8); ax[k].set_title(lab); ax[k].legend(fontsize=7); ax[k].grid(alpha=.3)
    fig.tight_layout(); fig.savefig(f'{PL}/envelope_vs_contract.png',dpi=80); plt.close(fig)
if __name__=='__main__':
    for n in sys.argv[1:]: scen(n)
