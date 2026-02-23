import pygame
import sys
import math
import random
import os

import config
import skins
import otros
import niveles

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
pygame.display.set_caption("GEOMETRY KIRK - MAIN MENU")
clock = pygame.time.Clock()

font_title = pygame.font.SysFont("Arial Black", 95)

# -----------------------------
# CARGAR FONDO
# -----------------------------
background_img = None
if os.path.exists(config.MENU_BACKGROUND):
    try:
        background_img = pygame.image.load(config.MENU_BACKGROUND).convert()
        background_img = pygame.transform.scale(background_img, (config.WIDTH, config.HEIGHT))
    except:
        background_img = None

# -----------------------------
# CARGAR MÚSICA DEL MENÚ (solo aquí)
# -----------------------------
if os.path.exists(config.MENU_MUSIC):
    try:
        pygame.mixer.music.load(config.MENU_MUSIC)
        pygame.mixer.music.set_volume(0.6)
        pygame.mixer.music.play(-1)
    except:
        pass

# -----------------------------
# ICONOS
# -----------------------------
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

# -----------------------------
# BOTÓN REDONDO
# -----------------------------
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

        pygame.draw.circle(surf, (40, 40, 80), (x, y), r)
        pygame.draw.circle(surf, (255, 255, 255), (x, y), r, 4)

        self.icon(surf, (x, y), int(r * 1.2))

    def update_hover(self, mouse_pos):
        mx, my = mouse_pos
        x, y = self.center
        self.hover = (mx - x)**2 + (my - y)**2 <= self.radius**2

    def handle_click(self, mouse_pos):
        mx, my = mouse_pos
        x, y = self.center
        if (mx - x)**2 + (my - y)**2 <= self.radius**2:
            return self.action
        return None

# -----------------------------
# PARTICULAS
# -----------------------------
class Particle:
    def __init__(self):
        self.x = random.randint(0, config.WIDTH)
        self.y = random.randint(0, config.HEIGHT)
        self.size = random.randint(3, 7)
        self.speed = random.uniform(0.3, 1.0)
        self.alpha = random.randint(80, 150)

    def update(self):
        self.y += self.speed
        if self.y > config.HEIGHT:
            self.y = -10
            self.x = random.randint(0, config.WIDTH)

    def draw(self, surf):
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        s.fill((0, 255, 200, self.alpha))
        surf.blit(s, (self.x, self.y))

particles = [Particle() for _ in range(50)]

# -----------------------------
# MENÚ PRINCIPAL
# -----------------------------
def main_menu():
    center_y = config.HEIGHT // 2 + 40
    spacing = 180

    buttons = [
        RoundButton((config.WIDTH//2 - spacing, center_y), 70, "SKINS", draw_skin_icon),
        RoundButton((config.WIDTH//2, center_y), 90, "LEVELS", draw_play_icon),
        RoundButton((config.WIDTH//2 + spacing, center_y), 70, "OTHERS", draw_settings_icon),
    ]

    t = 0

    running = True
    while running:
        clock.tick(config.FPS)
        mouse_pos = pygame.mouse.get_pos()
        t += 0.05

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for b in buttons:
                    action = b.handle_click(mouse_pos)
                    if action == "LEVELS":
                        niveles.run_levels_menu(screen, clock)
                    elif action == "SKINS":
                        skins.run_skins_menu(screen, clock)
                    elif action == "OTHERS":
                        otros.run_otros(screen, clock)

        # Fondo
        if background_img:
            screen.blit(background_img, (0, 0))
        else:
            screen.fill(config.C_BG)

        # Líneas diagonales animadas
        for i in range(0, config.WIDTH, 80):
            pygame.draw.line(
                screen,
                (60, 0, 120),
                (i + (t * 20) % 80, 0),
                (i - config.HEIGHT + (t * 20) % 80, config.HEIGHT),
                4
            )

        # Partículas
        for p in particles:
            p.update()
            p.draw(screen)

        # Título animado
        bounce = int(math.sin(t) * 10)

        title = font_title.render("GEOMETRY KIRK", True, config.C_TEXT)
        shadow = font_title.render("GEOMETRY KIRK", True, (0, 0, 0))

        screen.blit(shadow, (config.WIDTH//2 - title.get_width()//2 + 6,
                             80 + bounce + 6))
        screen.blit(title, (config.WIDTH//2 - title.get_width()//2,
                            80 + bounce))

        # Botones
        for b in buttons:
            b.update_hover(mouse_pos)
            b.draw(screen)

        pygame.display.flip()

if __name__ == "__main__":
    main_menu()




