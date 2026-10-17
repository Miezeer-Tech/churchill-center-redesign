import json,re,collections,sys
from playwright.sync_api import sync_playwright
C=json.load(open('/workspace/v2/content.json')); U=json.load(open('/workspace/v2/urlmap.json'))
def toks(s): return collections.Counter(w.lower() for w in re.findall(r"[\w’']+",s))
pairs=[]
for f in C:
  d=f.replace('index.html','')
  pairs.append((f,U.get(d,d)))
if len(sys.argv)>1: pairs=[p for p in pairs if p[0] in sys.argv[1:]]
res={}
OPEN="()=>{document.querySelectorAll('details').forEach(d=>d.open=true);document.querySelectorAll('[hidden]').forEach(e=>e.hidden=false);document.querySelectorAll('.clamp,.clamp3,.clamp4').forEach(e=>e.classList.remove('clamp','clamp3','clamp4'));const m=document.querySelector('main');return m?m.innerText:''}"
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
  ctx=b.new_context(viewport={'width':1280,'height':900}); ctx.route('**/*',lambda r:r.abort() if r.request.resource_type in('image','media','font') or not r.request.url.startswith('http://localhost') else r.continue_())
  pg=ctx.new_page(); cache={}
  for f,n in pairs:
    pg.goto('http://localhost:8812/'+f.replace('?','%3F'),wait_until='domcontentloaded'); pg.wait_for_timeout(700)
    old=pg.evaluate("()=>{document.querySelectorAll('.cf-header,.cf-footer,.cf-sticky,script,style,.skip-link').forEach(e=>e.remove());return document.body.innerText}")
    if re.match(r'\d{4}/',f):
      links=[re.search(r'href="([^"]+)"',b[2]).group(1) for b in C[f]['blocks'] if b[0]=='h' and 'href' in b[2]]
      tg=['reviews/','blog/']+[U.get(l.strip('/').replace('index.html','').rstrip('/')+'/',None) for l in links if l.startswith('/')]
      tg=[t for t in tg if t]
    else: tg=[n]
    n='+'.join(tg)
    if n not in cache:
      t=''
      for x in tg: pg.goto('http://localhost:8811/'+x,wait_until='domcontentloaded'); t+='\n'+pg.evaluate(OPEN)
      cache[n]=t
    o,nw=toks(old),toks(cache[n]); tot=sum(o.values()); kept=sum(min(c,nw[w]) for w,c in o.items())
    res[f]={'new':n,'pct':round(100*kept/max(tot,1),2),'words':tot,'missing':{w:c-nw[w] for w,c in o.items() if nw[w]<c}}
  b.close()
json.dump(res,open('/workspace/v2/retain.json','w'),ensure_ascii=False,indent=1)
low=sorted([(v['pct'],k) for k,v in res.items() if v['pct']<98])
print('pages',len(res),'below98',len(low))
for pct,k in low: print(pct,k,'->',res[k]['new'],res[k]['words'],list(res[k]['missing'].items())[:14])
