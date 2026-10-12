from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--use-gl=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
    for W,H,mob in [(390,844,True),(1400,900,False)]:
        ctx=b.new_context(viewport={'width':W,'height':H},device_scale_factor=2 if mob else 1,is_mobile=mob,has_touch=mob)
        for n in ['v2','v2_checks','v2_sim','index']:
            pg=ctx.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)[:300]));pg.on('console',lambda m:errs.append(m.text[:300]) if m.type=='error' else None)
            pg.goto(f'file:///workspace/robot-lab/site/{n}.html');pg.wait_for_timeout(9000 if n=='v2_sim' else 1500)
            st=pg.evaluate("(document.getElementById('simstatus')||{}).textContent||''")
            if n=='v2_sim':
                pg.select_option('#pdir','0');pg.click('#push');pg.wait_for_timeout(4000);st+=' | after 150N push: '+pg.evaluate("document.getElementById('simstatus').textContent")
            print(W,n,'overflowX',pg.evaluate('document.documentElement.scrollWidth>innerWidth+1'),'tables',pg.evaluate("document.querySelectorAll('table').length"),st,errs)
            if mob and n in('v2','v2_sim','v2_checks'): pg.screenshot(path=f'shots/m390_{n}.png')
            pg.close()
        ctx.close()
    b.close()
