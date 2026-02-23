import pygame
import os
import config

pygame.init()

# -----------------------------
# FUENTES
# -----------------------------
font_title = pygame.font.SysFont("Arial Black", 70)
font_small = pygame.font.SysFont("Arial", 24)

# -----------------------------
# CARGA DE SKINS
# -----------------------------
def load_skin(path, size=120):
    if not os.path.exists(path):
        surf = pygame.Surface((size, size))
        surf.fill((80, 80, 80))
        return surf

    try:
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.scale(img, (size, size))
        return img
    except:
        surf = pygame.Surface((size, size))
        surf.fill((80, 80, 80))
        return surf

# -----------------------------
# BOTÓN DE SKIN ESTILO GD
# -----------------------------
class SkinButton:
    def __init__(self, x, y, size, img, index):
        self.x = x
        self.y = y
        self.size = size
        self.img = img
        self.index = index
        self.hover = False
        self.scale = 1.0
        self.rotation = 0

    def draw(self, surf, selected):
        # Hover suave
        target = 1.12 if self.hover else 1.0
        self.scale += (target - self.scale) * 0.15

        s = int(self.size * self.scale)
        rect = pygame.Rect(0, 0, s, s)
        rect.center = (self.x, self.y)

        # Fondo del botón
        pygame.draw.rect(surf, (40, 40, 80), rect, border_radius=12)
        pygame.draw.rect(surf, (255, 255, 255), rect, 5, border_radius=12)

        # Skin rotando lentamente
        self.rotation += 1
        rotated = pygame.transform.rotate(self.img, self.rotation)
        surf.blit(rotated, rotated.get_rect(center=rect.center))

        # Si está seleccionada → borde verde animado
        if selected:
            glow = pygame.Surface((s + 20, s + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow, (0, 255, 0, 120), glow.get_rect(), border_radius=16)
            surf.blit(glow, glow.get_rect(center=rect.center))

            pygame.draw.rect(surf, (0, 255, 0), rect, 6, border_radius=12)

    def update_hover(self, mouse_pos):
        mx, my = mouse_pos
        s = int(self.size * self.scale)
        rect = pygame.Rect(0, 0, s, s)
        rect.center = (self.x, self.y)
        self.hover = rect.collidepoint(mx, my)

    def handle_click(self, mouse_pos):
        mx, my = mouse_pos
        s = int(self.size * self.scale)
        rect = pygame.Rect(0, 0, s, s)
        rect.center = (self.x, self.y)
        if rect.collidepoint(mx, my):
            return True
        return False

# -----------------------------
# MENÚ DE SKINS
# -----------------------------
def run_skins_menu(screen, clock):
    # Cargar skins reales
    skin_images = [load_skin(path) for path in config.SKINS]

    # Crear botones en cuadrícula estilo GD
    buttons = []
    size = 140
    spacing = 200
    start_x = config.WIDTH//2 - spacing
    start_y = 260

    for i, img in enumerate(skin_images):
        x = start_x + (i * spacing)
        y = start_y
        buttons.append(SkinButton(x, y, size, img, i))

    running = True
    t = 0

    while running:
        clock.tick(config.FPS)
        mouse_pos = pygame.mouse.get_pos()
        t += 0.05

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for b in buttons:
                    if b.handle_click(mouse_pos):
                        config.selected_skin_index = b.index

        # Fondo
        screen.fill((20, 20, 40))

        # Líneas diagonales animadas
        for i in range(0, config.WIDTH, 80):
            pygame.draw.line(
                screen,
                (60, 0, 120),
                (i + (t * 20) % 80, 0),
                (i - config.HEIGHT + (t * 20) % 80, config.HEIGHT),
                4
            )

        # Título
        title = font_title.render("SELECCIONAR SKIN", True, (0, 255, 200))
        shadow = font_title.render("SELECCIONAR SKIN", True, (0, 0, 0))
        screen.blit(shadow, (config.WIDTH//2 - title.get_width()//2 + 6, 80 + 6))
        screen.blit(title, (config.WIDTH//2 - title.get_width()//2, 80))

        # Botones
        for b in buttons:
            b.update_hover(mouse_pos)
            b.draw(screen, selected=(b.index == config.selected_skin_index))

        pygame.display.flip()






