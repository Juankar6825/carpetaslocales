#!/usr/bin/env python3
"""Construye el HTML del libro a partir de los archivos etiquetados m00..m08."""
import html, re, json, sys, os

D = os.path.dirname(os.path.abspath(__file__)) + '/..'
FM = os.path.dirname(os.path.abspath(__file__)) + '/node_modules/@fontsource'
E = lambda s: html.escape(s, quote=False)

def paras(lines):
    txt = '\n'.join(lines).strip()
    if not txt: return ''
    return ''.join(f'<p>{E(p.strip()).replace(chr(10), " ")}</p>' for p in re.split(r'\n\s*\n', txt) if p.strip())

def blocks(text):
    """Divide en (etiqueta, argumento, líneas) por cada línea que empieza por @."""
    out = []
    for line in text.split('\n'):
        m = re.match(r'^@([A-Z_]+)\s*(.*)$', line)
        if m:
            out.append([m.group(1), m.group(2).strip(), []])
        elif out:
            out[-1][2].append(line)
    return out

MOD_IMG = {'01': 'img/orig-000.jpg', '02': 'img/v3_espejo.png', '03': 'img/v1_libreta.png', '04': 'img/v2_puertas.png',
           '05': 'img/v1_tablero.png', '06': 'img/v3_roto.png', '07': 'img/v3_libro.png'}
NEOX_VIVIO = []   # (area, modulo, leccion, titulo)
INDEX = []        # (modulo, titulo, [lecciones])

def lines_of(arg, ls):
    return ([arg] if arg else []) + ls

def render_module(text):
    b = blocks(text)
    h = []
    mod_n, mod_t = b[0][1].split('|', 1)
    mod_n, mod_t = mod_n.strip(), mod_t.strip()
    les_titles = []
    i = 1
    intro, ruta = '', []
    lessons = []
    cur = None
    cierre = None
    for tag, arg, ls in b[1:]:
        if tag == 'INTRO': intro = paras(lines_of(arg, ls))
        elif tag == 'RUTA': ruta = [l.strip() for l in lines_of(arg, ls) if l.strip()]
        elif tag == 'LECCION':
            cur = {'n': arg, 'items': []}; lessons.append(cur)
        elif tag == 'CIERRE':
            cierre = {'items': []}; cur = cierre
        else:
            cur['items'].append((tag, arg, ls))
    # Portada de módulo
    ruta_html = ''.join(
        f'<li><span>{E(r[:2])}</span>{E(r[2:].strip())}</li>' for r in ruta)
    h.append(f'''<section class="modopen" id="m{mod_n}">
      <div class="mimg" style="background-image:url('{MOD_IMG.get(mod_n, '')}')"></div>
      <div class="mtext"><div class="mnum">MÓDULO {mod_n} · 07</div><h1>{E(mod_t)}</h1></div>
    </section>
    <section class="modintro"><div class="kicker">BIENVENIDA AL MÓDULO {mod_n}</div>{intro}
      <h3>Tu ruta de siete lecciones</h3><ol class="ruta">{ruta_html}</ol></section>''')
    for L in lessons:
        title = next((a for t, a, _ in L['items'] if t == 'TITULO'), '')
        les_titles.append(title)
        h.append(f'<section class="lesson" id="m{mod_n}l{L["n"]}">')
        for tag, arg, ls in L['items']:
            if tag == 'IMG': h.append(f'<img class="limg" src="img/{E(arg)}">')
            elif tag == 'TITULO': h.append(f'<div class="kicker">MÓDULO {mod_n} · LECCIÓN {E(L["n"])} / 07</div><h2>{E(arg)}</h2>')
            elif tag == 'SUBTITULO': h.append(f'<div class="sub">{E(arg)}</div>')
            elif tag == 'H': h.append(f'<h3>{E(arg)}</h3>' + paras(ls))
            elif tag == 'CITA': h.append(f'<blockquote>«{E(arg)}»</blockquote>' + paras(ls))
            elif tag == 'NEOX_VIVIO':
                NEOX_VIVIO.append((arg, mod_n, L['n'], title))
                h.append(f'<aside class="neox vivio"><div class="nh"><img src="img/neox.jpg"><div><b>LO QUE VIVIÓ NEOX</b><span>Área · {E(arg)}</span></div></div>{paras(ls)}</aside>')
            elif tag == 'NEOX_VOZ':
                h.append(f'<aside class="neox voz"><div class="nh2">LA VOZ DE NEOX</div>{paras(lines_of(arg, ls))}</aside>')
            elif tag == 'CUADERNO':
                h.append(f'<div class="cuaderno"><div class="ch">CUADERNO DE ACCIÓN</div>{paras(lines_of(arg, ls))}'
                         '<div class="linea">Mi decisión de hoy:</div><div class="linea">La revisaré el día:</div></div>')
            else:
                h.append(paras(lines_of(arg, ls)))
        h.append('</section>')
    if cierre:
        h.append('<section class="cierre"><div class="kicker">CIERRE DEL MÓDULO</div>')
        for tag, arg, ls in cierre['items']:
            if tag == 'TITULO': h.append(f'<h2>{E(arg)}</h2>' + paras(ls))
            elif tag == 'PLAN':
                items = [l.strip() for l in lines_of(arg, ls) if l.strip()]
                lis = ''
                for it in items:
                    m = re.match(r'^(D[ií]a\s*\d+)\s*[·:.]?\s*(.*)$', it)
                    lis += f'<li><span>{E(m.group(1)) if m else ""}</span>{E(m.group(2) if m else it)}</li>'
                h.append(f'<h3>Tu plan de siete días</h3><ul class="plan">{lis}</ul>')
            elif tag == 'FRASE': h.append(f'<blockquote class="final">«{E(arg)}»</blockquote>')
            else: h.append(paras(lines_of(arg, ls)))
        h.append('</section>')
    INDEX.append((mod_n, mod_t, les_titles))
    return '\n'.join(h)

def render_front(text):
    h = []
    for tag, arg, ls in blocks(text):
        if tag == 'NOTA':
            h.append(f'<section class="front"><div class="kicker">NOTA EDITORIAL</div><h2>{E(arg)}</h2>{paras(ls)}</section>')
        elif tag == 'NEOX_PRESENTA':
            h.append(f'<section class="front neoxp"><img class="neoxbig" src="img/neox.jpg"><div class="kicker">ANTES DE EMPEZAR</div><h2>{E(arg)}</h2>{paras(ls)}<div class="areas">')
        elif tag == 'AREA':
            n, d = arg.split('|', 1)
            h.append(f'<div class="area"><b>{E(n)}</b><span>{E(d)}</span></div>')
        elif tag == 'FIN':
            h.append(f'</div>{paras(lines_of(arg, ls))}</section>')
    return '\n'.join(h)

def render_back(text):
    h = []
    for tag, arg, ls in blocks(text):
        if tag == 'EPILOGO':
            h.append(f'<section class="front epi"><div class="kicker">EPÍLOGO</div><h2>{E(arg)}</h2>{paras(ls)}')
        elif tag == 'CITA': h.append(f'<blockquote>«{E(arg)}»</blockquote>')
        elif tag == 'NEOX_VOZ': h.append(f'<aside class="neox voz"><div class="nh2">LA VOZ DE NEOX</div>{paras(lines_of(arg, ls))}</aside></section>')
        elif tag == 'ANEXO':
            areas = ['Desarrollo personal', 'Negocio', 'Hijos', 'Pareja']
            rows = ''
            for a in areas:
                items = [x for x in NEOX_VIVIO if x[0].lower().startswith(a.lower()[:6])]
                lis = ''.join(f'<li>{E(t)} <span>Módulo {m}, lección {l}</span></li>' for _, m, l, t in items)
                if not lis: lis = '<li class="vacio">Las historias de NEOX en esta área llegarán en la próxima edición.</li>'
                rows += f'<div class="anx"><h3>{E(a)}</h3><ul>{lis}</ul></div>'
            h.append(f'<section class="front"><div class="kicker">ANEXO</div><h2>{E(arg)}</h2><p>Estas son las lecciones en las que NEOX cuenta una historia vivida, ordenadas por las cuatro áreas de su vida.</p>{rows}</section>')
    return '\n'.join(h)

def toc():
    h = '<section class="front toc"><div class="kicker">ÍNDICE GENERAL</div><h2>Contenido</h2>'
    h += '<div class="tocl"><a href="#neox">Quién es NEOX</a></div>'
    for n, t, ls in INDEX:
        h += f'<div class="tocm"><a href="#m{n}">Módulo {int(n)} · {E(t.title() if t.isupper() else t)}</a></div><ol>'
        for i, l in enumerate(ls, 1):
            h += f'<li><a href="#m{n}l{i:02d}">{E(l)}</a></li>'
        h += '</ol>'
    h += '<div class="tocl"><a href="#epi">Epílogo · La decisión que empieza hoy</a></div></section>'
    return h

def main():
    mods = ''.join(render_module(open(f'{D}/m{n:02d}.txt').read()) for n in range(1, 8))
    front = render_front(open(f'{D}/m00.txt').read()).replace('class="front neoxp"', 'class="front neoxp" id="neox"')
    back = render_back(open(f'{D}/m08.txt').read()).replace('class="front epi"', 'class="front epi" id="epi"')
    css = open(os.path.dirname(os.path.abspath(__file__)) + '/libro.css').read().replace('FM/', FM + '/')
    cover = '''<section class="cover"><div class="cimg"></div><div class="ctext">
      <div class="ck">EDICIÓN DE TRABAJO · NOVIEMBRE 2026</div>
      <h1>EL GRAN<br>MANIFESTADOR</h1>
      <div class="cs">Siete módulos. Cuarenta y nueve lecciones.<br>Una vida construida con intención y acción.</div>
      <div class="cn">Con las historias de NEOX</div></div></section>'''
    doc = f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><title>El Gran Manifestador</title>
    <style>{css}</style></head><body>{cover}{front}{toc()}{mods}{back}
    <section class="fin"><div>EL GRAN MANIFESTADOR</div><span>Fin del manuscrito · Edición de trabajo con las historias de NEOX</span></section></body></html>'''
    open(f'{D}/build/libro.html', 'w').write(doc)
    json.dump({'neox': NEOX_VIVIO, 'index': INDEX}, open(f'{D}/build/meta.json', 'w'), ensure_ascii=False, indent=1)
    print('ok', len(NEOX_VIVIO), 'historias')

main()
