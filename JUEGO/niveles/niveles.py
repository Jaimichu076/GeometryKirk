import pygame
import config
from niveles import nivel1
from niveles import nivel2
import os
import sys
import math
import random

from audio_manager import audio   # ← AÑADIDO

pygame.init()

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

font_title = pygame.font.SysFont("Arial Black", 70)
font_name = pygame.font.SysFont("Arial Black", 45)
font_small = pygame.font.SysFont("Arial", 26)

def draw_progress_bar(surface, x, y, width, percent, color):
    pygame.draw.rect(surface, (20, 20, 30), (x, y, width, 26), border_radius=12)
    fill = int(width * (percent / 100))
    pygame.draw.rect(surface, color, (x, y, fill, 26), border_radius=12)
    pygame.draw.rect(surface, (0, 0, 0), (x, y, width, 26), 3, border_radius=12)

    glow = pygame.Surface((width, 26), pygame.SRCALPHA)
    pygame.draw.rect(glow, (*color, 80), (0, 0, fill, 26), border_radius=12)
    surface.blit(glow, (x, y), special_flags=pygame.BLEND_PREMULTIPLIED)

class PlayButton:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.base_size = size
        self.scale = 1.0
        self.hover = False
        self.pulse_t = 0

    def draw(self, surf, dt):
        self.pulse_t += dt * 4
        pulse = 0.04 * math.sin(self.pulse_t * 2)
        target = 1.22 if self.hover else 1.05 + pulse
        self.scale += (target - self.scale) * 0.18
        s = int(self.base_size * self.scale)

        glow = pygame.Surface((s * 2, s * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 255, 0, 140), (s, s), s//2 + 12)
        surf.blit(glow, (self.x - s, self.y - s), special_flags=pygame.BLEND_PREMULTIPLIED)

        pygame.draw.circle(surf, (255, 255, 0), (self.x, self.y), s//2)
        pygame.draw.circle(surf, (0, 0, 0), (self.x, self.y), s//2, 5)

        pts = [
            (self.x - s//6, self.y - s//4),
            (self.x + s//3, self.y),
            (self.x - s//6, self.y + s//4),
        ]
        pygame.draw.polygon(surf, (255, 255, 255), pts)
        pygame.draw.polygon(surf, (0, 0, 0), pts, 4)

    def update_hover(self, mouse_pos):
        mx, my = mouse_pos
        self.hover = ((mx - self.x)**2 + (my - self.y)**2)**0.5 <= self.base_size//2

    def handle_click(self, mouse_pos):
        mx, my = mouse_pos
        return ((mx - self.x)**2 + (my - self.y)**2)**0.5 <= self.base_size//2

class ArrowButton:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.scale = 1.0
        self.hover = False
        self.pulse_t = 0

    def draw(self, surf, dt):
        self.pulse_t += dt * 3
        pulse = 0.03 * math.sin(self.pulse_t * 2)
        target = 1.25 if self.hover else 1.05 + pulse
        self.scale += (target - self.scale) * 0.2

        size = int(70 * self.scale)
        rect = pygame.Rect(0, 0, size, size)
        rect.center = (self.x, self.y)

        glow = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (120, 120, 255, 110), (size, size), size//2 + 8)
        surf.blit(glow, (rect.centerx - size, rect.centery - size), special_flags=pygame.BLEND_PREMULTIPLIED)

        pygame.draw.circle(surf, (40, 40, 80), rect.center, size//2)
        pygame.draw.circle(surf, (255, 255, 255), rect.center, size//2, 4)

        if self.direction == -1:
            pts = [
                (rect.centerx + size//4, rect.centery - size//3),
                (rect.centerx - size//4, rect.centery),
                (rect.centerx + size//4, rect.centery + size//3),
            ]
        else:
            pts = [
                (rect.centerx - size//4, rect.centery - size//3),
                (rect.centerx + size//4, rect.centery),
                (rect.centerx - size//4, rect.centery + size//3),
            ]

        pygame.draw.polygon(surf, (255, 255, 0), pts)
        pygame.draw.polygon(surf, (0, 0, 0), pts, 4)

    def update_hover(self, mouse_pos):
        mx, my = mouse_pos
        self.hover = ((mx - self.x)**2 + (my - self.y)**2)**0.5 <= 40

    def handle_click(self, mouse_pos):
        mx, my = mouse_pos
        return ((mx - self.x)**2 + (my - self.y)**2)**0.5 <= 40

def draw_animated_background(surface, t):
    w, h = surface.get_size()
    for y in range(0, h, 60):
        c = 40 + int(40 * math.sin(t * 0.7 + y * 0.03))
        pygame.draw.rect(surface, (10, c, 60 + c//3), (0, y, w, 60))
    for i in range(18):
        x = (i * 120 + int(t * 90)) % (w + 200) - 100
        y = 120 + int(40 * math.sin(t * 1.3 + i))
        alpha = 80 + int(60 * math.sin(t * 2 + i))
        pygame.draw.circle(surface, (0, 255, 255, alpha), (x, y), 6)

def transition_to_level(screen, clock, draw_last_frame_callback):
    w, h = screen.get_size()
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    duration = 650
    start = pygame.time.get_ticks()

    while True:
        now = pygame.time.get_ticks()
        t = (now - start) / duration
        if t > 1:
            t = 1

        draw_last_frame_callback()

        alpha = int(255 * t)
        overlay.fill((0, 0, 0, alpha))
        screen.blit(overlay, (0, 0))

        scale = 1 + 0.1 * t
        zoom_surf = pygame.transform.smoothscale(screen, (int(w * scale), int(h * scale)))
        zx = (w - zoom_surf.get_width()) // 2
        zy = (h - zoom_surf.get_height()) // 2
        screen.blit(zoom_surf, (zx, zy), special_flags=pygame.BLEND_MULT)

        pygame.display.flip()
        clock.tick(config.FPS)

        if t >= 1:
            break

def run_levels_menu(screen, clock):

    audio.resume()   # ← AÑADIDO (reanudar música del menú)

    levels = [
        {"name": "Maincra",          "difficulty": "Easy",   "color": (0, 200, 255), "progress": 0},
        {"name": "Bibi",             "difficulty": "Easy",   "color": (0, 200, 255), "progress": 0},
        {"name": "Epictetus Island", "difficulty": "Normal", "color": (0, 255, 0),   "progress": 0},
        {"name": "Brainrots",        "difficulty": "Normal", "color": (0, 255, 0),   "progress": 0},
        {"name": "Zona Gemelos",     "difficulty": "Hard",   "color": (255, 200, 0), "progress": 0},
        {"name": "LQSA",             "difficulty": "Hard",   "color": (255, 200, 0), "progress": 0},
        {"name": "COMING SOON",      "difficulty": "Harder", "color": (255, 100, 0), "progress": 0},
        {"name": "COMING SOON",      "difficulty": "Harder", "color": (255, 100, 0), "progress": 0},
        {"name": "COMING SOON",      "difficulty": "Insane", "color": (255, 0, 0),   "progress": 0},
        {"name": "COMING SOON",      "difficulty": "Harder", "color": (255, 100, 0), "progress": 0},
        {"name": "COMING SOON",      "difficulty": "Insane", "color": (255, 0, 0),   "progress": 0},
    ]

    current = 0

    play_button = PlayButton(config.WIDTH//2 + 250, config.HEIGHT//2 + 40, 130)
    arrow_left = ArrowButton(config.WIDTH//2 - 450, config.HEIGHT//2 + 20, -1)
    arrow_right = ArrowButton(config.WIDTH//2 + 450, config.HEIGHT//2 + 20, +1)

    running = True
    start_time = pygame.time.get_ticks()

    last_frame = pygame.Surface((config.WIDTH, config.HEIGHT))

    while running:
        dt = clock.tick(config.FPS) / 1000.0
        t = (pygame.time.get_ticks() - start_time) / 1000.0
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                audio.play_sfx(config.BUTTON_SOUND)   # ← AÑADIDO
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                audio.play_sfx(config.BUTTON_SOUND)   # ← AÑADIDO

                if arrow_left.handle_click(mouse_pos):
                    current = (current - 1) % len(levels)

                if arrow_right.handle_click(mouse_pos):
                    current = (current + 1) % len(levels)

                if play_button.handle_click(mouse_pos):
                    
                    # NIVEL 1
                    if current == 0:
                        audio.pause()

                        def draw_last():
                            screen.blit(last_frame, (0, 0))
                        last_frame.blit(screen, (0, 0))
                        transition_to_level(screen, clock, draw_last)

                        nivel1.run_level(screen, clock)

                        audio.resume()
                        start_time = pygame.time.get_ticks()

                    # NIVEL 2
                    if current == 1:
                        audio.pause()

                        def draw_last():
                            screen.blit(last_frame, (0, 0))
                        last_frame.blit(screen, (0, 0))
                        transition_to_level(screen, clock, draw_last)

                        nivel2.run_level(screen, clock)

                        audio.resume()
                        start_time = pygame.time.get_ticks()

                

        draw_animated_background(screen, t)

        title = font_title.render("SELECCIONAR NIVEL", True, (0, 255, 200))
        shadow = font_title.render("SELECCIONAR NIVEL", True, (0, 0, 0))
        screen.blit(shadow, (config.WIDTH//2 - title.get_width()//2 + 6, 40 + 6))
        screen.blit(title, (config.WIDTH//2 - title.get_width()//2, 40))

        card = pygame.Rect(config.WIDTH//2 - 400, 150, 800, 350)

        shadow_surf = pygame.Surface((card.width + 30, card.height + 30), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 160), shadow_surf.get_rect(), border_radius=30)
        screen.blit(shadow_surf, (card.x - 15, card.y - 8))

        inner_rect = card.inflate(-20, -20)
        offset = int(12 * math.sin(t * 1.4))
        base_color = (40 + offset, 40, 90 + offset)
        pygame.draw.rect(screen, base_color, card, border_radius=26)
        pygame.draw.rect(screen, (0, 0, 0), card, 6, border_radius=26)

        glow_card = pygame.Surface((card.width, card.height), pygame.SRCALPHA)
        pygame.draw.rect(glow_card, (0, 255, 255, 60), glow_card.get_rect(), border_radius=26)
        screen.blit(glow_card, card.topleft, special_flags=pygame.BLEND_ADD)

        pygame.draw.rect(screen, (60, 60, 130), inner_rect, border_radius=20)

        lvl = levels[current]

        name = font_name.render(lvl["name"], True, (255, 255, 255))
        screen.blit(name, (card.x + 40, card.y + 20))

        diff = font_small.render(lvl["difficulty"], True, lvl["color"])
        screen.blit(diff, (card.x + 40, card.y + 80))

        nm = font_small.render("NORMAL MODE", True, (255, 255, 255))
        screen.blit(nm, (card.x + 40, card.y + 150))
        draw_progress_bar(screen, card.x + 40, card.y + 185, 350, lvl["progress"], (0, 255, 0))

        dots_y = card.bottom - 40
        total = len(levels)
        spacing = 26
        total_width = (total - 1) * spacing
        start_x = config.WIDTH//2 - total_width//2

        for i in range(total):
            r = 6
            x = start_x + i * spacing
            color = (200, 200, 200) if i != current else (0, 255, 200)
            pygame.draw.circle(screen, (0, 0, 0), (x, dots_y + 2), r + 3)
            pygame.draw.circle(screen, color, (x, dots_y), r)

        arrow_left.update_hover(mouse_pos)
        arrow_left.draw(screen, dt)

        arrow_right.update_hover(mouse_pos)
        arrow_right.draw(screen, dt)

        play_button.update_hover(mouse_pos)
        play_button.draw(screen, dt)

        pygame.display.flip()
        audio.update()   # ← AÑADIDO
