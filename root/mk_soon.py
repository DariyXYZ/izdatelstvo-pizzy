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
  #home .acts{flex:1 1 auto;display:flex;align-items:center;justify-content:center;margin:0}
  #home h1.hm.soon{margin:0;font-weight:400;text-decoration:none;text-align:center;font-size:clamp(44px,5.2vw,96px);line-height:1.05;white-space:normal}
  #home h1.hm.soon::after{display:none!important}
  @media (max-width:820px){#home h1.hm.soon{font-size:clamp(36px,11vw,56px)}
    html body .hdr .nav .h-lang{grid-column:1/-1;justify-self:center}}
</style>
</head>'''
rep('</head>',css)
guard='<script>if(/^#(about|menu|book)/.test(location.hash))history.replaceState(null,"",location.pathname)</script>\n<body>'
rep('<body>',guard)
open(dst,'w',encoding='utf-8',newline='').write(s)
print('ok',len(s))
