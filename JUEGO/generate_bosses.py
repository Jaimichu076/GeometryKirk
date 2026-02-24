# generate_bosses.py
# Ejecuta este script una vez para generar boss0..boss10 a partir de boss_template.py
import os

TEMPLATE = """# AUTO-GENERATED boss{n}.py
from boss_template import *
# Ajustes específicos para boss{n}
BOSS_IMAGE = BOSS_IMAGE.replace("boss_X.png", "boss_{n}.png")
BOSS_MUSIC = BOSS_MUSIC.replace("boss_X.mp3", "boss_{n}.mp3")
BOSS_MAX_HP = {hp}
BOSS_SIZE = {size}
PROJECTILE_SIZE = {proj}
# run_boss ya está definido en boss_template y usará estas constantes
"""

def main():
    out_dir = os.path.dirname(__file__) or "."
    for n in range(0, 11):
        hp = 400 + n*200
        size = 140 + (n*6)
        proj = 12 + (n//3)*2
        content = TEMPLATE.format(n=n, hp=hp, size=size, proj=proj)
        path = os.path.join(out_dir, f"boss{n}.py")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    print("Generados boss0.py .. boss10.py (edítalos si quieres ajustar patrones/imagenes/música).")

if __name__ == "__main__":
    main()
