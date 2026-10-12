from playwright.sync_api import sync_playwright
import glob,os
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--use-gl=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
    for f in sorted(glob.glob('/workspace/robot-lab/site/*.html')):
        pg=b.new_page(viewport={'width':1400,'height':900});errs=[]
        pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None);pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto('file://'+f);pg.wait_for_timeout(2500)
        ok=pg.evaluate('window.__threeOK===true');n=pg.evaluate("document.querySelectorAll('table').length")
        if n: pg.click('table th >> nth=1')
        print(os.path.basename(f),'3D',ok,'tables',n,'errors',errs)
        if f.endswith(('index.html','legs.html')): pg.evaluate("document.getElementById('three').scrollIntoView()");pg.wait_for_timeout(500);pg.screenshot(path='/workspace/robot-lab/shot_'+os.path.basename(f)+'.png')
        pg.close()
    # click test on index: click center of 3D (torso)
    pg=b.new_page(viewport={'width':1400,'height':900});pg.goto('file:///workspace/robot-lab/site/index.html');pg.wait_for_timeout(2500)
    pg.evaluate("document.getElementById('three').scrollIntoView()");bb=pg.locator('#three canvas').bounding_box()
    pg.mouse.click(bb['x']+bb['width']/2,bb['y']+bb['height']*0.42);pg.wait_for_timeout(1500);print('after click:',pg.url)
    b.close()
