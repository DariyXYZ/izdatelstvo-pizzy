"""Рисунки сайта: тонкий контур + дрожание линии прямо в геометрии SVG (Дарий, 2026-10-21).

Исходники — рядом в temp/doodles-src/ (толщина 4 / 2.2, без дрожания); результат пишется в img/doodles/.
Кубики делятся на части (де Кастельжо), точки сдвигаются гладким 2D-шумом. Амплитуда и длина волны
задаются в экранных px и пересчитываются в единицы viewBox по масштабу показа рисунка на компе.
Запуск из корня репо: python temp/doodles-src/jitter.py
"""
import math, os, random, re

SRC = 'temp/doodles-src'
OUT = 'img/doodles'
STROKE = 1          # px на экране (non-scaling-stroke)
AMP_PX = 0.6        # амплитуда дрожания, px на экране
WAVE_PX = 14        # длина волны шума, px на экране
SPLIT = 3           # на сколько частей делить каждую кривую
# масштаб показа на компе (ширина на экране / ширина viewBox), замер на 1600px
SCALE = {'pizza-banki': .25, 'banka-lezhit': .25, 'maslo': .74, 'tarelka': 1.2, 'kartina': .48,
         'stul': .5, 'cvetok': .53, 'limony': .59, 'limon': .57}

def noise_fn(seed):
    rnd = random.Random(seed)
    g = {}
    def lat(i, j):
        k = (i, j)
        if k not in g: g[k] = rnd.uniform(-1, 1)
        return g[k]
    def sm(t): return t * t * (3 - 2 * t)
    def n(x, y):
        i, j = math.floor(x), math.floor(y); fx, fy = sm(x - i), sm(y - j)
        a = lat(i, j) + (lat(i + 1, j) - lat(i, j)) * fx
        b = lat(i, j + 1) + (lat(i + 1, j + 1) - lat(i, j + 1)) * fx
        return a + (b - a) * fy
    return n

def split_cubic(p0, p1, p2, p3, n):
    out, cur = [], (p0, p1, p2, p3)
    for k in range(n, 1, -1):
        t = 1 / k
        a, b, c, d = cur
        lerp = lambda u, v: (u[0] + (v[0] - u[0]) * t, u[1] + (v[1] - u[1]) * t)
        ab, bc, cd = lerp(a, b), lerp(b, c), lerp(c, d)
        abc, bcd = lerp(ab, bc), lerp(bc, cd)
        m = lerp(abc, bcd)
        out.append((ab, abc, m)); cur = (m, bcd, cd, d)
    out.append(cur[1:])
    return out

def process(d, amp, wave, nx, ny):
    toks = re.findall(r'[A-Za-z]|-?\d*\.?\d+(?:e-?\d+)?', d)
    i, cmd, cur, start, segs = 0, None, (0, 0), (0, 0), []
    num = lambda: float(toks[i])
    while i < len(toks):
        if re.match('[A-Za-z]', toks[i]): cmd = toks[i]; i += 1
        if cmd == 'M':
            cur = start = (float(toks[i]), float(toks[i + 1])); i += 2; segs.append(('M', [cur])); cmd = 'L'
        elif cmd == 'L':
            p = (float(toks[i]), float(toks[i + 1])); i += 2
            segs.append(('C', [(cur[0] + (p[0] - cur[0]) / 3, cur[1] + (p[1] - cur[1]) / 3), (cur[0] + (p[0] - cur[0]) * 2 / 3, cur[1] + (p[1] - cur[1]) * 2 / 3), p])); cur = p
        elif cmd in 'HV':
            v = float(toks[i]); i += 1
            p = (v, cur[1]) if cmd == 'H' else (cur[0], v)
            segs.append(('C', [(cur[0] + (p[0] - cur[0]) / 3, cur[1] + (p[1] - cur[1]) / 3), (cur[0] + (p[0] - cur[0]) * 2 / 3, cur[1] + (p[1] - cur[1]) * 2 / 3), p])); cur = p
        elif cmd == 'C':
            pts = [(float(toks[i + k]), float(toks[i + k + 1])) for k in (0, 2, 4)]; i += 6
            segs.append(('C', pts)); cur = pts[2]
        elif cmd in 'Zz':
            segs.append(('Z', [])); cur = start
        else:
            raise ValueError(cmd)
    # делим кривые
    out, cur = [], None
    for c, pts in segs:
        if c == 'C':
            for part in split_cubic(cur, *pts, SPLIT): out.append(('C', list(part)))
            cur = pts[2]
        else:
            out.append((c, pts))
            if c == 'M': cur = pts[0]
    def j(p):
        return (p[0] + amp * nx(p[0] / wave, p[1] / wave), p[1] + amp * ny(p[0] / wave, p[1] / wave))
    f = lambda p: '%.2f %.2f' % j(p)
    return ''.join(c + (' '.join(f(p) for p in pts)) for c, pts in out)

for fn in sorted(os.listdir(SRC)):
    if not fn.endswith('.svg'): continue
    name = fn[:-4]
    s = open(os.path.join(SRC, fn), encoding='utf-8', newline='').read()
    sc = SCALE.get(name, .5)
    amp, wave = AMP_PX / sc, WAVE_PX / sc
    nx, ny = noise_fn(sum(map(ord, name))), noise_fn(sum(map(ord, name)) + 1)
    s = re.sub(r' d="([^"]*)"', lambda m: ' d="%s"' % process(m.group(1), amp, wave, nx, ny), s)
    s = re.sub(r'stroke-width="[\d.]+"', 'stroke-width="%g"' % STROKE, s)
    s = s.replace('stroke-linecap="square"', 'stroke-linecap="round"')
    open(os.path.join(OUT, fn), 'w', encoding='utf-8', newline='').write(s)
    print(fn, 'amp %.1f wave %.0f' % (amp, wave))
