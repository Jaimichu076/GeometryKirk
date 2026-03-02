# skins.py — selector de skins de personaje y avión con hover mejorado
import pygame
import os
import config

pygame.init()

# Fuentes
font_title = pygame.font.SysFont("Arial Black", 56)
font_small = pygame.font.SysFont("Arial", 18)
font_search = pygame.font.SysFont("Arial", 26)

# Layout
SKIN_SIZE = 120
PADDING_X = 28
PADDING_Y = 24
SKINS_PER_ROW = 4
TOP_MARGIN = 210
BOTTOM_MARGIN = 40
SCROLL_STEP = 120
EASING = 0.18

# Hover
HOVER_SCALE = 1.18
HOVER_OFFSET_Y = -10
GLOW_MAX_ALPHA = 180


def _make_placeholder(size, text="COMING SOON"):
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    surf.fill((30, 30, 45))
    pygame.draw.rect(surf, (90, 90, 130), (0, 0, size, size), 4, border_radius=10)
    f = pygame.font.SysFont("Arial Black", max(18, size // 8))
    txt = f.render(text, True, (230, 230, 230))
    surf.blit(txt, ((size - txt.get_width()) // 2, (size - txt.get_height()) // 2))
    return surf


def _load_image_safe(path, size):
    if not path or not os.path.exists(path):
        return None
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.smoothscale(img, (size, size))
    except:
        return None


def _run_generic_menu(screen, clock, title_text, paths, index_attr_name):
    """Menú genérico para personaje o avión.

    paths: lista de rutas (CHAR_SKINS o PLANE_SKINS)
    index_attr_name: nombre del atributo en config (ej: 'selected_character_skin_index')
    """
    running = True

    placeholder = _make_placeholder(SKIN_SIZE)

    imgs = []
    for p in paths:
        img = _load_image_safe(p, SKIN_SIZE)
        imgs.append(img if img else placeholder)

    if not imgs:
        imgs = [placeholder]

    names = [os.path.splitext(os.path.basename(p))[0] for p in paths]
    if not names:
        names = ["coming_soon"]

    # índice actual real desde config
    current_index = getattr(config, index_attr_name, -1)

    search_text = ""
    active_search = False
    cursor_timer = 0
    cursor_visible = True

    scroll_offset = 0.0
    scroll_target = 0.0

    hover_scale = [1.0 for _ in imgs]
    hover_offset_y = [0 for _ in imgs]
    glow_alpha = [0 for _ in imgs]

    while running:
        dt = clock.tick(config.FPS)
        mx, my = pygame.mouse.get_pos()

        cursor_timer += dt
        if cursor_timer >= 450:
            cursor_timer = 0
            cursor_visible = not cursor_visible

        # EVENTOS
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False

                if active_search and ev.key == pygame.K_BACKSPACE:
                    search_text = search_text[:-1]
                elif active_search:
                    if len(ev.unicode) == 1 and ev.unicode.isprintable():
                        search_text += ev.unicode

                if ev.key == pygame.K_f and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    active_search = True

            if ev.type == pygame.MOUSEBUTTONDOWN:
                if ev.button == 1:
                    # activar buscador
                    if 50 <= mx <= config.WIDTH - 50 and 110 <= my <= 150:
                        active_search = True
                    else:
                        active_search = False

                    # selección de skin
                    for n, idx in enumerate(filtered_indices):
                        row = n // SKINS_PER_ROW
                        col = n % SKINS_PER_ROW

                        x = start_x + col * (SKIN_SIZE + PADDING_X)
                        y = TOP_MARGIN + row * (SKIN_SIZE + PADDING_Y) - int(scroll_offset)

                        rect = pygame.Rect(x, y, SKIN_SIZE, SKIN_SIZE)
                        if rect.collidepoint(mx, my):
                            current_index = idx
                            # guardar en config de verdad
                            setattr(config, index_attr_name, idx)

                # scroll
                if ev.button == 4:
                    scroll_target -= SCROLL_STEP
                elif ev.button == 5:
                    scroll_target += SCROLL_STEP

        # FILTRADO
        filtered_indices = [
            i for i, name in enumerate(names)
            if search_text.lower() in name.lower()
        ]

        total_skins = len(filtered_indices)
        rows = (total_skins + SKINS_PER_ROW - 1) // SKINS_PER_ROW

        total_row_width = SKINS_PER_ROW * SKIN_SIZE + (SKINS_PER_ROW - 1) * PADDING_X
        start_x = config.WIDTH // 2 - total_row_width // 2

        viewport_top = TOP_MARGIN
        viewport_bottom = config.HEIGHT - BOTTOM_MARGIN
        viewport_height = viewport_bottom - viewport_top

        total_height = rows * SKIN_SIZE + (rows - 1) * PADDING_Y if rows > 0 else 0
        max_scroll = max(0, total_height - viewport_height)

        scroll_target = max(0, min(max_scroll, scroll_target))
        scroll_offset += (scroll_target - scroll_offset) * EASING

        # DIBUJO
        screen.fill(config.C_BG)

        title = font_title.render(title_text, True, config.C_TEXT)
        screen.blit(title, (config.WIDTH // 2 - title.get_width() // 2, 20))

        # Buscador
        search_rect = pygame.Rect(50, 110, config.WIDTH - 100, 40)
        pygame.draw.rect(screen, (25, 25, 45), search_rect, border_radius=10)
        pygame.draw.rect(screen, (0, 200, 255) if active_search else (120, 120, 160),
                         search_rect, 3, border_radius=10)

        txt = font_search.render(search_text if search_text else "Buscar skin...", True, (230, 230, 230))
        screen.blit(txt, (search_rect.x + 12, search_rect.y + 7))

        if active_search and cursor_visible:
            cx = search_rect.x + 12 + txt.get_width() + 3
            cy = search_rect.y + 8
            pygame.draw.rect(screen, (255, 255, 255), (cx, cy, 2, 24))

        # Viewport
        surf = pygame.Surface((config.WIDTH, viewport_height), pygame.SRCALPHA)
        mouse_in_view = (mx, my - viewport_top)

        for n, idx in enumerate(filtered_indices):
            img = imgs[idx]

            row = n // SKINS_PER_ROW
            col = n % SKINS_PER_ROW

            x = start_x + col * (SKIN_SIZE + PADDING_X)
            y = row * (SKIN_SIZE + PADDING_Y) - int(scroll_offset)

            rect = pygame.Rect(x, y, SKIN_SIZE, SKIN_SIZE)
            is_hover = rect.collidepoint(mouse_in_view)

            target_scale = HOVER_SCALE if is_hover else 1.0
            target_offset = HOVER_OFFSET_Y if is_hover else 0
            target_glow = GLOW_MAX_ALPHA if is_hover else 0

            hover_scale[idx] += (target_scale - hover_scale[idx]) * 0.18
            hover_offset_y[idx] += (target_offset - hover_offset_y[idx]) * 0.18
            glow_alpha[idx] += (target_glow - glow_alpha[idx]) * 0.18

            new_size = int(SKIN_SIZE * hover_scale[idx])
            scaled = pygame.transform.smoothscale(img, (new_size, new_size))

            center_x = x + SKIN_SIZE // 2
            center_y = y + SKIN_SIZE // 2 + int(hover_offset_y[idx])
            scaled_rect = scaled.get_rect(center=(center_x, center_y))

            # Glow suave
            if glow_alpha[idx] > 5:
                glow_surf = pygame.Surface((new_size + 26, new_size + 26), pygame.SRCALPHA)
                pygame.draw.ellipse(
                    glow_surf,
                    (0, 200, 255, int(glow_alpha[idx])),
                    glow_surf.get_rect()
                )
                glow_rect = glow_surf.get_rect(center=(center_x, center_y + 4))
                surf.blit(glow_surf, glow_rect)

            # Marco de selección
            if idx == current_index:
                border_rect = pygame.Rect(0, 0, new_size + 14, new_size + 14)
                border_rect.center = (center_x, center_y)
                pygame.draw.rect(surf, (0, 255, 120), border_rect, 4, border_radius=10)

            surf.blit(scaled, scaled_rect.topleft)

        screen.blit(surf, (0, viewport_top))

        # Scrollbar
        if max_scroll > 0:
            bar_w = 10
            bar_h = max(40, int(viewport_height * (viewport_height / total_height)))
            bar_x = config.WIDTH - 24
            bar_y = viewport_top + int((scroll_offset / max_scroll) * (viewport_height - bar_h))

            pygame.draw.rect(screen, (60, 60, 80), (bar_x, viewport_top, bar_w, viewport_height), border_radius=6)
            pygame.draw.rect(screen, (120, 200, 255), (bar_x, bar_y, bar_w, bar_h), border_radius=6)

        pygame.display.flip()


def run_skins_menu(screen, clock):
    """Menú principal de skins: elegir personaje o avión."""
    running = True

    btn_char = pygame.Rect(config.WIDTH // 2 - 260, 120, 220, 60)
    btn_plane = pygame.Rect(config.WIDTH // 2 + 40, 120, 220, 60)

    while running:
        clock.tick(config.FPS)
        mx, my = pygame.mouse.get_pos()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                running = False
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if btn_char.collidepoint(mx, my):
                    _run_generic_menu(
                        screen, clock,
                        "SKINS DE PERSONAJE",
                        config.CHAR_SKINS,
                        "selected_character_skin_index"
                    )
                if btn_plane.collidepoint(mx, my):
                    _run_generic_menu(
                        screen, clock,
                        "SKINS DE AVIÓN",
                        config.PLANE_SKINS,
                        "selected_plane_skin_index"
                    )

        screen.fill(config.C_BG)

        title = font_title.render("SELECCIONAR TIPO DE SKIN", True, config.C_TEXT)
        screen.blit(title, (config.WIDTH // 2 - title.get_width() // 2, 20))

        pygame.draw.rect(screen, (40, 40, 80), btn_char, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), btn_char, 3, border_radius=10)
        txt = font_small.render("Skins de personaje", True, (255, 255, 255))
        screen.blit(txt, (btn_char.centerx - txt.get_width() // 2,
                          btn_char.centery - txt.get_height() // 2))

        pygame.draw.rect(screen, (40, 40, 80), btn_plane, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), btn_plane, 3, border_radius=10)
        txt2 = font_small.render("Skins de avión", True, (255, 255, 255))
        screen.blit(txt2, (btn_plane.centerx - txt2.get_width() // 2,
                           btn_plane.centery - txt2.get_height() // 2))

        pygame.display.flip()
