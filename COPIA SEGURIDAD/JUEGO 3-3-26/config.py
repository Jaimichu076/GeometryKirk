# config.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ASSETS_DIR = os.path.join(BASE_DIR, "assets")
ASSETS_IMG = os.path.join(ASSETS_DIR, "images")
ASSETS_AUDIO = os.path.join(ASSETS_DIR, "audio")

WIDTH, HEIGHT = 1100, 600
FPS = 60

# Física del jugador
PLAYER_SIZE = 64
GRAVITY = 1.0
JUMP_FORCE = -20
SPEED = 6
GROUND_Y = 500

# Colores
C_BG = (15, 15, 30)
C_TEXT = (255, 255, 255)
C_BTN_IDLE = (40, 40, 80)
C_BTN_HOVER = (60, 60, 120)

# Menu assets
MENU_BACKGROUND = os.path.join(ASSETS_IMG, "wallpaper.png")
MENU_MUSIC = os.path.join(ASSETS_AUDIO, "C418 - Aria Math.mp3")

# Logo compartido entre start y main
LOGO_IMG = os.path.join(ASSETS_IMG, "logogeometrykirk.png")

# Música del nivel
LEVEL_MUSIC = os.path.join(ASSETS_AUDIO, "level1_soundtrack.mp3")

# ---------------------------
# Descubrimiento automático de skins
# ---------------------------
_VALID_SKIN_EXT = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}

def _discover(folder, limit=150):
    if not folder or not os.path.isdir(folder):
        return []
    out = []
    for fn in sorted(os.listdir(folder)):
        _, ext = os.path.splitext(fn)
        if ext.lower() in _VALID_SKIN_EXT:
            out.append(os.path.join(folder, fn))
            if len(out) >= limit:
                break
    return out

# Skins de personaje
CHAR_SKINS_DIR = os.path.join(ASSETS_IMG, "skins", "characters")
CHAR_SKINS = _discover(CHAR_SKINS_DIR)
selected_character_skin_index = 0 if CHAR_SKINS else -1

def get_selected_character_skin_path():
    if 0 <= selected_character_skin_index < len(CHAR_SKINS):
        return CHAR_SKINS[selected_character_skin_index]
    return None

# Skins de avión
PLANE_SKINS_DIR = os.path.join(ASSETS_IMG, "skins", "planes")
PLANE_SKINS = _discover(PLANE_SKINS_DIR)
selected_plane_skin_index = 0 if PLANE_SKINS else -1

def get_selected_plane_skin_path():
    if 0 <= selected_plane_skin_index < len(PLANE_SKINS):
        return PLANE_SKINS[selected_plane_skin_index]
    return None

# Imagen placeholder
COMING_SOON_IMG = os.path.join(ASSETS_IMG, "coming_soon.png")

# Proyectiles
PROJ_PISTOL = os.path.join(ASSETS_IMG, "proj_pistol.png")
PROJ_SHOTGUN = os.path.join(ASSETS_IMG, "proj_shotgun.jpg")
PROJ_ROCKET = os.path.join(ASSETS_IMG, "proj_rocket.png")

# Iconos inventario
ICON_PISTOL = os.path.join(ASSETS_IMG, "icon_pistol.png")
ICON_SHOTGUN = os.path.join(ASSETS_IMG, "icon_shotgun.png")
ICON_ROCKET = os.path.join(ASSETS_IMG, "icon_rocket.png")

HEAL_PICKUP_IMG = os.path.join(ASSETS_IMG, "heal_cube.png")

# Explosiones
EXPLOSION_SOUND_BOSS0 = os.path.join(ASSETS_AUDIO, "explosion_boss0.wav")
EXPLOSION_SOUND_BOSS1 = os.path.join(ASSETS_AUDIO, "explosion_boss1.wav")
EXPLOSION_SOUND_BOSS2 = os.path.join(ASSETS_AUDIO, "explosion_boss2.wav")
EXPLOSION_SOUND_BOSS3 = os.path.join(ASSETS_AUDIO, "explosion_boss3.wav")
