# skins.py — selector de skins con botones circulares estilo niveles.py
import pygame
import os
import sys
import math
import config

pygame.init()

# === FUNCIÓN PARA CARGAR RECURSOS ===
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# === FUENTES ===
font_title = pygame.font.SysFont("Arial Black", 70)
font_small = pygame.font.SysFont("Arial", 20)
font_name = pygame.font.SysFont("Arial Black", 14)
font_search = pygame.font.SysFont("Arial", 26)

# === LAYOUT ===
SKIN_SIZE = 120
PADDING_X = 28
PADDING_Y = 40
SKINS_PER_ROW = 4
TOP_MARGIN = 260     # ← BAJADO PARA DEJAR ESPACIO
BOTTOM_MARGIN = 40
SCROLL_STEP = 120
EASING = 0.18

HOVER_SCALE = 1.18
HOVER_OFFSET_Y = -12
GLOW_MAX_ALPHA = 160

# -----------------------------
# FONDO ANIMADO (ONDAS + PARTÍCULAS NEÓN)
# -----------------------------
def draw_animated_background(surface, t):
    w, h = surface.get_size()

    for y in range(0, h, 60):
        c = 40 + int(40 * math.sin(t * 0.7 + y * 0.03))
        pygame.draw.rect(surface, (10, c, 60 + c//3), (0, y, w, 60))

    for i in range(18):
        x = (i * 120 + int(t * 90)) % (w + 200) - 100
        y = 120 + int(40 * math.sin(t * 1.3 + i))
        alpha = 80 + int(60 * math.sin(t * 2 + i))
        pygame.draw.circle(surface, (0, 255, 255, alpha), (x, y), 6)

# -----------------------------
# UTILIDADES
# -----------------------------
def wrap_text(text, font, max_width):
    words = text.split(" ")
    lines = []
    current = ""

    for w in words:
        test = current + (" " if current else "") + w
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = w

    if current:
        lines.append(current)

    return lines

def _make_placeholder(size, text="COMING SOON"):
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    surf.fill((36, 36, 46))
    pygame.draw.rect(surf, (80, 80, 100), (0, 0, size, size), 4, border_radius=10)
    f = pygame.font.SysFont("Arial Black", max(18, size // 8))
    txt = f.render(text, True, (220, 220, 220))
    surf.blit(txt, ((size - txt.get_width()) // 2, (size - txt.get_height()) // 2))
    return surf

def _load_image_safe(path, size):
    if not path or not os.path.exists(resource_path(path)):
        return None
    try:
        img = pygame.image.load(resource_path(path)).convert_alpha()
        return pygame.transform.smoothscale(img, (size, size))
    except:
        return None

# ----------------------------------------------------------
# MENÚ GENÉRICO (personaje o avión)
# ----------------------------------------------------------
def _run_generic_menu(screen, clock, title_text, paths, index_attr_name):
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

    start_time = pygame.time.get_ticks()

    while running:
        dt = clock.tick(config.FPS)
        t = (pygame.time.get_ticks() - start_time) / 1000.0
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
                    if 50 <= mx <= config.WIDTH - 50 and 160 <= my <= 200:
                        active_search = True
                    else:
                        active_search = False

                    for n, idx in enumerate(filtered_indices):
                        row = n // SKINS_PER_ROW
                        col = n % SKINS_PER_ROW

                        x = start_x + col * (SKIN_SIZE + PADDING_X)
                        y = TOP_MARGIN + row * (SKIN_SIZE + PADDING_Y) - int(scroll_offset)

                        rect = pygame.Rect(x, y, SKIN_SIZE, SKIN_SIZE)
                        if rect.collidepoint(mx, my):
                            current_index = idx
                            setattr(config, index_attr_name, idx)

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

        total_height = rows * (SKIN_SIZE + PADDING_Y)
        max_scroll = max(0, total_height - viewport_height)

        scroll_target = max(0, min(max_scroll, scroll_target))
        scroll_offset += (scroll_target - scroll_offset) * EASING

        # DIBUJO
        draw_animated_background(screen, t)

        # TÍTULO IGUAL QUE niveles.py
        title = font_title.render(title_text, True, (0, 255, 200))
        shadow = font_title.render(title_text, True, (0, 0, 0))
        screen.blit(shadow, (config.WIDTH//2 - title.get_width()//2 + 6, 40 + 6))
        screen.blit(title, (config.WIDTH//2 - title.get_width()//2, 40))

        # Buscador (BAJADO)
        search_rect = pygame.Rect(50, 160, config.WIDTH - 100, 40)
        pygame.draw.rect(screen, (30, 30, 50), search_rect, border_radius=10)
        pygame.draw.rect(screen, (0, 180, 255) if active_search else (120, 120, 160),
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
            name = names[idx]

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

            if glow_alpha[idx] > 5:
                glow_surf = pygame.Surface((new_size + 26, new_size + 26), pygame.SRCALPHA)
                pygame.draw.ellipse(
                    glow_surf,
                    (0, 200, 255, int(glow_alpha[idx])),
                    glow_surf.get_rect()
                )
                glow_rect = glow_surf.get_rect(center=(center_x, center_y + 4))
                surf.blit(glow_surf, glow_rect)

            if idx == current_index:
                border_rect = pygame.Rect(0, 0, new_size + 14, new_size + 14)
                border_rect.center = (center_x, center_y)
                pygame.draw.rect(surf, (0, 255, 120), border_rect, 4, border_radius=10)

            surf.blit(scaled, scaled_rect.topleft)

            lines = wrap_text(name, font_name, SKIN_SIZE)
            text_y = scaled_rect.bottom + 4

            for line in lines:
                name_surf = font_name.render(line, True, (255, 255, 255))
                shadow = font_name.render(line, True, (0, 0, 0))
                name_x = center_x - name_surf.get_width() // 2

                surf.blit(shadow, (name_x + 2, text_y + 2))
                surf.blit(name_surf, (name_x, text_y))

                text_y += name_surf.get_height() + 2

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

# ----------------------------------------------------------
# MENÚ PRINCIPAL DE SKINS (BOTONES CIRCULARES)
# ----------------------------------------------------------
def run_skins_menu(screen, clock):
    running = True

    # === Cargar imágenes de los botones ===
    img_char = pygame.image.load(resource_path("assets/images/icon_personaje.png")).convert_alpha()
    img_plane = pygame.image.load(resource_path("assets/images/icon_avion.png")).convert_alpha()

    # Tamaño base de los iconos (más pequeños que antes)
    ICON_SIZE = 140
    img_char = pygame.transform.smoothscale(img_char, (ICON_SIZE, ICON_SIZE))
    img_plane = pygame.transform.smoothscale(img_plane, (ICON_SIZE, ICON_SIZE))

    # Botones circulares
    radius = 110   # más pequeño que antes
    btn_char_center = (config.WIDTH//2 - 180, config.HEIGHT//2)
    btn_plane_center = (config.WIDTH//2 + 180, config.HEIGHT//2)

    # Escala animada
    scale_char = 1.0
    scale_plane = 1.0

    start_time = pygame.time.get_ticks()

    while running:
        dt = clock.tick(config.FPS) / 1000
        t = (pygame.time.get_ticks() - start_time) / 1000
        mx, my = pygame.mouse.get_pos()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                running = False

            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                # Click en botón personaje
                if (mx - btn_char_center[0])**2 + (my - btn_char_center[1])**2 <= (radius*1.2)**2:
                    _run_generic_menu(
                        screen, clock,
                        "SKINS DE PERSONAJE",
                        config.CHAR_SKINS,
                        "selected_character_skin_index"
                    )

                # Click en botón avión
                if (mx - btn_plane_center[0])**2 + (my - btn_plane_center[1])**2 <= (radius*1.2)**2:
                    _run_generic_menu(
                        screen, clock,
                        "SKINS DE AVIÓN",
                        config.PLANE_SKINS,
                        "selected_plane_skin_index"
                    )

        # Fondo animado
        draw_animated_background(screen, t)

        # Hover detección
        hover_char = (mx - btn_char_center[0])**2 + (my - btn_char_center[1])**2 <= radius**2
        hover_plane = (mx - btn_plane_center[0])**2 + (my - btn_plane_center[1])**2 <= radius**2

        # Animación de escala
        scale_char += ((1.18 if hover_char else 1.0) - scale_char) * 0.15
        scale_plane += ((1.18 if hover_plane else 1.0) - scale_plane) * 0.15

        # Dibujar botones
        for center, img, scale in [
            (btn_char_center, img_char, scale_char),
            (btn_plane_center, img_plane, scale_plane)
        ]:
            cx, cy = center
            r = int(radius * scale)

            # === Glow exterior ===
            glow = pygame.Surface((r*2+40, r*2+40), pygame.SRCALPHA)
            pygame.draw.circle(glow, (0,255,255, 120 if scale > 1.05 else 70), (r+20, r+20), r+18)
            screen.blit(glow, (cx-r-20, cy-r-20), special_flags=pygame.BLEND_ADD)

            # === Borde circular estilo GD ===
            pygame.draw.circle(screen, (255,255,255), (cx, cy), r, 6)
            pygame.draw.circle(screen, (0,0,0), (cx, cy), r, 10)

            # === Imagen centrada ===
            icon_scaled = pygame.transform.smoothscale(img, (int(ICON_SIZE*scale), int(ICON_SIZE*scale)))
            rect = icon_scaled.get_rect(center=(cx, cy))
            screen.blit(icon_scaled, rect)

        pygame.display.flip()


