"""r8 structure fixes: box re-solves using Grok Build's fea_r5 loaders with modified geometry.
  python fea_r8.py clevis <h> <fillet_mm>    (fillet 0 = as analysed)
Results: results/r8/<tag>.json (summaries only)."""
import os,sys,json
H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(H,'grokbuild'))
import fea_r5 as R, fea_tet as F, cadquery as cq
part,h,fr=sys.argv[1],float(sys.argv[2]),float(sys.argv[3])
def clevis_geom_f():
    cheek=F.box(-23,23,21,35,-21,41).union(F.box(-23,23,-35,-21,-21,41))
    bridge=F.box(3,43,-35,35,40,62)
    s=cheek.union(bridge)
    PAD=float(os.environ.get('PAD','0'))   # mm: bridge extended forward over the cheeks only (|y| 21..35)
    if PAD>0: s=s.union(F.box(3-PAD,3.01,21,35,40,62)).union(F.box(3-PAD,3.01,-35,-21,40,62))
    if fr>0:   # re-entrant y-edges: bridge x=3 face over cheek top z=41, and cheek x=23 face under bridge z=40
        s=s.edges(cq.selectors.BoxSelector((2.5,-36,40.5),(3.5,36,41.5))).fillet(fr) if False else s
        e=[x for x in s.edges('|X').vals() if abs(abs(x.Center().y)-21)<0.6 and abs(x.Center().z-40)<0.6]
        e+=[x for x in s.edges('|Y').vals() if abs(x.Center().x-(3-float(os.environ.get('PAD','0'))))<0.6 and abs(x.Center().z-41)<0.6]
        print('fillet edges',len(e),flush=True)
        s=s.newObject(e).fillet(fr)
    pocket=F.box(4,42,23,34.5,42,60).union(F.box(4,42,-34.5,-23,42,60))
    body=s.cut(F.cyl_y(8,-40,40)).cut(F.cyl_z(25,40,80,(18,0))).cut(pocket)
    return body.union(F.cyl_y(8,-36,36)),body
R.clevis_geom=clevis_geom_f
_save=F.save
def save(tag,d):
    t=f'{part}_h{h:g}_f{fr:g}_pad{os.environ.get("PAD","0")}'; d['r8_fillet_mm']=fr
    json.dump(d,open(os.path.join(H,'results','r8',t+'.json'),'w'),indent=1,default=str); print('saved',t)
F.save=save
if part=='clevis': R._pin_part('clevis',h)
if part=='clamp':
    import inspect,textwrap
    src=inspect.getsource(R.clamp_geom).replace("b, hz, ring_t, ring_h = 12.0, 30.0, 6.0, 34.0","b, hz, ring_t, ring_h = 12.0, %g, 6.0, 34.0"%fr)
    src=src.replace("abs(abs(c.x) - b / 2) < 0.4","abs(abs(c.x) - b / 2) < 0.4")
    src=src.replace("if len(edges) != 8:","if len(edges) != (4 if hz >= ring_h else 8):")
    exec(src,R.__dict__)
    R.run_clamp(h)
if part=='foot':
    _fwf=R.foot_with_flange
    def fwf():
        s,xy=_fwf()
        if fr>0:   # aluminium doubler collar around the steel flange: r 30.2..fr, z 18..21, 45° outer chamfer
            ring=F.cyl_z(fr,18,21).cut(F.cyl_z(30.2,17.9,21.1))
            try: ring=ring.faces('>Z').edges('not %LINE').edges(F.cq.selectors.RadiusNthSelector(1)).chamfer(2.5)
            except Exception as ex: print('chamfer skipped',ex)
            s=s.union(ring)
        return s,xy
    R.foot_with_flange=fwf
    def nocontact(*a,**k): raise RuntimeError('contact skipped in r8')
    R.sole_contact=nocontact
    _fa=R.foot_al
    R.run_foot(h)
if part=='tongue':
    def tg():
        if fr<=0: return F.cyl_y(27.5,-13.5,13.5).cut(F.cyl_y(17.5,-15,15)).union(F.box(-25,25,-13.5,13.5,-46.5,-26))
        # r8: neck widened to the hub OD (55, tangent: no step) and fillet fr on the neck-to-hub re-entrant lines
        hub=F.cyl_y(27.5,-13.5,13.5)
        neck=F.box(-27.5,27.5,-13.5,13.5,-46.5,0)
        s=hub.union(neck)
        try:
            e=[x for x in s.edges('|Y').vals() if abs(abs(x.Center().x)-27.5)<0.6 and abs(x.Center().z)<1.0]
            print('tangent edges',len(e))
        except Exception as ex: print(ex)
        return s.cut(F.cyl_y(17.5,-15,15))
    R.tongue_geom=tg
    R.run_tongue(h)
