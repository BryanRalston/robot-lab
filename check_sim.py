from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--use-gl=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
    for f in ['sim.html','torso.html']:
        pg=b.new_page(viewport={'width':1400,'height':900});errs=[]
        pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None);pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto('file:///workspace/robot-lab/site/'+f);pg.wait_for_timeout(8000)
        print(f,'sim',pg.evaluate('window.__simOK'),'3d',pg.evaluate('window.__threeOK'),pg.evaluate("(document.getElementById('simstatus')||{}).textContent"),errs)
        if f=='sim.html':
            pg.click('#push');pg.wait_for_timeout(3000);print('after push:',pg.evaluate("document.getElementById('simstatus').textContent"))
            pg.evaluate("document.getElementById('three').scrollIntoView()");pg.screenshot(path='/workspace/robot-lab/shot_sim.png')
        pg.close()
    b.close()
