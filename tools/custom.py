import re,os
def install(g):
  RB=g['render_blocks'];EX=g['expander'];IMG=g['img_tag'];HERO=g['hero'];plain=g['plain'];esc=g['esc'];norm=g['norm']
  def first_img(page,p):
    from bs4 import BeautifulSoup
    s=BeautifulSoup(open(page+'index.html',errors='ignore').read(),'lxml')
    r=s.find(attrs={'data-elementor-type':re.compile('^(wp-page|single)$')}) or s
    for x in r.find_all('img'):
      c=g['Ctx'](); c.base=os.path.dirname(page+'index.html'); i=g['img_of'](x,c)
      if i:
        i=dict(i); i['src']=p+os.path.normpath(os.path.join(page,i['src'])); return i
  def href(h): # extract href+text from heading-with-link
    m=re.search(r'href="([^"]+)"',h); return (m.group(1) if m else '', norm(re.sub(r'<span class="sr">.*?</span>','',re.sub(r'<a[^>]*>|</a>','',h))))
  def card(title,body='',im=None,link=None,cls='card'):
    media=f'<div class="card-media">{IMG(im)}</div>' if im else ''
    t=f'<a href="{esc(link)}">{title}</a>' if link else title
    return f'<article class="{cls}">{media}<div class="card-body"><h3>{t}</h3>{body}</div></article>'
  def sec(inner,head='',cls='',sub=''):
    return f'<section class="band {cls}"><div class="wrap">{f"<div class=sec-head><h2>{head}</h2>{sub}</div>" if head else ""}{inner}</div></section>'
  def home(B,p):
    T=lambda i:B[i][2] if B[i][0]=='h' else B[i][1]
    heroimg={'src':'wp-content/uploads/2020/06/Medical-Center－3.gif','alt':'The Churchill Center','w':None,'h':None}
    o=HERO(T(0),T(2),heroimg,p,kicker=plain(T(1)),big=True)
    o+=sec(f'<div class="narrow0"><h2>{T(3)}</h2>{EX([B[4]])}</div>',cls='intro')
    # treatment categories (from site nav groups)
    cats=''
    for gname,items in g['GROUPS']:
      gid=re.sub(r'\W+','-',gname.lower()).strip('-')
      lis=''.join(f'<li><a href="{u if u.startswith("http") else p+u}">{esc(l)}</a></li>' for l,u in items)
      cats+=f'<article class="card cat"><div class="card-body"><h3><a href="services/#{gid}">{esc(gname)}</a></h3><ul class="linklist">{lis}</ul></div></article>'
    feat=card(T(19).replace('<br><br>',' · ').replace('<br>',' '),f'<p>{T(20)}</p><p><a class="more-link" href="{esc(B[21][1])}">{B[21][2]} →</a></p>',first_img('rejuvenation-treatment-for-women-beauty-therapy/',''))
    feat+=card(T(34).replace('<br><br>',' · ').replace('<br>',' '),f'<p>{T(35)}</p><p><a class="more-link" href="{esc(B[36][1])}">{B[36][2]} →</a></p>',first_img('rejuvenation-for-men-beauty-therapy/',''))
    feat+=card(T(39),f'<figure class="fig">{IMG(B[38][1])}</figure><p><a class="more-link" href="treatments/iv-therapy-and-injections/">Learn more →</a></p>',B[37][1],link='treatments/iv-therapy-and-injections/')
    o+=sec(f'<div class="cards cards-4">{cats}</div><div class="cards cards-3 mt">{feat}</div>',head='Treatments',sub='<p><a class="more-link" href="services/">All treatments &amp; services →</a></p>')
    # why: 4 benefit + 2 Arcadia
    why=''.join(card(T(i),EX([B[i+1]])) for i in (40,42,44,46))
    why+=''.join(card(T(i),EX([B[i+1]])) for i in (49,51))
    o+=sec(f'<div class="cards cards-3">{why}</div>',head=T(48))
    # doctors preview
    dimg=first_img('ourdoctors/','')
    badge=f'<a class="badge" href="{esc(re.search(r"href=\"([^\"]+)",B[10][1]).group(1))}" target="_blank" rel="noopener">{IMG(B[9][1])}<span class="sr">HealthProfs verified (opens in new tab)</span></a>'
    o+=f'<section class="band doc-prev"><div class="wrap split"><div class="split-media">{IMG(dimg)}</div><div class="split-text"><h2>{T(5)}</h2>{EX([B[6],B[7]])}<div class="cta-row"><a class="btn btn-ghost" href="{esc(B[8][1])}">{B[8][2]}</a><a class="btn btn-ghost" href="ourdoctors/">Our Doctors</a>{badge}</div></div></div></section>'
    # offers
    off=''
    for hi,pi,bi in ((12,13,14),(16,17,18)):
      lk,tt=href(T(hi)); off+=f'<article class="card offer"><div class="card-body"><h3><a href="{esc(lk)}" target="_blank" rel="noopener">{esc(tt)}<span class="sr"> (opens in new tab)</span></a></h3><p>{T(pi)}</p><p><a class="btn" href="{esc(B[bi][1])}">{B[bi][2]}</a></p></div></article>'
    o+=sec(f'<div class="cards cards-2">{off}</div>',cls='tint')
    # media
    med=''
    for ii,hi,di in ((22,23,24),(25,26,27),(28,29,30),(31,32,33)):
      lk,tt=href(T(hi)); med+=f'<article class="card post"><a class="card-link" href="{esc(lk)}"><div class="card-media">{IMG(B[ii][1])}</div><div class="card-body"><p class="meta">{T(di)}</p><h3>{esc(tt)}</h3></div></a></article>'
    o+=sec(f'<div class="cards cards-4">{med}</div>',head='Dr. Dana Show &amp; Blog',sub='<p><a class="more-link" href="category/blog/">Blog →</a></p>')
    rv=''
    for hi in (54,56,58,60):
      lk,tt=href(T(hi)); rv+=f'<article class="card review"><div class="card-body"><span class="q" aria-hidden="true">“</span><h3>{esc(tt)}</h3><p><a class="more-link" href="{esc(lk)}">{T(hi+1)}</a></p></div></article>'
    o+=sec(f'<div class="cards cards-4">{rv}</div>',head=T(53),sub='<p><a class="more-link" href="category/reviews/">Reviews →</a></p>')
    used=set(range(0,62))
    return o
  def doctors(B,p):
    T=lambda i:B[i][2] if B[i][0]=='h' else B[i][1]
    o=HERO('Our Doctors','',None,p,kicker=plain(T(0)))
    o=o.replace('<div class="cta-row">',f'<p class="crumb">{T(1)}</p><p class="lead">{T(2)}</p><div class="cta-row">',1)
    def prof(name,img,sub,intro,rest,anchor):
      return f'''<article class="profile" id="{anchor}"><div class="profile-photo">{IMG(img)}</div><div class="profile-body"><h2>{name}</h2>{f'<p class="cred">{sub}</p>' if sub else ''}<p>{intro}</p><details class="more"><summary><span class="when-closed">Read full bio</span><span class="when-open">Show less</span></summary><div class="more-body">{RB(rest)}</div></details></div></article>'''
    i1=dict(B[4][1]); i1['alt']=i1['alt'] or plain(T(3))
    i2=dict(B[16][1]); i2['alt']=i2['alt'] or plain(T(15))
    o+=sec(prof(T(3),i1,'',T(5),B[6:15],'dana')+prof(T(15),i2,T(17),T(18),B[19:26],'thong'),cls='profiles')
    # AcuRoma services
    logo=B[26][1]
    svc=''
    for hi,si,ii in ((29,30,31),(32,33,34),(35,36,37)):
      svc+=f'<article class="card svc"><div class="card-media">{IMG(B[ii][1])}</div><div class="card-body"><h3>{T(hi)}</h3><p>{T(si)}</p></div></article>'
    det=''
    for a,b in ((38,47),(47,56),(56,65)):
      letter=plain(T(a+1)); det+=f'<details class="qa"><summary><span><span class="letter">{letter}</span> {T(a)}</span></summary><div class="qa-body">{RB(B[a+2:b])}</div></details>'
    head=f'<div class="acu-head">{IMG(logo,"acu-logo")}<div><h2>{T(27)}</h2><p>{T(28)}</p></div></div>'
    prot=f'<div class="protocol"><h3>{T(65)}</h3>{EX(B[66:])}</div>'
    o+=sec(head+f'<div class="cards cards-3">{svc}</div><div class="faq mt">{det}</div>'+prot,cls='tint')
    return o
  def wh_pre(B):
    # replace title-only related-treatment headings with a related-links row
    idx=[i for i,b in enumerate(B) if b[0]=='h' and plain(b[2]).replace(' ','') in ('Diagnostic','Detoxification','IVTherapy','Women’sHealth','Men’sHealth')]
    run=[i for i in idx if i+1 in idx or i-1 in idx]
    idx=run
    if len(idx)==5 and idx==list(range(idx[0],idx[0]+5)):
      L=[('Diagnostic','../diagnostic-testing/'),('Detoxification','../detoxification/'),('IV Therapy','../iv-therapy-and-injections/'),('Women’s Health','./'),('Men’s Health','../mens-health/')]
      B[idx[0]:idx[0]+5]=[('ul',[f'<a href="{u}">{t}</a>' for t,u in L],'nav')]
    for k,b in enumerate(B):
      if b[0]=='ul' and len(b[1])==1 and 'Woman’s Health &amp; Therapy' in b[1][0]:
        B[k]=('ul',['<a href="#merged-womans-health-therapy">Woman’s Health &amp; Therapy</a>'],'nav')
    return B
  return {'index.html':home,'ourdoctors/index.html':doctors},{'treatments/women-health/index.html':wh_pre}
