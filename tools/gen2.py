"""v2: photo-based Red Dead profile assets.

Photos are public domain / CC0 from Wikimedia Commons (see photos/raw/credits.tsv),
re-graded into a red/black duotone. Usage: python gen2.py <out_dir>
"""
import base64, io, math, os, random, sys
import numpy as np
from PIL import Image, ImageOps, ImageEnhance, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen as G  # helpers: T, svg, fit, tw, GRAIN, star, diamond, bird, palette
from gen import T, fit, tw, GRAIN, star, diamond, bird, INK, COAL, MAROON, MAROON2, BLOOD, RED, EMBER, BONE, BONE2, DUST

HERE = os.path.dirname(os.path.abspath(__file__))
PH = os.path.join(HERE, '..', 'photos')

# ── photo grading ─────────────────────────────────────────────────────────
PAL = {
    # deep blacks -> blood -> signal red -> hot highlight (no white: reads as red sky)
    'red': [(0, (5, 2, 2)), (.30, (38, 4, 6)), (.58, (140, 12, 20)), (.82, (222, 38, 36)), (1, (255, 112, 88))],
    # keeps a little pale highlight for faces / detail
    'blood': [(0, (5, 2, 2)), (.28, (36, 4, 6)), (.55, (138, 14, 22)), (.80, (220, 48, 42)), (.94, (246, 160, 140)), (1, (255, 226, 210))],
    # aged paper sepia for the wanted poster
    'sepia': [(0, (40, 20, 10)), (.5, (128, 92, 60)), (1, (233, 214, 178))],
}


def gradmap(g, stops):
    a = np.asarray(g, dtype=np.float32) / 255.0
    out = np.zeros(a.shape + (3,), np.float32)
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        m = (a >= p0) & (a <= p1)
        t = ((a - p0) / max(p1 - p0, 1e-6))[m][:, None]
        out[m] = np.array(c0) * (1 - t) + np.array(c1) * t
    return Image.fromarray(out.clip(0, 255).astype(np.uint8))


def photo(path, box, size, pal='blood', contrast=1.3, gamma=1.0, invert=False, cutoff=1, moon=None, flip=False, q=80):
    """box = (x0,y0,x1,y1) as fractions; size = output px (w,h). Returns data URI."""
    im = Image.open(os.path.join(PH, path)).convert('RGB')
    W, H = im.size
    x0, y0, x1, y1 = box
    im = im.crop((int(x0 * W), int(y0 * H), int(x1 * W), int(y1 * H)))
    im = ImageOps.fit(im, size, Image.LANCZOS)
    if flip: im = ImageOps.mirror(im)
    g = ImageOps.grayscale(im)
    if invert: g = ImageOps.invert(g)
    g = ImageOps.autocontrast(g, cutoff=cutoff)
    g = ImageEnhance.Contrast(g).enhance(contrast)
    if gamma != 1.0:
        g = g.point(lambda v: int(255 * (v / 255) ** gamma))
    if moon:  # paint a moon into the bright sky only (dark subject stays in front)
        mx, my, mr = moon
        a = np.asarray(g, np.float32) / 255
        yy, xx = np.mgrid[0:size[1], 0:size[0]]
        d = np.sqrt((xx - mx) ** 2 + (yy - my) ** 2)
        disc = np.clip((mr - d) / 3 + 0.5, 0, 1)
        halo = np.exp(-np.clip(d - mr, 0, None) / (mr * 0.9)) * 0.35
        sky = np.clip((a - 0.45) / 0.25, 0, 1)
        a = a * (1 - sky * 0.25) + sky * np.maximum(disc * 0.97, halo + a * 0.0)
        a = np.maximum(a * (1 - disc * sky), disc * sky * 0.97)
        g = Image.fromarray((a.clip(0, 1) * 255).astype(np.uint8))
    out = gradmap(g, PAL[pal])
    b = io.BytesIO(); out.save(b, 'JPEG', quality=q, optimize=True, progressive=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()


def img(uri, x, y, w, h, extra=''):
    return f'<image href="{uri}" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice" {extra}/>'


# ── icons (stroke/fill red, centred on cx,cy, ~44px) ──────────────────────
def icon(kind, cx, cy, s=1.0, col=RED):
    g = f'<g transform="translate({cx},{cy}) scale({s})" fill="none" stroke="{col}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">'
    if kind == 'hat':
        b = f'<path d="M-26,8 C-14,14 14,14 26,8" /><path d="M-24,7 C-20,2 -16,1 -14,2 L-12,-12 Q-6,-17 0,-13 Q6,-17 12,-12 L14,2 C16,1 20,2 24,7" fill="{col}" fill-opacity=".9"/>'
    elif kind == 'revolver':
        b = (f'<path d="M-12,-12 L2,-12 L2,-10 L26,-10 L26,-13 L28,-13 L28,-5 L2,-5 L2,0 L-4,0 L-7,1 L-11,1 Q-14,10 -15,19 Q-19,23 -24,20 Q-23,8 -16,-3 L-19,-9 L-16,-11Z" fill="{col}" stroke="none"/>'
             f'<path d="M-7,1 Q-7,8 -1,7 L1,1" stroke-width="2.2"/><path d="M-9,-9 H-1 M-9,-5 H-1" stroke="#140808" stroke-width="1.6"/>')
    elif kind == 'crosshair':
        b = '<circle r="16"/><circle r="5"/><path d="M0,-24 V-10 M0,10 V24 M-24,0 H-10 M10,0 H24"/>'
    elif kind == 'fire':
        b = (f'<path d="M0,-22 C8,-12 14,-6 10,4 C8,10 4,12 0,12 C-4,12 -9,9 -10,3 C-12,-5 -4,-8 -4,-14 C0,-10 2,-8 0,-22Z" fill="{col}" fill-opacity=".9"/>'
             '<path d="M-20,20 L20,10 M-20,10 L20,20"/>')
    elif kind == 'star':
        return star(cx, cy, 20 * s, col)
    elif kind == 'horseshoe':
        b = '<path d="M-14,18 L-16,4 C-18,-14 -8,-20 0,-20 C8,-20 18,-14 16,4 L14,18"/><path d="M-9,16 L-10,4 C-11,-8 -5,-12 0,-12 C5,-12 11,-8 10,4 L9,16"/>'
    elif kind == 'cards':
        b = '<rect x="-16" y="-18" width="20" height="30" rx="3" transform="rotate(-12)"/><rect x="-4" y="-14" width="20" height="30" rx="3" transform="rotate(10)"/>'
    elif kind == 'lantern':
        b = '<path d="M-8,-20 H8 M0,-24 V-20 M-10,-16 H10 L8,12 H-8Z M-12,12 H12 V16 H-12Z"/><path d="M0,-8 C4,-3 4,2 0,5 C-4,2 -4,-3 0,-8Z" fill="#FFB27A" stroke="none"/>'
    elif kind == 'compass':
        b = '<circle r="20"/><path d="M0,-14 L5,0 L0,14 L-5,0Z"/><path d="M0,-14 L5,0 L-5,0Z" fill="' + col + '"/>'
    return g + b + '</g>'


def grain_rect(w, h, rx=0):
    return f'<rect width="{w}" height="{h}" rx="{rx}" filter="url(#grain)"/>'


ROUGH = ('<filter id="speck" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="4"/>'
         '<feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  6 0 0 0 -3.9"/></filter>')


def rough_mask(w, h):
    return f'<mask id="rough"><rect width="{w}" height="{h}" fill="#fff"/><rect width="{w}" height="{h}" filter="url(#speck)"/></mask>'


def button(x, y, label, filled=True, w=None):
    tw_ = tw('anton', label, 15, 2)
    w = w or tw_ + 58
    rect = (f'<rect x="{x}" y="{y}" width="{w:.0f}" height="40" rx="2" fill="{BLOOD}"/>' if filled else
            f'<rect x="{x}" y="{y}" width="{w:.0f}" height="40" rx="2" fill="#000" fill-opacity=".35" stroke="{BONE}" stroke-opacity=".7"/>')
    arrow = (f'<path d="M{x+w-26},{y+14} L{x+w-20},{y+20} L{x+w-26},{y+26}" stroke="{BONE}" stroke-width="2" fill="none"/>' if filled else
             f'<path d="M{x+w-28},{y+14} L{x+w-18},{y+20} L{x+w-28},{y+26}Z" fill="{BONE}"/>')
    return rect + T('anton', x + 20, y + 26, label, 15, BONE, ls=2) + arrow


# ══════════════════════════════════════════════════════════════════════════
def hero():
    W, H = 1200, 580
    ph = photo('hi/00.jpg', (.10, .045, .93, .965), (760, 580), 'red', contrast=1.5, gamma=1.25)
    nav = ['HOME', 'STORY', 'ARSENAL', 'MISSIONS', 'BOUNTIES', 'LEDGER']
    nx = 230; navs = []
    for i, n in enumerate(nav):
        navs.append(T('anton', nx, 41, n, 14, RED if i == 0 else BONE, ls=2))
        if i == 0: navs.append(f'<rect x="{nx}" y="50" width="{tw("anton", n, 14, 2):.0f}" height="2" fill="{RED}"/>')
        nx += tw('anton', n, 14, 2) + 30
    for s in ('ANIMESH', 'GUPTA'): fit('anton', s, 118, 520, ls=2, where='hero')
    body = f'''<defs>{GRAIN}{ROUGH}{rough_mask(W, H)}
<linearGradient id="lf" x1="0" x2="1"><stop offset=".36" stop-color="{INK}"/><stop offset=".5" stop-color="{INK}" stop-opacity=".75"/><stop offset=".72" stop-color="{INK}" stop-opacity="0"/></linearGradient>
<linearGradient id="bf" x1="0" y1="0" x2="0" y2="1"><stop offset=".72" stop-color="{INK}" stop-opacity="0"/><stop offset="1" stop-color="{INK}"/></linearGradient>
<radialGradient id="bg" cx=".18" cy=".5" r=".55"><stop offset="0" stop-color="#5A0A0C" stop-opacity=".55"/><stop offset="1" stop-color="#5A0A0C" stop-opacity="0"/></radialGradient>
<radialGradient id="vig" cx=".6" cy=".5" r=".85"><stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".65"/></radialGradient>
<clipPath id="c"><rect width="{W}" height="{H}" rx="16"/></clipPath>
<filter id="sh"><feDropShadow dx="0" dy="3" stdDeviation="5" flood-color="#000" flood-opacity=".9"/></filter></defs>
<g clip-path="url(#c)">
<rect width="{W}" height="{H}" fill="{INK}"/>
{img(ph, 440, 0, 760, 580)}
<rect width="{W}" height="{H}" fill="url(#lf)"/><rect width="{W}" height="{H}" fill="url(#bg)"/><rect width="{W}" height="{H}" fill="url(#bf)"/>
{bird(1040, 120, 34, 15, 0, .8)}{bird(880, 88, 26, 12, -4, .65)}{bird(1120, 210, 22, 17, -8, .6)}
<rect width="{W}" height="{H}" fill="url(#vig)"/>{grain_rect(W, H)}
<rect width="{W}" height="66" fill="#000" fill-opacity=".62"/><line x1="0" y1="66" x2="{W}" y2="66" stroke="{BONE}" stroke-opacity=".12"/>
<g mask="url(#rough)">{T('anton', 34, 45, 'AG', 30, BONE, ls=1)}{T('anton', 76, 45, 'II', 30, RED)}</g>
<line x1="108" y1="20" x2="108" y2="48" stroke="{BONE}" stroke-opacity=".2"/>{T('type', 124, 40, 'anxmeshhh', 14, BONE2)}
{''.join(navs)}
<rect x="1018" y="20" width="150" height="28" rx="14" fill="none" stroke="{RED}"/>
<circle cx="1036" cy="34" r="4.5" fill="{RED}"><animate attributeName="opacity" values="1;.2;1" dur="1.6s" repeatCount="indefinite"/></circle>
{T('anton', 1048, 39, 'OPEN TO WORK', 13, BONE, ls=2)}
<g class="a1">{T('anton', 62, 140, 'ANXMESHHH PRESENTS', 15, RED, ls=3)}</g>
<g class="a2" filter="url(#sh)" mask="url(#rough)">{T('anton', 58, 254, 'ANIMESH', 118, BONE, ls=2)}{T('anton', 58, 368, 'GUPTA', 118, RED, ls=2)}</g>
<g class="a3"><line x1="62" y1="398" x2="232" y2="398" stroke="{RED}" stroke-width="1.5"/>{star(252, 398, 9)}<line x1="272" y1="398" x2="442" y2="398" stroke="{RED}" stroke-width="1.5"/>
{T('anton', 62, 444, 'CHENNAI, 2026.', 24, BONE, ls=1.5)}
{T('anton', 62, 474, 'THE ERA OF UNTESTED CODE IS OVER.', 20, BONE2, ls=1.5)}</g>
<g class="a4">{button(62, 502, 'VIEW MISSIONS')}{button(250, 502, 'HIRE ON SIGHT', False)}</g>
</g><rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="{MAROON2}"/>'''
    css = ('.a1,.a2,.a3,.a4{opacity:0;animation:rise .9s ease-out forwards}.a2{animation-delay:.15s}.a3{animation-delay:.4s}.a4{animation-delay:.6s}'
           '@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}')
    G.svg('hero.svg', W, H, body, css, 'Animesh Gupta, Software Engineer',
          'Animesh Gupta. Chennai, 2026. The era of untested code is over. Software Engineer, backend and AI/LLM systems, open to work.')


# ══════════════════════════════════════════════════════════════════════════
def features():
    W, H = 1200, 340
    tiles = [
        ('revolver', 'BACKEND SYSTEMS', ['Scalable, high-performance', 'services with Python, SQL', 'and REST APIs.'], 'DJANGO · FASTAPI · MYSQL',
         photo('raw/09.jpg', (.06, .12, .94, .9), (296, 340), 'red', 1.5)),
        ('crosshair', 'AGENTIC AI', ['LLMs that propose.', 'Deterministic systems', 'that verify and execute.'], 'LLM · AGENTS · SANDBOXES',
         photo('raw/13.jpg', (.08, .1, .62, .92), (296, 340), 'red', 1.3)),
        ('fire', 'DEVOPS & CLOUD', ['Containers, orchestration', 'and CI/CD that ship', 'reliably to production.'], 'DOCKER · K8S · ACTIONS',
         photo('raw/04.jpg', (.18, .2, .62, .95), (296, 340), 'red', 1.35)),
        ('star', 'FULL-STACK PRODUCTS', ['7+ client builds through', 'Webnify, owned from spec', 'to deployment.'], 'REACT · DRF · NGINX',
         photo('raw/08.jpg', (.30, .30, .66, .92), (296, 340), 'red', 1.35)),
    ]
    out = []
    for i, (ic, title, lines, tag, uri) in enumerate(tiles):
        x = i * 301; cx = x + 148
        fit('anton', title, 24, 270, ls=1.5, where='feat'); fit('anton', tag, 13, 270, ls=1.5, where='feat')
        for l in lines: fit('type', l, 14.5, 270, where='feat')
        out.append(f'''<g clip-path="url(#t{i})">{img(uri, x, 0, 298, H)}<rect x="{x}" width="298" height="{H}" fill="url(#dk)"/></g>
<rect x="{x+.5}" y=".5" width="297" height="{H-1}" rx="10" fill="none" stroke="{BONE}" stroke-opacity=".14"/>
<g class="f f{i}">{icon(ic, cx, 92, 1.15)}
{T('anton', cx, 166, title, 24, BONE, 'middle', 1.5)}
{''.join(T('type', cx, 200 + j * 22, l, 14.5, BONE2, 'middle') for j, l in enumerate(lines))}
{T('anton', cx, 300, tag, 13, RED, 'middle', 1.5)}<path d="M{cx-70},314 H{cx+70}" stroke="{RED}" stroke-opacity=".5"/></g>''')
    clips = ''.join(f'<clipPath id="t{i}"><rect x="{i*301}" width="298" height="{H}" rx="10"/></clipPath>' for i in range(4))
    body = f'''<defs>{GRAIN}{clips}<linearGradient id="dk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity=".55"/><stop offset=".45" stop-color="#000" stop-opacity=".72"/><stop offset="1" stop-color="#000" stop-opacity=".9"/></linearGradient></defs>
{''.join(out)}{grain_rect(W, H, 10)}'''
    css = '.f{opacity:0;animation:up .8s ease-out forwards}' + ''.join(f'.f{i}{{animation-delay:{.1+i*.15:.2f}s}}' for i in range(4)) + \
          '@keyframes up{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}'
    G.svg('features.svg', W, H, body, css, 'What I do',
          'Backend systems; agentic AI; DevOps and cloud; full-stack products.')


# ══════════════════════════════════════════════════════════════════════════
def story_panel():
    W, H = 1200, 540
    ph = photo('hi/00.jpg', (.255, .085, .675, .64), (620, 540), 'blood', 1.45, gamma=1.25)
    para = ['Software Engineer across the full SDLC, from',
            'development and testing to deployment, building',
            'scalable, high-performance backends with Python,',
            'SQL and REST APIs. Experienced in containers,',
            'orchestration, CI/CD, DevOps and the cloud.',
            'Focused on AI/LLM engineering and agentic',
            'systems, shipped reliably to production.']
    for p in para: fit('type', p, 16, 520, where='storypanel')
    stars = ''.join(f'<g opacity="{o}">{star(x, y, r, RED)}</g>' for x, y, r, o in [(1090, 120, 120, .10), (720, 470, 70, .08), (1160, 470, 50, .1)])
    body = f'''<defs>{GRAIN}{ROUGH}{rough_mask(W, H)}<clipPath id="c"><rect width="{W}" height="{H}" rx="16"/></clipPath>
<linearGradient id="lf" x1="0" x2="1"><stop offset="0" stop-color="{INK}"/><stop offset=".35" stop-color="{INK}" stop-opacity=".2"/><stop offset="1" stop-color="{INK}" stop-opacity="0"/></linearGradient>
<radialGradient id="bg" cx=".1" cy=".9" r=".9"><stop offset="0" stop-color="#3A0607"/><stop offset="1" stop-color="{INK}"/></radialGradient></defs>
<g clip-path="url(#c)"><rect width="{W}" height="{H}" fill="url(#bg)"/>
{img(ph, 580, 0, 620, H)}<rect x="580" width="620" height="{H}" fill="url(#lf)"/>{stars}{grain_rect(W, H)}
{T('anton', 62, 86, 'THE STORY', 16, RED, ls=3)}
<g mask="url(#rough)">{T('anton', 58, 156, 'BUILD.', 64, BONE, ls=2)}{T('anton', 58, 222, 'TEST.', 64, BONE, ls=2)}{T('anton', 58, 288, 'SHIP.', 64, RED, ls=2)}</g>
{''.join(T('type', 62, 330 + i * 23, p, 16, BONE2) for i, p in enumerate(para))}
{button(62, 486, 'EXPLORE THE MISSIONS')}</g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="{MAROON2}"/>'''
    G.svg('story.svg', W, H, body, '', 'The story: build, test, ship', ' '.join(para))


# ══════════════════════════════════════════════════════════════════════════
def strip():
    W, H = 1200, 118
    cells = [('revolver', 'LANGUAGES', ['Python · SQL · TypeScript', 'JavaScript · C++ · C']),
             ('horseshoe', 'BACKEND', ['Django · DRF · FastAPI', 'Flask · Node · React']),
             ('cards', 'DATA', ['MySQL · PostgreSQL', 'Redis · Supabase']),
             ('crosshair', 'DEVOPS & CLOUD', ['Docker · Kubernetes', 'Actions · Nginx · Celery']),
             ('lantern', 'AI / ML', ['LLMs · Agentic AI', 'TensorFlow · sklearn'])]
    out = []
    for i, (ic, t, ls) in enumerate(cells):
        x = i * 240
        fit('anton', t, 15, 165, ls=1.5, where='strip')
        for l in ls: fit('type', l, 12.5, 168, where='strip')
        out.append(icon(ic, x + 40, 59, .9) + T('anton', x + 70, 46, t, 15, BONE, ls=1.5) +
                   ''.join(T('type', x + 70, 70 + j * 19, l, 12.5, BONE2) for j, l in enumerate(ls)))
        if i: out.append(f'<line x1="{x}" y1="24" x2="{x}" y2="{H-24}" stroke="{BONE}" stroke-opacity=".15"/>')
    body = (f'<defs>{GRAIN}</defs><rect width="{W}" height="{H}" rx="12" fill="{INK}"/>{grain_rect(W, H, 12)}'
            f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{MAROON2}"/>' + ''.join(out))
    G.svg('arsenal.svg', W, H, body, '', 'The arsenal',
          '; '.join(f'{t}: {" · ".join(l)}' for _, t, l in cells))


# ══════════════════════════════════════════════════════════════════════════
def header(fname, kicker, title, right):
    W, H = 1200, 80
    tw_ = fit('anton', title, 30, 700, ls=1.5, where='hdr')
    body = (f'<defs>{GRAIN}</defs><rect width="{W}" height="{H}" rx="10" fill="{INK}"/>{grain_rect(W, H, 10)}'
            f'{T("anton", 24, 29, kicker, 15, RED, ls=3)}{T("anton", 22, 63, title, 32, BONE, ls=1.5)}'
            f'<line x1="{40+tw_:.0f}" y1="49" x2="{1176 - tw("anton", right, 15, 2) - 40:.0f}" y2="49" stroke="{BONE}" stroke-opacity=".15"/>'
            f'{T("anton", 1150, 55, right, 15, RED, "end", 2)}<path d="M1162,44 L1168,49 L1162,54" stroke="{RED}" stroke-width="2" fill="none"/>')
    G.svg(fname, W, H, body, '', title, kicker)


# ══════════════════════════════════════════════════════════════════════════
def experience():
    W, H = 1200, 540
    ph = photo('raw/03.jpg', (.0, .18, 1, .78), (1200, 230), 'red', 1.35)
    jobs = [('JAN 2025 — PRESENT', 'FOUNDER & FULL-STACK DEV', 'Webnify', 'Chennai, Tamil Nadu',
             ['Full-stack apps & automation', '7+ client projects delivered'], True),
            ('MAR 2025 — DEC 2025', 'FULL-STACK DEVELOPER', 'VerrGroup', 'Chennai, Tamil Nadu',
             ['Django + MySQL apps to release', 'VPS deploys: Gunicorn + Nginx'], False),
            ('SEP 2025 — MAY 2026', 'BACKEND LEAD', 'Brain Mint Technologies', 'Chennai, Tamil Nadu',
             ['Architecture, schema & RBAC', 'Led 35+ devs · JWT REST APIs'], False)]
    oy = 196
    ties = ''.join(f'<rect x="{x}" y="{oy+56}" width="6" height="26" fill="#3A0E0E"/>' for x in range(16, 1190, 22))
    cards = []
    for i, (dates, role, co, loc, bullets, live) in enumerate(jobs):
        sx = 210 + i * 390; x = sx - 180
        fit('anton', role, 28, 320, ls=1, where='exp'); fit('fell', co, 25, 320, where='exp')
        for b in bullets: fit('type', b, 16, 306, where='exp')
        pulse = (f'<circle cx="{sx}" cy="{oy+70}" r="14" fill="none" stroke="{RED}" stroke-width="2"><animate attributeName="r" values="14;26" dur="1.8s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values=".9;0" dur="1.8s" repeatCount="indefinite"/></circle>') if live else ''
        cards.append(f'''{pulse}<circle cx="{sx}" cy="{oy+70}" r="13" fill="{INK}" stroke="{RED}" stroke-width="3"/><circle cx="{sx}" cy="{oy+70}" r="5" fill="{RED if live else BONE2}"/>
{T('type', sx, oy+36, dates, 16, RED if live else BONE, 'middle', 1)}
<line x1="{sx}" y1="{oy+84}" x2="{sx}" y2="{oy+112}" stroke="{RED}" stroke-dasharray="3 3"/>
<rect x="{x}" y="{oy+112}" width="360" height="208" rx="12" fill="#140808" stroke="{MAROON2}"/><rect x="{x}" y="{oy+112}" width="360" height="4" rx="2" fill="{RED}"/>
{T('anton', x+22, oy+156, role, 28, BONE, ls=1)}{T('fell', x+22, oy+186, co, 25, RED)}{T('type', x+22, oy+208, loc, 14, DUST, ls=1)}
<line x1="{x+22}" y1="{oy+220}" x2="{x+338}" y2="{oy+220}" stroke="{MAROON2}"/>
{''.join(diamond(x+27, oy+249+j*32-5, 4.5) + T('type', x+40, oy+249+j*32, b, 16, BONE2) for j, b in enumerate(bullets))}''')
    body = f'''<defs>{GRAIN}{ROUGH}{rough_mask(W, H)}<clipPath id="c"><rect width="{W}" height="{H}" rx="16"/></clipPath>
<linearGradient id="bf" x1="0" y1="0" x2="0" y2="1"><stop offset=".35" stop-color="{INK}" stop-opacity="0"/><stop offset="1" stop-color="{INK}"/></linearGradient>
<linearGradient id="lf" x1="0" x2="1"><stop offset="0" stop-color="{INK}" stop-opacity=".9"/><stop offset=".5" stop-color="{INK}" stop-opacity=".1"/></linearGradient></defs>
<g clip-path="url(#c)"><rect width="{W}" height="{H}" fill="{INK}"/>{img(ph, 0, 0, W, 230)}<rect width="{W}" height="231" fill="url(#bf)"/><rect width="{W}" height="230" fill="url(#lf)"/>
{grain_rect(W, H)}
{T('anton', 40, 70, 'EXPERIENCE', 14, RED, ls=3)}
<g mask="url(#rough)">{T('anton', 38, 124, 'THE RIDE SO FAR', 54, BONE, ls=2)}</g>
{T('type', 40, 156, 'Three stations. One line: ship it, and ship it right.', 15, BONE2)}
{ties}<rect x="10" y="{oy+62}" width="1180" height="3" fill="#5A1414"/><rect x="10" y="{oy+74}" width="1180" height="3" fill="#5A1414"/>
{''.join(cards)}</g><rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="{MAROON2}"/>'''
    G.svg('experience.svg', W, H, body, '', 'The ride so far',
          'Founder & Full-Stack Developer at Webnify (Jan 2025 to present); Full-Stack Developer at VerrGroup (Mar to Dec 2025); Backend Lead at Brain Mint Technologies (Sep 2025 to May 2026).')


# ══════════════════════════════════════════════════════════════════════════
def mission(fname, title, sub, date, chips, uri, kind):
    W, H = 600, 410; IH = 270
    fit('anton', title, 40, 560, ls=1, where='mission'); fit('fell', sub, 21, 560, where='mission')
    cx = 22; cs = []
    for c in chips:
        w = tw('type', c, 15) + 20
        cs.append(f'<rect x="{cx:.1f}" y="364" width="{w:.1f}" height="30" rx="15" fill="#1E0909" stroke="{MAROON2}"/>{T("type", cx + w/2, 384, c, 15, BONE2, "middle")}')
        cx += w + 7
    if cx > 580: G.WARN.append(f'OVERFLOW chips {fname} {cx:.0f}')
    dw = tw('type', date, 15, 1) + 26; bw = tw('anton', kind, 13, 2) + 40
    body = f'''<defs>{GRAIN}<clipPath id="c"><rect width="{W}" height="{H}" rx="14"/></clipPath>
<linearGradient id="bf" x1="0" y1="0" x2="0" y2="1"><stop offset=".55" stop-color="{INK}" stop-opacity="0"/><stop offset="1" stop-color="{INK}"/></linearGradient>
<linearGradient id="tf" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity=".55"/><stop offset=".3" stop-color="#000" stop-opacity="0"/></linearGradient></defs>
<g clip-path="url(#c)"><rect width="{W}" height="{H}" fill="{INK}"/>{img(uri, 0, 0, W, IH)}<rect width="{W}" height="{IH+1}" fill="url(#bf)"/><rect width="{W}" height="{IH}" fill="url(#tf)"/>
{grain_rect(W, H)}
<rect x="18" y="18" width="{bw:.0f}" height="28" rx="2" fill="{BLOOD}"/>{diamond(32, 32, 4.5, BONE)}{T('anton', 44, 38, kind, 13, BONE, ls=2)}
<rect x="{W-18-dw:.1f}" y="18" width="{dw:.1f}" height="28" rx="2" fill="#000" fill-opacity=".6" stroke="{BONE}" stroke-opacity=".25"/>{T('type', W-18-dw/2, 37, date, 15, BONE, 'middle', 1)}
<circle cx="{W/2}" cy="{IH/2-10}" r="30" fill="#000" fill-opacity=".45" stroke="{BONE}" stroke-opacity=".8" stroke-width="2"/><path d="M{W/2-8},{IH/2-24} L{W/2+14},{IH/2-10} L{W/2-8},{IH/2+4}Z" fill="{BONE}"/>
{T('anton', 22, 316, title, 40, BONE, ls=1)}{T('fell', 22, 346, sub, 21, RED)}{''.join(cs)}</g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="14" fill="none" stroke="{MAROON2}"/>'''
    G.svg(fname, W, H, body, '', f'{title}: {sub}', f'{title}. {sub}. {date}. ' + '; '.join(chips))


# ══════════════════════════════════════════════════════════════════════════
def footer():
    W, H = 1200, 330
    ph = photo('raw/05.jpg', (0, .05, .985, .95), (1200, 170), 'red', 1.4)
    cols = [('CONTACT', ['guptaanimesh020@gmail.com', 'in/animesh-gupta2005', 'github.com/anxmeshhh']),
            ('BUILDING', ['Webnify · founder', 'GrowthOS · growth-os.tech', 'Sentinel AI · agentic SaaS']),
            ('CURRENTLY', ['B.Tech CSE (AI & ML)', 'SRM IST · class of 2027', 'Chennai, India'])]
    out = []
    for i, (h, ls) in enumerate(cols):
        x = 420 + i * 255
        out.append(T('anton', x, 214, h, 15, BONE, ls=2))
        for j, l in enumerate(ls):
            fit('type', l, 13.5, 235, where='footer'); out.append(T('type', x, 244 + j * 22, l, 13.5, BONE2))
    body = f'''<defs>{GRAIN}{ROUGH}{rough_mask(W, H)}<clipPath id="c"><rect width="{W}" height="{H}" rx="16"/></clipPath>
<linearGradient id="bf" x1="0" y1="0" x2="0" y2="1"><stop offset=".25" stop-color="{INK}" stop-opacity="0"/><stop offset="1" stop-color="{INK}"/></linearGradient></defs>
<g clip-path="url(#c)"><rect width="{W}" height="{H}" fill="{INK}"/>{img(ph, 0, 0, W, 170)}<rect width="{W}" height="171" fill="url(#bf)"/>
{bird(300, 60, 30, 14, 0, .7)}{bird(820, 46, 24, 12, -5, .6)}
{grain_rect(W, H)}
{T('anton', 600, 92, 'UNTIL NEXT TIME, PARTNER.', 40, BONE, 'middle', 3)}
<line x1="40" y1="176" x2="1160" y2="176" stroke="{BONE}" stroke-opacity=".14"/>
<g mask="url(#rough)">{T('anton', 40, 236, 'ANIMESH', 46, BONE, ls=1.5)}{T('anton', 40, 286, 'GUPTA', 46, RED, ls=1.5)}</g>
{''.join(out)}
{T('type', 40, 316, '© 2026 Animesh Gupta · Software should be trusted, not just deployed.', 12, DUST)}</g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="{MAROON2}"/>'''
    G.svg('footer.svg', W, H, body, '', 'Until next time, partner',
          'Contact guptaanimesh020@gmail.com, LinkedIn animesh-gupta2005, GitHub anxmeshhh. Software should be trusted, not just deployed.')


# ══════════════════════════════════════════════════════════════════════════
def wanted_portrait():
    """Sepia crop of the GitHub avatar for the wanted poster (returns data URI)."""
    return photo('avatar.jpg', (.22, .26, .72, .70), (232, 200), 'sepia', 1.25, gamma=.95)


if __name__ == '__main__':
    hero(); features(); story_panel(); strip(); experience(); footer()
    header('hdr-arsenal.svg', 'CHAPTER III', 'THE ARSENAL', 'WHAT I CARRY')
    header('hdr-missions.svg', 'CHAPTER IV', 'LATEST MISSIONS', 'SOLO-BUILT & SHIPPED')
    header('hdr-bounties.svg', 'CHAPTER V', 'BOUNTIES CLAIMED', 'HACKATHONS & CONTESTS')
    header('hdr-ledger.svg', 'CHAPTER VI', 'THE LEDGER', 'THE NUMBERS DO NOT LIE')
    header('hdr-outlaw.svg', 'CHAPTER I', 'THE OUTLAW', 'QUICK FACTS')
    mission('mission-sentinel.svg', 'SENTINEL AI', 'Multi-Provider Agentic Intelligence Platform', 'JUL – AUG 2026',
            ['75K LINES', '229 ENDPOINTS', '12 OAUTH PROVIDERS', '900+ TESTS'],
            photo('raw/10.jpg', (0, .08, 1, .62), (600, 270), 'red', 1.3), 'AGENTIC SAAS')
    mission('mission-verdict.svg', 'VERDICT', 'Pre-Deployment Code Verification Tool', 'JUL 2026',
            ['85% PRECISION', 'DOCKER SANDBOX', '5 PARALLEL JOBS', '0 DROPPED'],
            photo('raw/06.jpg', (.1, .19, .92, .46), (600, 270), 'red', 1.1, gamma=.9), 'DEV TOOLING')
    mission('mission-growthos.svg', 'GROWTHOS', 'AI-Powered Learning Platform · growth-os.tech', 'JUN 2026',
            ['LIVE', 'LLM SKILL-GAP MAPPING', 'SM-2 REPETITION', '5 CONTAINERS'],
            photo('raw/02.jpg', (.18, .23, .80, .77), (600, 270), 'red', 1.3), 'LIVE PLATFORM')
    mission('mission-school.svg', 'SCHOOL ERP', 'Full-Stack School Management System', 'MAR – DEC 2025',
            ['187 ROUTES', '700+ SQL QUERIES', '4 PORTALS', '250+ USERS'],
            photo('raw/15.jpg', (.03, .06, .97, .70), (600, 270), 'blood', 1.2), 'IN PRODUCTION')
    print('\n'.join(sorted(set(G.WARN))) or 'no warnings')

if __name__ == '__main__':
    G.wanted(wanted_portrait())
