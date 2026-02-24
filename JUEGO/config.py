# config.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ASSETS_DIR = os.path.join(BASE_DIR, "assets")
ASSETS_IMG = os.path.join(ASSETS_DIR, "images")
ASSETS_AUDIO = os.path.join(ASSETS_DIR, "audio")

WIDTH, HEIGHT = 1100, 600
FPS = 60

# Colores
C_BG = (15, 15, 30)
C_TEXT = (255, 255, 255)
C_BTN_IDLE = (40, 40, 80)
C_BTN_HOVER = (60, 60, 120)

# Menu assets (pon tus archivos en assets/)
MENU_BACKGROUND = os.path.join(ASSETS_IMG, "wallpaper.jpg")
MENU_MUSIC = os.path.join(ASSETS_AUDIO, "C418 - Aria Math.mp3")

# Skins (rutas de ejemplo; cámbialas por tus imágenes)
SKINS = [
    os.path.join(ASSETS_IMG, "Diddy.jpg"),
    os.path.join(ASSETS_IMG, "Epstein.jpg"),
    os.path.join(ASSETS_IMG, "Maduro.jpg"),
    os.path.join(ASSETS_IMG, "skin_3.jpg"),
]

selected_skin_index = 0

def get_selected_skin_path():
    if 0 <= selected_skin_index < len(SKINS):
        return SKINS[selected_skin_index]
    return None
