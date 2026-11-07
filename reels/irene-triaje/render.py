"""Reel Irene · Efincas10 — renderiza 1080x1920 a 30 fps y lo pasa por ffmpeg.
Uso: python3 render.py [irene_frames_dir]   (si no hay carpeta, Irene es imagen fija)
"""
import json, math, os, subprocess, sys, re
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, "assets")
W, H, FPS = 1080, 1920, 30
DUR = 34.2
NAVY = (31, 42, 82); NAVY2 = (43, 58, 103); ORANGE = (232, 98, 45); BLUE = (31, 127, 184)
WHITE = (255, 255, 255); GREEN = (37, 211, 102); RED = (226, 54, 54); CREAM = (255, 246, 238)

F = "/usr/share/fonts/opentype/inter/"
def font(name, size): return ImageFont.truetype(F + name, size)
BLACK = lambda s: font("Inter-Black.otf", s)
XBOLD = lambda s: font("Inter-ExtraBold.otf", s)
SEMI = lambda s: font("Inter-SemiBold.otf", s)
EMOJI = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)

def emoji(ch, size):
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((80, 80), ch, font=EMOJI, embedded_color=True, anchor="mm")
    im = im.crop(im.getbbox())
    return im.resize((size, int(size * im.height / im.width)), Image.LANCZOS)

# ---------- easing ----------
def clamp(x, a=0, b=1): return max(a, min(b, x))
def prog(t, t0, d): return clamp((t - t0) / d)
def ease_out(x): return 1 - (1 - x) ** 3
def ease_back(x, s=1.7):
    x -= 1; return x * x * ((s + 1) * x + s) + 1
def ease_in_out(x): return 3 * x * x - 2 * x * x * x

# ---------- assets ----------
words = [w for w in json.load(open(os.path.join(A, "words.json")))["words"] if w["type"] == "word" and not w["text"].startswith("[")]
DIG = {"seis": "6", "uno": "1", "nueve": "9", "cero": "0", "siete": "7", "tres": "3", "cinco": "5", "dos": "2", "ocho": "8"}
for w in words:
    raw = w["text"]
    core = re.sub(r"[^\wáéíóúñ]", "", raw.lower())
    if core in DIG:
        w["text"] = DIG[core]
    elif core == "diez":
        w["text"] = "10"
    else:
        w["text"] = raw.replace("...", "…")

# fusiona "Efincas" + "10" en una sola palabra visual
merged = []
for w in words:
    if w["text"] == "10" and merged and merged[-1]["text"] == "Efincas":
        merged[-1] = dict(merged[-1], text="Efincas10.", end=w["end"])
    else:
        merged.append(dict(w))
words = merged

# trozos de subtítulo: corta en puntuación o cada 3 palabras
chunks, cur = [], []
for i, w in enumerate(words):
    cur.append(w)
    end_punct = re.search(r"[.,?!:…]$", w["text"])
    is_digit = w["text"].isdigit()
    nxt_digit = i + 1 < len(words) and words[i + 1]["text"].isdigit()
    if is_digit and nxt_digit and not end_punct:
        continue
    if end_punct or len(cur) >= 3 and not is_digit:
        chunks.append(cur); cur = []
if cur: chunks.append(cur)
# los dígitos del teléfono los agrupamos en una línea 619 07 35 28
for c in chunks:
    for k in range(len(c)):
        c[k]["start"] = c[k]["start"]

logo = Image.open(os.path.join(A, "logo_efincas10.png")).convert("RGBA")
# quita el fondo blanco del logo
px = logo.load()
for y in range(logo.height):
    for x in range(logo.width):
        r, g, b, a = px[x, y]
        m = min(r, g, b)
        if m > 235: px[x, y] = (r, g, b, 0)
        elif m > 200: px[x, y] = (r, g, b, int(255 * (235 - m) / 35))
logo = logo.crop(logo.getbbox())

irene_src = Image.open(os.path.join(A, "irene2.png")).convert("RGB")  # 1280x720
IRENE_FRAMES = sys.argv[1] if len(sys.argv) > 1 else None
CROP_X = 270  # cuadrado 720x720 centrado en la cara
irene_still = irene_src.crop((CROP_X, 0, CROP_X + 720, 720))

def irene_at(t, size):
    if IRENE_FRAMES:
        idx = min(int(t * FPS) + 1, len(os.listdir(IRENE_FRAMES)))
        im = Image.open(os.path.join(IRENE_FRAMES, f"f{idx:05d}.jpg")).convert("RGB")
    else:
        z = 1 + 0.04 * math.sin(t * 0.6)  # respiración suave
        s = int(720 / z); o = (720 - s) // 2
        im = irene_still.crop((o, o, o + s, o + s))
    return im.resize((size, size), Image.LANCZOS)

def rounded_mask(size, r):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), r, fill=255)
    return m

def circle_mask(d):
    m = Image.new("L", (d * 4, d * 4), 0)
    ImageDraw.Draw(m).ellipse((0, 0, d * 4 - 1, d * 4 - 1), fill=255)
    return m.resize((d, d), Image.LANCZOS)

# ---------- fondos precalculados ----------
def make_bg(c1, c2):
    bg = Image.new("RGB", (W, H), c1)
    d = ImageDraw.Draw(bg)
    for y in range(H):
        k = y / H
        d.line((0, y, W, y), fill=tuple(int(c1[i] * (1 - k) + c2[i] * k) for i in range(3)))
    return bg
BG_NAVY = make_bg((24, 33, 68), (43, 58, 103))
BG_ORANGE = make_bg((240, 112, 55), (214, 78, 30))
BG_CREAM = make_bg((255, 250, 245), (255, 236, 222))
BG_RED = make_bg((200, 40, 40), (120, 18, 30))

GLOW = Image.new("RGBA", (1500, 1500), (0, 0, 0, 0))
ImageDraw.Draw(GLOW).ellipse((450, 450, 1050, 1050), fill=(232, 98, 45, 120))
GLOW = GLOW.filter(ImageFilter.GaussianBlur(120))

SPR = {k: emoji(v, s) for k, (v, s) in {
    "mail": ("📩", 260), "mail_s": ("📩", 150), "build": ("🏢", 150), "person": ("👷", 150),
    "siren": ("🚨", 300), "check": ("✅", 110), "phone": ("📱", 120), "drawer": ("🗄️", 200),
}.items()}

def paste_c(base, im, cx, cy, scale=1.0, alpha=1.0, rot=0):
    if scale <= 0.01 or alpha <= 0.01: return
    im = im.convert("RGBA")
    if scale != 1: im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.LANCZOS)
    if rot: im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 1:
        a = im.getchannel("A").point(lambda v: int(v * alpha)); im.putalpha(a)
    base.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

def text_sprite(txt, fnt, fill, stroke=0, stroke_fill=(0, 0, 0)):
    d0 = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    bb = d0.textbbox((0, 0), txt, font=fnt, stroke_width=stroke)
    im = Image.new("RGBA", (bb[2] - bb[0] + 20, bb[3] - bb[1] + 20), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10 - bb[0], 10 - bb[1]), txt, font=fnt, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    return im

_tcache = {}
def T(txt, fnt_fn, size, fill, stroke=0, sf=(0, 0, 0)):
    k = (txt, fnt_fn, size, fill, stroke, sf)
    if k not in _tcache: _tcache[k] = text_sprite(txt, fnt_fn(size), fill, stroke, sf)
    return _tcache[k]

def pill(w, h, color, r=None):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, h - 1), r if r is not None else h // 2, fill=color)
    return im

def shadow(im, blur=30, off=18, op=110):
    a = im.getchannel("A")
    s = Image.new("RGBA", (im.width + 160, im.height + 160), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, op)); sh.putalpha(a.point(lambda v: v * op // 255))
    s.alpha_composite(sh, (80, 80 + off))
    s = s.filter(ImageFilter.GaussianBlur(blur))
    s.alpha_composite(im, (80, 80))
    return s

# ---------- tarjetas reutilizables ----------
def irene_card(t, size=860):
    face = irene_at(t, size - 24).convert("RGBA")
    card = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, size - 1, size - 1), 70, fill=WHITE)
    m = rounded_mask(face.size, 58); face.putalpha(m)
    card.alpha_composite(face, (12, 12))
    return card

_shadow_cache = {}
def irene_block(base, t, cx, cy, scale, alpha, tag=True):
    card = irene_card(t)
    if "card" not in _shadow_cache:
        _base = Image.new("RGBA", card.size, (0, 0, 0, 0)); ImageDraw.Draw(_base).rounded_rectangle((0, 0, card.width - 1, card.height - 1), 70, fill=WHITE)
        _shadow_cache["card"] = shadow(_base, 40, 26, 120)
    sh = _shadow_cache["card"].copy()
    sh.alpha_composite(card, (80, 80))
    paste_c(base, sh, cx, cy, scale, alpha)
    if tag:
        tg = name_tag()
        paste_c(base, tg, cx, cy + 430 * scale, scale, alpha)

_nt = {}
def name_tag():
    if "t" not in _nt:
        t1 = T("Irene", BLACK, 56, WHITE); t2 = T("Asistente virtual · Efincas10", SEMI, 34, (255, 225, 205))
        w = max(t1.width, t2.width) + 110; h = 160
        p = pill(w, h, ORANGE, 44)
        p.alpha_composite(t1, ((w - t1.width) // 2, 14)); p.alpha_composite(t2, ((w - t2.width) // 2, 84))
        _nt["t"] = shadow(p, 20, 10, 90)
    return _nt["t"]

def step_card(icon, title, sub, w=900, h=230):
    c = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(c).rounded_rectangle((0, 0, w - 1, h - 1), 46, fill=WHITE)
    ImageDraw.Draw(c).rounded_rectangle((0, 0, 22, h - 1), 11, fill=ORANGE)
    ic = SPR[icon]; ic = ic.resize((130, int(130 * ic.height / ic.width)), Image.LANCZOS)
    c.alpha_composite(ic, (60, (h - ic.height) // 2))
    t1 = T(title, BLACK, 58, NAVY); c.alpha_composite(t1, (225, 40))
    t2 = T(sub, SEMI, 36, (110, 118, 140)); c.alpha_composite(t2, (228, 128))
    return shadow(c, 26, 14, 90)

STEP_CARDS = [
    (9.5, step_card("mail_s", "Tu aviso", "Se revisa al llegar")),
    (11.85, step_card("build", "Tu comunidad", "Se asigna donde toca")),
    (13.45, step_card("person", "Quien lo resuelve", "Va directo, sin rebotes")),
]

def check_row(txt, w=920, h=170):
    c = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(c).rounded_rectangle((0, 0, w - 1, h - 1), 44, fill=WHITE)
    c.alpha_composite(SPR["check"], (40, (h - SPR["check"].height) // 2))
    t1 = T(txt, BLACK, 54, NAVY); c.alpha_composite(t1, (180, (h - t1.height) // 2))
    return shadow(c, 24, 12, 80)
CHECKS = [(20.4, check_row("Nada en un cajón")), (22.0, check_row("Nada perdido en el correo"))]

def wa_button(digits_shown):
    w, h = 940, 230
    c = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(c).rounded_rectangle((0, 0, w - 1, h - 1), 115, fill=GREEN)
    ph = SPR["phone"]; c.alpha_composite(ph, (55, (h - ph.height) // 2))
    t1 = T("WhatsApp", XBOLD, 40, (220, 255, 230)); c.alpha_composite(t1, (200, 34))
    full = "619 07 35 28"
    shown = ""; n = 0
    for ch in full:
        if ch == " ": shown += " "; continue
        shown += ch if n < digits_shown else "·"; n += 1
    t2 = T(shown, BLACK, 92, WHITE); c.alpha_composite(t2, (196, 82))
    return shadow(c, 30, 16, 110)

# ---------- subtítulos ----------
SUB_Y = 1600
def draw_subs(base, t, y=SUB_Y, dark=False):
    cur = None
    for c in chunks:
        if c[0]["start"] - 0.05 <= t <= c[-1]["end"] + 0.25: cur = c
    if cur is None: return
    if cur[0]["text"].isdigit():  # el teléfono ya va en el botón
        return
    k = ease_back(prog(t, cur[0]["start"] - 0.05, 0.18))
    size = 86
    sprites = []
    for w in cur:
        active = w["start"] - 0.03 <= t <= w["end"] + 0.12 or (t > w["end"] and w is cur[-1])
        col = ORANGE if active else WHITE
        sprites.append(T(w["text"].upper(), BLACK, size, col, 9, (12, 16, 36)))
    gap = 22
    total = sum(s.width for s in sprites) + gap * (len(sprites) - 1)
    lines = [sprites]
    if total > W - 80:
        mid = len(sprites) // 2 or 1
        lines = [sprites[:mid], sprites[mid:]]
    line_h = 112
    y0 = y - (len(lines) - 1) * line_h / 2
    for li, ln in enumerate(lines):
        tw = sum(s.width for s in ln) + gap * (len(ln) - 1)
        x = W / 2 - tw / 2
        for s in ln:
            paste_c(base, s, x + s.width / 2, y0 + li * line_h, 0.6 + 0.4 * k, clamp(k * 1.5))
            x += s.width + gap

# ---------- escenas ----------
def scene_hook(f, t):
    f.paste(BG_NAVY)
    paste_c(f, GLOW, W / 2, 760 + 30 * math.sin(t * 2), 1.0, 0.8)
    # sobre que cae
    if t < 5.6:
        k = ease_back(prog(t, 0.0, 0.5))
        fall = ease_in_out(prog(t, 3.9, 1.5))
        y = 700 + 15 * math.sin(t * 3) + fall * 900
        paste_c(f, SPR["mail"], W / 2, y, k * (1 - 0.5 * fall), 1 - fall, rot=fall * 70)
        q = T("¿Y tu aviso?", BLACK, 120, WHITE)
        paste_c(f, q, W / 2, 330, ease_back(prog(t, 0.15, 0.4)), 1 - fall)
        d = SPR["drawer"]
        paste_c(f, d, W / 2, 1180, ease_out(prog(t, 3.9, 0.4)), clamp(prog(t, 3.9, 0.3)) * (1 - prog(t, 5.3, 0.3)))
    if 5.55 <= t < 6.35:
        k = ease_back(prog(t, 5.6, 0.25), 3)
        sh = 14 * math.sin(t * 90) * (1 - prog(t, 5.6, 0.5))
        paste_c(f, T("NADA.", BLACK, 260, (255, 255, 255)), W / 2 + sh, 860, k)
        paste_c(f, T("ni respuesta, ni noticias", SEMI, 48, (180, 190, 220)), W / 2, 1040, 1, clamp(prog(t, 5.7, 0.3)))
    if t >= 6.35:
        r = ease_out(prog(t, 6.35, 0.35))
        rad = int(r * 1400)
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).ellipse((W / 2 - rad, 900 - rad, W / 2 + rad, 900 + rad), fill=255)
        f.paste(BG_ORANGE, (0, 0), m)
        paste_c(f, T("AQUÍ NO.", BLACK, 210, WHITE, 0), W / 2, 860, ease_back(prog(t, 6.4, 0.3), 2.5))

def scene_irene(f, t, t0):
    f.paste(BG_CREAM)
    k = ease_back(prog(t, t0, 0.45))
    paste_c(f, GLOW, W / 2, 700, 1.2, 0.55)
    irene_block(f, t, W / 2, 690, 0.55 + 0.45 * k, clamp(k * 2))

def scene_steps(f, t):
    f.paste(BG_NAVY)
    paste_c(f, GLOW, W / 2, 900, 1.3, 0.5)
    ttl = T("Así funcionamos", BLACK, 72, WHITE)
    paste_c(f, ttl, W / 2, 230, 1, clamp(prog(t, 9.5, 0.3)))
    paste_c(f, pill(260, 10, ORANGE), W / 2, 300, ease_out(prog(t, 9.6, 0.4)), 1)
    ys = [520, 860, 1200]
    d = ImageDraw.Draw(f)
    for i, (t0, card) in enumerate(STEP_CARDS):
        if i > 0:
            lp = ease_out(prog(t, t0 - 0.4, 0.4))
            if lp > 0:
                y1 = ys[i - 1] + 120; y2 = y1 + (ys[i] - 120 - y1) * lp
                d.line((W / 2, y1, W / 2, y2), fill=ORANGE, width=10)
        k = ease_back(prog(t, t0, 0.45))
        paste_c(f, card, W / 2 + (1 - ease_out(prog(t, t0, 0.45))) * 600, ys[i], 1, clamp(k * 2))

def scene_urgent(f, t):
    pulse = 0.5 + 0.5 * math.sin((t - 16) * 9)
    f.paste(BG_RED)
    paste_c(f, GLOW, W / 2, 700, 1.4 + 0.2 * pulse, 0.6)
    k = ease_back(prog(t, 16.05, 0.4), 2.5)
    paste_c(f, SPR["siren"], W / 2, 560, k * (1 + 0.06 * pulse), 1, rot=6 * math.sin(t * 14))
    paste_c(f, T("¿URGENTE?", BLACK, 150, WHITE), W / 2, 920, ease_back(prog(t, 16.4, 0.35)))
    if t > 17.25:
        b = pill(820, 150, WHITE)
        tt = T("Pasa delante de todo", BLACK, 58, RED)
        b.alpha_composite(tt, ((b.width - tt.width) // 2, (b.height - tt.height) // 2))
        paste_c(f, shadow(b, 20, 10, 90), W / 2, 1130, ease_back(prog(t, 17.3, 0.35)))
    if t > 18.85:
        paste_c(f, T("PRIORIDAD MÁXIMA", BLACK, 92, (255, 220, 80), 6, (90, 10, 15)), W / 2, 1320, ease_back(prog(t, 18.9, 0.35), 3))

def scene_checks(f, t):
    f.paste(BG_NAVY)
    paste_c(f, GLOW, W / 2, 900, 1.2, 0.45)
    paste_c(f, T("Con nosotros…", BLACK, 80, WHITE), W / 2, 420, ease_back(prog(t, 20.3, 0.35)))
    for i, (t0, row) in enumerate(CHECKS):
        k = ease_back(prog(t, t0, 0.4))
        paste_c(f, row, W / 2 - (1 - ease_out(prog(t, t0, 0.4))) * 700, 720 + i * 240, 1, clamp(k * 2))

def scene_promise(f, t):
    scene_irene(f, t, 24.0)
    if t > 24.3:
        b = pill(760, 120, NAVY)
        tt = T("Tú solo avisas una vez", BLACK, 50, WHITE)
        b.alpha_composite(tt, ((b.width - tt.width) // 2, (b.height - tt.height) // 2))
        paste_c(f, shadow(b, 18, 10, 80), W / 2, 1330, ease_back(prog(t, 24.35, 0.35)))

def scene_cta(f, t):
    f.paste(BG_NAVY)
    paste_c(f, GLOW, W / 2, 600, 1.3, 0.6)
    # Irene en círculo
    d = 520
    face = irene_at(t, d).convert("RGBA"); face.putalpha(circle_mask(d))
    ring = Image.new("RGBA", (d + 36, d + 36), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse((0, 0, d + 35, d + 35), fill=ORANGE)
    ring.alpha_composite(face, (18, 18))
    k = ease_back(prog(t, 27.35, 0.45))
    paste_c(f, ring, W / 2, 520, k)
    paste_c(f, T("Escríbenos", BLACK, 104, WHITE), W / 2, 920, ease_back(prog(t, 27.5, 0.35)))
    # dígitos según los dice
    digit_times = [w["start"] for w in words if w["text"].isdigit()]
    shown = sum(1 for s in digit_times if t >= s - 0.03)
    paste_c(f, wa_button(shown), W / 2, 1130, ease_back(prog(t, 28.2, 0.4)))
    # logo + marca
    lg = logo.resize((120, int(120 * logo.height / logo.width)), Image.LANCZOS)
    plate = pill(560, 170, WHITE, 40)
    plate.alpha_composite(lg, (40, (170 - lg.height) // 2))
    plate.alpha_composite(T("Efincas10", BLACK, 64, NAVY), (190, 28))
    plate.alpha_composite(T("Administración de fincas", SEMI, 28, (110, 118, 140)), (194, 112))
    paste_c(f, plate, W / 2, 1440, ease_back(prog(t, 29.0, 0.4)), clamp(prog(t, 29.0, 0.3)))

SCENES = [  # (inicio, fin, función, subtítulos_y)
    (0.0, 7.30, scene_hook, SUB_Y),
    (7.30, 9.45, lambda f, t: scene_irene(f, t, 7.30), 1500),
    (9.45, 16.0, scene_steps, 1640),
    (16.0, 20.25, scene_urgent, 1600),
    (20.25, 23.98, scene_checks, 1450),
    (23.98, 27.35, scene_promise, 1560),
    (27.35, DUR, scene_cta, 1700),
]

def frame(t):
    f = Image.new("RGBA", (W, H))
    for t0, t1, fn, sy in SCENES:
        if t0 <= t < t1:
            fn(f, t)
            # flash blanco en los cortes
            fl = 1 - prog(t, t0, 0.12)
            if t0 > 0 and fl > 0:
                f.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(150 * fl))))
            draw_subs(f, t, sy)
            break
    # barra de progreso y logo pequeño arriba
    ImageDraw.Draw(f).rectangle((0, 0, int(W * t / DUR), 10), fill=ORANGE)
    return f.convert("RGB")

if __name__ == "__main__":
    out = os.path.join(HERE, "out", os.environ.get("OUT", "reel_irene_borrador.mp4"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    if os.environ.get("PREVIEW"):
        for ts in os.environ["PREVIEW"].split(","):
            frame(float(ts)).save(os.path.join(HERE, "out", f"prev_{ts}.jpg"), quality=85)
        sys.exit()
    n = int(DUR * FPS)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", os.path.join(A, "voz.mp3"), "-filter_complex", "[1:a]adelay=0|0,apad[a]", "-map", "0:v", "-map", "[a]",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                          "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for i in range(n):
        p.stdin.write(frame(i / FPS).tobytes())
        if i % 150 == 0: print(i, "/", n, flush=True)
    p.stdin.close(); p.wait(); print("OK", out)
