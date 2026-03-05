# start.py — pantalla inicial estilo Geometry Dash (6s exactos, silencio total)
import pygame
import sys
import random
import os
import time

import config
import main

pygame.init()

# === FUNCIÓN PARA CARGAR RECURSOS ===
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# ❌ NO TOCAR LA MÚSICA GLOBAL (start.py debe estar en silencio)

screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
pygame.display.set_caption("GEOMETRY KIRK - LOADING")
clock = pygame.time.Clock()

# Logo desde config
logo_img = None
if os.path.exists(resource_path(config.LOGO_IMG)):
    try:
        logo_img = pygame.image.load(resource_path(config.LOGO_IMG)).convert_alpha()
        logo_img = pygame.transform.smoothscale(
            logo_img,
            (int(config.WIDTH * 0.75), int(config.HEIGHT * 0.28))
        )
    except Exception:
        logo_img = None

# Frases aleatorias
LOADING_QUOTES = [
    "¿¿QUE JUEGO HIZO WILLIREX??",
    "Cargando… el juego ha visto tu skill y está preocupado.",
    "¿Sabes porque España esta sucia?... Porque Castilla la Manchaaa",
    "Ya me joderia ser estafado en un curso de cocina..",
    "2x1 en burros",
    "EFN",
    "Estamos en maximos historicos",
    "Me gustan los catalanes porque hacen cosas",
    "Camarero, la multa y un policia que corra poco",
    "Hueles pestaco,.. A zorro mata peyizcos!",
    "- --- -. - --- / . .-.. / --.- ..- . / .-.. --- / .-.. . .-",
    "Ay la cookieeee!!!",
]
quote = random.choice(LOADING_QUOTES)

font_quote = pygame.font.SysFont("Arial Black", 22)
font_percent = pygame.font.SysFont("Arial Black", 22)
font_small = pygame.font.SysFont("Arial", 16)

TOTAL_DURATION = 6.0  # EXACTO

def run_start_screen():
    bar_width = int(config.WIDTH * 0.55)
    bar_height = 30
    bar_x = config.WIDTH // 2 - bar_width // 2
    bar_y = config.HEIGHT // 2 + 80

    start_time = time.time()

    phases = [
        (0.30, 1.5),
        (0.65, 2.0),
        (1.00, 2.5),
    ]

    current_phase = 0
    phase_start_time = start_time
    progress = 0.0

    running = True
    while running:
        dt = clock.tick(config.FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        now = time.time()
        elapsed_total = now - start_time

        target_percent, phase_duration = phases[current_phase]
        elapsed_phase = now - phase_start_time

        phase_t = min(1.0, elapsed_phase / phase_duration)
        phase_progress = phase_t * phase_t * (3 - 2 * phase_t)

        prev_target = phases[current_phase - 1][0] if current_phase > 0 else 0.0
        progress = prev_target + (target_percent - prev_target) * phase_progress

        if phase_t >= 1.0 and current_phase < len(phases) - 1:
            current_phase += 1
            phase_start_time = now

        progress = min(1.0, progress)

        screen.fill((10, 10, 30))

        pygame.draw.rect(
            screen, (20, 20, 50),
            (config.WIDTH//2 - int(config.WIDTH*0.4), 90,
             int(config.WIDTH*0.8), int(config.HEIGHT*0.35)),
            border_radius=20
        )

        if logo_img:
            screen.blit(logo_img, (config.WIDTH//2 - logo_img.get_width()//2, 110))

        pygame.draw.rect(screen, (0, 0, 0),
                         (bar_x - 3, bar_y - 3, bar_width + 6, bar_height + 6),
                         border_radius=12)
        pygame.draw.rect(screen, (40, 40, 80),
                         (bar_x, bar_y, bar_width, bar_height),
                         border_radius=10)

        filled_width = int(bar_width * progress)
        if filled_width > 0:
            grad = pygame.Surface((filled_width, bar_height), pygame.SRCALPHA)
            for x in range(filled_width):
                t = x / max(1, filled_width)
                r = int(0 + 40 * t)
                g = int(180 + 60 * t)
                b = 255
                pygame.draw.line(grad, (r, g, b, 255), (x, 0), (x, bar_height))
            screen.blit(grad, (bar_x, bar_y))

        percent = int(progress * 100)
        percent_text = font_percent.render(f"{percent}%", True, (255, 255, 255))
        screen.blit(percent_text,
                    (bar_x + bar_width + 15,
                     bar_y + bar_height//2 - percent_text.get_height()//2))

        quote_surf = font_quote.render(quote, True, (255, 255, 0))
        screen.blit(quote_surf,
                    (config.WIDTH//2 - quote_surf.get_width()//2, bar_y + 50))

        tip_surf = font_small.render("Loading Geometry Kirk...", True, (180, 180, 220))
        screen.blit(tip_surf,
                    (config.WIDTH//2 - tip_surf.get_width()//2, bar_y + 80))

        pygame.display.flip()

        if elapsed_total >= TOTAL_DURATION:
            running = False

    # NO RESTAURAR VOLUMEN
    # NO TOCAR LA MÚSICA

    main.main_menu()


if __name__ == "__main__":
    run_start_screen()
