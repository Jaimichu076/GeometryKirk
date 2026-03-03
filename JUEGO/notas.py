import pygame
import sys
import os
import config

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

VERSIONES = [
    ("v1.0", [
        "Primer lanzamiento público.",
        "Menú principal funcional.",
        "Sistema de skins básico.",
        "Nivel 1 completamente jugable.",
        "Sistema de bosses inicial."
    ]),

]

def run_notas(screen, clock):
    font_title = pygame.font.SysFont("Arial Black", 60)
    font_ver = pygame.font.SysFont("Arial Black", 36)
    font_text = pygame.font.SysFont("Arial", 26)

    scroll = 0
    running = True

    # Área donde se dibuja el contenido scrolleable
    CONTENT_TOP = 140
    CONTENT_BOTTOM = config.HEIGHT - 40
    CONTENT_HEIGHT = CONTENT_BOTTOM - CONTENT_TOP

    # Crear superficie grande para el contenido
    content_surface = pygame.Surface((config.WIDTH, 2000), pygame.SRCALPHA)

    # Pre-renderizar contenido
    def render_content():
        y = 0
        for version, cambios in VERSIONES:
            ver_txt = font_ver.render(version, True, (255, 255, 0))
            content_surface.blit(ver_txt, (80, y))
            y += 50

            for c in cambios:
                txt = font_text.render("- " + c, True, (220, 220, 220))
                content_surface.blit(txt, (120, y))
                y += 35

            y += 20

        return y

    total_content_height = render_content()

    # Scroll limits
    max_scroll = 0
    min_scroll = -(total_content_height - CONTENT_HEIGHT)

    # Scrollbar settings
    scrollbar_width = 12
    scrollbar_color = (180, 180, 180)
    scrollbar_bg = (60, 60, 60)

    while running:
        clock.tick(config.FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # scroll up
                    scroll += 40
                if event.button == 5:  # scroll down
                    scroll -= 40

        # Limitar scroll
        scroll = max(min_scroll, min(max_scroll, scroll))

        # Fondo
        screen.fill((25, 25, 45))

        # Título fijo
        title = font_title.render("Notas de la versión", True, (0, 255, 200))
        screen.blit(title, (config.WIDTH//2 - title.get_width()//2, 40))

        # Dibujar contenido scrolleado dentro del área
        screen.blit(content_surface, (0, CONTENT_TOP), area=pygame.Rect(0, -scroll, config.WIDTH, CONTENT_HEIGHT))

        # Dibujar barra de scroll
        if total_content_height > CONTENT_HEIGHT:
            scrollbar_height = max(40, int(CONTENT_HEIGHT * (CONTENT_HEIGHT / total_content_height)))
            scrollbar_y = CONTENT_TOP + int((-scroll / (total_content_height - CONTENT_HEIGHT)) * (CONTENT_HEIGHT - scrollbar_height))

            pygame.draw.rect(screen, scrollbar_bg, (config.WIDTH - scrollbar_width - 10, CONTENT_TOP, scrollbar_width, CONTENT_HEIGHT), border_radius=6)
            pygame.draw.rect(screen, scrollbar_color, (config.WIDTH - scrollbar_width - 10, scrollbar_y, scrollbar_width, scrollbar_height), border_radius=6)

        pygame.display.flip()
