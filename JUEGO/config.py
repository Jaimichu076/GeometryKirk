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
JUMP_FORCE = -16
SPEED = 6
GROUND_Y = 500

# Colores
C_BG = (15, 15, 30)
C_TEXT = (255, 255, 255)
C_BTN_IDLE = (40, 40, 80)
C_BTN_HOVER = (60, 60, 120)

# Menu assets
MENU_BACKGROUND = os.path.join(ASSETS_IMG, "wallpaper.jpg")
MENU_MUSIC = os.path.join(ASSETS_AUDIO, "C418 - Aria Math.mp3")

# Música del nivel
LEVEL_MUSIC = os.path.join(ASSETS_AUDIO, "level1.mp3")

# ---------------------------
# Skins: ahora se descubren automáticamente en assets/images/skins
# ---------------------------
SKINS_DIR = os.path.join(ASSETS_IMG, "skins")
_VALID_SKIN_EXT = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}

def _discover_skins(folder, limit=150):
    """Devuelve una lista ordenada de rutas absolutas a imágenes dentro de folder.
       Limita a `limit` entradas para garantizar capacidad máxima."""
    if not folder or not os.path.isdir(folder):
        return []
    files = []
    for fn in sorted(os.listdir(folder)):
        _, ext = os.path.splitext(fn)
        if ext.lower() in _VALID_SKIN_EXT:
            files.append(os.path.join(folder, fn))
            if len(files) >= limit:
                break
    return files

# Lista de skins detectadas automáticamente (máx 150)
SKINS = _discover_skins(SKINS_DIR, limit=150)

# Índice seleccionado (por defecto 0 si hay skins)
selected_skin_index = 0 if SKINS else -1

def get_selected_skin_path():
    """Devuelve la ruta de la skin seleccionada o None si no hay ninguna."""
    if 0 <= selected_skin_index < len(SKINS):
        return SKINS[selected_skin_index]
    return None

# Imagen que se mostrará en el cubo si no hay skins (opcional)
COMING_SOON_IMG = os.path.join(ASSETS_IMG, "coming_soon.png")

# ---------------------------
# Weapon / projectile images (por defecto)
# ---------------------------
PROJ_PISTOL = os.path.join(ASSETS_IMG, "proj_pistol.png")
PROJ_SHOTGUN = os.path.join(ASSETS_IMG, "proj_shotgun.png")
PROJ_ROCKET = os.path.join(ASSETS_IMG, "proj_rocket.png")

# Inventory icons (opcional)
ICON_PISTOL = os.path.join(ASSETS_IMG, "icon_pistol.png")
ICON_SHOTGUN = os.path.join(ASSETS_IMG, "icon_shotgun.png")
ICON_ROCKET = os.path.join(ASSETS_IMG, "icon_rocket.png")

# Default heal pickup image
HEAL_PICKUP_IMG = os.path.join(ASSETS_IMG, "heal_cube.png")

# Rutas a sonidos de explosión por boss (ajusta nombres de archivo en assets/audio)
EXPLOSION_SOUND_BOSS0 = os.path.join(ASSETS_AUDIO, "explosion_boss0.wav")
EXPLOSION_SOUND_BOSS1 = os.path.join(ASSETS_AUDIO, "explosion_boss1.wav")
EXPLOSION_SOUND_BOSS2 = os.path.join(ASSETS_AUDIO, "explosion_boss2.wav")
EXPLOSION_SOUND_BOSS3 = os.path.join(ASSETS_AUDIO, "explosion_boss3.wav")
