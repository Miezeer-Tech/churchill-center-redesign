from playwright.sync_api import sync_playwright
B='http://localhost:8811/'
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
  pg=b.new_page(viewport={'width':1280,'height':900}); pg.goto(B,wait_until='networkidle')
  pg.hover('.cf-dd > a'); pg.wait_for_timeout(300); print('dropdown visible',pg.is_visible('.cf-menu'),pg.locator('.cf-menu a').count(),'links')
  pg.click('.cf-menu a:has-text("Detoxification")'); pg.wait_for_load_state(); print('dropdown ->',pg.url)
  pg.click('.cf-nav > a:has-text("Our Doctors")'); pg.wait_for_load_state(); print('nav Our Doctors ->',pg.url)
  pg.fill('.cf-search input','thyroid'); pg.wait_for_timeout(800); r=pg.locator('.cf-results a'); print('search thyroid',r.count(),r.first.inner_text().split('\n')[0]); r.first.click(); pg.wait_for_load_state(); print('search ->',pg.url)
  pg.goto(B+'treatments/women-health/'); d=pg.locator('details.more').first
  body=d.locator('.more-body'); print('expander closed visible',body.is_visible()); d.locator('summary').click(); pg.wait_for_timeout(200); print('expander open visible',body.is_visible(), 'label', d.locator('summary').inner_text())
  d.locator('summary').focus(); pg.keyboard.press('Enter'); pg.wait_for_timeout(200); print('keyboard toggle closes',not body.is_visible())
  pg.goto(B+'faq/'); q=pg.locator('details.qa'); print('faq items',q.count())
  if q.count(): q.first.locator('summary').click(); print('faq open',q.first.evaluate('e=>e.open'))
  m=b.new_page(viewport={'width':390,'height':844}); m.goto(B,wait_until='networkidle')
  print('mobile sticky CTA visible',m.is_visible('.cf-sticky .cf-book'),'h-scroll',m.evaluate('document.documentElement.scrollWidth>innerWidth'))
  m.click('.cf-burger-l'); print('mobile menu open',m.is_visible('.cf-nav'))
  m.keyboard.press('Tab'); print('first tab focus',m.evaluate('document.activeElement.className||document.activeElement.textContent'))
  imgs=m.evaluate("[...document.querySelectorAll('main img')].map(i=>[i.alt!==null,i.loading])"); print('main imgs',len(imgs),'lazy',sum(1 for a in imgs if a[1]=='lazy'))
  b.close()
