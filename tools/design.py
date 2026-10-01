"""UImiz Revamped for HIDIZS AP80 Pro Max (360x640) - Ulmiz-style now-playing screen, pastel purple accent.
Generates all bitmaps procedurally (4x supersampled) from the layout constants below."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 360, 640
SS = 4                       # supersampling factor
ACCENT = (197, 142, 230)     # pastel purple  #c58ee6
ACCENT_HEX = 'c58ee6'
OFF = (104, 90, 120)         # inactive icon (muted purple-grey)
BG = (33, 26, 41)            # dark purple base  #211a29
# palette (dark purple Ulmiz)
P = dict(
    tab_ring=((82, 70, 98), (70, 59, 86)), tab_in=(27, 21, 34),
    album=((44, 36, 54), (54, 45, 66)), year=((178, 162, 196), (206, 194, 220)),
    main_ring=((176, 162, 192), (152, 138, 170)),
    artist=((35, 28, 45), (43, 35, 55)), title=((234, 228, 241), (247, 244, 251)),
    track=(22, 17, 28), circle=((38, 30, 48), (45, 36, 57)),
    light_btn=((228, 220, 238), (196, 185, 212)), icon=(36, 27, 46),
)
TEXT_HEX = dict(status='ddd3e8', album='d9cfe4', year='2a2135', artist='f6f1fb', title='231b2c', times='ddd3e8')

# ------------------------------------------------------------ layout (screen px)
L = dict(
    art=(30, 46, 300, 300),
    tab=(20, 354, 340, 402),            # outer box of the album/year container (x0,y0,x1,y1)
    album=(25, 359, 261, 391),
    year=(266, 359, 335, 391),
    main=(8, 393, 352, 493),            # outer box of artist/title container
    artist=(13, 398, 347, 440),
    title=(13, 444, 347, 488),
    track=(17, 507, 343, 519),          # progress bar (x0,y0,x1,y1) -> %pb
    shuffle=(8, 571, 60, 623),
    prev=(67, 570, 131, 624),
    play=(138, 570, 222, 624),
    next=(229, 570, 293, 624),
    repeat=(300, 571, 352, 623),
)
UBU = '/home/user/scratch/Ubuntu-%s.ttf'


def S(v):  # scale coords to supersampled space
    return [int(round(c * SS)) for c in v]


def rr_mask(size, box, r):
    m = Image.new('L', size, 0)
    ImageDraw.Draw(m).rounded_rectangle(S(box), radius=r * SS, fill=255)
    return m


def solid(size, col):
    return Image.new('RGB', size, col)


def vgrad(size, box, top, bot):
    """full-size image with a vertical gradient inside box"""
    w, h = size
    x0, y0, x1, y1 = S(box)
    arr = np.zeros((h, w, 3), np.float32)
    t = np.clip((np.arange(h) - y0) / max(1, (y1 - y0)), 0, 1)[:, None]
    arr[:] = (np.array(top)[None, :] * (1 - t) + np.array(bot)[None, :] * t)[:, None, :]
    return Image.fromarray(arr.astype(np.uint8))


def paste_mask(img, src, mask):
    img.paste(src, (0, 0), mask)


def shadow(img, mask, offset=(0, 0), blur=4, color=(8, 4, 14), strength=0.6, spread=0):
    m = mask
    if spread:
        m = m.filter(ImageFilter.MaxFilter(spread * SS * 2 + 1))
    m = m.filter(ImageFilter.GaussianBlur(blur * SS))
    m = Image.fromarray((np.array(m, np.float32) * strength).astype(np.uint8))
    sh = Image.new('L', img.size, 0)
    sh.paste(m, (offset[0] * SS, offset[1] * SS))
    img.paste(solid(img.size, color), (0, 0), sh)


def inner_shadow(img, mask, offset=(0, 2), blur=3, color=(8, 4, 14), strength=0.5):
    inv = Image.fromarray(255 - np.array(mask))
    shifted = Image.new('L', img.size, 255)
    shifted.paste(inv, (offset[0] * SS, offset[1] * SS))
    b = shifted.filter(ImageFilter.GaussianBlur(blur * SS))
    a = (np.array(b, np.float32) / 255) * (np.array(mask, np.float32) / 255) * strength
    img.paste(solid(img.size, color), (0, 0), Image.fromarray((a * 255).astype(np.uint8)))


def pill(img, box, fill_top, fill_bot, r, ishadow=None, outer=None):
    m = rr_mask(img.size, box, r)
    if outer:
        shadow(img, m, **outer)
    paste_mask(img, vgrad(img.size, box, fill_top, fill_bot), m)
    if ishadow:
        inner_shadow(img, m, **ishadow)
    return m


# ------------------------------------------------------------ icons (drawn on supersampled canvas)
def ic_prev(d, cx, cy, s, col):
    # |<< : bar + two triangles
    h = s * 0.62
    bw = s * 0.11
    x = cx - s * 0.5
    d.rectangle([x, cy - h / 2, x + bw, cy + h / 2], fill=col)
    tw = s * 0.42
    for i in range(2):
        tx = x + bw + s * 0.02 + i * tw
        d.polygon([(tx, cy), (tx + tw, cy - h / 2), (tx + tw, cy + h / 2)], fill=col)


def ic_next(d, cx, cy, s, col):
    h = s * 0.62
    bw = s * 0.11
    x = cx + s * 0.5
    d.rectangle([x - bw, cy - h / 2, x, cy + h / 2], fill=col)
    tw = s * 0.42
    for i in range(2):
        tx = x - bw - s * 0.02 - i * tw
        d.polygon([(tx, cy), (tx - tw, cy - h / 2), (tx - tw, cy + h / 2)], fill=col)


def ic_play(d, cx, cy, s, col):
    h = s * 0.70
    w = h * 0.88
    d.polygon([(cx - w * 0.42, cy - h / 2), (cx - w * 0.42, cy + h / 2), (cx + w * 0.58, cy)], fill=col)


def ic_pause(d, cx, cy, s, col):
    h = s * 0.66
    bw = s * 0.20
    g = s * 0.13
    d.rectangle([cx - g - bw, cy - h / 2, cx - g, cy + h / 2], fill=col)
    d.rectangle([cx + g, cy - h / 2, cx + g + bw, cy + h / 2], fill=col)


def ic_stop(d, cx, cy, s, col):
    a = s * 0.30
    d.rounded_rectangle([cx - a, cy - a, cx + a, cy + a], radius=s * 0.05, fill=col)


def ic_shuffle(d, cx, cy, s, col):
    lw = max(2, int(s * 0.10))
    x0, x1 = cx - s * 0.48, cx + s * 0.30
    yt, yb = cy - s * 0.26, cy + s * 0.26
    ah = s * 0.20
    # crossing paths (two S-curves made of segments)
    for (ya, yb_) in [(yt, yb), (yb, yt)]:
        pts = [(x0, ya), (x0 + s * 0.20, ya), (x1 - s * 0.20, yb_), (x1, yb_)]
        d.line(pts, fill=col, width=lw, joint='curve')
        d.polygon([(x1 + ah * 1.1, yb_), (x1 - ah * 0.2, yb_ - ah), (x1 - ah * 0.2, yb_ + ah)], fill=col)


def ic_repeat(d, cx, cy, s, col, badge=None, font=None, badge_fg=None):
    lw = max(2, int(s * 0.10))
    ah = s * 0.17
    if badge:
        cx -= s * 0.06; cy -= s * 0.04
    w, h = s * 0.80, s * 0.50
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    d.line([(x0, cy + h * 0.12), (x0, y0), (x1 - ah * 1.1, y0)], fill=col, width=lw, joint='curve')
    d.polygon([(x1 + ah * 0.35, y0), (x1 - ah * 1.2, y0 - ah), (x1 - ah * 1.2, y0 + ah)], fill=col)
    if badge:
        d.line([(x1 - s * 0.05, y1), (x0 + ah * 1.1, y1)], fill=col, width=lw)
    else:
        d.line([(x1, cy - h * 0.12), (x1, y1), (x0 + ah * 1.1, y1)], fill=col, width=lw, joint='curve')
    d.polygon([(x0 - ah * 0.35, y1), (x0 + ah * 1.2, y1 - ah), (x0 + ah * 1.2, y1 + ah)], fill=col)
    if badge:
        bh = s * 0.40
        bw = max(bh, font.getlength(badge) + s * 0.16)
        bx, by = cx + s * 0.40, cy + s * 0.30
        d.rounded_rectangle([bx - bw / 2 - lw * 0.8, by - bh / 2 - lw * 0.8, bx + bw / 2 + lw * 0.8, by + bh / 2 + lw * 0.8],
                            radius=bh / 2 + lw * 0.8, fill=0)
        d.rounded_rectangle([bx - bw / 2, by - bh / 2, bx + bw / 2, by + bh / 2], radius=bh / 2, fill=col)
        d.text((bx, by + s * 0.01), badge, font=font, fill=0, anchor='mm')


# ------------------------------------------------------------ build
def build_bg():
    size = (W * SS, H * SS)
    img = solid(size, BG)

    # --- info panel: album/year tab container
    tab = L['tab']
    shadow(img, rr_mask(size, tab, 13), offset=(0, 1), blur=3, strength=0.55)
    pill(img, tab, *P['tab_ring'], 13)                     # ring #636163 (also fills between the pills)
    # like the original Ulmiz: the album and year pills are rounded only at the top and run straight down
    # under the artist/title block, so the tab flows into the block below instead of floating above it
    under = L['main'][1] + 8
    for k, ish in (('album', 0.55), ('year', 0.35)):
        b = L[k]
        pill(img, (b[0], b[1], b[2], under), *P[k], 9, ishadow=dict(offset=(0, 2), blur=2, strength=ish))

    # --- main container (artist/title)
    mn = L['main']
    shadow(img, rr_mask(size, mn, 17), offset=(0, 2), blur=1.5, strength=0.6)
    pill(img, mn, *P['main_ring'], 17)                   # ring #adb2ad
    pill(img, L['artist'], *P['artist'], 13,
         ishadow=dict(offset=(0, 2), blur=2.5, strength=0.6))
    pill(img, L['title'], *P['title'], 13,
         ishadow=dict(offset=(0, 2), blur=3, strength=0.35))

    # --- progress track (rockbox draws the purple border + fill on top)
    x0, y0, x1, y1 = L['track']
    d = ImageDraw.Draw(img)
    d.rectangle(S((x0, y0, x1 - 1 + 1, y1 - 1 + 1)), fill=P['track'])

    # --- transport buttons
    for k in ('shuffle', 'repeat'):
        b = L[k]
        m = Image.new('L', size, 0)
        ImageDraw.Draw(m).ellipse(S(b), fill=255)
        shadow(img, m, offset=(0, 0), blur=3, strength=0.55, spread=1)
        paste_mask(img, vgrad(size, b, *P['circle']), m)
        inner_shadow(img, m, offset=(0, 2), blur=2, strength=0.45)
    for k in ('prev', 'next'):
        b = L[k]
        r = (b[3] - b[1]) / 2
        pill(img, b, *P['light_btn'], r,
             outer=dict(offset=(0, 2), blur=2.5, strength=0.65))
    # glowing purple play button
    b = L['play']
    r = (b[3] - b[1]) / 2
    gm = rr_mask(size, b, r)
    shadow(img, gm, offset=(0, 1), blur=10, color=ACCENT, strength=1.0, spread=3)
    shadow(img, gm, offset=(0, 0), blur=3, color=ACCENT, strength=0.6)
    pill(img, b, (208, 160, 238), (192, 136, 228), r)

    d = ImageDraw.Draw(img)
    ICON = P['icon']
    for k, fn in (('prev', ic_prev), ('next', ic_next)):
        b = L[k]
        fn(d, (b[0] + b[2]) / 2 * SS, (b[1] + b[3]) / 2 * SS, 24 * SS, ICON)

    # fine texture like the Ulmiz backdrop
    out = img.resize((W, H), Image.LANCZOS)
    a = np.array(out, np.float32)
    rng = np.random.default_rng(7)
    a += rng.normal(0, 1.6, a.shape[:2])[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def ic_history(d, cx, cy, s, col):
    lw = max(2, int(s * 0.12))
    r = s * 0.40
    d.arc([cx - r, cy - r, cx + r, cy + r], start=200, end=500, fill=col, width=lw)
    # arrow head at the open end (pointing counter-clockwise, upper-left)
    import math
    a = math.radians(200)
    ex, ey = cx + r * math.cos(a), cy + r * math.sin(a)
    ah = s * 0.20
    d.polygon([(ex - ah * 0.9, ey - ah * 0.2), (ex + ah * 0.8, ey - ah * 0.5), (ex + ah * 0.1, ey + ah * 1.0)], fill=col)
    # clock hands
    d.line([(cx, cy - r * 0.55), (cx, cy), (cx + r * 0.45, cy + r * 0.3)], fill=col, width=lw, joint='curve')


SBS_BTNS = dict(cancel=(38, 574, 98, 619), resume=(263, 574, 323, 619))


def build_sbs(buttons=True):
    size = (W * SS, H * SS)
    img = solid(size, BG)
    for k, fn in ((('cancel', ic_history), ('resume', ic_play)) if buttons else ()):
        b = SBS_BTNS[k]
        r = (b[3] - b[1]) / 2
        pill(img, b, *P['light_btn'], r, outer=dict(offset=(0, 2), blur=2.5, strength=0.7))
        d = ImageDraw.Draw(img)
        fn(d, (b[0] + b[2]) / 2 * SS + (1.5 * SS if k == 'resume' else 0), (b[1] + b[3]) / 2 * SS, 24 * SS, P['icon'])
    out = img.resize((W, H), Image.LANCZOS)
    a = np.array(out, np.float32)
    # soft vignette (darker edges) like the original menu backdrop
    yy, xx = np.mgrid[0:H, 0:W]
    v = 1 - 0.22 * (np.abs(xx - W / 2) / (W / 2)) ** 2.2 - 0.12 * (np.abs(yy - H / 2) / (H / 2)) ** 3
    a *= v[..., None]
    rng = np.random.default_rng(11)
    a += rng.normal(0, 1.4, a.shape[:2])[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


# ------------------------------------------------------------ USB screen
USB = dict(
    top=42,                                   # image starts below the status bar
    icon=(180, 150, 52),                      # glow circle centre/radius (screen coords)
    card1=(16, 322, 344, 468), card2=(16, 482, 344, 558),
    big=(34, 354, 150, 53), state=(170, 362, 156, 20), volts=(170, 386, 156, 20),
    bar=(34, 424, 292, 14),
    row1=(494,), row2=(526,), rowval_x=(150, 176),
    hint=604,
)
MUTED = (157, 143, 176)
LABEL = (221, 211, 232)


def ic_usb(d, cx, cy, s, col):
    lw = s * 0.075
    top, bot = cy - s * 0.46, cy + s * 0.36
    d.line([(cx, top + s * 0.12), (cx, bot)], fill=col, width=int(lw))
    a = s * 0.13
    d.polygon([(cx, top), (cx - a, top + a * 1.4), (cx + a, top + a * 1.4)], fill=col)
    r = s * 0.10
    d.ellipse([cx - r, bot - r * 0.4, cx + r, bot + r * 1.6], fill=col)
    # left branch -> circle
    ly = cy + s * 0.06
    lx = cx - s * 0.26
    d.line([(cx, ly + s * 0.10), (lx, ly - s * 0.06), (lx, cy - s * 0.12)], fill=col, width=int(lw), joint='curve')
    rr = s * 0.075
    d.ellipse([lx - rr, cy - s * 0.12 - rr * 2, lx + rr, cy - s * 0.12], fill=col)
    # right branch -> square
    rx = cx + s * 0.26
    ry = cy - s * 0.02
    d.line([(cx, ry + s * 0.20), (rx, ry + s * 0.04), (rx, ry - s * 0.12)], fill=col, width=int(lw), joint='curve')
    q = s * 0.075
    d.rectangle([rx - q, ry - s * 0.12 - q * 2, rx + q, ry - s * 0.12], fill=col)


def ic_bolt(d, cx, cy, s, col):
    d.polygon([(cx + s * 0.10, cy - s * 0.50), (cx - s * 0.30, cy + s * 0.08), (cx - s * 0.02, cy + s * 0.08),
               (cx - s * 0.12, cy + s * 0.50), (cx + s * 0.30, cy - s * 0.10), (cx + s * 0.02, cy - s * 0.10)], fill=col)


def outline_card(img, box, r):
    size = img.size
    outer = rr_mask(size, box, r)
    inner = rr_mask(size, (box[0] + 1.5, box[1] + 1.5, box[2] - 1.5, box[3] - 1.5), r - 1.5)
    ring = Image.fromarray(np.clip(np.array(outer, np.int16) - np.array(inner, np.int16), 0, 255).astype(np.uint8))
    shadow(img, ring, offset=(0, 0), blur=4, color=ACCENT, strength=0.22)
    img.paste(vgrad(size, box, (122, 104, 144), (78, 64, 96)), (0, 0), ring)


def build_usb(sbs, out_dir):
    T0 = USB['top']
    size = (W * SS, H * SS)
    clean = build_sbs(buttons=False)              # menu backdrop without its buttons (identical pixels elsewhere)
    img = clean.resize(size, Image.BICUBIC)
    base = img.copy()
    cx, cy, r = USB['icon']
    m = Image.new('L', size, 0)
    ImageDraw.Draw(m).ellipse(S((cx - r, cy - r, cx + r, cy + r)), fill=255)
    shadow(img, m, blur=16, color=ACCENT, strength=0.9, spread=2)
    shadow(img, m, blur=4, color=ACCENT, strength=0.6)
    paste_mask(img, vgrad(size, (cx - r, cy - r, cx + r, cy + r), (214, 172, 242), (186, 128, 226)), m)
    d = ImageDraw.Draw(img)
    ic_usb(d, cx * SS, cy * SS, 62 * SS, P['icon'])

    fT = ImageFont.truetype(UBU % 'Medium', 29 * SS)
    fS = ImageFont.truetype(UBU % 'Regular', 15.5 * SS)
    fL = ImageFont.truetype(UBU % 'Medium', 12 * SS)
    fR = ImageFont.truetype(UBU % 'Regular', 17 * SS)
    d.text((180 * SS, 246 * SS), 'USB Connected', font=fT, fill=(246, 241, 251), anchor='ms')
    d.text((180 * SS, 274 * SS), 'Eject the player on your computer', font=fS, fill=MUTED, anchor='ms')
    d.text((180 * SS, 294 * SS), 'before unplugging the cable.', font=fS, fill=MUTED, anchor='ms')

    outline_card(img, USB['card1'], 18)
    outline_card(img, USB['card2'], 18)
    d = ImageDraw.Draw(img)

    def spaced(x, y, t, f, col, sp=1.6):
        for ch in t:
            d.text((x * SS, y * SS), ch, font=f, fill=col, anchor='ls')
            x += f.getlength(ch) / SS + sp
    spaced(34, 345, 'BATTERY', fL, MUTED)
    # rows in card 2 (labels baked, values are drawn by the theme on the right)
    for y, lab in ((USB['row1'][0], 'Charger'), (USB['row2'][0], 'Est. runtime')):
        d.text((34 * SS, (y + 15) * SS), lab, font=fR, fill=LABEL, anchor='ls')
    yline = (USB['row1'][0] + USB['row2'][0]) / 2 + 9
    d.line(S((34, yline, 326, yline)), fill=(64, 52, 80), width=SS)
    d.text((180 * SS, USB['hint'] * SS), 'Rockbox resumes when you unplug', font=fS, fill=(118, 104, 136), anchor='ms')

    out = img.resize((W, H), Image.LANCZOS)
    # keep untouched areas bit-identical to the backdrop so rockbox's text clears are invisible
    changed = np.array(img.resize((W, H), Image.LANCZOS), np.int16) - np.array(base.resize((W, H), Image.LANCZOS), np.int16)
    mask = (np.abs(changed).max(axis=2) > 0)
    o = np.array(clean).copy(); o[mask] = np.array(out)[mask]
    Image.fromarray(o).crop((0, T0, W, H)).save(out_dir + 'usb_screen.bmp')

    # battery bar: track (used as the bar's backdrop) + purple fill image
    x, y, w, h = USB['bar']
    tr = Image.new('RGB', (w * SS, h * SS)); tr.paste(sbs.crop((x, y, x + w, y + h)).resize((w * SS, h * SS)))
    tm = Image.new('L', tr.size, 0); ImageDraw.Draw(tm).rounded_rectangle([0, 0, w * SS - 1, h * SS - 1], radius=h * SS / 2, fill=255)
    tr.paste(solid(tr.size, P['track']), (0, 0), tm)
    inner_shadow(tr, tm, offset=(0, 2), blur=2, strength=0.6)
    tr.resize((w, h), Image.LANCZOS).save(out_dir + 'batt_track.bmp')
    fl = tr.copy()
    fm = Image.new('L', tr.size, 0); ImageDraw.Draw(fm).rounded_rectangle([0, 0, w * SS - 1, h * SS - 1], radius=h * SS / 2, fill=255)
    fl.paste(vgrad(tr.size, (0, 0, w, h), (216, 176, 242), (184, 126, 224)), (0, 0), fm)
    fl.resize((w, h), Image.LANCZOS).save(out_dir + 'batt_fill.bmp')

    # status bar charging bolt (1-bit, tinted by the theme)
    bm = Image.new('L', (10 * 8, 18 * 8), 0)
    ic_bolt(ImageDraw.Draw(bm), 5 * 8, 9 * 8, 18 * 8, 255)
    bm = bm.resize((10, 18), Image.LANCZOS).point(lambda v: 0 if v > 110 else 255).convert('1')
    bm.save(out_dir + 'bolt.bmp')


# ------------------------------------------------------------ status bar art (speaker, battery outline)
STATUS_FG = (221, 211, 232)
SPK = dict(waves=(27, 8, 14, 26), center=(24, 21), radii=(5.5, 10, 14.5))
BATT = dict(outline=(337, 13, 348, 32), nub=(340, 10, 345, 13), inner=(340, 16, 6, 14))


def _layer():
    return Image.new('RGBA', (W * SS, 42 * SS), (0, 0, 0, 0))


def _comp(bg, layer):
    lay = layer.resize((W, 42), Image.LANCZOS)
    top = bg.crop((0, 0, W, 42)).convert('RGBA')
    top.alpha_composite(lay)
    bg.paste(top.convert('RGB'), (0, 0))


def draw_speaker_body(d, col):
    k = SS
    d.rounded_rectangle([12 * k, 16.5 * k, 17.5 * k, 25.5 * k], radius=1.2 * k, fill=col)
    d.polygon([(16.5 * k, 16.5 * k), (24 * k, 10.5 * k), (24 * k, 31.5 * k), (16.5 * k, 25.5 * k)], fill=col)


def draw_waves(d, col):
    cx, cy = SPK['center']
    for r in SPK['radii']:
        d.arc([(cx - r) * SS, (cy - r) * SS, (cx + r) * SS, (cy + r) * SS], start=-48, end=48,
              fill=col, width=int(2.3 * SS))


def draw_batt_outline(d, col):
    x0, y0, x1, y1 = BATT['outline']
    d.rounded_rectangle([x0 * SS, y0 * SS, x1 * SS, y1 * SS], radius=2.5 * SS, outline=col, width=int(1.6 * SS))
    n = BATT['nub']
    d.rounded_rectangle([n[0] * SS, n[1] * SS, n[2] * SS, n[3] * SS], radius=0.8 * SS, fill=col)


# tiny 3-bar visualizer on Now Playing: (name, x, max height, peak channel); bars share the bottom line
VIZ = dict(bars=(('vz1', 162, 10, 'L'), ('vz2', 170, 15, 'R'), ('vz3', 178, 20, 'L'), ('vz4', 186, 16, 'R'), ('vz5', 194, 12, 'L')),
           w=5, bottom=31)  # 5 bars, x 162..198, centred on x=180


def add_status_art(bg, static_waves, speaker=True):
    lay = _layer(); d = ImageDraw.Draw(lay)
    if speaker:
        draw_speaker_body(d, STATUS_FG + (255,))
    if static_waves:
        draw_waves(d, STATUS_FG + (255,))
    draw_batt_outline(d, STATUS_FG + (255,))
    _comp(bg, lay)
    return bg


def status_images(bg, out_dir):
    """visualizer bar images (peak-meter bars) and the battery level images"""
    w = VIZ['w']
    for name, x, h, ch in VIZ['bars']:
        # lit image: pastel purple, slightly lighter at the top of the full-height bar (gradient stays in place)
        t = np.linspace(0, 1, 20)[20 - h:][:, None, None]
        top, bot = np.array((232, 205, 248), np.float32), np.array(ACCENT, np.float32)
        lit = (top * (1 - t) + bot * t) * np.ones((h, w, 1))
        Image.fromarray(lit.astype(np.uint8)).save(out_dir + name + 'l.bmp')
        Image.new('RGB', (w, h), (58, 47, 72)).save(out_dir + name + 'd.bmp')
    x, y, w, h = BATT['inner']
    Image.new('RGB', (w, h), P['track']).save(out_dir + 'batt_empty.bmp')
    vgrad((w * SS, h * SS), (0, 0, w, h), (214, 170, 242), (186, 128, 226)).resize((w, h), Image.LANCZOS) \
        .save(out_dir + 'batt_level.bmp')


def state_frames(bg, box, draw_fn, states):
    """opaque crops of the backdrop with the icon drawn on top (crisp, anti-aliased)"""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    frames = []
    base = bg.crop(box).resize((w * SS, h * SS), Image.BICUBIC)
    for st in states:
        # draw the icon on a transparent supersampled layer and composite onto the real bg crop
        m = Image.new('L', (w * SS, h * SS), 0)
        col = draw_fn(ImageDraw.Draw(m), w * SS / 2, h * SS / 2, st)
        m = m.resize((w, h), Image.LANCZOS)
        fr = bg.crop(box)
        fr.paste(Image.new('RGB', (w, h), col), (0, 0), m)
        frames.append(fr)
    strip = Image.new('RGB', (w, h * len(frames)))
    for i, f in enumerate(frames):
        strip.paste(f, (0, i * h))
    return strip


def build_all(out_dir):
    bg = add_status_art(build_bg(), static_waves=False, speaker=False)
    bg.save(out_dir + 'wps_bg.bmp')
    status_images(bg, out_dir)
    sbs = add_status_art(build_sbs(), static_waves=False, speaker=False)
    sbs.save(out_dir + 'sbs_bg.bmp')
    build_usb(sbs, out_dir)
    PLAYICON = (40, 24, 54)
    badge_font = ImageFont.truetype(UBU % 'Bold', 10 * SS)

    # play button: 1 stop, 2 play, 3 pause  (same order as before)
    def dplay(d, cx, cy, st):
        {'stop': ic_stop, 'play': ic_play, 'pause': ic_pause}[st](d, cx, cy, 26 * SS, 255)
        return PLAYICON
    state_frames(bg, L['play'], dplay, ['stop', 'play', 'pause']).save(out_dir + 'play.bmp')

    # shuffle: a = off, b = on
    def dshuf(d, cx, cy, st):
        ic_shuffle(d, cx, cy, 26 * SS, 255)
        return ACCENT if st else OFF
    state_frames(bg, L['shuffle'], dshuf, [0, 1]).save(out_dir + 'shuffle.bmp')

    # repeat: a = off, b = all, c = one, d = shuffle, e = A-B
    def drep(d, cx, cy, st):
        on, badge = st
        ic_repeat(d, cx, cy, 28 * SS, 255, badge, badge_font)
        return ACCENT if on else OFF
    state_frames(bg, L['repeat'], drep,
                 [(0, None), (1, None), (1, '1'), (1, 'S'), (1, 'AB')]).save(out_dir + 'repeat.bmp')
    return bg


if __name__ == '__main__':
    import sys, os
    o = sys.argv[1]
    os.makedirs(o, exist_ok=True)
    build_all(o)
