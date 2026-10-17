import re,os,glob,html,json,copy
from bs4 import BeautifulSoup,NavigableString,Tag,Comment
SRC='/workspace/churchill-findability'; OUT='/workspace/churchill-redesign'
os.chdir(SRC)
# header/footer/GROUPS from findability builder
code=open('/workspace/build_find.py').read(); code=code[:code.index('# hub')]
code=code.replace("R='/workspace/churchill-redesign'; os.chdir(R)","")
g={}; exec(code,g); GROUPS=g['GROUPS']; HEADER=g['header']; FOOTER=g['footer']; PHONE=g['PHONE']; TEL=g['TEL']
INLINE={'a','span','strong','b','em','i','u','br','sup','sub','font','small','mark','abbr','time','code','s','del','ins','label','cite','q'}
SKIPCLS=('elementor-hidden-desktop','elementor-nav-menu--dropdown','elementor-menu-toggle','elementor-widget-search-form','elementor-widget-share-buttons','elementor-widget-login','elementor-widget-spacer','elementor-widget-divider','elementor-widget-google','elementor-widget-social-icons','elementor-swiper-button','swiper-pagination')
def esc(s): return html.escape(s,quote=True)
def norm(s): return re.sub(r'\s+',' ',s).strip()
def resolve(base,u):
  if not u or u.startswith(('http','data:','mailto:','tel:','#','//')): return u
  return os.path.normpath(os.path.join(base,u.split('#')[0])).replace('\\','/')+('#'+u.split('#',1)[1] if '#' in u else '')
class Ctx: pass
def inline_html(node,ctx):
  out=[]
  for c in node.children:
    if isinstance(c,Comment): continue
    if isinstance(c,NavigableString): out.append(esc(str(c))); continue
    if not isinstance(c,Tag) or c.name in('script','style','noscript','svg','i') and not c.get_text(strip=True): continue
    if c.name in ('script','style','noscript','svg'): continue
    if c.name=='br': out.append('<br>'); continue
    if c.name=='img': continue
    inner=inline_html(c,ctx)
    if c.name in('span','time','label','small','cite','abbr') : inner=' '+inner+' '
    if c.name=='a' and c.get('href'):
      h=link(c['href'],ctx); ext=h.startswith('http') and 'thechurchillcenter.com' not in h
      out.append(f'<a href="{esc(h)}"'+(' target="_blank" rel="noopener"' if ext else '')+f'>{inner}{"<span class=\"sr\"> (opens in new tab)</span>" if ext else ""}</a>')
    elif c.name in('strong','b'): out.append(f'<strong>{inner}</strong>')
    elif c.name in('em',): out.append(f'<em>{inner}</em>')
    elif c.name in('sup','sub'): out.append(f'<{c.name}>{inner}</{c.name}>')
    else: out.append(inner)
  return ''.join(out)
def link(h,ctx):
  # hrefs in source are relative to source file dir; output pages at same paths, so keep relative unchanged
  return h
def img_of(t,ctx):
  src=t.get('data-src') or t.get('data-lazy-src') or t.get('src') or ''
  if not src or src.startswith('data:') or src.endswith('.svg'): return None
  if not src.startswith('http'):
    pth=resolve(ctx.base,src)
    if not os.path.exists(pth) and not os.path.exists(pth.split('?')[0]): return None
  w=t.get('width'); h=t.get('height')
  try:
    if w and int(w)<60: return None
  except: pass
  return {'src':src,'alt':norm(t.get('alt') or ''),'w':w,'h':h}
def hidden(t):
  cls=' '.join(t.get('class') or [])
  if any(k in cls for k in SKIPCLS): return True
  st=(t.get('style') or '').replace(' ','')
  if 'display:none' in st: return True
  
  return False
def walk(node,ctx,B):
  for c in node.children:
    if isinstance(c,Comment): continue
    if isinstance(c,NavigableString):
      s=norm(str(c))
      if s: B.append(('p',esc(s)))
      continue
    if not isinstance(c,Tag) or c.name in('script','style','noscript','svg','input','button','select','textarea','template'): continue
    if c.name=='video': continue
    if hidden(c): continue
    cls=' '.join(c.get('class') or [])
    if c.name=='iframe':
      s=c.get('src') or c.get('data-src') or ''
      if 'youtube' in s or 'vimeo' in s: B.append(('video',s,c.get('title') or 'Video'))
      continue
    if 'elementor-widget-video' in cls:
      m=re.search(r'youtube_url&quot;:&quot;([^&]+)|"youtube_url":"([^"]+)"',str(c.get('data-settings','')))
      ds=c.get('data-settings') or ''
      m=re.search(r'"youtube_url":"([^"]+)"',ds)
      if m:
        u=m.group(1).replace('\\/','/'); vid=re.search(r'(?:v=|youtu\.be/|embed/|shorts/)([\w-]{11})',u)
        if vid: B.append(('video','https://www.youtube-nocookie.com/embed/'+vid.group(1),'Video'))
      walk(c,ctx,B); continue
    if c.name=='article' and ctx.kind=='archive':
      a=c.find('a',href=True); im=c.find('img'); t=c.find(['h1','h2','h3','h4','h5'])
      ex=c.find(class_=re.compile('excerpt')); meta=c.find(class_=re.compile('post__meta|meta-data|elementor-post-date|post-date'))
      B.append(('post',{'href':(t.find('a') or a or {}).get('href','') if t else a.get('href','') if a else '','title':norm(t.get_text(' ')) if t else '','img':img_of(im,ctx) if im else None,'ex':norm(ex.get_text(' ')) if ex else '','meta':norm(meta.get_text(' ')) if meta else '','more':norm(c.find(class_=re.compile('read-more')).get_text(' ')) if c.find(class_=re.compile('read-more')) else ''}))
      continue
    if re.fullmatch(r'h[1-6]',c.name):
      t=inline_html(c,ctx)
      if words(t)>20: B.append(('p',norm(t)))
      elif norm(re.sub('<[^>]+>','',t)): B.append(('h',int(c.name[1]),t))
      continue
    if c.name in('ul','ol'):
      items=[]
      for li in c.find_all('li',recursive=False):
        if hidden(li): continue
        sub=li.find(['ul','ol'])
        t=inline_html(li,ctx) if not sub else inline_html(li,ctx)
        t=norm(t)
        if norm(re.sub('<[^>]+>','',t)): items.append(t)
      if items: B.append(('ul',items,'nav' if c.find_parent('nav') else ''))
      continue
    if c.name=='table':
      rows=[[inline_html(td,ctx) for td in tr.find_all(['td','th'])] for tr in c.find_all('tr')]
      B.append(('table',rows)); continue
    if c.name=='img':
      i=img_of(c,ctx)
      if i: B.append(('img',i))
      continue
    if 'elementor-tab-title' in cls or 'elementor-accordion-title' in cls or 'elementor-tab-mobile-title' in cls:
      if 'elementor-tab-mobile-title' in cls: continue
      B.append(('h',3,norm(inline_html(c,ctx)))); continue
    if c.name=='a' and ('elementor-button' in cls or 'button' in cls):
      t=norm(c.get_text(' '))
      if t: B.append(('btn',c.get('href',''),esc(t)))
      continue
    # inline-only container -> paragraph
    kids=[k for k in c.children if isinstance(k,Tag) and not hidden(k) and k.name not in('script','style','noscript','svg')]
    has_text=any(isinstance(k,NavigableString) and not isinstance(k,Comment) and norm(str(k)) for k in c.children)
    imgs=c.find_all('img')
    if all(k.name in INLINE for k in kids) and (has_text or kids):
      for im in imgs:
        i=img_of(im,ctx)
        if i: B.append(('img',i))
      btn=[k for k in kids if k.name=='a' and 'button' in ' '.join(k.get('class') or [])]
      if len(kids)==1 and btn and not has_text:
        t=norm(btn[0].get_text(' '))
        if t: B.append(('btn',btn[0].get('href',''),esc(t)))
        continue
      t=norm(inline_html(c,ctx))
      if norm(re.sub('<[^>]+>','',t)): B.append(('p',t))
      continue
    walk(c,ctx,B)
def words(s): return len(re.findall(r'\w+',re.sub('<[^>]+>',' ',html.unescape(s))))
def plain(s): return norm(html.unescape(re.sub('<[^>]+>',' ',s)))
# --- renderers
def img_tag(i,cls='',eager=False,sizes='(max-width: 760px) 100vw, 50vw'):
  wh=f' width="{esc(str(i["w"]))}" height="{esc(str(i["h"]))}"' if i.get('w') and i.get('h') and str(i['w']).isdigit() and str(i['h']).isdigit() else ''
  return f'<img class="{cls}" src="{esc(i["src"])}" alt="{esc(i["alt"])}"{wh} loading="{"eager" if eager else "lazy"}" decoding="async">'
def render_blocks(bl):
  o=[];k=0
  while k<len(bl):
    b=bl[k]
    if b[0]=='p': o.append(f'<p>{b[1]}</p>')
    elif b[0]=='h': o.append(f'<h{min(6,max(3,b[1]))} class="sub">{b[2]}</h{min(6,max(3,b[1]))}>')
    elif b[0]=='ul':
      items=b[1]
      if b[2]=='nav': o.append('<ul class="chips">'+''.join(f'<li>{x}</li>' for x in items)+'</ul>')
      else: o.append('<ul class="ticks">'+''.join(f'<li>{x}</li>' for x in items)+'</ul>')
    elif b[0]=='img': o.append('<figure class="fig">'+img_tag(b[1])+'</figure>')
    elif b[0]=='btn': o.append(f'<p><a class="btn btn-ghost" href="{esc(b[1])}">{b[2]}</a></p>')
    elif b[0]=='video': o.append(f'<div class="video"><iframe src="{esc(b[1])}" title="{esc(b[2])}" loading="lazy" allowfullscreen></iframe></div>')
    elif b[0]=='table': o.append('<div class="tablewrap"><table>'+''.join('<tr>'+''.join(f'<td>{c}</td>' for c in r)+'</tr>' for r in b[1])+'</table></div>')
    k+=1
  return '\n'.join(o)
SID=[0]
def expander(bl,label='Read more'):
  """first paragraph clamped, rest in details"""
  if not bl: return ''
  tw=sum(words(b[1]) if b[0]=='p' else words(' '.join(b[1])) if b[0]=='ul' else words(b[2]) if b[0]=='h' else 0 for b in bl)
  if tw<=70: return render_blocks(bl)
  # visible: first paragraph (clamped) + up to 4 bullets of first list
  vis=[];rest=list(bl)
  while rest and rest[0][0] in('img','btn','video'): vis.append(rest.pop(0))
  if rest and rest[0][0]=='p': vis.append(('pc',rest.pop(0)[1]))
  SID[0]+=1
  out=''
  for b in vis:
    out+= f'<p class="clamp" data-clamp>{b[1]}</p>' if b[0]=='pc' else render_blocks([b])
  if rest:
    hl=[b for b in rest if b[0]=='ul' and b[2]!='nav']
    if hl and not vis:
      pass
    out+=f'<details class="more"><summary><span class="when-closed">{label}</span><span class="when-open">Show less</span></summary><div class="more-body">{render_blocks(rest)}</div></details>'
  else:
    out=out.replace('<p class="clamp" data-clamp>','<p class="clamp" data-clamp data-solo>')
  return out
def sections(B):
  """split into (heading, blocks)"""
  S=[];cur=[None,[]]
  for b in B:
    if b[0]=='h' and (b[1]<=3 or plain(b[2]).endswith('?')):
      if cur[0] is not None or cur[1]: S.append(cur)
      cur=[b[2],[]]
    else: cur[1].append(b)
  if cur[0] is not None or cur[1]: S.append(cur)
  return S
def swords(s): return sum(words(b[1]) if b[0]=='p' else words(' '.join(b[1])) if b[0]=='ul' else words(b[2]) if b[0]=='h' else 0 for b in s[1])
def render_sections(S):
  out=[];i=0;n=0
  while i<len(S):
    h,bl=S[i]
    # FAQ group: consecutive question headings
    if h and plain(h).endswith('?'):
      grp=[]
      while i<len(S) and S[i][0] and plain(S[i][0]).endswith('?'): grp.append(S[i]); i+=1
      if len(grp)>=2:
        out.append('<section class="band"><div class="wrap narrow"><h2 class="eyebrow-h">Questions &amp; answers</h2><div class="faq">'+''.join(f'<details class="qa"><summary>{q}</summary><div class="qa-body">{render_blocks(b)}</div></details>' for q,b in grp)+'</div></div></section>'); continue
      i-=len(grp)
      grp=[]
    # card group: consecutive short sections
    if h and swords(S[i])<=45 and not any(b[0] in('video','table','post') for b in bl):
      grp=[]
      while i<len(S) and S[i][0] and swords(S[i])<=45 and not any(b[0] in('video','table','post') for b in S[i][1]): grp.append(S[i]); i+=1
      if len(grp)>=2:
        cards=''
        for q,b in grp:
          im=next((x[1] for x in b if x[0]=='img'),None); rest=[x for x in b if not(x[0]=='img' and x[1] is im)]
          cards+=f'<article class="card">{("<div class=card-media>"+img_tag(im)+"</div>") if im else "<span class=card-dot aria-hidden=true></span>"}<div class="card-body"><h3>{q}</h3>{render_blocks(rest)}</div></article>'
        out.append(f'<section class="band"><div class="wrap"><div class="cards">{cards}</div></div></section>'); continue
      i-=len(grp)
    n+=1
    imgs=[b for b in bl if b[0]=='img']
    lead_img=imgs[0][1] if imgs else None
    body=[b for b in bl if not(lead_img and b[0]=='img' and b[1] is lead_img)]
    alt=' flip' if n%2==0 else ''
    head=f'<h2>{h}</h2>' if h else ''
    if lead_img and swords([None,body])>0:
      out.append(f'<section class="band{alt}"><div class="wrap split"><div class="split-media">{img_tag(lead_img)}</div><div class="split-text">{head}{expander(body)}</div></div></section>')
    else:
      inner=expander(body) if not lead_img else '<figure class="fig">'+img_tag(lead_img)+'</figure>'
      if not head and not inner.strip(): i+=1; continue
      out.append(f'<section class="band"><div class="wrap narrow">{head}{inner}</div></section>')
    i+=1
  return '\n'.join(out)
def page_shell(rel,title,desc,main,canon,ogimg=None):
  p='../'*rel.count('/')
  return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><link rel="canonical" href="https://thechurchillcenter.com/{esc(canon)}"><meta name="robots" content="noindex">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">{f'<meta property="og:image" content="{esc(ogimg)}">' if ogimg else ''}
<link rel="icon" href="{p}wp-content/uploads/2024/11/cropped-Logo-Thechurchill.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=DM+Sans:wght@400;500;700&display=swap">
<link rel="stylesheet" href="{p}assets/modern/site.css"></head><body>
<a class="skip" href="#main">Skip to content</a>
{HEADER(p)}<main id="main">{main}</main>
<section class="cta-band"><div class="wrap"><h2>Ready to start?</h2><p>Consultations in person or virtual.</p><div class="cta-row"><a class="btn" href="{p}appointments/">Book Appointment</a><a class="btn btn-ghost light" href="{TEL}">Call {PHONE}</a></div></div></section>
{FOOTER(p)}<script src="{p}assets/modern/site.js" defer></script></body></html>'''
def hero(title,lead,img,p,kicker='The Churchill Center',big=False):
  im=img_tag(img,'hero-img',eager=True) if img else ''
  return f'''<section class="hero{' hero-big' if big else ''}{' has-img' if img else ''}"><div class="wrap hero-grid"><div class="hero-text"><p class="kicker">{kicker}</p><h1>{title}</h1>{f'<p class="lead">{lead}</p>' if lead else ''}<div class="cta-row"><a class="btn" href="{p}appointments/">Book Appointment</a><a class="btn btn-ghost" href="{TEL}">Call {PHONE}</a></div></div>{f'<div class="hero-media">{im}</div>' if im else ''}</div></section>'''
def first_sentence(t,maxw=28):
  t=plain(t); m=re.match(r'(.{20,}?[.!?])(\s|$)',t)
  s=m.group(1) if m else t
  w=s.split()
  return esc(' '.join(w[:maxw])+('…' if len(w)>maxw else ''))
# --- page loop
files=[f for f in glob.glob('**/*.html',recursive=True) if not f.startswith(('wp-','assets/','docs/','comments/','author/'))]
INDEX=[];PAGEINFO={}
for f in sorted(files):
  raw=open(f,encoding='utf-8',errors='ignore').read()
  if 'http-equiv="refresh"' in raw or '<body' not in raw:
    os.makedirs(os.path.dirname(os.path.join(OUT,f)) or OUT,exist_ok=True); open(os.path.join(OUT,f),'w').write(raw); continue
  soup=BeautifulSoup(raw,'lxml')
  ctx=Ctx(); ctx.base=os.path.dirname(f)
  r0=soup.find(attrs={'data-elementor-type':re.compile('^(wp-page|single|archive|single-post|single-page)$')})
  ctx.kind=r0.get('data-elementor-type') if r0 else 'page'
  root=soup.find('main',id='main') or r0
  if f=='services/index.html':
    root=soup.find('main',class_='cf-hub'); ctx.kind='hub'
  if root is None: root=soup.find(id='main') or soup.body
  for bad in root.select('.cf-header,.cf-footer,.cf-sticky,[data-elementor-type=popup]'): bad.decompose()
  B=[];walk(root,ctx,B)
  # collapse exact duplicate consecutive blocks
  D=[]
  for b in B:
    if D and repr(D[-1])==repr(b): continue
    D.append(b)
  B=D
  t=soup.title.get_text().strip() if soup.title else ''
  md=soup.find('meta',attrs={'name':'description'}) or soup.find('meta',attrs={'property':'og:description'})
  desc=norm(md['content']) if md and md.get('content') else ''
  rel=f; p='../'*rel.count('/')
  canon=f[:-10] if f.endswith('index.html') else f
  # title / h1
  h1=None
  for k,b in enumerate(B):
    if b[0]=='h': h1=b[2]; del B[k]; break
  if not h1: h1=esc(re.sub(r'\s*[-|]\s*(The )?Churchill Center\s*$','',t))
  PAGEINFO[f]={'title':plain(h1),'desc':desc}
  if ctx.kind=='archive':
    posts=[b[1] for b in B if b[0]=='post']; other=[b for b in B if b[0]!='post']
    cards=''
    for po in posts:
      im=po['img']
      cards+=f'<article class="card post"><a class="card-link" href="{esc(po["href"])}">{("<div class=card-media>"+img_tag(im)+"</div>") if im else ""}<div class="card-body">{f"<p class=meta>{esc(po["meta"])}</p>" if po["meta"] else ""}<h3>{esc(po["title"])}</h3>{f"<p>{esc(po["ex"])}</p>" if po["ex"] else ""}<span class="more-link">{esc(po["more"] or "Read more")} →</span></div></a></article>'
    pag=[b for b in other if b[0] in('p','btn','ul')]
    main=hero(h1,'',None,p,kicker='Blog &amp; media')+f'<section class="band"><div class="wrap"><div class="cards posts">{cards}</div><nav class="pager" aria-label="Pagination">{render_blocks(pag)}</nav></div></section>'
  elif ctx.kind=='hub':
    out=''
    for gname,items in GROUPS:
      cards=''
      for l,u in items:
        if u.startswith('http'): im=None; ex='Page on the live site (not included in this test copy).'; href=u
        else:
          href='../'+u; src=u+'index.html'; sraw=open(src,errors='ignore').read()
          ssoup=BeautifulSoup(sraw,'lxml'); sroot=ssoup.find(attrs={'data-elementor-type':re.compile('^(wp-page|single)$')}) or ssoup
          im=None
          for x in sroot.find_all('img'):
            c2=Ctx(); c2.base=os.path.dirname(src); i=img_of(x,c2)
            if i: im=dict(i); im['src']=os.path.relpath(resolve(c2.base,i['src']),'services'); break
          mm=ssoup.find('meta',attrs={'name':'description'}) or ssoup.find('meta',attrs={'property':'og:description'})
          ex=norm(mm['content']) if mm and mm.get('content') else ''
        cards+=f'<article class="card"><a class="card-link" href="{esc(href)}">{("<div class=card-media>"+img_tag(im)+"</div>") if im else "<div class=card-media ph aria-hidden=true></div>"}<div class="card-body"><h3>{esc(l)}</h3><p class="clamp3">{esc(ex)}</p><span class="more-link">Learn more →</span></div></a></article>'
      gid=re.sub(r'\W+','-',gname.lower()).strip('-')
      out+=f'<section class="band" id="{gid}"><div class="wrap"><h2>{esc(gname)}</h2><div class="cards">{cards}</div></div></section>'
    jump='<nav class="jump" aria-label="Categories">'+''.join(f'<a href="#{re.sub(r"\W+","-",gn.lower()).strip("-")}">{esc(gn)}</a>' for gn,_ in GROUPS)+'</nav>'
    main=hero('Treatments &amp; Services','Every treatment and service page in one place, grouped by category.',None,p)+f'<div class="wrap">{jump}</div>'+out
  else:
    # hero image: first content image
    himg=None
    for k,b in enumerate(B):
      if b[0]=='img': himg=b[1]; del B[k]; break
    if himg is None and r0 is not None and r0.get('data-elementor-id'):
      for cf in glob.glob('wp-content/uploads/elementor/css/post-%s.css*'%r0['data-elementor-id']):
        for u in re.findall(r'background-image:url\("?([^")]+)"?\)',open(cf,errors='ignore').read()):
          pth=os.path.normpath(os.path.join(os.path.dirname(cf),u))
          if os.path.exists(pth) and not pth.endswith('.svg'):
            himg={'src':os.path.relpath(pth,os.path.dirname(f) or '.'),'alt':'','w':None,'h':None}; break
        if himg: break
    if f=='index.html':
      for cand in ['wp-content/uploads/2020/06/Medical-Center－3.gif']:
        if os.path.exists(cand): himg={'src':cand,'alt':'The Churchill Center','w':None,'h':None}
    # lead: first paragraph
    lead=''
    S=sections(B)
    if S and S[0][0] is None and S[0][1] and S[0][1][0][0]=='p' and words(S[0][1][0][1])<=30:
      lead=S[0][1][0][1]; S[0][1].pop(0)
    main=hero(h1,lead,himg,p,big=(f=='index.html'))+render_sections(S)
  ogi=None
  html_out=page_shell(rel,t or plain(h1),desc,main,canon,ogi)
  os.makedirs(os.path.dirname(os.path.join(OUT,f)) or OUT,exist_ok=True)
  open(os.path.join(OUT,f),'w',encoding='utf-8').write(html_out)
  if '?' not in f and '/page/' not in f and not re.match(r'\d{4}/',f):
    tx=plain(main)
    INDEX.append({'t':PAGEINFO[f]['title'],'u':canon,'d':desc[:200],'x':tx[:4000]})
os.makedirs(OUT+'/assets/findability',exist_ok=True)
json.dump(INDEX,open(OUT+'/assets/findability/search-index.json','w'),ensure_ascii=False)
print('pages',len(INDEX))
