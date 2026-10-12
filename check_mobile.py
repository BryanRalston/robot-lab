from playwright.sync_api import sync_playwright
import os
pages=['index','head','torso','arms','hands','hips','legs','control','sim']
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--use-gl=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
    os.makedirs('/workspace/robot-lab/shots',exist_ok=True)
    for W,H in [(390,844),(360,780)]:
        ctx=b.new_context(viewport={'width':W,'height':H},device_scale_factor=2,is_mobile=True,has_touch=True)
        for n in pages:
            pg=ctx.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('console',lambda m:errs.append(m.text) if m.type=='error' else None)
            pg.goto(f'file:///workspace/robot-lab/site/{n}.html');pg.wait_for_timeout(5000 if n=='sim' else 2500)
            ov=pg.evaluate('document.documentElement.scrollWidth>innerWidth+1')
            cw=pg.evaluate("(()=>{const c=document.querySelector('#three canvas');return c?[Math.round(c.getBoundingClientRect().width),Math.round(c.getBoundingClientRect().height)]:null})()")
            print(W,n,'pageOverflowX',ov,'canvas',cw,'errs',errs)
            if W==390 and n in('index','legs','sim'): pg.screenshot(path=f'/workspace/robot-lab/shots/m390_{n}.png')
            if W==360 and n=='index':
                pg.tap('.topbar button');pg.wait_for_timeout(400);pg.screenshot(path='/workspace/robot-lab/shots/m360_menu.png');pg.tap('main',position={'x':330,'y':400});pg.wait_for_timeout(300)
                bb=pg.locator('#three canvas').bounding_box();pg.evaluate("document.getElementById('three').scrollIntoView()");bb=pg.locator('#three canvas').bounding_box()
                pg.touchscreen.tap(bb['x']+bb['width']/2,bb['y']+bb['height']*0.40);pg.wait_for_timeout(500)
                print('tap tip:',pg.evaluate("document.getElementById('tip').style.display+' | '+document.getElementById('tip').innerText"))
                pg.screenshot(path='/workspace/robot-lab/shots/m360_tap.png')
            pg.close()
        ctx.close()
    pg=b.new_page(viewport={'width':1400,'height':900});pg.goto('file:///workspace/robot-lab/site/index.html');pg.wait_for_timeout(2000);pg.screenshot(path='/workspace/robot-lab/shots/desktop_index.png');print('desktop nav visible',pg.is_visible('nav'),'topbar',pg.is_visible('.topbar'))
    b.close()
