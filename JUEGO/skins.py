# skins.py
import pygame
import config
import os
import math

pygame.init()

# Fuentes
font_title = pygame.font.SysFont("Arial Black", 56)
font_small = pygame.font.SysFont("Arial", 16)

# Layout y visual
SKIN_SIZE = 120
PADDING_X = 28
PADDING_Y = 24
SKINS_PER_ROW = 4
TOP_MARGIN = 140
BOTTOM_MARGIN = 40
SCROLL_STEP = 120
EASING = 0.18

# Hover visual tuning
HOVER_SCALE = 1.18
HOVER_OFFSET_Y = -10
GLOW_MAX_ALPHA = 160
GLOW_OUTER_PAD = 36
GLOW_INNER_PAD = 8

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
    except Exception:
        return None

def _create_glow_ring(size, color=(0,180,255), outer_pad=GLOW_OUTER_PAD, inner_pad=GLOW_INNER_PAD, alpha=GLOW_MAX_ALPHA):
    """
    Crea una superficie con un 'anillo' de glow (donut) para que no aparezca un círculo sólido
    detrás del cuadrado. El anillo se dibuja con una elipse exterior y se 'perfora' el centro.
    """
    total = size + outer_pad * 2
    surf = pygame.Surface((total, total), pygame.SRCALPHA)
    outer_rect = pygame.Rect(0, 0, total, total)
    inner_rect = pygame.Rect(outer_pad + inner_pad, outer_pad + inner_pad, size - inner_pad*2, size - inner_pad*2)
    glow_color = (color[0], color[1], color[2], alpha)
    pygame.draw.ellipse(surf, glow_color, outer_rect)
    pygame.draw.ellipse(surf, (0,0,0,0), inner_rect)
    # suavizado extra: capas con alpha decreciente
    for i in range(1, 3):
        fade = max(0, int(alpha * (0.25 / i)))
        if fade <= 0:
            continue
        pad = outer_pad + i*4
        rect_w = size + pad * 2
        tmp = pygame.Surface((rect_w, rect_w), pygame.SRCALPHA)
        pygame.draw.ellipse(tmp, (color[0], color[1], color[2], fade), tmp.get_rect())
        surf.blit(tmp, (- (pad - outer_pad), - (pad - outer_pad)), special_flags=pygame.BLEND_RGBA_ADD)
    return surf

def run_skins_menu(screen, clock):
    running = True

    # Rutas detectadas en config (config.SKINS limitado en config.py a 150)
    skin_paths = list(getattr(config, "SKINS", []))
    # Placeholder coming soon (puede venir de config)
    coming_img_path = getattr(config, "COMING_SOON_IMG", None)
    coming_img = _load_image_safe(coming_img_path, SKIN_SIZE) if coming_img_path else None
    placeholder = coming_img if coming_img else _make_coming_soon_surface(SKIN_SIZE)

    # Pre-cargar imágenes (si faltan, usar placeholder)
    skins_imgs = []
    for p in skin_paths:
        img = _load_image_safe(p, SKIN_SIZE)
        skins_imgs.append(img if img else placeholder)
    if not skins_imgs:
        skins_imgs = [placeholder]

    total_skins = len(skins_imgs)
    rows = (total_skins + SKINS_PER_ROW - 1) // SKINS_PER_ROW

    # Calcular centrado horizontal
    total_row_width = SKINS_PER_ROW * SKIN_SIZE + (SKINS_PER_ROW - 1) * PADDING_X
    start_x = config.WIDTH // 2 - total_row_width // 2

    viewport_top = TOP_MARGIN
    viewport_bottom = config.HEIGHT - BOTTOM_MARGIN
    viewport_height = viewport_bottom - viewport_top

    total_height = rows * SKIN_SIZE + (rows - 1) * PADDING_Y if rows > 0 else 0

    scroll_offset = 0.0
    scroll_target = 0.0
    max_scroll = max(0, total_height - viewport_height)

    # Animaciones por skin
    hover_scale = [1.0 for _ in skins_imgs]
    hover_offset_y = [0 for _ in skins_imgs]
    glow_alpha = [0 for _ in skins_imgs]
    glow_cache = {}

    while running:
        dt = clock.tick(config.FPS)
        mx, my = pygame.mouse.get_pos()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False
            if ev.type == pygame.MOUSEWHEEL:
                scroll_target -= ev.y * SCROLL_STEP
                scroll_target = max(0, min(max_scroll, scroll_target))
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if ev.button == 4:
                    scroll_target -= SCROLL_STEP
                    scroll_target = max(0, min(max_scroll, scroll_target))
                elif ev.button == 5:
                    scroll_target += SCROLL_STEP
                    scroll_target = max(0, min(max_scroll, scroll_target))
                elif ev.button == 1:
                    # click: seleccionar skin (usar coordenadas del viewport)
                    mouse_in_view_y = my - viewport_top
                    for i in range(total_skins):
                        row = i // SKINS_PER_ROW
                        col = i % SKINS_PER_ROW
                        x = start_x + col * (SKIN_SIZE + PADDING_X)
                        y = row * (SKIN_SIZE + PADDING_Y) - int(scroll_offset)
                        rect = pygame.Rect(x, y, SKIN_SIZE, SKIN_SIZE)
                        if rect.collidepoint(mx, mouse_in_view_y):
                            if i < len(getattr(config, "SKINS", [])):
                                config.selected_skin_index = i
                            else:
                                config.selected_skin_index = -1

        # Suavizar scroll hacia target
        scroll_offset += (scroll_target - scroll_offset) * EASING
        if abs(scroll_target - scroll_offset) < 0.5:
            scroll_offset = scroll_target

        # Fondo y título
        screen.fill(config.C_BG)
        title = font_title.render("SELECCIONAR SKIN", True, config.C_TEXT)
        screen.blit(title, (config.WIDTH // 2 - title.get_width() // 2, 24))

        # Superficie para dibujar el contenido (viewport)
        surf = pygame.Surface((config.WIDTH, viewport_height), pygame.SRCALPHA)

        # Coordenada del ratón relativa al viewport (para hover correcto)
        mouse_in_view = (mx, my - viewport_top)

        # Dibujar cada skin en coordenadas relativas al viewport
        for i, img in enumerate(skins_imgs):
            row = i // SKINS_PER_ROW
            col = i % SKINS_PER_ROW
            x = start_x + col * (SKIN_SIZE + PADDING_X)
            y = row * (SKIN_SIZE + PADDING_Y) - int(scroll_offset)

            rect = pygame.Rect(x, y, SKIN_SIZE, SKIN_SIZE)
            # Detección de hover usando coordenadas relativas al viewport
            is_hover = rect.collidepoint(mouse_in_view)

            # Objetivos de animación
            target_scale = HOVER_SCALE if is_hover else 1.0
            target_offset = HOVER_OFFSET_Y if is_hover else 0
            target_glow = GLOW_MAX_ALPHA if is_hover else 0

            # Easing animaciones
            hover_scale[i] += (target_scale - hover_scale[i]) * 0.16
            hover_offset_y[i] += (target_offset - hover_offset_y[i]) * 0.16
            glow_alpha[i] += (target_glow - glow_alpha[i]) * 0.16

            new_size = int(SKIN_SIZE * hover_scale[i])
            scaled = pygame.transform.smoothscale(img, (new_size, new_size))
            center_x = x + SKIN_SIZE // 2
            center_y = y + SKIN_SIZE // 2 + int(hover_offset_y[i])
            scaled_rect = scaled.get_rect(center=(center_x, center_y))

            # Sombra (siempre detrás)
            shadow = pygame.Surface((new_size + 36, new_size + 18), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 120), shadow.get_rect())
            shadow_rect = shadow.get_rect(center=(center_x, center_y + 18))
            surf.blit(shadow, shadow_rect.topleft)

            # Glow ring: crear o reutilizar del cache según tamaño y alpha
            if glow_alpha[i] > 6:
                glow_key = (new_size, int(glow_alpha[i]))
                if glow_key not in glow_cache:
                    ring = _create_glow_ring(new_size, color=(0,180,255), outer_pad=GLOW_OUTER_PAD, inner_pad=GLOW_INNER_PAD, alpha=int(glow_alpha[i]))
                    glow_cache[glow_key] = ring
                ring_surf = glow_cache[glow_key]
                ring_rect = ring_surf.get_rect(center=(center_x, center_y))
                # Blit del anillo detrás de la skin (el centro está perforado)
                surf.blit(ring_surf, ring_rect.topleft)

            # Borde verde si está seleccionada (dibujado sobre el anillo pero debajo de la skin)
            if i == getattr(config, "selected_skin_index", -1):
                border_rect = pygame.Rect(x - 7, y - 7, SKIN_SIZE + 14, SKIN_SIZE + 14)
                pygame.draw.rect(surf, (0, 255, 0), border_rect, 6, border_radius=8)

            # Dibujar la skin encima de todo (cubre el hueco central del anillo)
            surf.blit(scaled, scaled_rect.topleft)

            # Si hover, dibujar un sutil outline encima para mayor claridad
            if is_hover:
                outline_rect = scaled_rect.inflate(6, 6)
                pygame.draw.rect(surf, (255,255,255,30), outline_rect, 2, border_radius=8)

        # Blit de la superficie recortada al screen en la posición viewport_top
        screen.blit(surf, (0, viewport_top))

        # Scrollbar (si hace falta)
        if max_scroll > 0:
            bar_w = 10
            bar_h = max(40, int(viewport_height * (viewport_height / (total_height if total_height > 0 else 1))))
            bar_x = config.WIDTH - 24
            bar_y = viewport_top + int((scroll_offset / max_scroll) * (viewport_height - bar_h))
            pygame.draw.rect(screen, (60, 60, 80), (bar_x, viewport_top, bar_w, viewport_height), border_radius=6)
            pygame.draw.rect(screen, (120, 200, 255), (bar_x, bar_y, bar_w, bar_h), border_radius=6)

        pygame.display.flip()
