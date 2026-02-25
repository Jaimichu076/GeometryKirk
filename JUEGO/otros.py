# otros.py
import pygame
import config
import importlib

boss_modules = {}
for i in range(0, 11):
    name = f"boss{i}"
    try:
        boss_modules[name] = importlib.import_module(f"boss.{name}")
    except Exception:
        boss_modules[name] = None

pygame.init()
font_title = pygame.font.SysFont("Arial Black", 56)
font_btn = pygame.font.SysFont("Arial", 26)
font_small = pygame.font.SysFont("Arial", 18)

class MenuButton:
    def __init__(self, rect, text, action, available=True):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.action = action
        self.hover = False
        self.available = available

    def draw(self, surf, offset_y=0):
        r = self.rect.move(0, offset_y)
        color = config.C_BTN_HOVER if self.hover else config.C_BTN_IDLE
        if not self.available:
            color = (30, 30, 30)
        pygame.draw.rect(surf, color, r, border_radius=10)
        pygame.draw.rect(surf, (255,255,255), r, 3, border_radius=10)
        txt = font_btn.render(self.text, True, config.C_TEXT if self.available else (160,160,160))
        surf.blit(txt, (r.x + 20, r.y + r.height//2 - txt.get_height()//2))

    def update(self, mouse_pos, offset_y=0):
        r = self.rect.move(0, offset_y)
        self.hover = r.collidepoint(mouse_pos)

def run_otros(screen, clock):
    btn_w, btn_h = 560, 56
    start_x = config.WIDTH//2 - btn_w//2
    start_y = 140
    gap = 72

    boss_names = [
    "Tutorial – Silver-Russell",           # boss0
    "Nivel 1 – El Mago",                   # boss1
    "Nivel 2 – SAPOOOOOOOOOOO",            # boss2
    "Nivel 3 – Baby oil",                  # boss3
    "Nivel 4 – Amego",                     # boss4 (Amego)
    "Nivel 5 – COMING SOON",               # boss5
    "Nivel 6 – COMING SOON",               # boss6
    "Nivel 7 – COMING SOON",               # boss7
    "Nivel 8 – COMING SOON",               # boss8
    "Nivel 9 – COMING SOON",               # boss9
    "Nivel 10 – COMING SOON"               # boss10 
    ] 

    labels = []
    for i in range(0, 11):
        labels.append((boss_names[i], f"boss{i}"))


    buttons = []
    for i, (txt, act) in enumerate(labels):
        r = (start_x, start_y + i*gap, btn_w, btn_h)
        available = boss_modules.get(act) is not None
        buttons.append(MenuButton(r, txt, act, available=available))

    offset_y = 0
    content_height = start_y + len(buttons)*gap + 40
    view_height = config.HEIGHT - 120
    max_offset = max(0, content_height - view_height)
    scroll_speed = 40

    bar_x = start_x + btn_w + 16
    bar_w = 12
    bar_h = view_height - 20
    bar_rect = pygame.Rect(bar_x, 100, bar_w, bar_h)

    running = True
    while running:
        clock.tick(config.FPS)
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); raise SystemExit

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                    # 🔥 VOLVER A PONER LA MÚSICA DEL MENÚ
                    try:
                        pygame.mixer.music.load(config.MENU_MUSIC)
                        pygame.mixer.music.set_volume(0.6)
                        pygame.mixer.music.play(-1)
                    except:
                        pass

                if event.key == pygame.K_DOWN:
                    offset_y = max(offset_y - scroll_speed, -max_offset)
                if event.key == pygame.K_UP:
                    offset_y = min(offset_y + scroll_speed, 0)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for b in buttons:
                        if b.rect.move(0, offset_y).collidepoint(mouse_pos):
                            if b.available:
                                module = boss_modules.get(b.action)
                                try:
                                    module.run_boss(screen, clock)
                                except Exception as e:
                                    print(f"ERROR ejecutando {b.action}.run_boss():", e)
                            else:
                                screen.fill(config.C_BG)
                                title = font_title.render("MINIJUEGOS / BOSS", True, config.C_TEXT)
                                screen.blit(title, (config.WIDTH//2 - title.get_width()//2, 40))
                                msg = font_small.render(f"{b.action} no disponible.", True, config.C_TEXT)
                                screen.blit(msg, (config.WIDTH//2 - msg.get_width()//2, config.HEIGHT//2))
                                pygame.display.flip()
                                pygame.time.delay(700)

                elif event.button == 4:
                    offset_y = min(offset_y + scroll_speed, 0)
                elif event.button == 5:
                    offset_y = max(offset_y - scroll_speed, -max_offset)

        screen.fill(config.C_BG)
        title = font_title.render("MINIJUEGOS / BOSS", True, config.C_TEXT)
        screen.blit(title, (config.WIDTH//2 - title.get_width()//2, 40))

        for b in buttons:
            b.update(mouse_pos, offset_y)
            b.draw(screen, offset_y)

        pygame.draw.rect(screen, (40,40,60), bar_rect, border_radius=6)
        if max_offset > 0:
            thumb_h = max(30, int(bar_h * (view_height / content_height)))
            thumb_y = int(bar_rect.y + (-offset_y / max_offset) * (bar_h - thumb_h))
            thumb_rect = pygame.Rect(bar_x, thumb_y, bar_w, thumb_h)
            pygame.draw.rect(screen, (180,180,180), thumb_rect, border_radius=6)
        else:
            pygame.draw.rect(screen, (120,120,120), bar_rect, border_radius=6)

        hint = font_small.render("Pulsa ESC para volver al menú principal. Usa rueda o flechas para bajar.", True, config.C_TEXT)
        screen.blit(hint, (config.WIDTH//2 - hint.get_width()//2, config.HEIGHT - 40))

        pygame.display.flip()
