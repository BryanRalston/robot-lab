import sys
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8800'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--use-gl=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
    for W,H,mob in [(390,844,True),(1400,900,False)]:
        ctx=b.new_context(viewport={'width':W,'height':H},device_scale_factor=2 if mob else 1,is_mobile=mob,has_touch=mob)
        for n in ['v3','v3_checks','v3_sim','v2_cad']:
            pg=ctx.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)[:300]));pg.on('console',lambda m:errs.append(m.text[:300]) if m.type=='error' else None)
            pg.goto(f'{BASE}/{n}.html');pg.wait_for_timeout(12000 if n in('v3_sim','v3') else 2000)
            st=pg.evaluate("((document.getElementById('simstatus')||{}).textContent||'')+' '+((document.getElementById('cadload')||{}).textContent||'')")
            if n=='v3_sim':
                pg.select_option('#pdir','0');pg.fill('#force','100');pg.click('#push');pg.wait_for_timeout(4000);st+=' | after push: '+pg.evaluate("document.getElementById('simstatus').textContent")
                st+=' | cad meshes on: '+str(pg.evaluate("!document.getElementById('cadtog').disabled"))
            print(W,n,'overflowX',pg.evaluate('document.documentElement.scrollWidth>innerWidth+1'),'tables',pg.evaluate("document.querySelectorAll('table').length"),st.strip(),errs,flush=True)
            if n in('v3','v3_sim','v3_checks'): pg.screenshot(path=f'shots/{"m390" if mob else "d1400"}_{n}.png')
            pg.close()
        ctx.close()
    b.close()
