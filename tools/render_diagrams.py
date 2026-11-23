"""Render pinned Mermaid 11.12.0 to checked-in SVG. No CDN needed by viewers."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json
root=Path(__file__).resolve().parents[1]
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
 page=browser.new_page();page.goto('https://cdn.jsdelivr.net')
 page.evaluate('''async()=>{window.mm=(await import('https://cdn.jsdelivr.net/npm/mermaid@11.12.0/dist/mermaid.esm.min.mjs')).default;mm.initialize({startOnLoad:false,securityLevel:'strict',theme:'dark',themeVariables:{darkMode:true,background:'#101927',primaryColor:'#193148',primaryTextColor:'#edf2fb',primaryBorderColor:'#85b9ff',lineColor:'#9babbe',fontFamily:'system-ui,sans-serif',fontSize:'15px'},flowchart:{htmlLabels:false},er:{useMaxWidth:false},maxTextSize:100000});}''')
 for name in ['datamodel-overview','datamodel-full']:
  src=(root/f'docs/diagrams/{name}.mmd').read_text()
  svg=page.evaluate('''async({src,id})=>{let r=await mm.render(id,src);return r.svg}''',{'src':src,'id':name})
  (root/f'docs/diagrams/{name}.svg').write_text(svg)
  print(name,len(svg),'SVG chars')
 browser.close()
