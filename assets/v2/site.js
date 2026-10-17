(function(){var root=document.body.getAttribute('data-root')||'';
var mb=document.querySelector('.menu-btn'),nav=document.getElementById('nav');
if(mb&&nav){mb.addEventListener('click',function(){var o=nav.classList.toggle('open');mb.setAttribute('aria-expanded',o);mb.setAttribute('aria-label',o?'Close menu':'Open menu')});document.addEventListener('keydown',function(e){if(e.key==='Escape'&&nav.classList.contains('open')){nav.classList.remove('open');mb.setAttribute('aria-expanded','false');mb.focus()}})}
document.querySelectorAll('details.exp').forEach(function(d){d.addEventListener('toggle',function(){d.parentElement.classList.toggle('unclamp',d.open)})});
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
// search dialog
var dlg=document.querySelector('dialog.search'),idx=null;
document.querySelectorAll('[data-search-open]').forEach(function(b){b.addEventListener('click',function(){dlg.showModal();dlg.querySelector('input').focus()})});
if(dlg){var inp=dlg.querySelector('input'),res=dlg.querySelector('.search-res'),cnt=dlg.querySelector('.search-count');
inp.addEventListener('input',function(){var q=inp.value.trim().toLowerCase();if(q.length<2){res.innerHTML='';cnt.textContent='';return}
(idx?Promise.resolve(idx):fetch(root+'assets/v2/search.json').then(function(r){return r.json()}).then(function(j){idx=j;return j})).then(function(I){var ws=q.split(/\s+/),out=[];I.forEach(function(p){var t=p.t.toLowerCase(),x=(p.d+' '+p.x).toLowerCase(),s=0;for(var i=0;i<ws.length;i++){if(t.indexOf(ws[i])>-1)s+=10;else if(x.indexOf(ws[i])>-1)s+=1;else{s=0;break}}if(p.k==='Treatment')s+=s?3:0;if(s)out.push([s,p])});out.sort(function(a,b){return b[0]-a[0]});
cnt.textContent=out.length+' result'+(out.length===1?'':'s');res.innerHTML=out.slice(0,15).map(function(r){return '<li><a href="'+root+r[1].u+'"><span class="k">'+esc(r[1].k)+'</span> '+esc(r[1].t)+'<small>'+esc(r[1].d)+'</small></a></li>'}).join('')})})}
// finder + post filter
function filt(gridSel,cardSel,attr,inputSel,chipSel,countSel,emptySel){var grid=document.querySelector(gridSel);if(!grid)return;var cards=[].slice.call(grid.querySelectorAll(cardSel)),inp=inputSel&&document.querySelector(inputSel),chips=[].slice.call(document.querySelectorAll(chipSel)),cnt=document.querySelector(countSel),empty=emptySel&&document.querySelector(emptySel),cat='';
function run(){var q=inp?inp.value.trim().toLowerCase():'',n=0;cards.forEach(function(c){var ok=(!cat||(' '+c.getAttribute(attr)+' ').indexOf(cat)>-1)&&(!q||q.split(/\s+/).every(function(w){return (c.getAttribute('data-k')||c.textContent.toLowerCase()).indexOf(w)>-1}));c.hidden=!ok;if(ok)n++});if(cnt)cnt.textContent=n+' shown';if(empty)empty.hidden=n>0}
chips.forEach(function(ch){ch.addEventListener('click',function(){chips.forEach(function(o){o.setAttribute('aria-pressed','false')});ch.setAttribute('aria-pressed','true');cat=ch.getAttribute('data-cat')||ch.getAttribute('data-f')||'';run()})});
if(inp)inp.addEventListener('input',run);
var u=new URLSearchParams(location.search);if(inp&&u.get('q')){inp.value=u.get('q')}if(u.get('c')){chips.forEach(function(ch){if(ch.getAttribute('data-slug')===u.get('c'))ch.click()})}run()}
filt('.finder-grid','.tcard','data-cat','#fq','.finder .chip','.finder-count','.finder-empty');
filt('.posts','.pcard','data-cats',null,'.post-filter .chip','.finder-count',null);
})();
