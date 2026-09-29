from board_processor import recortar_casillas
from PIL import Image
import os
import numpy as np
import re

BRAILLE_TO_NUM = {'⠂':'1','⠆':'2','⠒':'3','⠲':'4','⠢':'5','⠖':'6','⠶':'7','⠦':'8'}

def parse_braille_transcription(text):
    board_dict = {}
    for match in re.finditer(r'([RDTCA])([a-h])([⠂⠆⠒⠲⠢⠖⠶⠦])', text):
        piece, col, row_braille = match.groups()
        row = BRAILLE_TO_NUM[row_braille]
        square = col + row
        board_dict[square] = piece
    for match in re.finditer(r'([a-h])([⠂⠆⠒⠲⠢⠖⠶⠦])', text):
        if not re.match(r'[RDTCA]' + match.group(0), text[:match.start()]):
            col, row_braille = match.groups()
            row = BRAILLE_TO_NUM[row_braille]
            square = col + row
            if square not in board_dict:
                board_dict[square] = 'P'
    return board_dict

training_files = ['tablero1.png', 'tablero2.png', 'tablero4.png', 'tablero5.png', 
                  'tablero6.png', 'diagrama01.png', 'diagrama05.png', 'diagrama23.png']

with open('REFERENCIA.md', 'r', encoding='utf-8') as f:
    ref_text = f.read()

ground_truth = {}
for fname in training_files:
    key = fname.replace('.png', '')
    start = ref_text.find(f'### {key}.png')
    if start == -1:
        continue
    end = ref_text.find('###', start + 1)
    section = ref_text[start:end] if end != -1 else ref_text[start:]
    
    white_match = re.search(r'Blancas: (.+)', section)
    black_match = re.search(r'Negras: (.+)', section)
    
    if white_match and black_match:
        white_text = white_match.group(1).split('\n')[0]
        black_text = black_match.group(1).split('\n')[0]
        
        white_pieces = parse_braille_transcription('Blancas: ' + white_text)
        black_pieces = parse_braille_transcription('Negras: ' + black_text)
        
        ground_truth[fname] = (white_pieces, black_pieces)

print(f'Loaded ground truth for {len(ground_truth)} training images')

crops_dir = 'crops_corrected'
os.makedirs(crops_dir, exist_ok=True)

total_crops = 0
for fname in training_files:
    if fname not in ground_truth:
        print(f'WARNING: No ground truth for {fname}')
        continue
    
    img = Image.open(f'ejemplos/{fname}')
    squares = recortar_casillas(img, tam=32, margen=0, recorte_interior=0.06)
    
    white_pieces, black_pieces = ground_truth[fname]
    
    for idx, square_img in enumerate(squares):
        fen_row = idx // 8
        fen_col = idx % 8
        chess_rank = 8 - fen_row
        chess_file = chr(ord('a') + fen_col)
        square_name = f'{chess_file}{chess_rank}'
        
        if square_name in white_pieces:
            label = white_pieces[square_name]
        elif square_name in black_pieces:
            label = black_pieces[square_name].lower()
        else:
            label = 'empty'
        
        crop_filename = f'{crops_dir}/{fname[:-4]}_{square_name}_{label}.png'
        square_img.save(crop_filename)
        total_crops += 1

print(f'Extracted {total_crops} crops to {crops_dir}/')
