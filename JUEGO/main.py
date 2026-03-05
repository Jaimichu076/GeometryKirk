# main.py — menú principal con iconos avanzados y animación
import pygame
import sys 
import os

import config
import skins
import otros
from niveles import niveles
import perfil
import notas

from audio_manager import audio   # ← AUDIO GLOBAL

pygame.init()

# === FUNCIÓN UNIVERSAL PARA CARGAR RECURSOS ===
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
pygame.display.set_caption("GEOMETRY KIRK - MAIN MENU")
clock = pygame.time.Clock()

# Cargar logo
logo_img = None
logo_path = resource_path(config.LOGO_IMG)
if os.path.exists(logo_path):
    try:
        logo_img = pygame.image.load(logo_path).convert_alpha()
        logo_img = pygame.transform.smoothscale(
            logo_img,
            (int(config.WIDTH * 0.65), int(config.HEIGHT * 0.22))
        )
    except Exception:
        logo_img = None

# Fondo
background_img = None
bg_path = resource_path(config.MENU_BACKGROUND)
if os.path.exists(bg_path):
    try:
        background_img = pygame.image.load(bg_path).convert()
        background_img = pygame.transform.scale(background_img, (config.WIDTH, config.HEIGHT))
    except Exception:
        background_img = None


# === ICONOS GENERADOS AUTOMÁTICAMENTE (CALIDAD ALTA) ===

def draw_icon_perfil(size, hover=False):
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    glow = 12 if hover else 6
    pygame.draw.circle(surf, (255, 255, 0, 80), (size//2, size//2), size//2 + glow)
    pygame.draw.circle(surf, (255, 255, 0), (size//2, size//2 - 10), size//4)
    pygame.draw.rect(surf, (255, 255, 0), (size//4, size//2, size//2, size//3), border_radius=12)
    pygame.draw.circle(surf, (0, 0, 0), (size//2, size//2 - 10), size//4, 3)
    pygame.draw.rect(surf, (0, 0, 0), (size//4, size//2, size//2, size//3), 3, border_radius=12)
    return surf

def draw_icon_notas(size, hover=False):
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    glow = 12 if hover else 6
    pygame.draw.circle(surf, (255, 255, 255, 80), (size//2, size//2), size//2 + glow)
    pygame.draw.rect(surf, (255, 255, 255), (size*0.2, size*0.15, size*0.6, size*0.7), border_radius=8)
    pygame.draw.rect(surf, (0, 0, 0), (size*0.2, size*0.15, size*0.6, size*0.7), 3, border_radius=8)
    for i in range(4):
        pygame.draw.line(surf, (0, 0, 0), (size*0.28, size*0.28 + i*size*0.13), (size*0.72, size*0.28 + i*size*0.13), 3)
    return surf

ICON_SIZE = 70
perfil_hover = False
notas_hover = False

perfil_rect = pygame.Rect(20, config.HEIGHT - ICON_SIZE - 20, ICON_SIZE, ICON_SIZE)
notas_rect = pygame.Rect(110, config.HEIGHT - ICON_SIZE - 20, ICON_SIZE, ICON_SIZE)

# === ICONOS DE LOS BOTONES PRINCIPALES ===

def draw_play_icon(surf, center, size):
    x, y = center
    pts = [(x - size//3, y - size//2), (x + size//2, y), (x - size//3, y + size//2)]
    pygame.draw.polygon(surf, (255, 255, 0), pts)
    pygame.draw.polygon(surf, (0, 0, 0), pts, 4)

def draw_skin_icon(surf, center, size):
    x, y = center
    rect = pygame.Rect(x - size//2, y - size//2, size, size)
    pygame.draw.rect(surf, (0, 255, 200), rect, border_radius=8)
    pygame.draw.rect(surf, (0, 0, 0), rect, 4, border_radius=8)

def draw_settings_icon(surf, center, size):
    x, y = center
    pygame.draw.circle(surf, (255, 150, 0), (x, y), size//2)
    pygame.draw.circle(surf, (0, 0, 0), (x, y), size//2, 4)

class RoundButton:
    def __init__(self, center, radius, action, icon):
        self.center = center
        self.radius = radius
        self.action = action
        self.icon = icon
        self.hover = False
        self.scale = 1.0

    def draw(self, surf):
        target = 1.15 if self.hover else 1.0
        self.scale += (target - self.scale) * 0.15
        r = int(self.radius * self.scale)
        x, y = self.center
        pygame.draw.circle(surf, config.C_BTN_IDLE, (x, y), r)
        pygame.draw.circle(surf, (255, 255, 255), (x, y), r, 4)
        self.icon(surf, (x, y), int(r * 1.2))

    def update_hover(self, mouse_pos):
        mx, my = mouse_pos
        x, y = self.center
        self.hover = (mx - x)**2 + (my - y)**2 <= (self.radius)**2

    def handle_click(self, mouse_pos):
        mx, my = mouse_pos
        x, y = self.center
        if (mx - x)**2 + (my - y)**2 <= (self.radius)**2:
            return self.action
        return None


# ============================
#   MENÚ PRINCIPAL ARREGLADO
# ============================
def main_menu():
    global perfil_hover, notas_hover

    # ARRANCAR MÚSICA DEL MENÚ SI NO SUENA NADA
    if not pygame.mixer.music.get_busy():
        audio.play_random_menu_music()
    else:
        audio.resume()

    center_y = config.HEIGHT // 2 + 40
    spacing = 180

    buttons = [
        RoundButton((config.WIDTH//2 - spacing, center_y), 70, "SKINS", draw_skin_icon),
        RoundButton((config.WIDTH//2, center_y), 90, "LEVELS", draw_play_icon),
        RoundButton((config.WIDTH//2 + spacing, center_y), 70, "OTHERS", draw_settings_icon),
    ]

    running = True
    while running:
        clock.tick(config.FPS)
        mouse_pos = pygame.mouse.get_pos()

        perfil_hover = perfil_rect.collidepoint(mouse_pos)
        notas_hover = notas_rect.collidepoint(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                audio.play_sfx(config.BUTTON_SOUND)

                for b in buttons:
                    action = b.handle_click(mouse_pos)
                    if action == "LEVELS":
                        niveles.run_levels_menu(screen, clock)
                    elif action == "SKINS":
                        skins.run_skins_menu(screen, clock)
                    elif action == "OTHERS":
                        otros.run_otros(screen, clock)

                if perfil_rect.collidepoint(mouse_pos):
                    perfil.run_perfil(screen, clock)

                if notas_rect.collidepoint(mouse_pos):
                    notas.run_notas(screen, clock)

        if background_img:
            screen.blit(background_img, (0, 0))
        else:
            screen.fill(config.C_BG)

        if logo_img:
            screen.blit(logo_img, (config.WIDTH//2 - logo_img.get_width()//2, 60))

        for b in buttons:
            b.update_hover(mouse_pos)
            b.draw(screen)

        perfil_icon_final = draw_icon_perfil(ICON_SIZE, perfil_hover)
        notas_icon_final = draw_icon_notas(ICON_SIZE, notas_hover)

        screen.blit(perfil_icon_final, perfil_rect)
        screen.blit(notas_icon_final, notas_rect)

        pygame.display.flip()
        audio.update()   # ← CAMBIO DE CANCIÓN AUTOMÁTICO


if __name__ == "__main__":
    main_menu()
