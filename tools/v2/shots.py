from playwright.sync_api import sync_playwright
import sys
tag=sys.argv[1]
P={'before':[('home',''),('finder','services/'),('treatment','treatments/detoxification/'),('doctors','ourdoctors/'),('blog','category/blog/')],
   'after':[('home',''),('finder','treatments/'),('treatment','treatments/detoxification/'),('doctors','doctors/'),('blog','blog/')]}[tag]
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
  for n,u in P:
    for w in (1280,390):
      pg=b.new_page(viewport={'width':w,'height':900}); pg.goto(f'http://localhost:8811/{u}',wait_until='networkidle',timeout=60000)
      for _ in range(18): pg.mouse.wheel(0,700); pg.wait_for_timeout(100)
      pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(1500)
      pg.screenshot(path=f'/workspace/churchill-redesign-shots/v2/{tag}-{n}-{w}.png',full_page=True); pg.close()
