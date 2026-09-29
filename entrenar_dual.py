"""
Entrena DOS clasificadores separados, uno por estilo visual, y valida los diez
diagramas contra la verdad de referencia de la ONCE.

Ejecutar:  python entrenar_dual.py
"""
import re, pickle, numpy as np
from PIL import Image
from sklearn.neighbors import KNeighborsClassifier
from deteccion_tablero import recortar_casillas, detect_board

BR = {'⠂':1,'⠆':2,'⠒':3,'⠲':4,'⠢':5,'⠖':6,'⠶':7,'⠦':8}
PZ = {'R':'K','D':'Q','T':'R','C':'N','A':'B','P':'P'}

def idx(col, row):                      # a8 -> 0 ... h1 -> 63
    return (8 - row) * 8 + (ord(col) - ord('a'))

def gt_braille(linea, color):
    out = {}
    for m in re.finditer(r'([RDTCAP]?)([a-h])([⠂⠆⠒⠲⠢⠖⠶⠦])', linea):
        p, c, r = m.groups()
        out[idx(c, BR[r])] = color + (PZ[p] if p else 'P')
    return out

def gt_audio(linea, color):
    """'Rey en E2, Torres en C1 y H1, Peones en A2, B2 y C2'"""
    out = {}
    tipo = None
    NOMB = [('Peon','P'),('Peón','P'),('Rey','K'),('Dama','Q'),('Torre','R'),
            ('Alfil','B'),('Caballo','N')]
    for tok in re.split(r'[,;]| y ', linea):
        for n, p in NOMB:
            if n.lower() in tok.lower():
                tipo = p
                break
        m = re.search(r'\b([A-Ha-h])\s?([1-8])\b', tok)
        if m and tipo:
            out[idx(m.group(1).lower(), int(m.group(2)))] = color + tipo
    return out

GT = {
 'tablero1.png':  ('b', "Re⠂ Dd⠂ Ta⠂ Th⠂ Cc⠒ Cf⠒ Ac⠲ Ag⠒ a⠆ b⠆ c⠆ d⠒ e⠲ f⠆ g⠆ h⠆",
                        "Re⠦ Dd⠦ Ta⠦ Th⠦ Cc⠖ Cf⠖ Ac⠢ Ac⠦ a⠶ b⠶ c⠶ d⠖ e⠢ f⠶ g⠢ h⠖", 'moderno', 0),
 'tablero2.png':  ('b', "Re⠂ Dd⠂ Ta⠂ Th⠂ Cc⠒ Af⠂ Af⠲ a⠆ b⠆ c⠆ e⠲ f⠆ g⠆ h⠆",
                        "Re⠦ Dd⠦ Ta⠦ Th⠦ Cg⠲ Ac⠦ Af⠦ a⠶ b⠶ d⠖ e⠢ f⠶ g⠶ h⠶", 'moderno', 180),
 'tablero3.png':  ('b', "Re⠂ Dd⠂ Ta⠂ Th⠂ Cb⠂ Cf⠒ Af⠂ Ag⠢ a⠆ b⠆ c⠲ d⠲ e⠆ f⠆ g⠆ h⠆",
                        "Re⠦ Dd⠦ Ta⠦ Th⠦ Cb⠦ Cf⠖ Ac⠦ Af⠦ a⠶ b⠶ c⠶ d⠶ e⠖ f⠢ g⠶ h⠖", 'moderno', 0),
 'tablero4.png':  ('b', "Rh⠂ a⠲ b⠒ c⠆ f⠒ g⠲ h⠒", "Ra⠦ a⠶ b⠖ f⠲ g⠢ h⠲", 'moderno', 0),
 'tablero5.png':  ('b', "Rg⠂ Dd⠒ Tc⠂ Cd⠆ Ch⠢ Ac⠒ c⠲ d⠢ e⠲ g⠆ h⠒",
                        "Rg⠦ Db⠦ Ta⠆ Tb⠖ Ad⠖ Ad⠶ c⠢ e⠢ f⠖ f⠶ h⠖", 'moderno', 0),
 'tablero6.png':  ('b', "Rg⠂ Dd⠂ Ta⠂ Te⠂ Cd⠆ Cf⠒ Ac⠂ Ac⠆ b⠲ c⠒ d⠢ e⠲ f⠆ g⠆ h⠒",
                        "Rg⠦ Dc⠶ Tb⠦ Tf⠦ Cb⠶ Cf⠖ Ac⠦ Ae⠶ b⠢ c⠢ d⠖ e⠢ f⠶ g⠶ h⠶", 'moderno', 0),
 'diagrama01.png':('a', "Rey en E2, Dama en A4, Torres en C1 y H1, Alfil en B5, Caballos en C3 y F3, Peones en A2, B2, D2, F2, G2 y H2",
                        "Rey en E8, Dama en D7, Torres en A8 y H8, Alfiles en F8 y G4, Caballo en C6, Peones en A7, B7, C5, E7, F7, G7 y H7", 'escaneado', 0),
 'diagrama02.png':('a', "Rey en D2, Alfil en H6, Caballo en E1, Peones en A3, B2, G2 y H3",
                        "Rey en E6, Alfil en C4, Caballo en C6, Peones en B7, B6, D5, G6 y H7", 'escaneado', 0),
 'diagrama05.png':('a', "Rey en G1, Dama en D1, Torres en A1 y E1, Alfiles en B3 y C1, Caballos en B1 y F3, Peones en A2, B2, C3, D4, E4, F2, G2 y H2",
                        "Rey en G8, Dama en D8, Torres en A8 y F8, Alfiles en E7 y C4, Caballos en A6 y F6, Peones en B5, C7, D6, E5, F7, G7 y H7", 'escaneado', 0),
 'diagrama23.png':('a', "Rey en H3, Dama en F5, Torre en F1, Caballo en E2, Peones en A6, C4, D5, G3 y G4",
                        "Rey en H7, Dama en G6, Torre en E7, Alfil en E3, Peones en A7, C5, E4, G5 y H6", 'escaneado', 0),
}

# Los dos que NO se usan para entrenar: se reservan como diagramas nuevos
RESERVADOS = {'tablero3.png', 'diagrama02.png'}


def etiquetas(nombre):
    modo, bl, ne, estilo, giro = GT[nombre]
    f = gt_braille if modo == 'b' else gt_audio
    lab = {}
    lab.update(f(bl, 'w'))
    lab.update(f(ne, 'b'))
    return lab, estilo, giro


def vector(crop):
    return np.asarray(crop.convert('L'), dtype=np.float32).ravel() / 255.0


def cargar(nombre):
    lab, estilo, giro = etiquetas(nombre)
    im = Image.open('ejemplos/' + nombre)
    if giro:
        im = im.rotate(180)
    crops = recortar_casillas(im, tam=32)
    X = np.array([vector(c) for c in crops])
    y = np.array([lab.get(i, 'empty') for i in range(64)])
    return X, y, estilo


def main():
    datos = {n: cargar(n) for n in GT}

    print('=' * 68)
    print('VALIDACION POR ESTILO — leave-one-image-out, 1-NN')
    print('=' * 68)

    total_ok = total_n = 0
    exactos = 0
    resumen = {}

    for estilo in ('moderno', 'escaneado'):
        pool = [n for n in GT if datos[n][2] == estilo and n not in RESERVADOS]
        print(f'\n--- {estilo.upper()}  ({len(pool)} diagramas de entrenamiento) ---')
        for held in pool:
            Xtr = np.vstack([datos[n][0] for n in pool if n != held])
            ytr = np.concatenate([datos[n][1] for n in pool if n != held])
            Xte, yte, _ = datos[held]
            knn = KNeighborsClassifier(n_neighbors=1).fit(Xtr, ytr)
            pred = knn.predict(Xte)
            ok = int((pred == yte).sum())
            exacto = ok == 64
            exactos += exacto
            total_ok += ok
            total_n += 64
            resumen[held] = ok
            print(f'  {held:16s} {ok:2d}/64 casillas  {"[EXACTO]" if exacto else ""}')

    print('\n' + '=' * 68)
    print(f'TOTAL: {total_ok}/{total_n} casillas ({100*total_ok/total_n:.1f}%)')
    print(f'EXACTOS: {exactos}/{total_n//64} diagramas')
    print('=' * 68)

    # Modelos finales: cada estilo con TODOS sus diagramas de entrenamiento
    for estilo in ('moderno', 'escaneado'):
        pool = [n for n in GT if datos[n][2] == estilo and n not in RESERVADOS]
        X = np.vstack([datos[n][0] for n in pool])
        y = np.concatenate([datos[n][1] for n in pool])
        knn = KNeighborsClassifier(n_neighbors=1).fit(X, y)
        with open(f'knn_{estilo}.pkl', 'wb') as fh:
            pickle.dump(knn, fh)
        print(f'guardado knn_{estilo}.pkl  ({len(X)} muestras)')

    # Prueba sobre los dos reservados
    print('\n--- DIAGRAMAS RESERVADOS (nunca usados para entrenar) ---')
    for n in sorted(RESERVADOS):
        X, y, estilo = datos[n]
        with open(f'knn_{estilo}.pkl', 'rb') as fh:
            knn = pickle.load(fh)
        ok = int((knn.predict(X) == y).sum())
        print(f'  {n:16s} {ok:2d}/64 casillas  ({estilo})')


if __name__ == '__main__':
    main()
