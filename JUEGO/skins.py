# skins.py — buscador mejorado con UX profesional
import pygame
import config
import os
import math

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
GLOW_MAX_ALPHA = 160
GLOW_OUTER_PAD = 36
GLOW_INNER_PAD = 8

# ----------------------------------------------------------
# Utilidades
# ----------------------------------------------------------

def _make_coming_soon_surface(size):
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    surf.fill((36, 36, 46))
    pygame.draw.rect(surf, (80, 80, 100), (0, 0, size, size), 4, border_radius=8)
    f = pygame.font.SysFont("Arial Black", max(18, size // 8))
    txt = f.render("COMING SOON", True, (220, 220, 220))
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

def _create_glow_ring(size, color=(0,180,255), outer_pad=GLOW_OUTER_PAD, inner_pad=GLOW_INNER_PAD, alpha=GLOW_MAX_ALPHA):
    total = size + outer_pad * 2
    surf = pygame.Surface((total, total), pygame.SRCALPHA)

    outer_rect = pygame.Rect(0, 0, total, total)
    inner_rect = pygame.Rect(
        outer_pad + inner_pad,
        outer_pad + inner_pad,
        size - inner_pad * 2,
        size - inner_pad * 2
    )

    glow_color = (color[0], color[1], color[2], alpha)
    pygame.draw.ellipse(surf, glow_color, outer_rect)
    pygame.draw.ellipse(surf, (0, 0, 0, 0), inner_rect)

    return surf

# ----------------------------------------------------------
# MENÚ PRINCIPAL
# ----------------------------------------------------------

def run_skins_menu(screen, clock):
    running = True

    skin_paths = list(getattr(config, "SKINS", []))

    coming_img_path = getattr(config, "COMING_SOON_IMG", None)
    coming_img = _load_image_safe(coming_img_path, SKIN_SIZE) if coming_img_path else None
    placeholder = coming_img if coming_img else _make_coming_soon_surface(SKIN_SIZE)

    skins_imgs = []
    for p in skin_paths:
        img = _load_image_safe(p, SKIN_SIZE)
        skins_imgs.append(img if img else placeholder)

    if not skins_imgs:
        skins_imgs = [placeholder]

    skin_names = [os.path.splitext(os.path.basename(p))[0] for p in skin_paths]
    if not skin_names:
        skin_names = ["coming_soon"]

    search_text = ""
    active_search = False
    cursor_timer = 0
    cursor_visible = True

    scroll_offset = 0.0
    scroll_target = 0.0

    hover_scale = [1.0 for _ in skins_imgs]
    hover_offset_y = [0 for _ in skins_imgs]
    glow_alpha = [0 for _ in skins_imgs]
    glow_cache = {}

    while running:
        dt = clock.tick(config.FPS)
        mx, my = pygame.mouse.get_pos()

        cursor_timer += dt
        if cursor_timer >= 450:
            cursor_timer = 0
            cursor_visible = not cursor_visible

        # ----------------------------------------------------------
        # EVENTOS
        # ----------------------------------------------------------
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); raise SystemExit

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
                    # Click dentro del buscador
                    if 50 <= mx <= config.WIDTH - 50 and 110 <= my <= 150:
                        active_search = True
                    else:
                        active_search = False

                    # ----------------------------------------------------------
                    # SELECCIÓN DE SKIN (AÑADIDO)
                    # ----------------------------------------------------------
                    for n, idx in enumerate(filtered_indices):
                        row = n // SKINS_PER_ROW
                        col = n % SKINS_PER_ROW

                        x = start_x + col * (SKIN_SIZE + PADDING_X)
                        y = TOP_MARGIN + row * (SKIN_SIZE + PADDING_Y) - int(scroll_offset)

                        rect = pygame.Rect(x, y, SKIN_SIZE, SKIN_SIZE)

                        if rect.collidepoint(mx, my):
                            config.selected_skin_index = idx

                # Scroll
                if ev.button == 4:
                    scroll_target -= SCROLL_STEP
                elif ev.button == 5:
                    scroll_target += SCROLL_STEP

        # ----------------------------------------------------------
        # FILTRADO DE SKINS
        # ----------------------------------------------------------
        filtered_indices = [
            i for i, name in enumerate(skin_names)
            if search_text.lower() in name.lower()
        ]

        if not filtered_indices:
            filtered_indices = []

        # ----------------------------------------------------------
        # CALCULAR GRID
        # ----------------------------------------------------------
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

        # ----------------------------------------------------------
        # DIBUJO
        # ----------------------------------------------------------
        screen.fill(config.C_BG)

        title = font_title.render("SELECCIONAR SKIN", True, config.C_TEXT)
        screen.blit(title, (config.WIDTH // 2 - title.get_width() // 2, 20))

        # ----------------------------------------------------------
        # BUSCADOR
        # ----------------------------------------------------------
        search_rect = pygame.Rect(50, 110, config.WIDTH - 100, 40)
        pygame.draw.rect(screen, (30, 30, 50), search_rect, border_radius=10)
        pygame.draw.rect(screen, (0, 180, 255) if active_search else (120, 120, 160), search_rect, 3, border_radius=10)

        txt = font_search.render(search_text if search_text else "Buscar skin...", True, (230,230,230))
        screen.blit(txt, (search_rect.x + 12, search_rect.y + 7))

        if active_search and cursor_visible:
            cx = search_rect.x + 12 + txt.get_width() + 3
            cy = search_rect.y + 8
            pygame.draw.rect(screen, (255,255,255), (cx, cy, 2, 24))

        # ----------------------------------------------------------
        # VIEWPORT
        # ----------------------------------------------------------
        surf = pygame.Surface((config.WIDTH, viewport_height), pygame.SRCALPHA)
        mouse_in_view = (mx, my - viewport_top)

        for n, idx in enumerate(filtered_indices):
            img = skins_imgs[idx]

            row = n // SKINS_PER_ROW
            col = n % SKINS_PER_ROW

            x = start_x + col * (SKIN_SIZE + PADDING_X)
            y = row * (SKIN_SIZE + PADDING_Y) - int(scroll_offset)

            rect = pygame.Rect(x, y, SKIN_SIZE, SKIN_SIZE)
            is_hover = rect.collidepoint(mouse_in_view)

            target_scale = HOVER_SCALE if is_hover else 1.0
            target_offset = HOVER_OFFSET_Y if is_hover else 0
            target_glow = GLOW_MAX_ALPHA if is_hover else 0

            hover_scale[idx] += (target_scale - hover_scale[idx]) * 0.16
            hover_offset_y[idx] += (target_offset - hover_offset_y[idx]) * 0.16
            glow_alpha[idx] += (target_glow - glow_alpha[idx]) * 0.16

            new_size = int(SKIN_SIZE * hover_scale[idx])
            scaled = pygame.transform.smoothscale(img, (new_size, new_size))

            center_x = x + SKIN_SIZE // 2
            center_y = y + SKIN_SIZE // 2 + int(hover_offset_y[idx])
            scaled_rect = scaled.get_rect(center=(center_x, center_y))

            # Seleccionada
            if idx == config.selected_skin_index:
                border = pygame.Rect(x - 7, y - 7, SKIN_SIZE + 14, SKIN_SIZE + 14)
                pygame.draw.rect(surf, (0,255,0), border, 6, border_radius=8)

            surf.blit(scaled, scaled_rect.topleft)

        screen.blit(surf, (0, viewport_top))

        # Scrollbar
        if max_scroll > 0:
            bar_w = 10
            bar_h = max(40, int(viewport_height * (viewport_height / total_height)))
            bar_x = config.WIDTH - 24
            bar_y = viewport_top + int((scroll_offset / max_scroll) * (viewport_height - bar_h))

            pygame.draw.rect(screen, (60,60,80), (bar_x, viewport_top, bar_w, viewport_height), border_radius=6)
            pygame.draw.rect(screen, (120,200,255), (bar_x, bar_y, bar_w, bar_h), border_radius=6)

        pygame.display.flip()
