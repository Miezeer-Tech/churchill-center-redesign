import glob,os,re,json,collections,sys
from playwright.sync_api import sync_playwright
os.chdir('/workspace/churchill-redesign')
files=sorted(f for f in glob.glob('**/*.html',recursive=True) if not f.startswith(('wp-','assets/','docs/','comments/','author/')) and 'http-equiv="refresh"' not in open(f,errors='ignore').read())
only=sys.argv[1:] or None
if only: files=[f for f in files if f in only]
def toks(s): return collections.Counter(w.lower() for w in re.findall(r"[\w’']+",s))
res={}
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
  ctx=b.new_context(viewport={'width':1280,'height':900}); ctx.route('**/*',lambda r:r.abort() if r.request.resource_type in('image','media','font') or not r.request.url.startswith('http://localhost') else r.continue_())
  pg=ctx.new_page()
  for f in files:
    u=f.replace('?','%3F')
    pg.goto('http://localhost:8812/'+u,wait_until='domcontentloaded'); pg.wait_for_timeout(300)
    old=pg.evaluate("()=>{document.querySelectorAll('.cf-header,.cf-footer,.cf-sticky,script,style,.skip-link,a[href=\"#main\"]').forEach(e=>e.remove());return document.body.innerText}")
    pg.goto('http://localhost:8811/'+u,wait_until='domcontentloaded')
    new=pg.evaluate("()=>{document.querySelectorAll('details').forEach(d=>d.open=true);document.querySelectorAll('.clamp,.clamp3').forEach(e=>e.classList.remove('clamp','clamp3'));const m=document.querySelector('main');return m?m.innerText:''}")
    o=toks(old);n=toks(new)
    tot=sum(o.values()); kept=sum(min(c,n[w]) for w,c in o.items())
    miss=[w for w,c in o.items() if n[w]<c]
    res[f]=(round(100*kept/max(tot,1),2),tot,miss[:25])
  b.close()
json.dump(res,open('/workspace/redesign/retain.json','w'),ensure_ascii=False,indent=0)
low={k:v for k,v in res.items() if v[0]<98}
print('pages',len(res),'below98',len(low))
for k,v in sorted(low.items(),key=lambda x:x[1][0]): print(k,v[0],v[1],v[2][:15])
