import pygame
import config
import nivel1

def run_levels_menu(screen, clock):
    font_title = pygame.font.SysFont("Arial Black", 60)
    font_btn = pygame.font.SysFont("Arial Black", 36)

    btn_w, btn_h = 260, 70
    cx = config.WIDTH // 2 - btn_w // 2

    buttons = [
        ("NIVEL 1", "LEVEL1", 220),
        ("VOLVER", "BACK", 350),
    ]

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
                for text, action, y in buttons:
                    rect = pygame.Rect(cx, y, btn_w, btn_h)
                    if rect.collidepoint(mouse_pos):
                        if action == "LEVEL1":
                            nivel1.run_level(screen, clock)
                        elif action == "BACK":
                            running = False

        screen.fill(config.C_BG)

        title = font_title.render("SELECCIONAR NIVEL", True, config.C_TEXT)
        screen.blit(title, (config.WIDTH//2 - title.get_width()//2, 80))

        for text, action, y in buttons:
            rect = pygame.Rect(cx, y, btn_w, btn_h)
            pygame.draw.rect(screen, config.C_BTN_IDLE, rect, border_radius=15)
            pygame.draw.rect(screen, (255, 255, 255), rect, 3, border_radius=15)

            txt = font_btn.render(text, True, config.C_TEXT)
            screen.blit(txt, txt.get_rect(center=rect.center))

        pygame.display.flip()


