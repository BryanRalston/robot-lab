from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--use-gl=swiftshader','--enable-unsafe-swiftshader'])
    pg=b.new_page(viewport={'width':1400,'height':900});errs=[]
    pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None);pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///workspace/robot-lab/humanoid_design.html');pg.wait_for_timeout(4000)
    print('three',pg.evaluate('window.__threeOK'),'canvas',pg.evaluate("!!document.querySelector('#three canvas')"),'tables',pg.evaluate("document.querySelectorAll('table').length"))
    pg.click('table th:nth-child(3)');print('sorted',pg.evaluate("document.querySelector('table th:nth-child(3)').dataset.dir"))
    pg.evaluate("document.getElementById('three').scrollIntoView()");pg.wait_for_timeout(800);pg.screenshot(path='shot.png')
    print('errors',errs);b.close()
