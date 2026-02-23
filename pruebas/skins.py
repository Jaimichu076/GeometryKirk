import pygame
import os
import config

def load_skin_preview(path, size=120):
    if not os.path.exists(path):
        surf = pygame.Surface((size, size))
        surf.fill((80, 80, 80))
        return surf
    try:
        img = pygame.image.load(path).convert()
        img = pygame.transform.scale(img, (size, size))
        return img
    except:
        surf = pygame.Surface((size, size))
        surf.fill((80, 80, 80))
        return surf

def run_skins_menu(screen, clock):
    font_title = pygame.font.SysFont("Arial Black", 60)
    font_ui = pygame.font.SysFont("Arial", 24)

    previews = [load_skin_preview(p) for p in config.SKINS]
    selected = config.selected_skin_index

    running = True
    while running:
        clock.tick(config.FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                for i, surf in enumerate(previews):
                    x = 200 + i * 250
                    y = 260
                    rect = pygame.Rect(x, y, surf.get_width(), surf.get_height())
                    if rect.collidepoint(mx, my):
                        config.selected_skin_index = i
                        selected = i

        screen.fill(config.C_BG)

        title = font_title.render("SELECCIONAR SKIN", True, config.C_TEXT)
        screen.blit(title, (config.WIDTH//2 - title.get_width()//2, 80))

        info = font_ui.render("Haz clic en una skin. ESC para volver.", True, config.C_TEXT)
        screen.blit(info, (config.WIDTH//2 - info.get_width()//2, 160))

        for i, surf in enumerate(previews):
            x = 200 + i * 250
            y = 260
            rect = pygame.Rect(x, y, surf.get_width(), surf.get_height())
            border = (0, 255, 0) if i == selected else (255, 255, 255)
            screen.blit(surf, rect)
            pygame.draw.rect(screen, border, rect, 4)

        pygame.display.flip()


