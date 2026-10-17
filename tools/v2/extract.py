import os,re,json,glob,sys
src=open('/workspace/redesign/build.py').read(); src=src[:src.index('import sys; sys.path')]
g={};exec(src,g)
from bs4 import BeautifulSoup
os.chdir('/workspace/churchill-findability')
out={}
for f in sorted(glob.glob('**/*.html',recursive=True)):
  if f.startswith(('wp-','assets/','docs/','comments/','author/','tools/')) or '?' in f: continue
  raw=open(f,errors='ignore').read()
  if 'http-equiv="refresh"' in raw or '<body' not in raw: continue
  soup=BeautifulSoup(raw,'lxml')
  r0=soup.find(attrs={'data-elementor-type':re.compile('^(wp-page|single|archive)$')})
  kind=r0.get('data-elementor-type') if r0 else 'page'
  root=soup.find('main',id='main') or r0
  if f=='services/index.html': continue
  for bad in root.select('.cf-header,.cf-footer,.cf-sticky,[data-elementor-type=popup]'): bad.decompose()
  c=g['Ctx'](); c.base=os.path.dirname(f); c.kind=kind; B=[]; g['walk'](root,c,B)
  D=[]
  for b in B:
    if D and repr(D[-1])==repr(b): continue
    D.append(b)
  cls=' '.join(r0.get('class',[])) if r0 else ''
  cats=re.findall(r'category-([\w-]+)',cls)
  t=soup.title.get_text().strip() if soup.title else ''
  md=soup.find('meta',attrs={'name':'description'}) or soup.find('meta',attrs={'property':'og:description'})
  og=soup.find('meta',attrs={'property':'og:image'})
  tm=soup.find('meta',attrs={'property':'article:published_time'})
  # normalize image/link paths to site-root-relative
  def fix(u):
    if not u or u.startswith(('http','#','mailto:','tel:','data:','//')): return u
    return g['resolve'](c.base,u)
  def fixhtml(h): return re.sub(r'href="([^"]+)"',lambda m:'href="/'+fix(m.group(1)).lstrip('/')+'"' if not m.group(1).startswith(('http','#','mailto:','tel:')) else m.group(0),h)
  NB=[]
  for b in D:
    if b[0] in('p','h'): NB.append([b[0]]+list(b[1:-1])+[fixhtml(b[-1])])
    elif b[0]=='ul': NB.append(['ul',[fixhtml(x) for x in b[1]],b[2]])
    elif b[0]=='img': i=dict(b[1]); i['src']='/'+fix(i['src']) if not i['src'].startswith('http') else i['src']; NB.append(['img',i])
    elif b[0]=='btn': NB.append(['btn','/'+fix(b[1]).lstrip('/') if b[1] and not b[1].startswith(('http','#','tel:','mailto:')) else b[1],b[2]])
    elif b[0]=='post':
      d=dict(b[1]); d['href']='/'+fix(d['href']).lstrip('/') if d['href'] and not d['href'].startswith('http') else d['href']
      if d['img']: d['img']=dict(d['img']); d['img']['src']='/'+fix(d['img']['src'])
      NB.append(['post',d])
    elif b[0]=='table': NB.append(['table',[[fixhtml(x) for x in r] for r in b[1]]])
    else: NB.append(list(b))
  out[f]={'title':t,'desc':(md.get('content') if md else '') or '','og':og.get('content') if og else '','date':tm.get('content') if tm else '','kind':kind,'cats':cats,'blocks':NB}
json.dump(out,open('/workspace/v2/content.json','w'),ensure_ascii=False)
print(len(out))
from collections import Counter
print(Counter(v['kind'] for v in out.values())); print(Counter(c for v in out.values() for c in v['cats']))
