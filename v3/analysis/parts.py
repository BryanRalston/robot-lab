"""v3 catalog parts. Every number here is copied from the cited source; anything not from a source is tagged EST."""
import json, os
H=os.path.dirname(__file__)
SRC={
 'TBM2G':('Kollmorgen TBM2G Frameless Motor Instruction Manual Rev B (June 2023), section 9 per-model specification pages',
          'https://shop.oxni.ch/files/v240708160007/Kollmorgen/TBM/MN%20TBM2G%20RevB%20En.pdf ; https://www.kollmorgen.com/en-us/products/motors/direct-drive/tbm2g-series-frameless'),
 'HD-CSG':('Harmonic Drive CSG-2A component set rating table (rated L10, repeated peak, momentary peak, mass) and CSF/CSG catalog (ratcheting torque Table 6, average torque, life formula)',
          'https://www.harmonicdrive.net/products/component-sets/cup-type/csg-2a ; https://www.harmonicdrive.net/_hd/content/documents/csf-csg.pdf ; https://innodrive.ru/upload/iblock/195/ip72y4t28r1me60a2i9db29chijhvzqf.pdf (CSG-2A catalog, sizes 14/17 and average torque)'),
 'RV':('Rollvis RV planetary roller screw product tables (Ca, C0a, nut dims, efficiency)','https://rollvis.com/wp-content/uploads/2024/05/Product-Tables-Rollvis-RV-Planetary-Roller-Screw-EN.pdf'),
 'IKO':('IKO Crossed Roller Bearings catalog CAT-57151 (CRBH dimensions, C, C0, equivalent load with moment)','https://www.ikont.eu/files/Documents/Catalogues/CAT-57151UKv3_IKO_CRB.pdf'),
 'EVE':('Novanta Everest XCR servo drive product description (45 A crest cont., 60 A crest 1 s, 80 V, 38 g)','https://drives.novantamotion.com/eve-xcr/product-description'),
 'AKSIM':('RLS AksIM-2 off-axis absolute encoder datasheet MBD01 (17–20 bit, ring/readhead masses)','https://cdn.rls.si/documents/datasheets/MBD01_07_ds.pdf'),
 'DCX22':('maxon DCX 22 S graphite brushes datasheet (24 V winding: 15.3 mNm cont., 66 g, Rth 16+7 K/W)','https://innodrive.ru/upload/iblock/5b9/wra0c4ctrwv0jzqxwuy3ze74t678s55p.pdf'),
 'GPX22':('maxon GPX 22 HP gearhead (3-stage: 3.3 N·m cont., 65 % max eff., 107 g, ratios 62–231)','https://www.maxongroup.com/medias/sys_master/root/9406758256670/Cataloge-Page-EN-393.pdf'),
 'DCX16':('maxon DCX 16 S datasheet (5.2 mNm cont., 26 g)','https://www.maxongroup.com/medias/sys_master/root/8992244498462/EN-22-101.pdf'),
 'GPX16':('maxon GPX 16 LN gearhead (3-stage 0.28 N·m cont., 75 %, 25.7 mm, 27 g)','https://www.maxongroup.com/medias/sys_master/root/9406695473182/Cataloge-Page-EN-382.pdf'),
 'LIROS':('LIROS D-Pro 1 mm (Dyneema SK78, 12-plait, breaking strength 195 daN)','https://www.liros.com/catalog/en/d-pro-1mm-p3511/'),
 'CBOS':('Bending-over-sheave endurance of small cables in prosthetic applications (HBO Kennisbank): 10 mm sheave, 150 N, Dyneema SK78 ≥ 31,826 cycles, none survived 50,000','https://hbo-kennisbank.nl/details/sharekit_hh:oai:surfsharekit.nl:6534b4a7-f407-403f-bdd8-826dd64ce87a'),
 'AL7075':('Anchor Harvey 7075 datasheet (T6: Su 572 MPa, Sy 503 MPa, fatigue 159 MPa at 5e8 cycles, R=-1)','https://www.anchorharvey.com/media/fiahg3e0/anchorharvey-aluminum7075-datasheet.pdf'),
 'P45B':('Molicel INR-21700-P45B product data sheet (4.5 Ah typ., 16.2 Wh, ≤70 g, 45 A cont.)','https://www.molicel.com/wp-content/uploads/INR21700P45B_1.4_Product-Data-Sheet-of-INR-21700-P45B-80109.pdf'),
 'IGUS':('igus chainflex CFROBOT data sheets: min. bend radius 10×d moving (e-chain), 8×d flexible, 5×d fixed','https://www.igus.com/ContentData/Products/Downloads/2_EU_Data_sheet_chainflex_CFROBOT9.pdf'),
 'ISO898':('ISO 898-1 property class 12.9: Rp0.2 ≥ 1100 MPa, Rm ≥ 1220 MPa (standard values)','ISO 898-1:2013'),
 'VDI2230':('VDI 2230 Part 1 (2015) systematic bolted-joint calculation: tightening preload, load factor, embedding, ASV fatigue limit for rolled-after-HT threads','VDI 2230 Blatt 1:2015'),
}
MOT=json.load(open(os.path.join(H,'tbm2g.json')))   # per model: lists are windings [A, C, D]
WIND=['A','C','D']
# Harmonic Drive CSG-2A component sets, ratio 100 (N·m, kg). ratchet: catalog Table 6. avg: 'limit for average torque' (20/25/32 from catalog; 14/17 not captured -> None)
CSG={
 'CSG-14-100':dict(N=100,rated=10,rep=36,mom=70,avg=None,ratchet=100,mass=None,src='HD-CSG'),
 'CSG-17-100':dict(N=100,rated=31,rep=70,mom=143,avg=None,ratchet=200,mass=None,src='HD-CSG'),
 'CSG-20-100':dict(N=100,rated=52,rep=107,mom=191,avg=64,ratchet=330,mass=0.28,src='HD-CSG'),
 'CSG-25-100':dict(N=100,rated=87,rep=204,mom=369,avg=140,ratchet=650,mass=0.42,src='HD-CSG'),
 'CSG-32-100':dict(N=100,rated=178,rep=433,mom=841,avg=281,ratchet=1300,mass=0.89,src='HD-CSG'),
}
CSG_MASS_EST={'CSG-14-100':0.09,'CSG-17-100':0.15}   # EST: component-set masses for 14/17 not captured from catalog
HD_LIFE=dict(L10_h=10000,Nr_rpm=2000)                   # HD catalog: Lh = Ln (Tr/Tav)^3 (Nr/Nav), Ln=10,000 h (L10)
HD_ETA=0.75   # EST: read from HD efficiency curves at ~1000 rpm, 25 °C, rated torque; drops at low temp/low load
# Rollvis RV single nut: (Ca N, C0a N, eta_direct, eta_inverse, nut D1 mm, nut length L1 mm (column mapping of the extracted table is uncertain: treat L1 as EST))
RV={
 'RV12x4':dict(d=12,lead=4,Ca=17200,C0a=27200,eta=0.89,D1=26,L1=36),
 'RV12x5':dict(d=12,lead=5,Ca=18100,C0a=27300,eta=0.89,D1=26,L1=36),
 'RV15x4':dict(d=15,lead=4,Ca=26800,C0a=49500,eta=0.88,D1=34,L1=45),
 'RV15x5':dict(d=15,lead=5,Ca=28900,C0a=51500,eta=0.89,D1=34,L1=45),
 'RV20x5':dict(d=19.5,lead=5,Ca=48000,C0a=100200,eta=0.88,D1=42,L1=53),
}
# IKO CRBH ... A high-rigidity crossed-roller bearings: d, D, B mm, C, C0 N, mass kg
CRBH={n:dict(d=a,D=b,B=c,C=e,C0=f,m=g) for n,a,b,c,e,f,g in [
 ('CRBH 208 A',20,36,8,2910,2430,0.04),('CRBH 258 A',25,41,8,3120,2810,0.05),('CRBH 3010 A',30,55,10,7600,8370,0.12),('CRBH 4010 A',40,65,10,8610,10600,0.15),('CRBH 5013 A',50,80,13,17300,20900,0.29),
 ('CRBH 6013 A',60,90,13,18800,24300,0.33),('CRBH 7013 A',70,100,13,20100,27700,0.38),('CRBH 8016 A',80,120,16,32100,43400,0.74),
 ('CRBH 9016 A',90,130,16,33100,46800,0.81),('CRBH 10020 A',100,150,20,50900,72200,1.45),('CRBH 11020 A',110,160,20,52400,77400,1.56),
 ('CRBH 12025 A',120,180,25,73400,108000,2.62)]}
DRIVE=dict(name='Novanta Everest XCR (EVE-XCR-E)',I_cont_crest=45,I_peak_crest=60,Vmax=80,mass=0.038,src='EVE')
ENC=dict(name='RLS AksIM-2 MRA053/MB0xx (20 bit)',ring_mass=0.016,head_mass=0.005,src='AKSIM')   # readhead mass range 2.7–6.9 g per datasheet; 5 g used
CELL=dict(name='Molicel INR-21700-P45B',Wh=16.2,mass=0.070,Ah=4.5,V=3.6,I_cont=45,src='P45B')
FINGER=dict(motor=dict(name='maxon DCX 22 S 24 V',T_cont=0.0153,mass=0.066,Rth=23.0,src='DCX22'),
            gear=dict(name='maxon GPX 22 HP 3-stage 111:1',N=111,eta=0.65,T_cont=3.3,mass=0.107,src='GPX22'),
            small_motor=dict(name='maxon DCX 16 S',T_cont=0.0052,mass=0.026,src='DCX16'),
            small_gear=dict(name='maxon GPX 16 LN 3-stage 103:1',N=103,eta=0.75,T_cont=0.28,mass=0.027,src='GPX16'),
            tendon=dict(name='LIROS D-Pro 1 mm Dyneema SK78',F_break=1950,src='LIROS'))
AL7075=dict(Su=572,Sy=503,Sf_5e8=159,src='AL7075')
BOLT129=dict(Rp=1100,Rm=1220,src='ISO898')
