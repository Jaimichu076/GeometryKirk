import pygame
import config
import importlib
import os
import sys
import math
from audio_manager import audio

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

boss_modules = {}
for i in range(0, 11):
    name = f"boss{i}"
    try:
        boss_modules[name] = importlib.import_module(f"boss.{name}")
    except Exception:
        boss_modules[name] = None

pygame.init()
font_title = pygame.font.SysFont("Arial Black", 64)
font_btn = pygame.font.SysFont("Arial", 28)
font_small = pygame.font.SysFont("Arial", 20)

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

class MenuButton:
    def __init__(self, rect, text, action, available=True):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.action = action
        self.hover = False
        self.available = available
        self.hover_alpha = 0  # transición suave

    def draw(self, surf, offset_y=0):
        r = self.rect.move(0, offset_y)

        if not self.available:
            base_color = (40, 40, 40)
            border_color = (90, 90, 90)
            text_color = (150, 150, 150)
        else:
            base_color = config.C_BTN_IDLE
            border_color = (255, 255, 255)
            text_color = config.C_TEXT

        if self.hover:
            self.hover_alpha = min(255, self.hover_alpha + 20)
        else:
            self.hover_alpha = max(0, self.hover_alpha - 20)

        hover_overlay = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
        pygame.draw.rect(
            hover_overlay,
            (0, 255, 255, int(self.hover_alpha * 0.35)),
            hover_overlay.get_rect(),
            border_radius=12
        )
        surf.blit(hover_overlay, r.topleft)

        pygame.draw.rect(surf, base_color, r, border_radius=12)
        pygame.draw.rect(surf, border_color, r, 3, border_radius=12)

        txt = font_btn.render(self.text, True, text_color)
        surf.blit(txt, (r.x + 20, r.y + r.height//2 - txt.get_height()//2))

    def update(self, mouse_pos, offset_y=0):
        r = self.rect.move(0, offset_y)
        self.hover = r.collidepoint(mouse_pos)

def run_otros(screen, clock):
    audio.resume()

    boss_names = [
        "Tutorial – Silver-Russell",
        "Nivel 1 – El Mago",
        "Nivel 2 – SAPOOOOOOOOOOO",
        "Nivel 3 – Baby oil",
        "Nivel 4 – COMING SOON",
        "Nivel 5 – COMING SOON",
        "Nivel 6 – COMING SOON",
        "Nivel 7 – COMING SOON",
        "Nivel 8 – COMING SOON",
        "Nivel 9 – COMING SOON",
        "Nivel 10 – COMING SOON"
    ]
    labels = [(boss_names[i], f"boss{i}") for i in range(11)]

    panel = pygame.Rect(
        config.WIDTH//2 - 420,
        150,
        840,
        450
    )

    btn_w, btn_h = 640, 62
    start_x = panel.centerx - btn_w//2
    start_y = panel.y + 40
    gap = 95  # MÁS SEPARACIÓN ENTRE BOTONES

    buttons = []
    for i, (txt, act) in enumerate(labels):
        r = (start_x, start_y + i*gap, btn_w, btn_h)
        available = boss_modules.get(act) is not None
        buttons.append(MenuButton(r, txt, act, available=available))

    offset_y = 0
    content_height = start_y + len(buttons)*gap - panel.y
    view_height = panel.height - 80
    max_offset = max(0, content_height - view_height)
    scroll_speed = 40

    bar_x = panel.right - 26
    bar_w = 10
    bar_h = view_height
    bar_rect = pygame.Rect(bar_x, panel.y + 40, bar_w, bar_h)

    running = True
    start_time = pygame.time.get_ticks()

    while running:
        dt = clock.tick(config.FPS) / 1000.0
        t = (pygame.time.get_ticks() - start_time) / 1000.0
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); raise SystemExit

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    audio.play_sfx(config.BUTTON_SOUND)
                    running = False
                if event.key == pygame.K_DOWN:
                    offset_y = max(offset_y - scroll_speed, -max_offset)
                if event.key == pygame.K_UP:
                    offset_y = min(offset_y + scroll_speed, 0)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    audio.play_sfx(config.BUTTON_SOUND)
                    for b in buttons:
                        if b.rect.move(0, offset_y).collidepoint(mouse_pos):
                            if b.available:
                                module = boss_modules.get(b.action)
                                try:
                                    module.run_boss(screen, clock)
                                except Exception as e:
                                    print(f"ERROR ejecutando {b.action}.run_boss():", e)
                            else:
                                msg = font_small.render(f"{b.action} no disponible.", True, config.C_TEXT)
                                screen.blit(msg, (config.WIDTH//2 - msg.get_width()//2, config.HEIGHT//2))
                                pygame.display.flip()
                                pygame.time.delay(700)
                elif event.button == 4:
                    offset_y = min(offset_y + scroll_speed, 0)
                elif event.button == 5:
                    offset_y = max(offset_y - scroll_speed, -max_offset)

        draw_animated_background(screen, t)

        title = font_title.render("MINIJUEGOS / BOSS", True, (0, 255, 200))
        shadow = font_title.render("MINIJUEGOS / BOSS", True, (0, 0, 0))
        screen.blit(shadow, (config.WIDTH//2 - title.get_width()//2 + 4, 44))
        screen.blit(title, (config.WIDTH//2 - title.get_width()//2, 40))

        shadow_surf = pygame.Surface((panel.width + 30, panel.height + 30), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 160), shadow_surf.get_rect(), border_radius=30)
        screen.blit(shadow_surf, (panel.x - 15, panel.y - 8))

        inner = panel.inflate(-20, -20)
        offset = int(12 * math.sin(t * 1.4))
        base_color = (40 + offset, 40, 90 + offset)
        pygame.draw.rect(screen, base_color, panel, border_radius=26)
        pygame.draw.rect(screen, (0, 0, 0), panel, 6, border_radius=26)

        glow_panel = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
        pygame.draw.rect(glow_panel, (0, 255, 255, 60), glow_panel.get_rect(), border_radius=26)
        screen.blit(glow_panel, panel.topleft, special_flags=pygame.BLEND_ADD)

        pygame.draw.rect(screen, (60, 60, 130), inner, border_radius=20)

        clip = screen.get_clip()
        screen.set_clip(inner)

        for b in buttons:
            b.update(mouse_pos, offset_y)
            b.draw(screen, offset_y)

        screen.set_clip(clip)

        pygame.draw.rect(screen, (40, 40, 60), bar_rect, border_radius=6)
        if max_offset > 0:
            thumb_h = max(30, int(bar_h * (view_height / content_height)))
            thumb_y = int(bar_rect.y + (-offset_y / max_offset) * (bar_h - thumb_h))
            thumb_rect = pygame.Rect(bar_x, thumb_y, bar_w, thumb_h)
            pygame.draw.rect(screen, (180, 180, 180), thumb_rect, border_radius=6)
        else:
            pygame.draw.rect(screen, (120, 120, 120), bar_rect, border_radius=6)

        hint = font_small.render("ESC: volver | Rueda / ↑↓: desplazarse", True, config.C_TEXT)
        screen.blit(hint, (config.WIDTH//2 - hint.get_width()//2, config.HEIGHT - 40))

        pygame.display.flip()
