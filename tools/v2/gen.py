import json,re,os,html,shutil,glob
from collections import OrderedDict
C=json.load(open('/workspace/v2/content.json'))
OUT='/workspace/v2/site'
if os.path.exists(OUT): shutil.rmtree(OUT)
os.makedirs(OUT)
esc=lambda s:html.escape(s or '',quote=True)
def plain(s): return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',s or ''))).strip()
def words(s): return len(re.findall(r'\w+',plain(s)))
def ttl(t): return re.sub(r'\s*[-|│]\s*(The )?Churchill Cent(er|re)\s*$','',html.unescape(t)).strip()
PHONE='(626) 842-9123'; TEL='tel:626-842-9123'; ADDR='289 W Huntington Dr, Ste 307, Arcadia, CA 91007'
MAPQ='289%20W%20Huntington%20Dr%2C%20Ste%20307%2C%20Arcadia%2C%20CA%2091007'
# ---------- IA ----------
TREAT=OrderedDict([ # old path -> (new slug, category, short label)
 ('treatments/prevention-why/','prevention|Prevention & Diagnostics|Prevention Why?'),
 ('treatments/diagnostic-testing/','diagnostic-testing|Prevention & Diagnostics|Diagnostic Testing'),
 ('treatments/detoxification/','detoxification|Detox & IV Therapy|Detoxification'),
 ('treatments/iv-therapy-and-injections/','iv-therapy|Detox & IV Therapy|IV Therapy and Injections'),
 ('treatments/hypothyroidism/','hypothyroidism|Hormones & Thyroid|Hypothyroidism Treatment'),
 ('treatments/women-health/','womens-health|Hormones & Thyroid|Women’s Health'),
 ('treatments/mens-health/','mens-health|Hormones & Thyroid|Men’s Health'),
 ('naturopathic-medicine-2/','naturopathic-medicine|Natural & Integrative Care|Naturopathic Medicine'),
 ('the-drug-free-solution-for-migraine-and-cluster-headache/','migraine-cluster-headache|Natural & Integrative Care|Migraine & Cluster Headache'),
 ('vibrational-individualized-body-enhancement-system-v-i-b-e-s/','vibes-sound-therapy|Therapies & Bodywork|V.I.B.E.S Sound Therapy'),
 ('lumagenix-led-light-therapy/','led-light-therapy|Therapies & Bodywork|LumaGenix LED Light Therapy'),
 ('acuroma-wellness-lymphatic-therapy/','acuroma-lymphatic-therapy|Therapies & Bodywork|AcuRoma™ Wellness & Lymphatic Therapy'),
 ('rejuvenation-treatment-for-women-beauty-therapy/','rejuvenation-women|Beauty & Rejuvenation|Rejuvenation for Women'),
 ('rejuvenation-for-men-beauty-therapy/','rejuvenation-men|Beauty & Rejuvenation|Rejuvenation for Men'),
 ('anti-aging-cream/','anti-aging-skincare|Beauty & Rejuvenation|Anti-Aging Skincare'),
])
EXTERNAL=[('Joint Pain Regeneration Treatment','https://thechurchillcenter.com/?page_id=11881','Therapies & Bodywork'),('Shockwave Therapy','https://thechurchillcenter.com/?page_id=12132','Therapies & Bodywork')]
CATS=['Prevention & Diagnostics','Detox & IV Therapy','Hormones & Thyroid','Natural & Integrative Care','Therapies & Bodywork','Beauty & Rejuvenation']
URL={}  # old path (dir/) -> new path
for o,v in TREAT.items(): URL[o]='treatments/'+v.split('|')[0]+'/'
URL.update({'':'', 'ourdoctors/':'doctors/','welcome/':'about/','contact-us/':'contact/','appointments/':'book/','services/':'treatments/','treatments/':'treatments/',
 'faq/':'faq/','privacy-policy/':'privacy-policy/','terms-conditions/':'terms-conditions/','dr-dana-show/':'dr-dana-show/',
 'treatments/knowledge/womans-health-therapy/':'treatments/womens-health/','treatments/mobile-ivs-therapy/':'treatments/iv-therapy/'})
POSTS=OrderedDict()
for f,v in C.items():
  if v['kind']=='single' and f.replace('index.html','') not in TREAT:
    slug=f.split('/')[0]; isrev='reviews' in v['cats']
    clean=re.sub(r'[^\w-]','',slug.replace('’','')) or slug
    if slug.startswith('сorey'): clean='corey-calliet-final-cut'
    new=('reviews/' if isrev else 'blog/')+clean+'/'
    URL[slug+'/']=new; POSTS[f]=dict(v,new=new,old=slug+'/',review=isrev)
for f,v in C.items():
  if v['kind'] in('archive',) or re.match(r'\d{4}/',f):
    d=f.replace('index.html','')
    URL[d]='reviews/' if 'reviews' in f else ('dr-dana-show/' if 'dr-dana-show' in f else 'blog/')
for f in C:
  if re.match(r'\d{4}/',f): URL[f.replace('index.html','')]='reviews/' if any('category/reviews' in str(b) or 'Reviews' in str(b) for b in C[f]['blocks'][:3]) else 'blog/'
def mapurl(u):
  if not u or not u.startswith('/'): return u
  path,_,frag=u[1:].partition('#')
  p=re.sub(r'index\.html$','',path)
  if p and not p.endswith('/') and '.' not in p.split('/')[-1]: p+='/'
  if p in URL: return '/'+URL[p]+('#'+frag if frag else '')
  return u
def maphtml(h): return re.sub(r'href="(/[^"]*)"',lambda m:'href="'+esc(mapurl(html.unescape(m.group(1))))+'"',h)
# ---------- post registry ----------
def post_meta(v):
  B=v['blocks']; title=next((plain(b[2]) for b in B if b[0]=='h' and b[1]==1),ttl(v['title']))
  date=''
  for b in B[:4]:
    if b[0]=='ul':
      for x in b[1]:
        m=re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})',plain(x))
        if m: date=m.group(1)
  img=next((b[1] for b in B if b[0]=='img'),None)
  return title,date,img
REG=OrderedDict()  # href(new or ext) -> card dict
for f,v in POSTS.items():
  t,d,i=post_meta(v); REG['/'+v['new']]={'title':t,'date':d,'img':i,'ex':'','cats':v['cats'],'review':v['review'],'href':'/'+v['new']}
for f,v in C.items():
  if not(v['kind']=='archive' or re.match(r'\d{4}/',f)): continue
  B=v['blocks']
  for b in B:
    if b[0]=='post':
      d=b[1]; h=mapurl(d['href']); r=REG.setdefault(h,{'title':d['title'],'date':'','img':None,'ex':'','cats':[],'review':'reviews' in f,'href':h})
      if d['img'] and not r['img']: r['img']=d['img']
      if d['ex'] and d['ex'] not in r['ex']: r['ex']=(r['ex']+' '+d['ex']).strip()
      if d['meta'] and not r['date']: r['date']=d['meta']
      mc=re.match(r'category/([\w-]+)/',f)
      if mc and mc.group(1) not in r['cats']: r['cats'].append(mc.group(1))
  if re.match(r'\d{4}/',f):
    i=0
    while i<len(B):
      if B[i][0]=='h':
        m=re.search(r'href="([^"]+)"',B[i][2]); h=mapurl(m.group(1)) if m else ''
        r=REG.setdefault(h,{'title':plain(B[i][2]),'date':'','img':None,'ex':'','cats':[],'review':True,'href':h})
        j=i+1
        while j<len(B) and B[j][0]!='h':
          if B[j][0]=='ul':
            for x in B[j][1]:
              px=plain(x)
              if px.startswith('Post published:') and not r['date']: r['date']=px.split(':',1)[1].strip()
              if 'Post category:' in px:
                r['review']='Reviews' in px
          elif B[j][0]=='p' and not plain(B[j][1]).startswith('Continue Reading'):
            if plain(B[j][1]) not in r['ex']: r['ex']=(r['ex']+' '+plain(B[j][1])).strip()
          elif B[j][0]=='img' and not r['img']: r['img']=B[j][1]
          j+=1
        i=j
      else: i+=1
# ---------- rendering primitives ----------
def img(i,cls='',eager=False,alt=None):
  if not i: return ''
  a=i.get('alt') if alt is None else alt
  wh=f' width="{i["w"]}" height="{i["h"]}"' if str(i.get('w') or '').isdigit() and str(i.get('h') or '').isdigit() else ''
  return f'<img class="{cls}" src="{esc(i["src"])}" alt="{esc(a or "")}"{wh} loading="{"eager" if eager else "lazy"}" decoding="async">'
def rb(bl):
  o=[]
  for b in bl:
    k=b[0]
    if k=='p': o.append(f'<p>{maphtml(b[1])}</p>')
    elif k=='h': lv=min(6,max(3,b[1])); o.append(f'<h{lv}>{maphtml(b[2])}</h{lv}>')
    elif k=='ul': o.append(f'<ul class="{"pills" if b[2]=="nav" else "dots"}">'+''.join(f'<li>{maphtml(x)}</li>' for x in b[1])+'</ul>')
    elif k=='img': o.append(f'<figure class="media">{img(b[1])}</figure>')
    elif k=='btn':
      if b[1]: o.append(f'<p><a class="btn btn-line" href="{esc(mapurl(b[1]))}">{b[2]}</a></p>')
      else: o.append(f'<p class="muted-note">{b[2]}</p>')
    elif k=='video': o.append(f'<div class="video"><iframe src="{esc(b[1])}" title="{esc(b[2])}" loading="lazy" allowfullscreen></iframe></div>')
    elif k=='table': o.append('<div class="table"><table>'+''.join('<tr>'+''.join(f'<td>{maphtml(c)}</td>' for c in r)+'</tr>' for r in b[1])+'</table></div>')
    elif k=='post': d=b[1]; o.append(f'<p><a href="{esc(mapurl(d["href"]))}">{esc(d["title"])}</a> {esc(d["ex"])}</p>')
  return '\n'.join(o)
def more(bl,label='Read more',vis_words=60):
  """show first paragraph (clamped), rest in an expander"""
  bl=[b for b in bl]
  if not bl: return ''
  tw=sum(words(b[1] if b[0]=='p' else ' '.join(b[1]) if b[0]=='ul' else b[-1] if b[0]=='h' else '') for b in bl)
  if tw<=vis_words: return rb(bl)
  first=''
  if bl[0][0]=='p': first=f'<p class="clamp">{maphtml(bl.pop(0)[1])}</p>'
  if not bl: return first.replace('class="clamp"','class="clamp solo"')
  return first+f'<details class="exp"><summary><span class="c">{label}</span><span class="o">Show less</span></summary><div class="exp-body">{rb(bl)}</div></details>'
def acc(items,cls='acc'):
  return f'<div class="{cls}">'+''.join(f'<details class="acc-item"><summary>{q}</summary><div class="acc-body">{a}</div></details>' for q,a in items)+'</div>'
def sections(B):
  S=[];cur=[None,[]]
  for b in B:
    if b[0]=='h' and (b[1]<=3 or plain(b[2]).endswith('?')):
      if cur[0] is not None or cur[1]: S.append(cur)
      cur=[b[2],[]]
    else: cur[1].append(b)
  if cur[0] is not None or cur[1]: S.append(cur)
  return S
# ---------- page shell ----------
NAV=[('Treatments','/treatments/'),('Doctors','/doctors/'),('Dr. Dana Show','/dr-dana-show/'),('Blog','/blog/'),('Reviews','/reviews/'),('Contact','/contact/')]
def header(cur):
  links=''.join(f'<li><a href="{u}"{" aria-current=\"page\"" if cur.startswith(u.strip("/")) and u!="/" and cur else ""}>{n}</a></li>' for n,u in NAV)
  return f'''<a class="skip" href="#main">Skip to content</a>
<div class="topbar"><div class="w"><span>{ADDR}</span><a href="{TEL}">{PHONE}</a></div></div>
<header class="hdr"><div class="w hdr-in">
<a class="brand" href="/"><img src="/wp-content/uploads/2024/11/cropped-Logo-Thechurchill.png" alt="" width="44" height="44"><span>The Churchill Center<small>Integrative &amp; Functional Medicine</small></span></a>
<nav class="nav" id="nav" aria-label="Main"><ul>{links}</ul></nav>
<div class="hdr-act"><button class="icon-btn" type="button" data-search-open aria-label="Search the site"><svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg></button>
<a class="btn btn-gold hide-sm" href="/book/">Book Appointment</a>
<button class="icon-btn menu-btn" type="button" aria-controls="nav" aria-expanded="false" aria-label="Open menu"><svg aria-hidden="true" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M3 12h18M3 18h18"/></svg></button></div>
</div></header>
<dialog class="search" aria-label="Search the site"><form method="dialog" class="search-in" role="search"><label for="q" class="sr">Search the site</label><input id="q" type="search" name="q" placeholder="Search treatments, articles, reviews…" autocomplete="off"><button class="icon-btn" value="close" aria-label="Close search">✕</button></form><p class="search-count" aria-live="polite"></p><ul class="search-res"></ul></dialog>'''
def footer():
  tl=''.join(f'<li><a href="/treatments/?c={re.sub(r"[^a-z]+","-",c.lower()).strip("-")}">{esc(c)}</a></li>' for c in CATS)
  return f'''<section class="final-cta"><div class="w"><p class="eyebrow">The Churchill Center · Arcadia</p><h2>Take back your health for life</h2><p>Consultations in person or virtual.</p><div class="row"><a class="btn btn-gold" href="/book/">Book Appointment</a><a class="btn btn-ghost-light" href="{TEL}">Call {PHONE}</a></div></div></section>
<footer class="ftr"><div class="w ftr-grid">
<div><p class="ftr-brand">The Churchill Center</p><p>Churchill Center-Arcadia<br>{ADDR}</p><p><a href="{TEL}">{PHONE}</a></p><p><a class="btn btn-gold" href="/book/">Book Appointment</a></p></div>
<div><h2 class="ftr-h">Treatments</h2><ul><li><a href="/treatments/">Treatment finder</a></li>{tl}</ul></div>
<div><h2 class="ftr-h">Explore</h2><ul><li><a href="/about/">About</a></li><li><a href="/doctors/">Our Doctors</a></li><li><a href="/dr-dana-show/">Dr. Dana Show</a></li><li><a href="/blog/">Blog</a></li><li><a href="/reviews/">Reviews</a></li><li><a href="/faq/">FAQ</a></li></ul></div>
<div><h2 class="ftr-h">Visit</h2><ul><li><a href="/contact/">Contact &amp; hours</a></li><li><a href="/book/">Book Appointment</a></li><li><a href="https://thechurchillcenter.store/">Shop<span class="sr"> (external site)</span></a></li></ul></div>
</div><div class="w ftr-legal"><a href="/privacy-policy/">Privacy</a><a href="/terms-conditions/">Terms</a><span>© The Churchill Center</span></div></footer>
<div class="mbar"><a href="{TEL}">Call</a><a class="btn btn-gold" href="/book/">Book Appointment</a></div>'''
INDEX=[]
def page(path,title,desc,main,kind='page',index_text=None):
  main=re.sub(r'<a [^>]*href="/author/[^"]*"[^>]*>(.*?)</a>',r'\1',main,flags=re.S)
  d=path.count('/')
  pre='../'*d
  h=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(desc[:300])}"><meta name="robots" content="noindex"><link rel="canonical" href="https://thechurchillcenter.com/{esc(path)}">
<link rel="icon" href="/wp-content/uploads/2024/11/cropped-Logo-Thechurchill.png"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Manrope:wght@400;500;700&display=swap">
<link rel="stylesheet" href="/assets/v2/site.css"></head><body data-root="{pre}">
{header(path)}<main id="main">{main}</main>{footer()}<script src="/assets/v2/site.js" defer></script></body></html>'''
  # relativize root-absolute urls
  h=re.sub(r'(href|src)="/(?!/)',lambda m:f'{m.group(1)}="{pre}',h)
  h=re.sub(r'(href|src)="(\.\./)*"',lambda m:f'{m.group(1)}="{pre or "./"}"',h)
  fp=os.path.join(OUT,path,'index.html'); os.makedirs(os.path.dirname(fp),exist_ok=True); open(fp,'w').write(h)
  if kind!='noindex':
    INDEX.append({'t':title.split(' | ')[0],'u':path,'k':kind,'d':plain(desc)[:160],'x':(index_text or plain(main))[:3000]})
def hero(eyebrow,title,sub,image=None,actions=True,cls=''):
  im=f'<div class="hero-art"><div class="arch">{img(image,eager=True)}</div></div>' if image else ''
  act=f'<div class="row"><a class="btn btn-gold" href="/book/">Book Appointment</a><a class="btn btn-line" href="{TEL}">Call {PHONE}</a></div>' if actions else ''
  return f'<section class="hero {cls}{" has-art" if image else ""}"><div class="w hero-in"><div class="hero-copy"><p class="eyebrow">{eyebrow}</p><h1>{title}</h1>{sub}{act}</div>{im}</div></section>'
# ---------- treatment pages ----------
RX={'benefits':re.compile(r'benefit|why choose|advantage|results',re.I),'who':re.compile(r'\bwho\b|ideal|candidate|right for|symptom|signs|suffer',re.I),'expect':re.compile(r'expect|process|how (it|does|we|to)|session|procedure|step|consult|treatment plan',re.I)}
NAVHEADS={'Diagnostic','Detoxification','IVTherapy','Women’sHealth','Men’sHealth'}
REL={'Diagnostic':'/treatments/diagnostic-testing/','Detoxification':'/treatments/detoxification/','IV Therapy':'/treatments/iv-therapy/','Women’s Health':'/treatments/womens-health/','Men’s Health':'/treatments/mens-health/'}
TINFO={}
def tr_clean(B):
  B=[b for b in B]
  # heading-only related run -> pills
  out=[];i=0
  while i<len(B):
    run=[]
    while i+len(run)<len(B) and B[i+len(run)][0]=='h' and plain(B[i+len(run)][2]).replace(' ','') in NAVHEADS: run.append(B[i+len(run)])
    if len(run)>=3:
      out.append(['ul',[f'<a href="{REL[plain(h[2]).replace("’s ","’s ").strip()] if plain(h[2]).strip() in REL else "/treatments/"}">{esc(plain(h[2]))}</a>' for h in run],'nav']); i+=len(run); continue
    out.append(B[i]); i+=1
  return out
for old,v in TREAT.items():
  slug,cat,label=v.split('|'); src=C[old+'index.html']; B=tr_clean(src['blocks'])
  h1=next((k for k,b in enumerate(B) if b[0]=='h' and b[1]==1),None)
  title=plain(B[h1][2]) if h1 is not None else label
  if h1 is not None: B.pop(h1)
  B=[b for b in B if not(b[0]=='p' and '»' in plain(b[1]) and words(b[1])<8)]
  # meta from single-post chrome (VIBES is a post)
  himg=None
  for k,b in enumerate(B):
    if b[0]=='img': himg=b[1]; B.pop(k); break
  if not himg:
    og=src.get('og') or ''
    m=re.search(r'(/wp-content/uploads/[^?#]+)',og)
    if m and os.path.exists('/workspace/churchill-findability'+m.group(1)): himg={'src':m.group(1),'alt':'','w':None,'h':None}
  TINFO[slug]={'title':label,'full':title,'cat':cat,'desc':plain(src['desc']),'img':himg,'old':old}
for slug,ti in TINFO.items():
  src=C[ti['old']+'index.html']; B=tr_clean(src['blocks'])
  h1=next((k for k,b in enumerate(B) if b[0]=='h' and b[1]==1),None)
  if h1 is not None: B.pop(h1)
  crumbs=[b for b in B if b[0]=='p' and '»' in plain(b[1]) and words(b[1])<8]
  B=[b for b in B if b not in crumbs]
  if ti['img']:
    for k,b in enumerate(B):
      if b[0]=='img' and b[1]['src']==ti['img']['src']: B.pop(k); break
  navs=[b for b in B if b[0]=='ul' and b[2]=='nav']; B=[b for b in B if not(b[0]=='ul' and b[2]=='nav')]
  S=sections(B)
  overview=[];slots={'benefits':[],'who':[],'expect':[],'faq':[],'more':[]}
  for h,bl in S:
    if h is None and not overview: overview=bl; continue
    if h is None: slots['more'].append(('Details',bl)); continue
    ph=plain(h)
    if ph.endswith('?'): slots['faq'].append((h,bl)); continue
    for k in('benefits','who','expect'):
      if RX[k].search(ph): slots[k].append((h,bl)); break
    else: slots['more'].append((h,bl))
  if not overview and slots['more']: overview=[['h',3,slots['more'][0][0]]]+slots['more'].pop(0)[1]
  parts=[];tabs=[]
  # overview
  facts=f'''<aside class="facts"><p class="eyebrow">{esc(ti["cat"])}</p><p class="facts-t">{esc(ti["title"])}</p><a class="btn btn-gold wide" href="/book/">Book Appointment</a><a class="btn btn-line wide" href="{TEL}">Call {PHONE}</a><p class="facts-a">{ADDR}</p>{('<p class="facts-r">Related</p>'+rb(navs)) if navs else ''}</aside>'''
  tabs.append(('overview','Overview'))
  parts.append(f'<section class="sec" id="overview"><div class="w two"><div class="prose"><h2>Overview</h2>{more(overview,vis_words=80)}</div>{facts}</div></section>')
  def slot(key,label,render):
    if not slots[key]: return
    tabs.append((key,label)); parts.append(f'<section class="sec{" tint" if len(tabs)%2==0 else ""}" id="{key}"><div class="w"><h2>{label}</h2>{render(slots[key])}</div></section>')
  def cards_or_prose(items):
    o=''
    for h,bl in items:
      lists=[b for b in bl if b[0]=='ul']; rest=[b for b in bl if b[0]!='ul']
      o+=f'<div class="slot-block"><h3>{maphtml(h)}</h3>{more(rest)}'
      for l in lists: o+='<ul class="benefits">'+''.join(f'<li>{maphtml(x)}</li>' for x in l[1])+'</ul>'
      o+='</div>'
    return o
  slot('benefits','Benefits',cards_or_prose)
  slot('who','Who it’s for',cards_or_prose)
  slot('expect','What to expect',cards_or_prose)
  if slots['more']:
    tabs.append(('details','In depth'))
    parts.append(f'<section class="sec" id="details"><div class="w narrow"><h2>In depth</h2>{acc([(maphtml(h),rb(bl)) for h,bl in slots["more"]])}</div></section>')
  slot('faq','FAQs',lambda it:acc([(maphtml(h),rb(bl)) for h,bl in it]))
  rel=[s for s,t in TINFO.items() if t['cat']==ti['cat'] and s!=slug]
  if rel:
    parts.append('<section class="sec tint"><div class="w"><h2>Related treatments</h2><div class="grid g3">'+''.join(tcard(s) if False else '' for s in rel)+'%%REL%%</div></div></section>')
  tabnav='<nav class="tabs" aria-label="On this page"><div class="w"><ul>'+''.join(f'<li><a href="#{k}">{l}</a></li>' for k,l in tabs)+'</ul></div></nav>'
  sub=f'<p class="lead">{esc(ti["desc"])}</p>' if ti['desc'] else ''
  crumb=f'<p class="crumb">{maphtml(crumbs[0][1])}</p>' if crumbs else ''
  ti['main']=hero(f'<a href="/treatments/">Treatments</a> · {esc(ti["cat"])}',esc(ti['full']),crumb+sub,ti['img'])+tabnav+''.join(parts)
  ti['rel']=rel
def tcard(slug,h=3):
  t=TINFO[slug]
  return f'<article class="tcard" data-cat="{esc(t["cat"])}" data-k="{esc((t["title"]+" "+t["full"]+" "+t["desc"]).lower())}"><a href="/treatments/{slug}/"><div class="arch sm">{img(t["img"],alt="") if t["img"] else f'<span class="arch-ph" aria-hidden="true"><b>{esc(t["title"][:1])}</b></span>'}</div><p class="eyebrow">{esc(t["cat"])}</p><h{h}>{esc(t["title"])}</h{h}><p class="clamp3">{esc(t["desc"])}</p><span class="go">View treatment →</span></a></article>'
def ecard(t,u,cat):
  return f'<article class="tcard" data-cat="{esc(cat)}" data-k="{esc(t.lower())}"><a href="{u}"><div class="arch sm"><span class="arch-ph" aria-hidden="true"><b>{esc(t[:1])}</b></span></div><p class="eyebrow">{esc(cat)}</p><h3>{esc(t)}</h3><p>Page on the live site (not included in this test copy).<span class="sr"> External link.</span></p><span class="go">Open on live site →</span></a></article>'
for slug,ti in TINFO.items():
  m=ti['main'].replace('%%REL%%',''.join(tcard(s) for s in ti['rel']))
  page(f'treatments/{slug}/',f'{ti["title"]} | The Churchill Center',ti['desc'],m,'Treatment')
# ---------- finder ----------
tb=C['treatments/index.html']['blocks']
intro=next(b for b in tb if b[0]=='p' and words(b[1])>20)
chips='<button type="button" class="chip" aria-pressed="true" data-cat="">All</button>'+''.join(f'<button type="button" class="chip" aria-pressed="false" data-cat="{esc(c)}" data-slug="{re.sub(r"[^a-z]+","-",c.lower()).strip("-")}">{esc(c)}</button>' for c in CATS)
grid=''.join(tcard(s) for s in TINFO)+''.join(ecard(t,u,c) for t,u,c in EXTERNAL)
fm=hero('Treatment finder','Find the right treatment','<p class="lead">Search by what you need help with, or browse by category.</p>',None,actions=False,cls='hero-finder')
fm+=f'''<section class="sec finder"><div class="w"><h2 class="sr">Find a treatment</h2><div class="finder-bar" role="search"><label for="fq" class="sr">What would you like help with?</label><input id="fq" type="search" placeholder="What would you like help with? e.g. thyroid, detox, skin" autocomplete="off"><div class="chips" role="group" aria-label="Filter by category">{chips}</div><p class="finder-count" aria-live="polite"></p></div><div class="grid g3 finder-grid">{grid}</div><p class="finder-empty" hidden>No treatments match. Try another word, or <a href="/contact/">contact us</a>.</p></div></section>
<section class="sec tint"><div class="w narrow prose"><h2>About our treatments</h2>{more([intro])}{rb([b for b in tb if b[0]=='ul'])}</div></section>'''
page('treatments/','Treatment Finder | The Churchill Center','Find treatments at The Churchill Center by concern or category.',fm,'Page')
# ---------- posts ----------
CATNAME={'articles':'Articles','blog':'Doctor’s Blog','videos':'Video Library','meda':'Media','news':'Fresh News','dr-dana-show':'Dr. Dana Show','reviews':'Reviews'}
def split_post(B):
  B=list(B); title=None
  if B and B[0][0]=='h' and B[0][1]==1: title=B.pop(0)[2]
  meta=None
  if B and B[0][0]=='ul': meta=B.pop(0)
  k=next((i for i,b in enumerate(B) if b[0]=='p' and re.match(r'(Prev|Next)\b',plain(b[1]))),len(B))
  body=B[:k]; tail=B[k:]
  pn=[b for b in tail if b[0]=='p' and re.match(r'(Prev|Next)\b',plain(b[1]))]
  rel=[b for b in tail if b not in pn and not(b[0]=='btn' and not b[1])]
  return title,meta,body,pn,rel
def card(r,h=3,show_ex=True):
  im=r.get('img'); ext=r['href'].startswith('http')
  cats=' · '.join(CATNAME.get(c,c) for c in r.get('cats',[]))
  return f'''<article class="pcard" data-cats="{esc(" ".join(r.get("cats",[])))}"><a href="{esc(r["href"])}">{f'<div class="pimg">{img(im,alt="")}</div>' if im else ''}<div class="pbody"><p class="eyebrow">{esc(cats or ("Reviews" if r.get("review") else ""))}{(" · " if cats or r.get("review") else "")+esc(r["date"]) if r.get("date") else ""}</p><h{h}>{esc(r["title"])}</h{h}>{f'<p class="clamp3">{esc(r["ex"])}</p>' if show_ex and r.get("ex") else ''}<span class="go">{"Read on live site" if ext else ("Read review" if r.get("review") else "Read more")} →</span>{'<span class="sr"> (external site)</span>' if ext else ''}</div></a></article>'''
for f,v in POSTS.items():
  title,meta,body,pn,rel=split_post(v['blocks']); r=REG['/'+v['new']]
  ml=' · '.join(plain(x) for x in meta[1]) if meta else ''
  mh=''.join(f'<li>{maphtml(x)}</li>' for x in meta[1]) if meta else ''
  himg=None
  if body and body[0][0]=='img': himg=body.pop(0)[1]
  bodyhtml=rb(body) if body else '<p class="muted-note">This post’s video was not included in this test copy.</p>'
  if v['review']:
    content=f'<blockquote class="review-full">{bodyhtml}</blockquote>'
  else:
    long=sum(words(b[1]) for b in body if b[0]=='p')>350
    if long:
      S=sections(body); first=S[0] if S and S[0][0] is None else None
      lead=rb(first[1]) if first else ''
      rest=[s for s in S if s is not first]
      content=lead+(acc([(maphtml(h) if h else 'More',rb(bl)) for h,bl in rest]) if rest else '')
    else: content=bodyhtml
  pnh=''.join(f'<a class="pn" rel="{"prev" if plain(b[1]).startswith("Prev") else "next"}" href="{esc(mapurl(re.search(r"href=\"([^\"]+)",b[1]).group(1)))}">{esc(plain(b[1]))}</a>' for b in pn if 'href' in b[1])
  relh=''
  hs=[b for b in rel if b[0]=='h']
  if hs:
    items=''
    for b in hs:
      m=re.search(r'href="([^"]+)"',b[2]); u=mapurl(html.unescape(m.group(1))) if m else '#'
      items+=f'<li><a href="{esc(u)}">{esc(plain(b[2]))}</a></li>'
    others=[b for b in rel if b[0] not in('h','img')]
    relh=f'<section class="sec tint"><div class="w narrow"><h2>{"More reviews" if v["review"] else "Keep reading"}</h2><ul class="linklist">{items}</ul>{rb(others)}</div></section>'
  elif rel:
    relh=f'<section class="sec tint"><div class="w narrow"><h2>{"More reviews" if v["review"] else "Keep reading"}</h2>{rb([b for b in rel if b[0]!="img"])}</div></section>'
  kind='Review' if v['review'] else 'Article'
  hd=f'<section class="post-hd"><div class="w narrow"><p class="eyebrow"><a href="/{"reviews" if v["review"] else "blog"}/">{"Reviews" if v["review"] else "Blog"}</a></p><h1>{maphtml(title) if title else esc(r["title"])}</h1><ul class="post-meta">{mh}</ul></div></section>'
  art=f'<article class="sec"><div class="w narrow prose">{f"<figure class=media>{img(himg,eager=True)}</figure>" if himg else ""}{content}<nav class="pns" aria-label="Previous and next">{pnh}</nav></div></article>'
  page(v['new'],f'{r["title"]} | The Churchill Center',v['desc'] or r['title'],hd+art+relh,kind)
# ---------- lists ----------
nonrev=[r for r in REG.values() if not r['review']]; revs=[r for r in REG.values() if r['review']]
fil='<button type="button" class="chip" aria-pressed="true" data-f="">All</button>'+''.join(f'<button type="button" class="chip" aria-pressed="false" data-f="{c}">{CATNAME[c]}</button>' for c in ['articles','blog','videos','dr-dana-show','meda','news'])
bm=hero('Blog &amp; media','Articles, videos and news from Dr. Dana Churchill','',None,actions=False,cls='hero-slim')
bm+=f'<section class="sec"><div class="w"><h2 class="sr">All posts</h2><div class="chips post-filter" role="group" aria-label="Filter posts">{fil}</div><p class="finder-count" aria-live="polite"></p><div class="grid g3 posts">{"".join(card(r) for r in nonrev)}</div></div></section>'
page('blog/','Blog | The Churchill Center','Articles, videos and news from The Churchill Center.',bm,'Page')
rm=hero('Reviews','What patients say','',None,actions=True,cls='hero-slim')
rm+=f'<section class="sec"><div class="w"><h2 class="sr">All reviews</h2><div class="grid g3 posts">{"".join(card(r) for r in revs)}</div></div></section>'
page('reviews/','Reviews | The Churchill Center','Patient reviews of The Churchill Center.',rm,'Page')
# ---------- Dr Dana Show ----------
SB=C['dr-dana-show/index.html']['blocks']
eps=[r for r in REG.values() if not r['review'] and ('dr-dana-show' in r['cats'] or 'videos' in r['cats'])]
yt=next(b for b in SB if b[0]=='p' and 'youtube' in b[1])
showimg=next(b[1] for b in SB if b[0]=='img')
extra=[b for b in SB[30:] ]
sm=hero(esc(plain(SB[0][2])),SB[3][2],f'<p class="lead">{SB[1][2]}</p><p class="muted">{plain(SB[2][2])}</p><p>{maphtml(yt[1]).replace("<a ","<a class=\"btn btn-line\" ",1)}</p>',showimg,actions=False)
sm+=f'<section class="sec"><div class="w"><h2>Episodes &amp; expert talks</h2><div class="grid g3 posts">{"".join(card(r) for r in eps)}</div>{rb(extra)}</div></section>'
page('dr-dana-show/','Dr. Dana Show | The Churchill Center','Dr. Dana Show: real stories of resilience, healing and renewal.',sm,'Page')
# ---------- doctors ----------
D=C['ourdoctors/index.html']['blocks']; T=lambda i:D[i][2] if D[i][0]=='h' else D[i][1]
def prof(anchor,name,photo,cred,intro,rest):
  return f'''<article class="doc" id="{anchor}"><div class="arch doc-photo">{img(photo,alt=plain(name))}</div><div class="doc-body"><h2>{maphtml(name)}</h2>{f'<p class="cred">{maphtml(cred)}</p>' if cred else ''}<p>{maphtml(intro)}</p><details class="exp"><summary><span class="c">Read full bio</span><span class="o">Show less</span></summary><div class="exp-body">{rb(rest)}</div></details></div></article>'''
dm=hero(esc(plain(T(0))),'Our Doctors',f'<p class="crumb">{maphtml(T(1))}</p><p class="lead">{maphtml(T(2))}</p>',None)
dm+=f'<section class="sec"><div class="w docs">{prof("dana",T(3),D[4][1],"",T(5),D[6:15])}{prof("thong",T(15),D[16][1],T(17),T(18),D[19:26])}</div></section>'
svc=''.join(f'<article class="svc"><div class="svc-ic">{img(D[i][1],alt="")}</div><h3>{T(h)}</h3><p>{T(s)}</p></article>' for h,s,i in ((29,30,31),(32,33,34),(35,36,37)))
det=acc([(f'<span class="letter">{plain(T(a+1))}</span> {T(a)}',rb(D[a+2:b])) for a,b in ((38,47),(47,56),(56,65))])
dm+=f'''<section class="sec tint" id="acuroma"><div class="w"><div class="acu-hd">{img(D[26][1],"acu-logo",alt="AcuRoma logo")}<div><h2>{T(27)}</h2><p>{maphtml(T(28))}</p></div></div><div class="grid g3">{svc}</div>{det}<div class="protocol"><h3>{T(65)}</h3>{rb(D[66:])}</div><p><a class="btn btn-line" href="/treatments/acuroma-lymphatic-therapy/">AcuRoma™ Wellness &amp; Lymphatic Therapy</a></p></div></section>'''
page('doctors/','Our Doctors | The Churchill Center',C['ourdoctors/index.html']['desc'],dm,'Page')
# ---------- about ----------
W=C['welcome/index.html']['blocks']
wimg=next(b[1] for b in W if b[0]=='img')
am=hero('About',W[0][2],'',wimg)+f'<section class="sec"><div class="w narrow prose">{rb([b for b in W[1:] if b[0]!="img"])}<p><a class="btn btn-line" href="/doctors/">Meet our doctors</a></p></div></section>'
page('about/','About | The Churchill Center',C['welcome/index.html']['desc'],am,'Page')
# ---------- contact / book ----------
K=C['contact-us/index.html']['blocks']
km=hero('Contact','Visit The Churchill Center',f'<p class="lead">{ADDR}</p>',None)
km+=f'''<section class="sec"><div class="w two"><div class="prose"><h2>{K[0][2]}</h2><p>{maphtml(K[1][1])}</p><h2>{plain(K[2][1])}</h2>{rb([K[3]])}<p class="pill-note">{maphtml(K[4][2])}</p>{rb(K[5:])}</div>
<div class="map"><iframe title="Map: {ADDR}" src="https://maps.google.com/maps?q={MAPQ}&amp;t=m&amp;z=14&amp;output=embed" loading="lazy"></iframe><p><a class="btn btn-gold" href="/book/">Book Appointment</a> <a class="btn btn-line" href="{TEL}">Call {PHONE}</a></p></div></div></section>'''
page('contact/','Contact | The Churchill Center',C['contact-us/index.html']['desc'],km,'Page')
A=C['appointments/index.html']['blocks']
bk=hero('Book','Book an appointment',f'<p class="lead">{plain(C["appointments/index.html"]["desc"])}</p>',None,actions=False)
bk+=f'<section class="sec"><div class="w narrow"><div class="notice">{rb(A)}</div><div class="book-opts"><a class="opt" href="{TEL}"><span class="eyebrow">Call</span><strong>{PHONE}</strong></a><a class="opt" href="/contact/"><span class="eyebrow">Visit</span><strong>{ADDR}</strong></a></div></div></section>'
page('book/','Book Appointment | The Churchill Center',C['appointments/index.html']['desc'],bk,'Page')
# ---------- faq / legal ----------
F=C['faq/index.html']['blocks']; S=sections(F)
head=[s for s in S if not (s[0] and plain(s[0]).endswith('?'))]; qs=[s for s in S if s[0] and plain(s[0]).endswith('?')]
fm=hero('FAQ',maphtml(head[0][0]) if head and head[0][0] else 'Frequently Asked Questions',''.join(f'<p class="lead">{plain(x[0])}</p>'+rb(x[1]) for x in head[1:]) + (rb(head[0][1]) if head else ''),None,actions=False,cls='hero-slim')
fm+=f'<section class="sec"><div class="w narrow">{acc([(maphtml(h),rb(bl)) for h,bl in qs])}</div></section>'
page('faq/','FAQ | The Churchill Center',C['faq/index.html']['desc'],fm,'Page')
for lp in ('privacy-policy','terms-conditions'):
  L=C[lp+'/index.html']['blocks']; t=next((b[2] for b in L if b[0]=='h' and b[1]==1),ttl(C[lp+'/index.html']['title']))
  L=[b for b in L if not(b[0]=='h' and b[2]==t)]
  page(lp+'/',ttl(C[lp+'/index.html']['title'])+' | The Churchill Center','',hero('Legal',t,'',None,actions=False,cls='hero-slim')+f'<section class="sec"><div class="w narrow prose">{rb(L)}</div></section>','Page')
# ---------- home ----------
H=C['index.html']['blocks']; T=lambda i:H[i][2] if H[i][0]=='h' else H[i][1]
def hlink(h):
  m=re.search(r'href="([^"]+)"',h); return (mapurl(html.unescape(m.group(1))) if m else '#', plain(re.sub(r'<span class="sr">.*?</span>','',h)))
dimg={'src':'/wp-content/uploads/2023/01/Dr-Dana-Chruchill.jpg','alt':'Dr. Dana Churchill, NMD','w':None,'h':None}
hm=hero(f'{esc(plain(T(0)))} · {esc(plain(T(1)))}',T(5),f'<p class="lead">{T(3)}</p><p class="muted">{plain(T(2))}</p>',dimg,cls='hero-home')
badge_href=re.search(r'href="([^"]+)"',H[10][1]).group(1)
hm+=f'''<section class="proof" aria-label="At a glance"><div class="w proof-in"><p><strong>Established in 2005</strong><span>Naturopathic medical clinic</span></p><p><strong>Arcadia, CA</strong><span>{ADDR}</span></p><p><strong>In person or virtual</strong><span>Consultations</span></p><p><strong>Mandarin Spoken</strong><span>我们讲普通话</span></p><a class="badge" href="{esc(badge_href)}" target="_blank" rel="noopener">{img(H[9][1],alt="Verified by HealthProfs.com")}<span class="sr"> (opens in new tab)</span></a></div></section>'''
hm+=f'<section class="sec"><div class="w narrow center prose"><p class="big">{T(4)}</p></div></section>'
tiles=''.join(f'<a class="tile" href="/treatments/?c={re.sub(r"[^a-z]+","-",c.lower()).strip("-")}"><span class="tile-n">{sum(1 for t in TINFO.values() if t["cat"]==c)+sum(1 for e in EXTERNAL if e[2]==c)}</span><span class="tile-t">{esc(c)}</span><span class="go" aria-hidden="true">→</span></a>' for c in CATS)
def feat(hi,pi,bi,link=None,im=None):
  u=mapurl(H[bi][1]) if bi is not None else link
  return f'<article class="pcard"><a href="{esc(u)}">{f"<div class=pimg>{img(im,alt='')}</div>" if im else ""}<div class="pbody"><h3>{T(hi).replace("<br><br>"," · ").replace("<br>"," ")}</h3>{f"<p>{T(pi)}</p>" if pi is not None else ""}<span class="go">{H[bi][2] if bi is not None else "View treatment"} →</span></div></a></article>'
feats=feat(19,20,21,im=TINFO['rejuvenation-women']['img'])+feat(34,35,36,im=TINFO['rejuvenation-men']['img'])+f'<article class="pcard"><a href="/treatments/iv-therapy/"><div class="pimg">{img(H[37][1],alt="")}</div><div class="pbody"><h3>{T(39)}</h3><figure class="media">{img(H[38][1],alt="")}</figure><span class="go">View treatment →</span></div></a></article>'
hm+=f'''<section class="sec tint"><div class="w"><div class="sec-hd"><p class="eyebrow">Treatment finder</p><h2>What would you like help with?</h2></div>
<form class="finder-bar home-finder" action="/treatments/" method="get" role="search"><label for="hq" class="sr">What would you like help with?</label><input id="hq" name="q" type="search" placeholder="e.g. thyroid, detox, skin, weight loss"><button class="btn btn-gold" type="submit">Find treatments</button></form>
<div class="tiles">{tiles}</div><div class="grid g3 mt">{feats}</div></div></section>'''
ben=''.join(f'<article class="bcard"><span class="bnum" aria-hidden="true">{n:02d}</span><h3>{T(i)}</h3>{more([H[i+1]],vis_words=40)}</article>' for n,i in enumerate((40,42,44,46,49,51),1))
hm+=f'<section class="sec"><div class="w"><div class="sec-hd"><p class="eyebrow">Why The Churchill Center</p><h2>{T(48)}</h2></div><div class="grid g3">{ben}</div></div></section>'
D2=C['ourdoctors/index.html']['blocks']
docs=''.join(f'<a class="mini-doc" href="/doctors/#{a}"><div class="arch xs">{img(D2[i][1],alt="")}</div><span>{plain(D2[n][2])}</span></a>' for a,n,i in (('dana',3,4),('thong',15,16)))
hm+=f'''<section class="sec forest"><div class="w two"><div class="prose"><p class="eyebrow">Our doctors</p>{more([H[6],H[7]],vis_words=50)}<p class="row"><a class="btn btn-gold" href="/doctors/">Meet our doctors</a><a class="btn btn-ghost-light" href="{esc(mapurl(H[8][1]))}">{H[8][2]}</a></p></div><div class="mini-docs">{docs}</div></div></section>'''
rv=''
for hi in (54,56,58,60):
  u,t=hlink(T(hi)); r=REG.get(u,{})
  rv+=f'<article class="qcard"><span class="qmark" aria-hidden="true">“</span><h3>{esc(t)}</h3>{f"<p class=clamp4>{esc(r.get("ex") or "")}</p>" if r.get("ex") else ""}<a class="go" href="{esc(u)}">{T(hi+1)}<span class="sr"> {esc(t)}</span></a></article>'
hm+=f'<section class="sec"><div class="w"><div class="sec-hd row-hd"><div><p class="eyebrow">Patient stories</p><h2>{T(53)}</h2></div><a class="btn btn-line" href="/reviews/">All reviews</a></div><div class="grid g4">{rv}</div></div></section>'
md=''
for ii,hi,di in ((22,23,24),(25,26,27),(28,29,30),(31,32,33)):
  u,t=hlink(T(hi)); md+=f'<article class="pcard"><a href="{esc(u)}"><div class="pimg">{img(H[ii][1],alt="")}</div><div class="pbody"><p class="eyebrow">{T(di)}</p><h3>{esc(t)}</h3></div></a></article>'
hm+=f'<section class="sec tint"><div class="w"><div class="sec-hd row-hd"><div><p class="eyebrow">Dr. Dana Show &amp; blog</p><h2>Latest from Dr. Dana</h2></div><a class="btn btn-line" href="/blog/">All posts</a></div><div class="grid g4">{md}</div></div></section>'
off=''
for hi,pi,bi in ((12,13,14),(16,17,18)):
  u,t=hlink(T(hi)); off+=f'<article class="offer"><h3><a href="{esc(u)}" target="_blank" rel="noopener">{esc(t)}<span class="sr"> (opens in new tab)</span></a></h3><p>{T(pi)}</p><a class="btn btn-gold" href="{esc(mapurl(H[bi][1]))}">{H[bi][2].title()}</a></article>'
hm+=f'<section class="sec"><div class="w grid g2">{off}</div></section>'
page('','The Churchill Center | Integrative & Functional Medicine in Arcadia',C['index.html']['desc'],hm,'Page')
# ---------- redirects ----------
def stub(old,new):
  fp=os.path.join(OUT,old)
  if old.endswith('/') or not old: fp=os.path.join(fp,'index.html')
  if os.path.exists(fp): return
  d=old.count('/') if old.endswith('/') else old.count('/')
  pre='../'*d; tgt=pre+new
  os.makedirs(os.path.dirname(fp),exist_ok=True)
  open(fp,'w').write(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Moved</title><link rel="canonical" href="https://thechurchillcenter.com/{new}"><meta http-equiv="refresh" content="0; url={tgt or "./"}"><meta name="robots" content="noindex"></head><body><p>This page has moved: <a href="{tgt or "./"}">{new or "Home"}</a></p></body></html>')
RED={}
for o,n in URL.items():
  if o!=n: RED[o]=n
# old ?p= stubs and merged stubs from findability
for f in glob.glob('/workspace/churchill-findability/index.html?p=*.html'):
  t=re.search(r'url=([^"]+)"',open(f).read()).group(1); RED[os.path.basename(f)]=URL.get(t,t)
for o,n in RED.items(): stub(o,n)
os.makedirs(OUT+'/assets/v2',exist_ok=True); json.dump(INDEX,open(OUT+'/assets/v2/search.json','w'),ensure_ascii=False); shutil.copy('/workspace/v2/assets/site.css',OUT+'/assets/v2/'); shutil.copy('/workspace/v2/assets/site.js',OUT+'/assets/v2/')
json.dump(RED,open('/workspace/v2/redirects.json','w'),ensure_ascii=False,indent=0)
json.dump({o:n for o,n in URL.items()},open('/workspace/v2/urlmap.json','w'),ensure_ascii=False,indent=0)
print('pages',len(INDEX),'redirects',len(RED))
