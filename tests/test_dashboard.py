"""Run with: uv run --no-project --with playwright python tests/test_dashboard.py
Uses an isolated headless Chrome; does not touch user tabs or accounts.
"""
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
 page=browser.new_page(viewport={'width':1440,'height':1080});errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.route('https://observatory.test/**',lambda r:r.fulfill(path=str(root/'docs'/(urlparse(r.request.url).path.lstrip('/') or 'index.html'))))
 page.goto('https://observatory.test/');page.locator('#nodes button').first.wait_for()
 assert page.locator('#nodes button').count()==14
 assert page.locator('#best').inner_text()=='0,341'
 for title in ['02 Winst en verlies','03 Datamodel','04 Governance','05 Proceslogs en Git','06 Begrippen']:
  page.get_by_role('button',name=title).click()
 page.get_by_role('button',name='03 Datamodel').click()
 page.locator('#diagram-canvas svg').wait_for()
 assert page.locator('#diagram-canvas g.node[data-select]').count()==11
 page.locator('#zoom-actual').click();assert page.locator('#zoom-label').inner_text()=='100%'
 page.locator('#diagram-mode').select_option('full')
 page.wait_for_function("document.querySelector('#diagram-status').textContent.includes('37 klikbare')")
 page.locator('#diagram-canvas [data-select=\"LIN-01\"]').first.dispatch_event('click')
 assert 'LIN-01' in page.locator('#detail').inner_text()
 page.locator('#zoom-fit').click()
 page.get_by_role('button',name='06 Begrippen').click()
 page.locator('#search').fill('BG001');assert page.locator('#terms .term').count()==1
 page.get_by_role('button',name='05 Proceslogs en Git').click()
 assert 'observatory-browser-qa-v1' in page.locator('#events').inner_text()
 page.locator('#gitB').select_option(index=2);assert '...' in page.locator('#compare').get_attribute('href')
 page.get_by_role('button',name='07 Methodelandschap').click()
 page.locator('#landscape-queue article').first.wait_for()
 assert page.locator('#landscape-queue article').count()==6
 page.locator('#landscape-search').fill('LambdaRank')
 assert page.locator('#landscape-counts tr').count()==1
 assert 'niet promoveren' in page.locator('#landscape-result').inner_text()
 page.get_by_role('button',name='08 Experimenten en submissies').click()
 page.locator('#plan-experiments article').first.wait_for()
 assert page.locator('#plan-experiments article').count()==7
 assert page.locator('#plan-submissions tr').count()==4
 assert page.locator('#plan-calendar tr').count()==12
 page.get_by_role('button',name='01 Proces en lineage').click()
 page.locator('[data-select="LOG-01"]').first.click()
 assert 'casmi26-research-observatory/blob/main/tools/log_event.py' in page.locator('#detail a').first.get_attribute('href')
 assert 'LOG-01' in page.locator('#detail a').last.get_attribute('href')
 page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
 assert not errors,errors
 browser.close()
print('PASS: components, views, metrics, glossary, process log, Git selection, issue URLs, mobile, JavaScript errors')
