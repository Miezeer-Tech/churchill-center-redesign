import json,sys
from playwright.sync_api import sync_playwright
B='http://localhost:8811/'
R=[]
def ok(name,cond,info=''):
  R.append((name,bool(cond),info)); print(('PASS' if cond else 'FAIL'),name,info)
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
  # desktop menu + nav
  pg=b.new_page(viewport={'width':1280,'height':900}); pg.goto(B,wait_until='networkidle')
  links=pg.eval_on_selector_all('header nav a','els=>els.map(e=>[e.textContent.trim(),e.getAttribute("href")])')
  ok('desktop nav links',len(links)>=6,str(links))
  bad=[]
  for t,h in links:
    r=pg.request.get(B+h.lstrip('./')) if not h.startswith('http') else None
    if r and r.status!=200: bad.append((h,r.status))
  ok('nav links resolve 200',not bad,str(bad))
  # skip link first tab
  pg.keyboard.press('Tab'); f=pg.evaluate('[document.activeElement.textContent.trim(),document.activeElement.getAttribute("href")]')
  ok('skip link first Tab stop','skip' in f[0].lower() or f[1]=='#main',str(f))
  oc=pg.evaluate('getComputedStyle(document.activeElement).outlineStyle+" "+getComputedStyle(document.activeElement).outlineWidth')
  ok('visible focus outline',not oc.startswith('none'),oc)
  # search dialog
  pg.click('button[aria-label*="earch" i], .search-btn')
  pg.wait_for_selector('dialog[open]')
  inp=pg.locator('dialog[open] input'); inp.fill('thyroid'); pg.wait_for_timeout(600)
  res=pg.eval_on_selector_all('dialog[open] a','els=>els.map(e=>e.textContent.trim().slice(0,50))')
  ok('search "thyroid" results',any('hyroid' in r for r in res),str(res[:5]))
  pg.locator('dialog[open] a',has_text='hyroid').first.click(); pg.wait_for_load_state('networkidle')
  ok('search result click-through',pg.url!=B and pg.locator('h1').count()==1,pg.url)
  pg.goto(B,wait_until='networkidle'); pg.click('button[aria-label*="earch" i], .search-btn'); pg.wait_for_selector('dialog[open]')
  pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
  ok('search Esc closes',pg.locator('dialog[open]').count()==0)
  # finder
  pg.goto(B+'treatments/',wait_until='networkidle')
  vis=lambda: pg.eval_on_selector_all('.finder-grid .tcard','els=>els.filter(e=>!e.hidden&&e.offsetParent).length')
  tot=vis(); ok('finder shows all cards',tot>=15,str(tot))
  pg.fill('#fq','detox'); pg.wait_for_timeout(300); n=vis()
  cnt=pg.text_content('.finder-count'); live=pg.get_attribute('.finder-count','aria-live')
  ok('finder query filters',0<n<tot,f'{n} visible, count="{cnt.strip()}", aria-live={live}')
  pg.fill('#fq','zzzqqq'); pg.wait_for_timeout(300)
  ok('finder empty state',vis()==0 and pg.is_visible('.finder-empty'))
  pg.fill('#fq',''); chip=pg.locator('.finder .chip').nth(2); chip.click(); pg.wait_for_timeout(300)
  ok('finder chip filters + aria-pressed',vis()<tot and chip.get_attribute('aria-pressed')=='true',f'{vis()} visible; url={pg.url}')
  pg.goto(B+'treatments/?q=iv',wait_until='networkidle'); ok('finder ?q= param',0<vis()<tot and pg.input_value('#fq')=='iv',str(vis()))
  pg.goto(B+'treatments/?c=hormones-thyroid',wait_until='networkidle'); ok('finder ?c= param',0<vis()<tot,str(vis()))
  # home finder form
  pg.goto(B,wait_until='networkidle')
  pg.locator('form[action*="treatments"] input').first.fill('migraine'); pg.locator('form[action*="treatments"] input').first.press('Enter'); pg.wait_for_load_state('networkidle')
  ok('home finder form -> finder',('q=migraine' in pg.url) and 0<vis()<tot,pg.url+' '+str(vis()))
  # blog filter
  pg.goto(B+'blog/',wait_until='networkidle')
  allp=pg.eval_on_selector_all('.posts .pcard','els=>els.filter(e=>e.offsetParent).length')
  pg.locator('.post-filter .chip').nth(1).click(); pg.wait_for_timeout(300)
  np_=pg.eval_on_selector_all('.posts .pcard','els=>els.filter(e=>e.offsetParent).length')
  ok('blog filter chips',0<np_<allp,f'{np_}/{allp}')
  # expanders
  pg.goto(B+'doctors/',wait_until='networkidle')
  d=pg.locator('details').first; d.locator('summary').click(); ok('doctors expander opens',d.evaluate('e=>e.open'))
  # mobile menu
  m=b.new_page(viewport={'width':390,'height':844}); m.goto(B,wait_until='networkidle')
  tg=m.locator('[aria-expanded]').filter(has_text='').first
  tg=m.locator('button[aria-controls]').first
  ok('mobile toggle aria-expanded=false',tg.get_attribute('aria-expanded')=='false')
  tg.click(); m.wait_for_timeout(300)
  navv=m.eval_on_selector_all('header nav a','els=>els.filter(e=>e.offsetParent).length')
  ok('mobile menu opens',tg.get_attribute('aria-expanded')=='true' and navv>=5,str(navv))
  m.keyboard.press('Escape'); m.wait_for_timeout(200); ok('mobile menu Esc closes',tg.get_attribute('aria-expanded')=='false')
  ok('mobile Call/Book bar',m.locator('.mbar a[href^="tel:"]').count()==1)
  # a11y per page
  pages=['','treatments/','treatments/detoxification/','treatments/womens-health/','doctors/','blog/','reviews/','dr-dana-show/','contact/','book/','about/','faq/']
  for u in pages:
    for w in (1280,390):
      q=b.new_page(viewport={'width':w,'height':900}); q.goto(B+u,wait_until='networkidle')
      a=q.evaluate('''()=>({h1:document.querySelectorAll('h1').length,
        noalt:[...document.images].filter(i=>!i.hasAttribute('alt')).length,
        skip:(()=>{let l=0,bad=0;document.querySelectorAll('main h1,main h2,main h3,main h4').forEach(h=>{let n=+h.tagName[1];if(l&&n>l+1)bad++;l=n});return bad})(),
        hs:document.documentElement.scrollWidth>innerWidth+1,
        lang:document.documentElement.lang,
        unl:[...document.querySelectorAll('a,button')].filter(e=>!(e.textContent.trim()||e.getAttribute('aria-label')||e.querySelector('img[alt]:not([alt=""])'))).length,
        small:[...document.querySelectorAll('main a.btn,header button,.chip')].filter(e=>e.offsetParent&&e.getBoundingClientRect().height<40).length})''')
      okk=a['h1']==1 and a['noalt']==0 and a['skip']==0 and not a['hs'] and a['lang'] and a['unl']==0 and a['small']==0
      ok(f'a11y {u or "/"} @{w}',okk,json.dumps(a))
      q.close()
  # redirects
  for o,n in [('ourdoctors/','doctors/'),('contact-us/','contact/'),('services/','treatments/'),('appointments/','book/'),('treatments/women-health/','treatments/womens-health/'),('the-drug-free-solution-for-migraine-and-cluster-headache/','treatments/migraine-cluster-headache/'),('rejuvenation-treatment-for-women-beauty-therapy/','treatments/rejuvenation-women/'),('esthetic-medicine/','blog/esthetic-medicine/'),('eczema-since-childhood-it-became-worse-especially-on-my-face-and-hands/','reviews/eczema-since-childhood-it-became-worse-especially-on-my-face-and-hands/'),('category/reviews/','reviews/'),('welcome/','about/')]:
    q=b.new_page(); q.goto(B+o); q.wait_for_timeout(1500)
    ok(f'redirect {o}',q.url.endswith(n),q.url); q.close()
  b.close()
json.dump(R,open('/workspace/v2/test.json','w'),indent=1)
print(sum(r[1] for r in R),'/',len(R))
