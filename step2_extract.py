from board_processor import recortar_casillas
from PIL import Image
import os, re

BRAILLE_TO_NUM = {'\u2802':'1', '\u2806':'2', '\u2812':'3', '\u2832':'4', '\u2822':'5', '\u2816':'6', '\u2836':'7', '\u2826':'8'}

def parse_braille(text):
    bd = {}
    for m in re.finditer(r'([RDTCA])([a-h])([\u2802\u2806\u2812\u2832\u2822\u2816\u2836\u2826])', text):
        p, c, r = m.groups()
        bd[c + BRAILLE_TO_NUM[r]] = p
    for m in re.finditer(r'([a-h])([\u2802\u2806\u2812\u2832\u2822\u2816\u2836\u2826])', text):
        c, r = m.groups()
        sq = c + BRAILLE_TO_NUM[r]
        if sq not in bd: bd[sq] = 'P'
    return bd

train = ['tablero1.png', 'tablero2.png', 'tablero4.png', 'tablero5.png', 'tablero6.png', 'diagrama01.png', 'diagrama05.png', 'diagrama23.png']
ref = open('REFERENCIA.md', encoding='utf-8').read()
gt = {}
for f in train:
    k = f.replace('.png', '')
    s = ref.find(f'### {k}.png')
    if s == -1: continue
    e = ref.find('###', s + 1)
    sec = ref[s:e] if e != -1 else ref[s:]
    wm = re.search(r'Blancas: (.+)', sec)
    bm = re.search(r'Negras: (.+)', sec)
    if wm and bm:
        gt[f] = (parse_braille(wm.group(1).split('\n')[0]), parse_braille(bm.group(1).split('\n')[0]))

print(f'GT: {len(gt)}')
os.makedirs('crops_corrected', exist_ok=True)
tot = 0
for f in train:
    if f not in gt: continue
    img = Image.open(f'ejemplos/{f}')
    sqs = recortar_casillas(img, 32, 0, 0.06)
    wp, bp = gt[f]
    for i, sq_img in enumerate(sqs):
        r, c = divmod(i, 8)
        sn = chr(ord('a') + c) + str(8 - r)
        lbl = wp.get(sn, bp.get(sn, {}).get(sn.lower(), 'empty') if sn in bp else 'empty')
        if sn in bp: lbl = bp[sn].lower()
        elif sn not in wp: lbl = 'empty'
        sq_img.save(f'crops_corrected/{f[:-4]}_{sn}_{lbl}.png')
        tot += 1
print(f'Extracted: {tot}')
