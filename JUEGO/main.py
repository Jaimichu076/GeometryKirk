# main.py — menú principal con logo desde config
import pygame
import sys
import os

import config
import skins
import otros
import niveles

pygame.init()
try:
    pygame.mixer.init()
except Exception:
    pass

screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
pygame.display.set_caption("GEOMETRY KIRK - MAIN MENU")
clock = pygame.time.Clock()

# Cargar logo desde config
logo_img = None
if os.path.exists(config.LOGO_IMG):
    try:
        logo_img = pygame.image.load(config.LOGO_IMG).convert_alpha()
        logo_img = pygame.transform.smoothscale(
            logo_img,
            (int(config.WIDTH * 0.65), int(config.HEIGHT * 0.22))
        )
    except Exception:
        logo_img = None

# Fondo
background_img = None
if os.path.exists(config.MENU_BACKGROUND):
    try:
        background_img = pygame.image.load(config.MENU_BACKGROUND).convert()
        background_img = pygame.transform.scale(background_img, (config.WIDTH, config.HEIGHT))
    except Exception:
        background_img = None

# Música
try:
    if os.path.exists(config.MENU_MUSIC):
        pygame.mixer.music.load(config.MENU_MUSIC)
        pygame.mixer.music.set_volume(0.6)
        pygame.mixer.music.play(-1)
except Exception:
    pass

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

def main_menu():
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

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for b in buttons:
                    action = b.handle_click(mouse_pos)
                    if action == "LEVELS":
                        niveles.run_levels_menu(screen, clock)
                    elif action == "SKINS":
                        skins.run_skins_menu(screen, clock)
                    elif action == "OTHERS":
                        otros.run_otros(screen, clock)

        if background_img:
            screen.blit(background_img, (0, 0))
        else:
            screen.fill(config.C_BG)

        if logo_img:
            screen.blit(logo_img, (config.WIDTH//2 - logo_img.get_width()//2, 60))

        for b in buttons:
            b.update_hover(mouse_pos)
            b.draw(screen)

        pygame.display.flip()

if __name__ == "__main__":
    main_menu()
