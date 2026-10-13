import clash,io,contextlib,json
out={}
for a in (120,125,130,135,140,145):
    with contextlib.redirect_stdout(io.StringIO()): c=clash.run({'L_knee':a},'x')
    out[a]=[x[:2] for x in c]
for a in (-6,-8): 
    with contextlib.redirect_stdout(io.StringIO()): c=clash.run({'L_hip_roll':a},'x')
    out[f'single_roll_{a}']=[x[:2] for x in c]
json.dump(out,open('out/knee_adduction_sweep.json','w'),indent=1)
