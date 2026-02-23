import pygame
import config

def run_otros(screen, clock):
    font_title = pygame.font.SysFont("Arial Black", 60)
    font_ui = pygame.font.SysFont("Arial", 24)

    running = True
    while running:
        clock.tick(config.FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        screen.fill(config.C_BG)

        title = font_title.render("OTROS", True, config.C_TEXT)
        screen.blit(title, (config.WIDTH//2 - title.get_width()//2, 80))

        msg = font_ui.render("Coming soon...", True, config.C_TEXT)
        screen.blit(msg, (config.WIDTH//2 - msg.get_width()//2, 200))

        msg2 = font_ui.render("Pulsa ESC para volver al menú principal.", True, config.C_TEXT)
        screen.blit(msg2, (config.WIDTH//2 - msg2.get_width()//2, 260))

        pygame.display.flip()








