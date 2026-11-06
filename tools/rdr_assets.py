"""Red Dead themed SVG asset generator for the anxmeshhh profile README.

Fonts (all SIL OFL / Apache, embeddable): Anton (condensed poster headline,
closest open cousin of the RDR 'Redemption'/Chinese Rocks lettering), Rye
(19th-century wood type), IM Fell English SC (period print), Special Elite
(typewriter / telegram). Each SVG embeds only the glyphs it uses (woff2).
"""
import base64, html, io, math, os, random, re, sys
from fontTools.ttLib import TTFont
from fontTools import subset

HERE = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(HERE, '..', 'fonts')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'profile', 'assets')

FONTS = {
    'anton': ('Anton-Regular.ttf', 'RDAnton'),
    'rye': ('Rye-Regular.ttf', 'RDRye'),
    'fell': ('IMFeENsc28P.ttf', 'RDFell'),
    'type': ('SpecialElite-Regular.ttf', 'RDType'),
}
TT = {k: TTFont(os.path.join(FD, v[0])) for k, v in FONTS.items()}

# ── palette ────────────────────────────────────────────────────────────────
INK = '#0A0606'      # night black
COAL = '#120808'     # panel black
MAROON = '#2A0A0A'   # panel maroon
MAROON2 = '#3D0E0E'  # borders
BLOOD = '#B3121B'    # deep red
RED = '#E3242B'      # signal red
EMBER = '#FF5A36'    # sun / fire
BONE = '#F1E4CF'     # primary text
BONE2 = '#C9B59A'    # secondary text
DUST = '#8F7B66'     # muted text
SIL = '#080303'      # silhouettes

WARN = []


def esc(s):
    return html.escape(s, quote=True)


def tw(font, s, size, ls=0.0):
    t = TT[font]
    cmap = t.getBestCmap(); hm = t['hmtx']; upm = t['head'].unitsPerEm
    w = 0
    for ch in s:
        g = cmap.get(ord(ch))
        if g is None:
            WARN.append(f'missing glyph {ch!r} U+{ord(ch):04X} in {font}')
            g = '.notdef'
        w += hm[g][0]
    return w * size / upm + ls * len(s)


def fit(font, s, size, maxw, ls=0.0, where=''):
    w = tw(font, s, size, ls)
    if w > maxw:
        WARN.append(f'OVERFLOW [{where}] {s!r} {w:.0f}px > {maxw}px')
    return w


def face(key, text):
    path, fam = FONTS[key]
    f = TTFont(os.path.join(FD, path))
    o = subset.Options(); o.flavor = 'woff2'; o.layout_features = ['kern', 'liga']
    o.name_IDs = []; o.notdef_outline = True; o.hinting = False; o.desubroutinize = True
    s = subset.Subsetter(o); s.populate(text=text + ' '); s.subset(f)
    f.flavor = 'woff2'; b = io.BytesIO(); f.save(b)
    data = base64.b64encode(b.getvalue()).decode()
    return f"@font-face{{font-family:'{fam}';src:url(data:font/woff2;base64,{data}) format('woff2');}}"


def T(font, x, y, s, size, fill=BONE, anchor='start', ls=0, extra=''):
    fam = FONTS[font][1]
    a = f' text-anchor="{anchor}"' if anchor != 'start' else ''
    l = f' letter-spacing="{ls}"' if ls else ''
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" fill="{fill}"{a}{l} {extra}>'
            f'{esc(s)}</text>')


GRAIN = ('<filter id="grain" x="0" y="0" width="100%" height="100%">'
         '<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch"/>'
         '<feColorMatrix type="saturate" values="0"/>'
         '<feComponentTransfer><feFuncA type="table" tableValues="0 0.13"/></feComponentTransfer></filter>')


def svg(name, w, h, body, css='', title='', desc=''):
    textonly = html.unescape(re.sub(r'<[^>]+>', ' ', body))
    used = [k for k in FONTS if FONTS[k][1] in body]
    faces = ''.join(face(k, textonly) for k in used)
    doc = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
           f'role="img" aria-labelledby="t d"><title id="t">{esc(title or name)}</title>'
           f'<desc id="d">{esc(desc)}</desc><style>{faces}{css}</style>{body}</svg>')
    with open(os.path.join(OUT, name), 'w', encoding='utf-8') as fh:
        fh.write(doc)
    print(f'{name:28s} {len(doc)/1024:7.1f} KB')


# ── reusable silhouettes ───────────────────────────────────────────────────
def cowboy(x, y, s=1.0, fill=SIL):
    return f'''<g transform="translate({x},{y}) scale({s})" fill="{fill}">
<path d="M-36,-143 C-30,-146 -26,-148 -18,-149 C-8,-151 8,-151 18,-149 C26,-148 30,-146 36,-143 C30,-140 22,-139 0,-139 C-22,-139 -30,-140 -36,-143Z"/>
<path d="M-16,-147 L-14,-163 Q-7,-168 0,-164 Q7,-168 14,-163 L16,-147Z"/>
<ellipse cx="0" cy="-132" rx="9.5" ry="11.5"/><rect x="-5" y="-124" width="10" height="6"/>
<path d="M-19,-121 Q0,-126 19,-121 L22,-112 L18,-78 L19,-64 L-19,-64 L-18,-78 L-22,-112Z"/>
<path d="M-19,-66 L19,-66 L20,-56 L-20,-56Z"/><path d="M18,-64 L26,-60 L25,-40 L19,-42Z"/>
<path d="M-21,-118 L-28,-114 L-38,-78 L-41,-60 L-34,-58 L-31,-76 L-24,-98Z"/>
<path d="M21,-118 L28,-114 L36,-80 L35,-62 L29,-62 L29,-80 L23,-98Z"/>
<path d="M-20,-58 L0,-58 L-11,-4 L-23,-4Z"/><path d="M0,-58 L20,-58 L23,-4 L11,-4Z"/>
<path d="M-25,-6 L-9,-6 L-8,0 L-28,0Z"/><path d="M9,-6 L25,-6 L28,0 L8,0Z"/>
<path d="M4,-123 L24,-127 L19,-119Z"><animate attributeName="d" dur="1.3s" repeatCount="indefinite" values="M4,-123 L24,-127 L19,-119Z;M4,-123 L25,-121 L18,-116Z;M4,-123 L24,-127 L19,-119Z"/></path></g>'''


def cactus(x, y, s=1.0, fill=SIL):
    return f'''<g transform="translate({x},{y}) scale({s})" fill="{fill}">
<rect x="-7" y="-78" width="14" height="80" rx="7"/>
<rect x="-26" y="-40" width="22" height="10" rx="5"/><rect x="-26" y="-62" width="10" height="30" rx="5"/>
<rect x="4" y="-52" width="22" height="10" rx="5"/><rect x="16" y="-70" width="10" height="26" rx="5"/></g>'''


def pole(x, ground, h, fill=SIL):
    top = ground - h
    return (f'<g fill="{fill}"><rect x="{x-2}" y="{top}" width="4" height="{h}"/>'
            f'<rect x="{x-18}" y="{top+6}" width="36" height="3"/><rect x="{x-12}" y="{top+14}" width="24" height="2.5"/></g>')


def wire(x1, y1, x2, y2, sag=12):
    mx = (x1 + x2) / 2; my = max(y1, y2) + sag
    return f'<path d="M{x1},{y1} Q{mx},{my} {x2},{y2}" stroke="{SIL}" stroke-width="1.3" fill="none"/>'


def bird(cx, cy, r, dur, begin=0, s=1.0):
    return f'''<g><g transform="scale({s})"><path stroke="{SIL}" stroke-width="2.4" fill="none" stroke-linecap="round" d="M-12,0 Q-6,-7 0,0 Q6,-7 12,0">
<animate attributeName="d" dur="0.9s" repeatCount="indefinite" values="M-12,0 Q-6,-7 0,0 Q6,-7 12,0;M-12,-5 Q-6,2 0,0 Q6,2 12,-5;M-12,0 Q-6,-7 0,0 Q6,-7 12,0"/></path></g>
<animateMotion dur="{dur}s" begin="{begin}s" repeatCount="indefinite" path="M{cx-r},{cy} a{r},{r*0.45} 0 1,0 {2*r},0 a{r},{r*0.45} 0 1,0 {-2*r},0"/></g>'''


def star(cx, cy, R, fill=RED):
    pts = []
    for i in range(12):
        a = -math.pi / 2 + i * math.pi / 6
        rr = R if i % 2 == 0 else R * 0.52
        pts.append(f'{cx + rr*math.cos(a):.1f},{cy + rr*math.sin(a):.1f}')
    balls = ''.join(f'<circle cx="{cx + R*math.cos(-math.pi/2 + i*math.pi/3):.1f}" '
                    f'cy="{cy + R*math.sin(-math.pi/2 + i*math.pi/3):.1f}" r="{R*0.15:.1f}"/>' for i in range(6))
    return (f'<g fill="{fill}"><polygon points="{" ".join(pts)}"/>{balls}'
            f'<circle cx="{cx}" cy="{cy}" r="{R*0.3:.1f}" fill="{INK}"/><circle cx="{cx}" cy="{cy}" r="{R*0.18:.1f}"/></g>')


def diamond(cx, cy, r, fill=RED):
    return f'<path d="M{cx},{cy-r} L{cx+r},{cy} L{cx},{cy+r} L{cx-r},{cy}Z" fill="{fill}"/>'


def dust(n, x0, x1, y0, y1, seed, dur=(9, 16)):
    rnd = random.Random(seed); out = []
    for _ in range(n):
        y = rnd.uniform(y0, y1); r = rnd.uniform(0.8, 2.1); d = rnd.uniform(*dur); b = -rnd.uniform(0, d)
        out.append(f'<circle cx="{x0}" cy="{y:.0f}" r="{r:.1f}" fill="#FFD9B8" opacity="0">'
                   f'<animate attributeName="cx" from="{x0 - 40}" to="{x1 + 40}" dur="{d:.1f}s" begin="{b:.1f}s" repeatCount="indefinite"/>'
                   f'<animate attributeName="cy" values="{y:.0f};{y-14:.0f};{y+6:.0f}" dur="{d:.1f}s" begin="{b:.1f}s" repeatCount="indefinite"/>'
                   f'<animate attributeName="opacity" values="0;0.55;0.4;0" dur="{d:.1f}s" begin="{b:.1f}s" repeatCount="indefinite"/></circle>')
    return ''.join(out)


def mesa_path(w, base, seed, lo, hi, bottom):
    rnd = random.Random(seed); x = 0; y = rnd.uniform(lo, hi); d = [f'M0,{y:.0f}']
    while x < w:
        kind = rnd.random()
        if kind < 0.35:  # flat-topped butte
            top = rnd.uniform(lo - 26, lo - 8); wd = rnd.uniform(40, 110)
            d += [f'L{x+10:.0f},{top+6:.0f}', f'L{x+16:.0f},{top:.0f}', f'L{x+16+wd:.0f},{top+2:.0f}',
                  f'L{x+24+wd:.0f},{top+10:.0f}', f'L{x+36+wd:.0f},{rnd.uniform(lo, hi):.0f}']
            x += 36 + wd
        else:
            x += rnd.uniform(30, 80); d.append(f'L{x:.0f},{rnd.uniform(lo, hi):.0f}')
    d.append(f'L{w},{bottom} L0,{bottom}Z')
    return ' '.join(d)


# ══════════════════════════════════════════════════════════════════════════
# 1. HERO
# ══════════════════════════════════════════════════════════════════════════
def hero():
    W, H = 1200, 460
    name1, name2 = 'ANIMESH', 'GUPTA'
    fit('anton', name1, 116, 560, where='hero'); fit('anton', name2, 116, 560, where='hero')
    role = 'Software Engineer  ·  Backend  ·  AI & LLM Systems'
    fit('fell', role, 27, 600, where='hero role')
    tag = 'Backends built to last. Agents kept on a short leash.'
    fit('type', tag, 17, 600, where='hero tag')
    kick = 'EST. 2025  ·  CHENNAI, INDIA'
    sunx, suny = 905, 322
    rnd = random.Random(3)
    streaks = ''.join(
        f'<ellipse cx="{rnd.uniform(700, 1150):.0f}" cy="{y}" rx="{rnd.uniform(160, 300):.0f}" ry="{rnd.uniform(3, 7):.1f}" fill="#1E0303" opacity="{rnd.uniform(.35, .6):.2f}">'
        f'<animateTransform attributeName="transform" type="translate" values="0 0;-70 0;0 0" dur="{rnd.uniform(40, 60):.0f}s" repeatCount="indefinite"/></ellipse>'
        for y in (78, 124, 168, 206))
    body = f'''
<defs>{GRAIN}
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0E0202"/><stop offset=".38" stop-color="#4A0707"/><stop offset=".72" stop-color="#A3121A"/><stop offset="1" stop-color="#E8432E"/></linearGradient>
<radialGradient id="glow" cx="{sunx}" cy="{suny}" r="560" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#FF8A4C" stop-opacity=".95"/><stop offset=".22" stop-color="#F0432A" stop-opacity=".6"/><stop offset="1" stop-color="#E3242B" stop-opacity="0"/></radialGradient>
<radialGradient id="sun" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFE7C9"/><stop offset=".6" stop-color="#FFB27A"/><stop offset="1" stop-color="#FF6A3D"/></radialGradient>
<linearGradient id="shade" x1="0" x2="1"><stop offset="0" stop-color="#000" stop-opacity=".78"/><stop offset=".42" stop-color="#000" stop-opacity=".5"/><stop offset=".62" stop-color="#000" stop-opacity="0"/></linearGradient>
<radialGradient id="vig" cx=".55" cy=".5" r=".8"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".7"/></radialGradient>
<clipPath id="clip"><rect width="{W}" height="{H}" rx="18"/></clipPath>
<filter id="soft"><feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000" flood-opacity=".8"/></filter>
</defs>
<g clip-path="url(#clip)">
<rect width="{W}" height="{H}" fill="url(#sky)"/>
<rect width="{W}" height="{H}" fill="url(#glow)"><animate attributeName="opacity" values=".85;1;.85" dur="6s" repeatCount="indefinite"/></rect>
{streaks}
<circle cx="{sunx}" cy="{suny}" r="98" fill="url(#sun)"><animate attributeName="r" values="98;101;98" dur="6s" repeatCount="indefinite"/></circle>
<ellipse cx="{sunx}" cy="{suny-30}" rx="190" ry="3.5" fill="#7A0B0E" opacity=".75"/>
<ellipse cx="{sunx+30}" cy="{suny-8}" rx="150" ry="2.6" fill="#7A0B0E" opacity=".6"/>
{bird(640, 120, 46, 16)}{bird(760, 92, 30, 12, -5, .8)}{bird(1060, 150, 36, 19, -9, .7)}
<path d="{mesa_path(W, 0, 11, 340, 356, H)}" fill="#6A0C0E"/>
<path d="M0,392 Q150,372 300,388 T600,384 T900,380 T1200,386 L1200,{H} L0,{H}Z" fill="#2E0505"/>
{wire(560, 340, 650, 330, 10)}{wire(650, 330, 770, 338, 12)}{wire(770, 338, 1120, 316, 26)}{wire(1120, 316, 1200, 322, 8)}
{wire(560, 348, 650, 338, 10)}{wire(650, 338, 770, 346, 12)}{wire(770, 346, 1120, 324, 26)}{wire(1120, 324, 1200, 330, 8)}
{pole(650, 420, 92)}{pole(770, 414, 78)}{pole(1120, 414, 100)}
<path d="M0,420 Q200,410 400,418 Q560,424 700,414 Q820,404 905,402 Q1000,400 1080,410 Q1150,416 1200,414 L1200,{H} L0,{H}Z" fill="{SIL}"/>
{cactus(1038, 410, .9)}{cactus(585, 422, .5)}
{cowboy(sunx, 404, 1.05)}
{dust(18, 0, W, 300, 450, 5)}
<rect width="{W}" height="{H}" fill="url(#shade)"/>
<rect width="{W}" height="{H}" fill="url(#vig)"/>
<rect width="{W}" height="{H}" filter="url(#grain)"/>
<g class="in1"><rect x="64" y="62" width="44" height="3" fill="{RED}"/>{T('type', 120, 70, kick, 16, BONE2, ls=3)}</g>
<g class="in2" filter="url(#soft)">{T('anton', 58, 196, name1, 116, BONE, ls=2)}</g>
<g class="in3" filter="url(#soft)">{T('anton', 58, 312, name2, 116, RED, ls=2)}</g>
<g class="in4">{T('fell', 62, 358, role, 27, BONE)}{T('type', 64, 394, tag, 17, BONE2)}</g>
</g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="18" fill="none" stroke="{MAROON2}"/>'''
    css = ('.in1,.in2,.in3,.in4{opacity:0;animation:rise .9s ease-out forwards}'
           '.in2{animation-delay:.15s}.in3{animation-delay:.35s}.in4{animation-delay:.6s}'
           '@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}')
    svg('hero.svg', W, H, body, css, 'Animesh Gupta, Software Engineer',
        'Red Dead styled banner: Animesh Gupta, Software Engineer, Backend and AI/LLM systems, Chennai, India.')


# ══════════════════════════════════════════════════════════════════════════
# 2. CHAPTER CARDS
# ══════════════════════════════════════════════════════════════════════════
def chapter(fname, num, title, sub):
    W, H = 1200, 132
    tws = fit('anton', title, 46, 700, ls=2, where='chapter')
    half = tws / 2 + 34
    body = f'''<defs>{GRAIN}<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#160808"/><stop offset="1" stop-color="{INK}"/></linearGradient>
<radialGradient id="hl" cx=".5" cy="1" r=".6"><stop offset="0" stop-color="{BLOOD}" stop-opacity=".35"/><stop offset="1" stop-color="{BLOOD}" stop-opacity="0"/></radialGradient>
<clipPath id="c"><rect width="{W}" height="{H}" rx="14"/></clipPath></defs>
<g clip-path="url(#c)"><rect width="{W}" height="{H}" fill="url(#bg)"/><rect width="{W}" height="{H}" fill="url(#hl)"/>
<rect width="{W}" height="{H}" filter="url(#grain)"/></g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="14" fill="none" stroke="{MAROON}"/>
{T('rye', 600, 40, num, 17, RED, 'middle', 5)}
<g class="t">{T('anton', 600, 93, title, 46, BONE, 'middle', 2)}</g>
{T('type', 600, 118, sub, 13, DUST, 'middle', 3)}
<g stroke="{RED}" stroke-width="1.6"><line class="ln" x1="{600-half}" y1="74" x2="110" y2="74"/><line class="ln" x1="{600+half}" y1="74" x2="1090" y2="74"/></g>
<g stroke="{BLOOD}" stroke-width=".8" opacity=".7"><line class="ln" x1="{600-half}" y1="80" x2="150" y2="80"/><line class="ln" x1="{600+half}" y1="80" x2="1050" y2="80"/></g>
{diamond(100, 74, 6)}{diamond(1100, 74, 6)}{diamond(600-half+8, 74, 3.5, BONE2)}{diamond(600+half-8, 74, 3.5, BONE2)}'''
    css = ('.ln{stroke-dasharray:500;stroke-dashoffset:500;animation:draw 1.4s .2s ease-out forwards}'
           '@keyframes draw{to{stroke-dashoffset:0}}'
           '.t{opacity:0;animation:fade .8s ease-out forwards}@keyframes fade{to{opacity:1}}')
    svg(fname, W, H, body, css, f'{num}: {title}', sub)


# ══════════════════════════════════════════════════════════════════════════
# 3. WANTED POSTER
# ══════════════════════════════════════════════════════════════════════════
def wanted():
    W, H = 440, 620
    ink = '#2A1208'; red = '#9E1016'
    rnd = random.Random(21)
    x0, y0, x1, y1 = 22, 26, 418, 600
    pts = []
    for x in range(x0, x1, 11): pts.append((x, y0 + rnd.uniform(-3, 3)))
    for y in range(y0, y1, 11): pts.append((x1 + rnd.uniform(-3, 3), y))
    for x in range(x1, x0, -11): pts.append((x, y1 + rnd.uniform(-4, 4)))
    for y in range(y1, y0, -11): pts.append((x0 + rnd.uniform(-3, 3), y))
    torn = 'M' + ' L'.join(f'{a:.1f},{b:.1f}' for a, b in pts) + 'Z'
    cx = 220
    para = ['For building backend systems that hold up', 'in production. Last seen riding with Python,',
            'SQL, Docker and a gang of LLM agents.']
    for p in para: fit('type', p, 13.5, 360, where='poster')
    fit('rye', 'WANTED', 74, 370, where='poster')
    fit('anton', 'ANIMESH GUPTA', 44, 370, ls=1, where='poster')
    fit('fell', 'ALIVE · AND SHIPPING TO PRODUCTION', 17, 360, where='poster')
    body = f'''<defs>{GRAIN}
<filter id="stain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.013" numOctaves="4" seed="7"/>
<feColorMatrix type="matrix" values="0 0 0 0 .36  0 0 0 0 .19  0 0 0 0 .07  1.5 0 0 0 -.6"/></filter>
<filter id="speck" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.7" numOctaves="2" seed="3"/>
<feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  5 0 0 0 -2.9"/></filter>
<mask id="rough"><rect width="{W}" height="{H}" fill="#fff"/><rect width="{W}" height="{H}" filter="url(#speck)"/></mask>
<radialGradient id="burn" cx=".5" cy=".48" r=".72"><stop offset=".55" stop-color="#5A2A10" stop-opacity="0"/><stop offset=".9" stop-color="#5A2A10" stop-opacity=".45"/><stop offset="1" stop-color="#3A1606" stop-opacity=".85"/></radialGradient>
<clipPath id="paper"><path d="{torn}"/></clipPath>
<filter id="drop" x="-10%" y="-10%" width="120%" height="120%"><feDropShadow dx="0" dy="8" stdDeviation="9" flood-color="#000" flood-opacity=".55"/></filter>
</defs>
<g transform="rotate(-1.6 220 310)">
<path d="{torn}" fill="#E7D3AE" filter="url(#drop)"/>
<g clip-path="url(#paper)">
<rect width="{W}" height="{H}" filter="url(#stain)"/><rect width="{W}" height="{H}" fill="url(#burn)"/><rect width="{W}" height="{H}" filter="url(#grain)"/>
<g mask="url(#rough)">
{T('rye', cx, 112, 'WANTED', 74, ink, 'middle')}
<line x1="52" y1="128" x2="388" y2="128" stroke="{ink}" stroke-width="2.5"/><line x1="52" y1="134" x2="388" y2="134" stroke="{ink}" stroke-width="1"/>
{T('fell', cx, 156, 'ALIVE · AND SHIPPING TO PRODUCTION', 17, ink, 'middle')}
<rect x="104" y="172" width="232" height="200" fill="#D9C094" stroke="{ink}" stroke-width="3"/>
<rect x="111" y="179" width="218" height="186" fill="none" stroke="{ink}" stroke-width="1"/>
<g fill="{ink}">
<path d="M122,365 Q130,318 186,304 L254,304 Q310,318 318,365Z"/>
<rect x="208" y="276" width="24" height="32"/>
<ellipse cx="220" cy="266" rx="27" ry="33"/>
<path d="M146,240 C178,224 262,224 294,240 C262,250 178,250 146,240Z"/>
<path d="M186,239 L191,200 Q205,191 220,198 Q235,191 249,200 L254,239Z"/>
</g>
<path d="M194,272 Q220,280 246,272 L246,280 Q232,300 220,306 Q208,300 194,280Z" fill="{red}"/>
<rect x="187" y="232" width="66" height="6" fill="{red}" opacity=".85"/>
{T('anton', cx, 420, 'ANIMESH GUPTA', 44, ink, 'middle', 1)}
{T('type', cx, 443, 'alias "anxmeshhh"', 15, ink, 'middle')}
{''.join(T('type', cx, 470 + i*19, p, 13.5, ink, 'middle') for i, p in enumerate(para))}
<line x1="90" y1="538" x2="350" y2="538" stroke="{ink}" stroke-width="1"/>
{T('rye', cx, 568, 'REWARD', 26, red, 'middle', 3)}
{T('anton', cx, 594, 'ONE INTERVIEW', 22, ink, 'middle', 3)}
</g></g>
<circle cx="220" cy="44" r="6" fill="#3A2A20"/><circle cx="218.5" cy="42.5" r="2" fill="#A89480"/>
<g transform="rotate(-14 322 345)"><g class="stamp" mask="url(#rough)">
<rect x="248" y="322" width="148" height="46" rx="4" fill="none" stroke="{RED}" stroke-width="3.5"/>
{T('anton', 322, 356, 'HIRE ON SIGHT', 24, RED, 'middle', 1)}</g></g>
</g>'''
    css = ('.stamp{opacity:0;transform-box:fill-box;transform-origin:center;animation:slam .55s 1s cubic-bezier(.2,.9,.3,1.2) forwards}'
           '@keyframes slam{0%{opacity:0;transform:scale(2.4)}70%{opacity:1;transform:scale(.94)}100%{opacity:.9;transform:scale(1)}}')
    svg('wanted.svg', W, H, body, css, 'Wanted: Animesh Gupta',
        'Wanted poster. Alive and shipping to production. For building backend systems that hold up in production. Reward: one interview.')


# ══════════════════════════════════════════════════════════════════════════
# 4. PLAYER STATISTICS (cores)
# ══════════════════════════════════════════════════════════════════════════
def stats_panel():
    W, H = 1200, 310
    items = [('9.66', 'CGPA', 'SRM IST · out of 10', .966),
             ('75K', 'LINES SHIPPED', 'Sentinel AI · solo', .75),
             ('900+', 'TESTS WRITTEN', 'one codebase', .9),
             ('35+', 'DEVELOPERS LED', 'as Backend Lead', .7),
             ('7+', 'CLIENT PROJECTS', 'via Webnify', .62),
             ('5', 'PODIUMS & WINS', 'hackathons & contests', .84)]
    r = 50; C = 2 * math.pi * r
    rings = []; css = []
    for i, (v, lab, sub, p) in enumerate(items):
        cx = 110 + i * 196; cy = 168
        fit('anton', v, 34, 80, where='stat'); fit('fell', lab, 17, 185, where='stat'); fit('type', sub, 12, 185, where='stat')
        css.append(f'.r{i}{{stroke-dasharray:{C:.1f};stroke-dashoffset:{C:.1f};animation:f{i} 1.6s {0.2+i*0.15:.2f}s cubic-bezier(.3,.7,.2,1) forwards}}'
                   f'@keyframes f{i}{{to{{stroke-dashoffset:{C*(1-p):.1f}}}}}')
        rings.append(f'''<g>
<circle cx="{cx}" cy="{cy}" r="{r+13}" fill="none" stroke="{MAROON2}" stroke-width="1"/>
<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#4A1212" stroke-width="9" stroke-dasharray="3 3.55"/>
<circle class="r{i}" cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{RED}" stroke-width="9" transform="rotate(-90 {cx} {cy})"/>
<circle cx="{cx}" cy="{cy}" r="{r-10}" fill="#1A0606" stroke="{BLOOD}" stroke-opacity=".5"/>
{T('anton', cx, cy + 12, v, 34, BONE, 'middle')}
{T('fell', cx, 262, lab, 17, BONE, 'middle')}{T('type', cx, 283, sub, 12, DUST, 'middle')}</g>''')
    body = f'''<defs>{GRAIN}<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2E0B0B"/><stop offset=".6" stop-color="#170707"/><stop offset="1" stop-color="{INK}"/></linearGradient>
<radialGradient id="g" cx=".15" cy="0" r=".9"><stop offset="0" stop-color="{BLOOD}" stop-opacity=".35"/><stop offset="1" stop-color="{BLOOD}" stop-opacity="0"/></radialGradient>
<clipPath id="c"><rect width="{W}" height="{H}" rx="18"/></clipPath></defs>
<g clip-path="url(#c)"><rect width="{W}" height="{H}" fill="url(#bg)"/><rect width="{W}" height="{H}" fill="url(#g)"/><rect width="{W}" height="{H}" filter="url(#grain)"/></g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="18" fill="none" stroke="#4A1010"/>
{T('anton', 40, 56, 'PLAYER STATISTICS', 28, BONE, ls=2)}
<rect x="900" y="30" width="260" height="36" rx="18" fill="#1A0606" stroke="{RED}" stroke-width="1.5"/>
<circle cx="922" cy="48" r="5" fill="{RED}"><animate attributeName="opacity" values="1;.25;1" dur="1.6s" repeatCount="indefinite"/></circle>
{T('type', 1038, 53, 'HONOR: HIGH  ·  STATUS: SHIPPING', 12.5, BONE2, 'middle')}
<line x1="40" y1="78" x2="1160" y2="78" stroke="{MAROON2}"/><line x1="40" y1="78" x2="250" y2="78" stroke="{RED}" stroke-width="2"/>
{''.join(rings)}'''
    svg('player-stats.svg', W, H, body, ''.join(css), 'Player statistics',
        'CGPA 9.66 of 10; 75K lines shipped solo on Sentinel AI; 900+ tests; led 35+ developers; 7+ client projects; 5 hackathon podiums and wins.')


# ══════════════════════════════════════════════════════════════════════════
# 5. THE STORY SO FAR (railroad timeline)
# ══════════════════════════════════════════════════════════════════════════
def story():
    W, H = 1200, 344
    jobs = [('JAN 2025 — PRESENT', 'FOUNDER & FULL-STACK DEV', 'Webnify', 'Chennai, Tamil Nadu',
             ['Full-stack apps & workflow automation', '7+ client projects, full SDLC owned'], True),
            ('MAR 2025 — DEC 2025', 'FULL-STACK DEVELOPER', 'VerrGroup', 'Chennai, Tamil Nadu',
             ['Django + MySQL apps, schema to release', 'Shipped on a VPS with Gunicorn + Nginx'], False),
            ('SEP 2025 — MAY 2026', 'BACKEND LEAD', 'Brain Mint Technologies', 'Chennai, Tamil Nadu',
             ['Backend architecture, schema & RBAC', 'Led 35+ developers · JWT-secured APIs'], False)]
    ties = ''.join(f'<rect x="{x}" y="56" width="6" height="26" fill="#3A0E0E"/>' for x in range(16, 1190, 22))
    train = f'''<g class="train"><g fill="{BLOOD}">
<rect x="0" y="40" width="70" height="22" rx="6"/><rect x="60" y="24" width="34" height="38" rx="3"/><rect x="56" y="20" width="42" height="6"/>
<path d="M8,40 L4,22 L18,22 L14,40Z"/><rect x="30" y="34" width="10" height="7"/><path d="M0,58 L-14,66 L0,66Z"/>
<rect x="104" y="40" width="58" height="22" rx="3"/></g>
<rect x="68" y="30" width="18" height="12" fill="#FFB27A" opacity=".85"/>
<g fill="#1A0606" stroke="{RED}" stroke-width="2"><circle cx="20" cy="64" r="7"/><circle cx="46" cy="64" r="7"/><circle cx="80" cy="62" r="9"/><circle cx="116" cy="65" r="6"/><circle cx="150" cy="65" r="6"/></g>
<g fill="{DUST}"><circle cx="11" cy="14" r="5" opacity=".5"><animate attributeName="cy" values="14;-20" dur="1.4s" repeatCount="indefinite"/><animate attributeName="r" values="4;12" dur="1.4s" repeatCount="indefinite"/><animate attributeName="opacity" values=".55;0" dur="1.4s" repeatCount="indefinite"/></circle>
<circle cx="11" cy="14" r="5" opacity=".5"><animate attributeName="cy" values="14;-20" dur="1.4s" begin=".7s" repeatCount="indefinite"/><animate attributeName="r" values="4;12" dur="1.4s" begin=".7s" repeatCount="indefinite"/><animate attributeName="opacity" values=".55;0" dur="1.4s" begin=".7s" repeatCount="indefinite"/></circle></g></g>'''
    cards = []
    for i, (dates, role, co, loc, bullets, live) in enumerate(jobs):
        sx = 210 + i * 390; x = sx - 180
        fit('anton', role, 25, 320, ls=1, where='story'); fit('fell', co, 22, 320, where='story')
        for b in bullets: fit('type', b, 13.5, 318, where='story')
        fit('type', dates, 14, 300, ls=1, where='story')
        pulse = (f'<circle cx="{sx}" cy="70" r="14" fill="none" stroke="{RED}" stroke-width="2">'
                 f'<animate attributeName="r" values="14;26" dur="1.8s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values=".9;0" dur="1.8s" repeatCount="indefinite"/></circle>') if live else ''
        cards.append(f'''{pulse}<circle cx="{sx}" cy="70" r="13" fill="{INK}" stroke="{RED}" stroke-width="3"/><circle cx="{sx}" cy="70" r="5" fill="{RED if live else BONE2}"/>
{T('type', sx, 32, dates, 14, BONE2 if not live else RED, 'middle', 1)}
<line x1="{sx}" y1="84" x2="{sx}" y2="112" stroke="{RED}" stroke-dasharray="3 3"/>
<rect x="{x}" y="112" width="360" height="208" rx="12" fill="#140808" stroke="{MAROON2}"/>
<rect x="{x}" y="112" width="360" height="4" rx="2" fill="{RED}"/>
{T('anton', x+22, 154, role, 25, BONE, ls=1)}
{T('fell', x+22, 182, co, 22, RED)}
{T('type', x+22, 204, loc, 12.5, DUST, ls=1)}
<line x1="{x+22}" y1="220" x2="{x+338}" y2="220" stroke="{MAROON2}"/>
{''.join(diamond(x+27, 247+j*30-4, 4) + T('type', x+40, 247+j*30, b, 13.5, BONE2) for j, b in enumerate(bullets))}''')
    body = f'''<defs>{GRAIN}<clipPath id="c"><rect width="{W}" height="{H}" rx="18"/></clipPath></defs>
<rect width="{W}" height="{H}" rx="18" fill="{INK}"/><rect width="{W}" height="{H}" rx="18" filter="url(#grain)"/><rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="18" fill="none" stroke="{MAROON2}"/>
{ties}<rect x="10" y="62" width="1180" height="3" fill="#5A1414"/><rect x="10" y="74" width="1180" height="3" fill="#5A1414"/>
<g clip-path="url(#c)"><g transform="translate(0,0)">{train}</g></g>
{''.join(cards)}'''
    css = ('.train{animation:ride 16s linear infinite}'
           '@keyframes ride{from{transform:translate(-200px,0)}to{transform:translate(1400px,0)}}')
    svg('story.svg', W, H, body, css, 'The story so far',
        'Founder & Full-Stack Developer at Webnify (Jan 2025 to present); Full-Stack Developer at VerrGroup (Mar to Dec 2025); Backend Lead at Brain Mint Technologies (Sep 2025 to May 2026).')


# ══════════════════════════════════════════════════════════════════════════
# 6. MISSION CARDS
# ══════════════════════════════════════════════════════════════════════════
def scene_watchtower():
    x = 430
    braces = ''.join(f'<path d="M{x-22+i*2.2:.1f},{208-i*26} L{x+22-(i+1)*2.2:.1f},{208-(i+1)*26} M{x+22-i*2.2:.1f},{208-i*26} L{x-22+(i+1)*2.2:.1f},{208-(i+1)*26}" stroke="{SIL}" stroke-width="2"/>' for i in range(4))
    return f'''<g fill="{SIL}"><path d="M{x-24},208 L{x-12},106 L{x-8},106 L{x-19},208Z"/><path d="M{x+24},208 L{x+12},106 L{x+8},106 L{x+19},208Z"/>
<rect x="{x-30}" y="100" width="60" height="7"/><rect x="{x-22}" y="74" width="44" height="27"/><path d="M{x-32},76 L{x},52 L{x+32},76Z"/></g>{braces}
<rect x="{x-13}" y="80" width="26" height="12" fill="#FFB27A"><animate attributeName="opacity" values=".95;.55;.95" dur="2.4s" repeatCount="indefinite"/></rect>
<path d="M{x+13},86 L600,40 L600,110Z" fill="#FFD9B8" opacity=".08"><animateTransform attributeName="transform" type="rotate" values="-8 {x} 86;10 {x} 86;-8 {x} 86" dur="9s" repeatCount="indefinite"/></path>
{cactus(150, 212, .55)}{cowboy(250, 210, .36)}'''


def scene_courthouse():
    cols = ''.join(f'<rect x="{x}" y="160" width="9" height="40"/>' for x in (152, 174, 196, 218, 240))
    return f'''<g fill="{SIL}"><path d="M134,152 L200,124 L266,152Z"/><rect x="140" y="150" width="120" height="11"/>{cols}
<rect x="100" y="158" width="44" height="52"/><rect x="256" y="158" width="44" height="52"/><rect x="126" y="198" width="148" height="12"/>
<rect x="184" y="92" width="32" height="34"/><path d="M180,94 L200,70 L220,94Z"/><rect x="198" y="58" width="4" height="14"/></g>
<circle cx="200" cy="108" r="9" fill="{EMBER}" opacity=".9"/><path d="M200,108 L200,102 M200,108 L205,110" stroke="{SIL}" stroke-width="1.6"/>
<g fill="#FFB27A" opacity=".7"><rect x="110" y="170" width="8" height="12"/><rect x="126" y="170" width="8" height="12"/><rect x="266" y="170" width="8" height="12"/><rect x="282" y="170" width="8" height="12"/></g>
{cactus(520, 214, .6)}{cowboy(400, 212, .38)}'''


def scene_windmill():
    x, hy = 440, 92
    blades = ''.join(f'<path d="M{x},{hy} L{x+34*math.cos(math.radians(a-6)):.1f},{hy+34*math.sin(math.radians(a-6)):.1f} L{x+34*math.cos(math.radians(a+6)):.1f},{hy+34*math.sin(math.radians(a+6)):.1f}Z"/>' for a in range(0, 360, 30))
    braces = ''.join(f'<path d="M{x-20+i*3:.0f},{210-i*28} L{x+20-(i+1)*3:.0f},{210-(i+1)*28} M{x+20-i*3:.0f},{210-i*28} L{x-20+(i+1)*3:.0f},{210-(i+1)*28}" stroke="{SIL}" stroke-width="1.8"/>' for i in range(4))
    return f'''<g fill="{SIL}"><path d="M{x-22},210 L{x-5},{hy+6} L{x-1},{hy+6} L{x-16},210Z"/><path d="M{x+22},210 L{x+5},{hy+6} L{x+1},{hy+6} L{x+16},210Z"/>
<path d="M{x},{hy-3} L{x+52},{hy-12} L{x+56},{hy+4} L{x},{hy+4}Z"/>
<g>{blades}<circle cx="{x}" cy="{hy}" r="34" fill="none" stroke="{SIL}" stroke-width="2"/><circle cx="{x}" cy="{hy}" r="6"/>
<animateTransform attributeName="transform" type="rotate" from="0 {x} {hy}" to="360 {x} {hy}" dur="7s" repeatCount="indefinite"/></g>
<rect x="150" y="168" width="90" height="42"/><path d="M142,170 L195,138 L248,170Z"/><rect x="214" y="140" width="10" height="20"/></g>{braces}
<g fill="#FFB27A" opacity=".75"><rect x="166" y="180" width="12" height="12"/><rect x="208" y="180" width="12" height="12"/></g>
{cactus(80, 214, .45)}{cowboy(330, 212, .34)}'''


def scene_school():
    fence = ''.join(f'<rect x="{x}" y="190" width="4" height="22"/>' for x in range(340, 560, 22))
    return f'''<g fill="{SIL}"><rect x="186" y="150" width="128" height="60"/><path d="M176,152 L250,112 L324,152Z"/>
<rect x="238" y="80" width="5" height="40"/><rect x="257" y="80" width="5" height="40"/><path d="M232,82 L250,60 L268,82Z"/><rect x="236" y="104" width="28" height="5"/>
<path d="M244,96 Q250,84 256,96Z"/>{fence}<rect x="338" y="196" width="222" height="3"/><rect x="338" y="204" width="222" height="3"/></g>
<g fill="#FFB27A" opacity=".8"><rect x="200" y="166" width="16" height="20"/><rect x="284" y="166" width="16" height="20"/><rect x="242" y="168" width="16" height="42" opacity=".55"/></g>
{cactus(90, 214, .5)}{cowboy(470, 212, .34)}'''


def mission(fname, title, sub, date, chips, scene, sunx, seed):
    W, H = 600, 360
    fit('anton', title, 42, 560, ls=1, where='mission'); fit('fell', sub, 19, 560, where='mission')
    cx = 22; chip_svg = []
    for c in chips:
        w = tw('type', c, 12.5) + 24
        chip_svg.append(f'<rect x="{cx:.1f}" y="320" width="{w:.1f}" height="26" rx="13" fill="#1E0909" stroke="{MAROON2}"/>'
                        f'{T("type", cx + w/2, 337.5, c, 12.5, BONE2, "middle")}')
        cx += w + 8
    if cx > 580: WARN.append(f'OVERFLOW chips {fname} {cx:.0f}')
    dw = tw('type', date, 12.5, 1) + 26
    body = f'''<defs>{GRAIN}
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1A0303"/><stop offset=".55" stop-color="#7A0B0E"/><stop offset="1" stop-color="#E0392A"/></linearGradient>
<radialGradient id="glow" cx="{sunx}" cy="190" r="320" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#FF8A4C" stop-opacity=".9"/><stop offset="1" stop-color="#E3242B" stop-opacity="0"/></radialGradient>
<radialGradient id="sun" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFE7C9"/><stop offset=".6" stop-color="#FFB27A"/><stop offset="1" stop-color="#FF6A3D"/></radialGradient>
<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{INK}" stop-opacity="0"/><stop offset="1" stop-color="{INK}"/></linearGradient>
<clipPath id="c"><rect width="{W}" height="{H}" rx="16"/></clipPath></defs>
<g clip-path="url(#c)"><rect width="{W}" height="{H}" fill="{INK}"/>
<rect width="{W}" height="240" fill="url(#sky)"/><rect width="{W}" height="240" fill="url(#glow)"><animate attributeName="opacity" values=".8;1;.8" dur="6s" repeatCount="indefinite"/></rect>
<circle cx="{sunx}" cy="182" r="46" fill="url(#sun)"/><ellipse cx="{sunx}" cy="170" rx="90" ry="2.5" fill="#7A0B0E" opacity=".7"/>
{bird(sunx - 140, 60, 26, 13, -seed, .7)}
<path d="{mesa_path(W, 0, seed, 186, 196, 240)}" fill="#6A0C0E"/>
<path d="M0,212 Q150,204 300,210 T600,206 L600,240 L0,240Z" fill="{SIL}"/>
{scene}
<rect y="150" width="{W}" height="92" fill="url(#fade)"/><rect y="240" width="{W}" height="{H-240}" fill="{INK}"/>
<rect width="{W}" height="{H}" filter="url(#grain)"/>
<rect x="18" y="18" width="{tw('type', 'MISSION COMPLETE', 13, 1) + 46:.1f}" height="30" rx="6" fill="{BLOOD}"/>{diamond(34, 33, 5, BONE)}{T('type', 46, 38, 'MISSION COMPLETE', 13, BONE, ls=1)}
<rect x="{W-18-dw:.1f}" y="18" width="{dw:.1f}" height="30" rx="6" fill="#000" fill-opacity=".55" stroke="{MAROON2}"/>
{T('type', W-18-dw/2, 38, date, 12.5, BONE2, 'middle', 1)}
{T('anton', 22, 280, title, 42, BONE, ls=1)}
{T('fell', 22, 308, sub, 19, RED)}
{''.join(chip_svg)}</g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="{MAROON2}"/>'''
    svg(fname, W, H, body, '', f'{title}: {sub}', f'{title}. {sub}. {date}. ' + '; '.join(chips))


# ══════════════════════════════════════════════════════════════════════════
# 7. BOUNTIES CLAIMED
# ══════════════════════════════════════════════════════════════════════════
def bounties():
    rows = [('1ST PLACE', 'AgentsFest National Hackathon', 'National level · hosted by Amity University, Noida'),
            ('TOP 200 / 15,000', 'Google Prompt Wars Hackathon', 'Ranked 200th of 15,000 participants in Round 1'),
            ('2ND RUNNER-UP', 'HackStorm Hackathon', 'AgentRoute AI · multi-agent shipment risk prediction'),
            ('WINNER', 'SERBOT Competition', 'Smart Agriculture Service Robot · SRM IST'),
            ('WINNER', 'Earthquake Prediction & Simulation', 'AI/ML + IoT project competition · SRM IST')]
    W = 1200; rh = 74; H = 24 + len(rows) * (rh + 10) + 10
    out = []; css = []
    for i, (rank, title, det) in enumerate(rows):
        y = 20 + i * (rh + 10)
        fit('anton', rank, 26, 220, ls=1, where='bounty'); fit('fell', title, 23, 640, where='bounty'); fit('type', det, 13.5, 640, where='bounty')
        css.append(f'.s{i}{{animation-delay:{0.6+i*0.25:.2f}s}}')
        out.append(f'''<rect x="10" y="{y}" width="1180" height="{rh}" rx="10" fill="{'#140808' if i%2==0 else '#100606'}" stroke="{MAROON}"/>
<rect x="10" y="{y}" width="4" height="{rh}" rx="2" fill="{RED}"/>
{star(56, y+rh/2, 20)}
{T('anton', 92, y+rh/2+10, rank, 26, RED, ls=1)}
<line x1="320" y1="{y+16}" x2="320" y2="{y+rh-16}" stroke="{MAROON2}"/>
{T('fell', 344, y+33, title, 23, BONE)}{T('type', 345, y+56, det, 13.5, DUST)}
<g transform="rotate(-6 1086 {y+rh/2})"><g class="st s{i}"><rect x="1022" y="{y+rh/2-17}" width="128" height="34" rx="3" fill="none" stroke="{RED}" stroke-width="2.5"/>
{T('rye', 1086, y+rh/2+7, 'CLAIMED', 19, RED, 'middle', 3)}</g></g>''')
    body = f'<defs>{GRAIN}</defs>' + ''.join(out)
    css = ('.st{opacity:0;transform-box:fill-box;transform-origin:center;animation:slam .45s cubic-bezier(.2,.9,.3,1.2) forwards}'
           '@keyframes slam{0%{opacity:0;transform:scale(2.2)}70%{opacity:1;transform:scale(.95)}100%{opacity:.92;transform:scale(1)}}' + ''.join(css))
    svg('bounties.svg', W, H, body, css, 'Bounties claimed',
        '; '.join(f'{r}: {t} ({d})' for r, t, d in rows))


# ══════════════════════════════════════════════════════════════════════════
# 8. FOOTER
# ══════════════════════════════════════════════════════════════════════════
def footer():
    W, H = 1200, 250
    t1 = 'UNTIL NEXT TIME, PARTNER.'
    t2 = 'Software should be trusted, not just deployed.'
    fit('anton', t1, 44, 900, ls=3, where='footer')
    body = f'''<defs>{GRAIN}
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{INK}"/><stop offset=".55" stop-color="#5A0909"/><stop offset="1" stop-color="#D2352A"/></linearGradient>
<radialGradient id="glow" cx="600" cy="230" r="420" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#FF8A4C" stop-opacity=".85"/><stop offset="1" stop-color="#E3242B" stop-opacity="0"/></radialGradient>
<radialGradient id="sun" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFE7C9"/><stop offset=".6" stop-color="#FFB27A"/><stop offset="1" stop-color="#FF6A3D"/></radialGradient>
<clipPath id="c"><rect width="{W}" height="{H}" rx="18"/></clipPath></defs>
<g clip-path="url(#c)"><rect width="{W}" height="{H}" fill="url(#sky)"/><rect width="{W}" height="{H}" fill="url(#glow)"/>
<circle cx="600" cy="232" r="70" fill="url(#sun)"/><ellipse cx="600" cy="205" rx="140" ry="2.5" fill="#7A0B0E" opacity=".7"/>
<path d="{mesa_path(W, 0, 44, 214, 222, H)}" fill="#6A0C0E"/>
<path d="M0,232 Q300,224 600,230 T1200,228 L1200,{H} L0,{H}Z" fill="{SIL}"/>
{pole(180, 234, 64)}{pole(330, 232, 56)}{wire(180, 176, 330, 182, 8)}{wire(0, 172, 180, 176, 8)}{wire(330, 182, 470, 196, 8)}
{cactus(980, 236, .55)}{cowboy(820, 232, .5)}
{bird(400, 70, 30, 15, 0, .7)}{bird(860, 90, 24, 12, -4, .6)}
{dust(10, 0, W, 150, 245, 9)}
<rect width="{W}" height="{H}" filter="url(#grain)"/>
{T('anton', 600, 92, t1, 44, BONE, 'middle', 3)}
{T('type', 600, 126, t2, 16, BONE2, 'middle', 1)}</g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="18" fill="none" stroke="{MAROON2}"/>'''
    svg('footer.svg', W, H, body, '', 'Until next time, partner', t2)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    hero()
    for f, n, t, s in [('ch1-outlaw.svg', 'CHAPTER I', 'THE OUTLAW', 'WHO I AM'),
                       ('ch2-story.svg', 'CHAPTER II', 'THE STORY SO FAR', 'WHERE I HAVE RIDDEN'),
                       ('ch3-arsenal.svg', 'CHAPTER III', 'THE ARSENAL', 'WHAT I CARRY'),
                       ('ch4-missions.svg', 'CHAPTER IV', 'MISSIONS COMPLETED', 'WHAT I HAVE BUILT'),
                       ('ch5-bounties.svg', 'CHAPTER V', 'BOUNTIES CLAIMED', 'WHAT I HAVE WON'),
                       ('ch6-ledger.svg', 'CHAPTER VI', 'THE LEDGER', 'THE NUMBERS DO NOT LIE'),
                       ('ch7-epilogue.svg', 'EPILOGUE', 'RIDE WITH ME', 'WHERE TO FIND ME')]:
        chapter(f, n, t, s)
    wanted(); stats_panel(); story(); bounties(); footer()
    mission('mission-sentinel.svg', 'SENTINEL AI', 'Multi-Provider Agentic Intelligence Platform', 'JUL – AUG 2026',
            ['75K LINES', '229 ENDPOINTS', '12 OAUTH PROVIDERS', '900+ TESTS'], scene_watchtower(), 140, 4)
    mission('mission-verdict.svg', 'VERDICT', 'Pre-Deployment Code Verification Tool', 'JUL 2026',
            ['85% PRECISION', 'DOCKER SANDBOXES', '5 PARALLEL JOBS', '0 DROPPED'], scene_courthouse(), 470, 8)
    mission('mission-growthos.svg', 'GROWTHOS', 'AI-Powered Learning Platform · growth-os.tech', 'JUN 2026',
            ['LIVE', 'LLM SKILL-GAP MAPPING', 'SM-2 REPETITION', '5 CONTAINERS'], scene_windmill(), 150, 12)
    mission('mission-school.svg', 'SCHOOL ERP', 'Full-Stack School Management System', 'MAR – DEC 2025',
            ['187 ROUTES', '700+ SQL QUERIES', '4 PORTALS', '250+ USERS'], scene_school(), 450, 16)
    print('\n'.join(sorted(set(WARN))) or 'no warnings')
