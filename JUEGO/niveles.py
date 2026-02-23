import pygame
import config
import nivel1

pygame.init()

# -----------------------------
# FUENTES
# -----------------------------
font_title = pygame.font.SysFont("Arial Black", 70)
font_name = pygame.font.SysFont("Arial Black", 45)
font_small = pygame.font.SysFont("Arial", 26)

# -----------------------------
# BARRA DE PROGRESO
# -----------------------------
def draw_progress_bar(surface, x, y, width, percent, color):
    pygame.draw.rect(surface, (40, 40, 40), (x, y, width, 25), border_radius=8)
    fill = int(width * (percent / 100))
    pygame.draw.rect(surface, color, (x, y, fill, 25), border_radius=8)
    pygame.draw.rect(surface, (0, 0, 0), (x, y, width, 25), 3, border_radius=8)

# -----------------------------
# BOTÓN PLAY ESTILO GD
# -----------------------------
class PlayButton:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.hover = False
        self.scale = 1.0

    def draw(self, surf):
        target = 1.12 if self.hover else 1.0
        self.scale += (target - self.scale) * 0.15

        s = int(self.size * self.scale)
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
        self.hover = ((mx - self.x)**2 + (my - self.y)**2)**0.5 <= self.size//2

    def handle_click(self, mouse_pos):
        mx, my = mouse_pos
        return ((mx - self.x)**2 + (my - self.y)**2)**0.5 <= self.size//2

# -----------------------------
# FLECHAS IZQUIERDA / DERECHA
# -----------------------------
class ArrowButton:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction  # -1 izquierda, +1 derecha
        self.hover = False
        self.scale = 1.0

    def draw(self, surf):
        target = 1.15 if self.hover else 1.0
        self.scale += (target - self.scale) * 0.15

        size = int(70 * self.scale)
        rect = pygame.Rect(0, 0, size, size)
        rect.center = (self.x, self.y)

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

# -----------------------------
# MENÚ DE NIVELES
# -----------------------------
def run_levels_menu(screen, clock):

    # Lista de niveles (puedes añadir más)
    levels = [
        {"name": "LEVEL 1", "difficulty": "Easy", "color": (0, 200, 255), "progress": 100},
        {"name": "LEVEL 2", "difficulty": "Normal", "color": (0, 255, 0), "progress": 0},
        {"name": "LEVEL 3", "difficulty": "Hard", "color": (255, 200, 0), "progress": 0},
        {"name": "LEVEL 4", "difficulty": "Harder", "color": (255, 100, 0), "progress": 0},
        {"name": "LEVEL 5", "difficulty": "Insane", "color": (255, 0, 0), "progress": 0},
    ]

    current = 0  # Nivel actual mostrado

    play_button = PlayButton(config.WIDTH//2 + 350, config.HEIGHT//2 + 20, 130)
    arrow_left = ArrowButton(config.WIDTH//2 - 450, config.HEIGHT//2 + 20, -1)
    arrow_right = ArrowButton(config.WIDTH//2 + 450, config.HEIGHT//2 + 20, +1)

    running = True

    while running:
        clock.tick(config.FPS)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                if arrow_left.handle_click(mouse_pos):
                    current = (current - 1) % len(levels)

                if arrow_right.handle_click(mouse_pos):
                    current = (current + 1) % len(levels)

                if play_button.handle_click(mouse_pos):
                    if current == 0:
                        nivel1.run_level(screen, clock)
                    # Aquí puedes añadir más niveles:
                    # elif current == 1: nivel2.run_level(...)

        # Fondo
        screen.fill((20, 20, 40))

        # Título
        title = font_title.render("SELECCIONAR NIVEL", True, (0, 255, 200))
        shadow = font_title.render("SELECCIONAR NIVEL", True, (0, 0, 0))
        screen.blit(shadow, (config.WIDTH//2 - title.get_width()//2 + 6, 40 + 6))
        screen.blit(title, (config.WIDTH//2 - title.get_width()//2, 40))

        # Tarjeta del nivel
        card = pygame.Rect(config.WIDTH//2 - 400, 150, 800, 350)
        pygame.draw.rect(screen, (50, 50, 80), card, border_radius=20)
        pygame.draw.rect(screen, (0, 0, 0), card, 6, border_radius=20)

        # Datos del nivel actual
        lvl = levels[current]

        # Nombre del nivel
        name = font_name.render(lvl["name"], True, (255, 255, 255))
        screen.blit(name, (card.x + 40, card.y + 20))

        # Dificultad
        diff = font_small.render(lvl["difficulty"], True, lvl["color"])
        screen.blit(diff, (card.x + 40, card.y + 80))

        # Barra de progreso
        nm = font_small.render("NORMAL MODE", True, (255, 255, 255))
        screen.blit(nm, (card.x + 40, card.y + 150))
        draw_progress_bar(screen, card.x + 40, card.y + 185, 350, lvl["progress"], (0, 255, 0))

        # Flechas
        arrow_left.update_hover(mouse_pos)
        arrow_left.draw(screen)

        arrow_right.update_hover(mouse_pos)
        arrow_right.draw(screen)

        # Botón PLAY
        play_button.update_hover(mouse_pos)
        play_button.draw(screen)

        pygame.display.flip()








