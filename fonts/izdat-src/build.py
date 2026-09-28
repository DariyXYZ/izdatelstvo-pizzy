"""Izdat — на основе Forum (c) 2011 Denis Masharov, SIL OFL 1.1 (RFN «Forum» не используется).
Сжатие по горизонтали: ширина заглавных ≈ CoFo Cinema1909 × 1.1 (по пропорции ширина/высота заглавной).
Упрощение засечек: см. simplify_serifs()."""
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen

SX = float(sys.argv[1]) if len(sys.argv) > 1 else 0.839
SERIF = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0   # укорачивание засечек (1 = как есть)
OUT = sys.argv[3] if len(sys.argv) > 3 else 'Izdat-Regular.ttf'

f = TTFont('Forum-Regular.ttf')
glyf = f['glyf']; hmtx = f['hmtx']; gs = f.getGlyphSet()
order = f.getGlyphOrder()

CAP = f['OS/2'].sCapHeight
# буквы с прямыми вертикальными штрихами — у них засечки упрощаем; диагональные и круглые не трогаем
SERIF_CHARS = 'БВГЕЁНПРТЦШЩЪЬBDEFHIJLPRTU'
cmap = f.getBestCmap()
SERIF_GLYPHS = {cmap[ord(c)] for c in SERIF_CHARS if ord(c) in cmap}

def flatten(coords, ends, flags):
    """Контуры TrueType -> ломаные (квадратичные сегменты по 8 шагов)."""
    polys = []; st = 0
    for e in ends:
        pts = [(coords[i], flags[i] & 1) for i in range(st, e + 1)]; st = e + 1
        n = len(pts)
        # стартуем с on-curve точки
        k = next((i for i, (_, on) in enumerate(pts) if on), None)
        if k is None:
            continue
        pts = pts[k:] + pts[:k]
        out = [pts[0][0]]; i = 1
        while i <= n:
            p, on = pts[i % n]
            if on:
                out.append(p); i += 1
            else:
                q, qon = pts[(i + 1) % n]
                end = q if qon else ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
                a0 = out[-1]
                for t in (1/8, 2/8, 3/8, 4/8, 5/8, 6/8, 7/8, 1):
                    out.append(((1-t)**2*a0[0] + 2*(1-t)*t*p[0] + t*t*end[0], (1-t)**2*a0[1] + 2*(1-t)*t*p[1] + t*t*end[1]))
                i += 2 if qon else 1
        polys.append(out)
    return polys

def scan(polys, y):
    xs = []
    for poly in polys:
        for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
            if (y0 <= y < y1) or (y1 <= y < y0):
                xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
    xs.sort()
    return list(zip(xs[0::2], xs[1::2]))

ZONE, REF, REACH = 75, 140, 120
def simplify(name, coords, ends, flags):
    """Засечки: точки у основания и у верха заглавной, выступающие за вертикальный штрих,
    подтягиваются к краю штриха (вынос × SERIF). Край штриха берём по сечению контура выше засечки."""
    if SERIF == 1.0 or name not in SERIF_GLYPHS:
        return list(coords)
    polys = flatten(coords, ends, flags)
    bot, top = scan(polys, REF), scan(polys, CAP - REF)
    out = []
    for x, y in coords:
        nx = x
        ivs = bot if y < ZONE else top if y > CAP - ZONE else None
        if ivs:
            for x0, x1 in ivs:
                if x0 - REACH < x < x0:   nx = x0 - (x0 - x) * SERIF; break
                if x1 < x < x1 + REACH:   nx = x1 + (x - x1) * SERIF; break
        out.append((nx, y))
    return out

for name in order:
    g = glyf[name]
    adv, lsb = hmtx[name]
    if g.isComposite():
        for c in g.components:
            c.x = round(c.x * SX)
        hmtx[name] = (round(adv * SX), round(lsb * SX))
        continue
    if g.numberOfContours == 0:
        hmtx[name] = (round(adv * SX), lsb)
        continue
    coords, ends, flags = g.getCoordinates(glyf)
    new = [(round(x * SX), y) for x, y in simplify(name, coords, ends, flags)]
    g.coordinates = type(coords)(new)
    g.recalcBounds(glyf)
    hmtx[name] = (round(adv * SX), g.xMin)

# хинтинг после масштабирования неверен — убираем
for t in ('fpgm','prep','cvt ','hdmx','LTSH','VDMX'):
    if t in f: del f[t]
from fontTools.ttLib.tables import ttProgram
for n in order:
    g=glyf[n]
    if hasattr(g,'program'): g.program=ttProgram.Program(); g.program.fromBytecode(b'')

# кернинг и позиционирование (GPOS) — масштабируем горизонтальные значения
if 'GPOS' in f:
    from fontTools.otlLib import builder
    def scale_vr(vr):
        if vr is None: return
        for a in ('XPlacement', 'XAdvance'):
            if hasattr(vr, a) and getattr(vr, a):
                setattr(vr, a, round(getattr(vr, a) * SX))
    for lookup in f['GPOS'].table.LookupList.Lookup:
        for st in lookup.SubTable:
            t = st.ExtSubTable if lookup.LookupType == 9 else st
            if getattr(t, 'Format', None) is None: continue
            if hasattr(t, 'PairSet'):
                for ps in t.PairSet:
                    for pvr in ps.PairValueRecord:
                        scale_vr(pvr.Value1); scale_vr(pvr.Value2)
            if hasattr(t, 'Class1Record'):
                for c1 in t.Class1Record:
                    for c2 in c1.Class2Record:
                        scale_vr(c2.Value1); scale_vr(c2.Value2)
            if hasattr(t, 'Value') and not isinstance(t.Value, list):
                scale_vr(t.Value)

f['hhea'].advanceWidthMax = max(a for a, _ in hmtx.metrics.values())
f['OS/2'].xAvgCharWidth = round(f['OS/2'].xAvgCharWidth * SX)
f['OS/2'].usWidthClass = 4   # semi-condensed

# имя: Izdat. Копирайт Forum сохраняем (требование OFL), лицензия — OFL
name = f['name']
for rec in list(name.names):
    if rec.nameID in (1, 3, 4, 6, 16, 17, 21, 22):
        name.removeNames(nameID=rec.nameID)
for pid, eid, lid in ((3, 1, 0x409), (1, 0, 0)):
    name.setName('Izdat', 1, pid, eid, lid)
    name.setName('Regular', 2, pid, eid, lid)
    name.setName('Izdat Regular; 1.000; izdatelstvo-pizzy', 3, pid, eid, lid)
    name.setName('Izdat Regular', 4, pid, eid, lid)
    name.setName('Izdat-Regular', 6, pid, eid, lid)
name.setName('Copyright (c) 2011, Denis Masharov <denis.masharov@gmail.com>, with Reserved Font Name "Forum". '
             'Izdat — modified version (horizontally condensed, simplified serifs), 2026, for «Издательство пиццы».', 0, 3, 1, 0x409)
name.setName('Version 1.000', 5, 3, 1, 0x409)
name.setName('This Font Software is licensed under the SIL Open Font License, Version 1.1.', 13, 3, 1, 0x409)
name.setName('https://openfontlicense.org', 14, 3, 1, 0x409)
f['head'].fontRevision = 1.0
f.save(OUT)
print('saved', OUT, 'SX', SX)
