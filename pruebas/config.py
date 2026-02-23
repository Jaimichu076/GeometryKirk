import os

# Tamaño de ventana
WIDTH, HEIGHT = 1100, 600
GROUND_Y = HEIGHT - 100
FPS = 60

# Físicas
PLAYER_SIZE = 50
GRAVITY = 0.8
JUMP_FORCE = -14.5
SPEED = 8.5

# Colores
C_BG = (15, 15, 30)
C_GROUND = (25, 25, 50)
C_LINE = (0, 255, 200)
C_TEXT = (255, 255, 255)
C_BTN_IDLE = (40, 40, 80)
C_BTN_HOVER = (60, 60, 120)

# Rutas base
ASSETS_IMG = os.path.join("assets", "images")
ASSETS_AUDIO = os.path.join("assets", "audio")

# Fondo del menú
MENU_BACKGROUND = os.path.join(ASSETS_IMG, "wallpaper.jpg")

# Música del menú
MENU_MUSIC = os.path.join(ASSETS_AUDIO, "C418 - Aria Math (Minecraft Vol. ...).mp3")

# Música del nivel
LEVEL_MUSIC = os.path.join(ASSETS_AUDIO, "wearecharliekirk.mp3")

# Skins disponibles
SKINS = [
    os.path.join(ASSETS_IMG, "Epstein.jpg"),
    os.path.join(ASSETS_IMG, "Diddy.jpg"),
    os.path.join(ASSETS_IMG, "Maduro.jpg"),
]

selected_skin_index = 0

def get_selected_skin_path():
    if 0 <= selected_skin_index < len(SKINS):
        return SKINS[selected_skin_index]
    return None

