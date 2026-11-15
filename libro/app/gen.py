#!/usr/bin/env python3
"""Genera la app de lectura móvil (un solo HTML) a partir de los archivos m00..m08."""
import re, json, base64, os, sys
D = os.path.dirname(os.path.abspath(__file__)) + '/..'
A = os.path.dirname(os.path.abspath(__file__))

def blocks(text):
    out = []
    for line in text.split('\n'):
        m = re.match(r'^@([A-Z_]+)\s*(.*)$', line)
        if m: out.append([m.group(1), m.group(2).strip(), []])
        elif out: out[-1][2].append(line)
    return out

def paras(arg, ls):
    txt = '\n'.join(([arg] if arg else []) + ls).strip()
    return [re.sub(r'\s*\n\s*', ' ', p.strip()) for p in re.split(r'\n\s*\n', txt) if p.strip()]

def b64(path):
    return 'data:image/jpeg;base64,' + base64.b64encode(open(path, 'rb').read()).decode()

book = {'front': [], 'modules': [], 'back': []}
# portada y presentación
for tag, arg, ls in blocks(open(f'{D}/m00.txt').read()):
    if tag == 'NOTA': book['front'].append({'id': 'nota', 'kicker': 'Nota editorial', 'title': arg, 'body': [['p', x] for x in paras('', ls)]})
    elif tag == 'NEOX_PRESENTA': cur = {'id': 'neox', 'kicker': 'Antes de empezar', 'title': arg, 'body': [['p', x] for x in paras('', ls)], 'areas': []}; book['front'].append(cur)
    elif tag == 'AREA': n, d = arg.split('|', 1); cur['areas'].append([n, d])
    elif tag == 'FIN': cur['after'] = paras(arg, ls)

stories = []
for n in range(1, 8):
    bl = blocks(open(f'{D}/m{n:02d}.txt').read())
    num, title = [x.strip() for x in bl[0][1].split('|', 1)]
    mod = {'n': num, 'title': title, 'intro': [], 'ruta': [], 'lessons': [], 'cierre': None, 'img': f'mod{num}.jpg'}
    cur = None
    for tag, arg, ls in bl[1:]:
        if tag == 'INTRO': mod['intro'] = paras(arg, ls)
        elif tag == 'RUTA': mod['ruta'] = [l.strip()[2:].strip() for l in ([arg] + ls) if l.strip()]
        elif tag == 'LECCION': cur = {'n': arg, 'title': '', 'sub': '', 'body': []}; mod['lessons'].append(cur)
        elif tag == 'CIERRE': cur = {'title': '', 'body': [], 'plan': [], 'frase': ''}; mod['cierre'] = cur
        elif tag == 'TITULO':
            cur['title'] = arg
            cur['body'] += [['p', x] for x in paras('', ls)]
        elif tag == 'SUBTITULO': cur['sub'] = arg
        elif tag == 'IMG': pass
        elif tag == 'H': cur['body'].append(['h', arg]); cur['body'] += [['p', x] for x in paras('', ls)]
        elif tag == 'CITA': cur['body'].append(['q', arg])
        elif tag == 'NEOX_VIVIO':
            cur['body'].append(['vivio', arg, paras('', ls)])
            stories.append([arg, num, cur['n'], cur['title']])
        elif tag == 'NEOX_VOZ': cur['body'].append(['voz', paras(arg, ls)])
        elif tag == 'CUADERNO': cur['body'].append(['cuaderno', paras(arg, ls)])
        elif tag == 'PLAN': cur['plan'] = [l.strip() for l in ([arg] + ls) if l.strip()]
        elif tag == 'FRASE': cur['frase'] = arg
    book['modules'].append(mod)

for tag, arg, ls in blocks(open(f'{D}/m08.txt').read()):
    if tag == 'EPILOGO': epi = {'id': 'epilogo', 'kicker': 'Epílogo', 'title': arg, 'body': [['p', x] for x in paras('', ls)]}; book['back'].append(epi)
    elif tag == 'CITA': epi['body'].append(['q', arg])
    elif tag == 'NEOX_VOZ': epi['body'].append(['voz', paras(arg, ls)])
    elif tag == 'ANEXO': book['back'].append({'id': 'anexo', 'kicker': 'Anexo', 'title': arg, 'stories': stories})

imgs = {f'mod{n:02d}.jpg': b64(f'{A}/mod{n:02d}.jpg') for n in range(1, 8)}
imgs['neox.jpg'] = b64(f'{A}/neox.jpg')
tpl = open(f'{A}/plantilla.html').read()
out = tpl.replace('/*__BOOK__*/', 'const BOOK=' + json.dumps(book, ensure_ascii=False) + ';const IMGS=' + json.dumps(imgs) + ';')
open(f'{A}/el_gran_manifestador_app.html', 'w').write(out)
print('ok', len(out) // 1024, 'KB', len(stories), 'historias')
