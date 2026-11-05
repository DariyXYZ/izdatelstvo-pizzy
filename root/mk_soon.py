import re,sys
src,dst=sys.argv[1],sys.argv[2]
s=open(src,encoding='utf-8',newline='').read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)>=1,a
    s=s.replace(a,b) if cnt==0 else s.replace(a,b,cnt)
# видео не грузим
s=re.sub(r'\s(src|data-src|poster)="img/video/[^"]*"','',s)
# вместо «меню» — надпись
rep('<a class="hm" href="#menu" data-go="menu" data-open="menu">Меню</a>','<h1 class="hm soon">скоро тут будет сайт</h1>')
rep('<nav class="nav acts" aria-label="Действия">','<div class="nav acts">')
s=re.sub(r'(<h1 class="hm soon">[^<]*</h1>\s*)</nav>',r'\1</div>',s,1)
css='''<style id="soon">
  /* ЗАГЛУШКА /pizza/: главная на белом, без видео и разделов. Генерится root/mk_soon.py из index.html: python root/mk_soon.py index.html root/pizza-soon.html */
  #home .bg{display:none!important}
  #about,#menu,#book,.tabbar,.hdr .nav a.pb:not(.h-lang){display:none!important}
  html body .hdr,html body .hdr a,html body .hdr .nav .lang [data-lang],#home,#home .nav a,#home .hm{color:var(--ink)!important}
  #home .infobar{border-top-color:rgba(0,0,0,.34)}
  #home .infobar .cap,#home .note,#home .privl{color:var(--mute)}
  #home .u{text-decoration-color:currentColor}
  /* надпись — на пересечении диагоналей области от верха экрана до линии инфостроки: шапка вынута из потока */
  html body .hdr{position:absolute;top:0;left:var(--gut);right:var(--gut)}
  main #home{min-height:100dvh!important;box-sizing:border-box}
  html body #home .acts{position:absolute!important;left:0!important;right:0!important;top:0!important;height:var(--soon-h,70vh)!important;display:flex!important;align-items:center!important;justify-content:center!important;margin:0!important;padding:0 var(--gut)!important;transform:none!important}
  #home h1.hm.soon{margin:0;font-weight:400;text-decoration:none;text-align:center;font-size:clamp(44px,5.2vw,96px);line-height:1.05;white-space:normal}
  #home h1.hm.soon::after{display:none!important}
  @media (max-width:820px){#home h1.hm.soon{font-size:clamp(36px,11vw,56px)}
    /* телефон: шапка как на компе — лого слева в две строки Oswald, ( ru / en ) справа */
    html body .hdr,html body:has(main[data-tab="home"]) .hdr{display:flex!important;justify-content:space-between;align-items:flex-start;grid-template-areas:none}
    html body .hdr .logo{justify-self:start;text-align:left;white-space:normal;line-height:1.12}
    html body .hdr .logo .l1,html body .hdr .logo .l2{display:block;margin:0;font-family:var(--sans);font-weight:300;text-transform:uppercase;letter-spacing:.01em}
    html body .hdr .nav{display:flex!important}
    html body .hdr .nav:not(.r){display:none!important}
    html body .hdr .nav .h-lang{margin:0!important;align-self:flex-start}}
</style>
</head>'''
rep('</head>',css)
# перевод надписи для ru/en
rep('const EN_TEXT = {',"const EN_TEXT = {\n    'скоро тут будет сайт':'website coming soon',")
guard='<script>if(/^#(about|menu|book)/.test(location.hash))history.replaceState(null,"",location.pathname)</script>\n<body>'
rep('<body>',guard)
fit='<script>(function(){function f(){var i=document.querySelector("#home .infobar"),h=document.getElementById("home");if(i&&h)h.style.setProperty("--soon-h",(i.getBoundingClientRect().top-h.getBoundingClientRect().top)+"px")}addEventListener("resize",f);addEventListener("load",f);document.fonts&&document.fonts.ready.then(f);f()})()</script>\n</body>'
assert s.count('</body>')==1
s=s.replace('</body>',fit)
open(dst,'w',encoding='utf-8',newline='').write(s)
print('ok',len(s))
