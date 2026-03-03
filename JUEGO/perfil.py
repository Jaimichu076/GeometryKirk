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

def run_perfil(screen, clock):
    font_big = pygame.font.SysFont("Arial Black", 70)
    font_small = pygame.font.SysFont("Arial", 28)

    running = True
    while running:
        clock.tick(config.FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        screen.fill((20, 20, 40))

        txt = font_big.render("COMING SOON", True, (255, 255, 0))
        screen.blit(txt, (config.WIDTH//2 - txt.get_width()//2, config.HEIGHT//2 - 60))

        hint = font_small.render("Pulsa ESC para volver", True, (255, 255, 255))
        screen.blit(hint, (config.WIDTH//2 - hint.get_width()//2, config.HEIGHT//2 + 20))

        pygame.display.flip()
