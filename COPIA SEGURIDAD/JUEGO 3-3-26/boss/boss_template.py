# boss_template.py
import pygame
import random
import os
import math
import config
from player import Player, PLAYER_MAX_HP
pygame.init()

# run_boss_generic(screen, clock, params)
# params keys (extended):
#  - image_path (str) optional
#  - proj_image_path (str) optional
#  - big_proj_image_path (str) optional
#  - music_path (str) optional
#  - explosion_sound (str) optional -> sonido específico para la explosión de este boss
#  - boss_size (int)
#  - boss_hp (int)
#  - name (str)
#  - phases (list of dict) optional
#  - base_pattern (str): "fan","aimed","mixed","rotating","burst"
#  - shoot_interval (int)
#  - projectile_speed (float)
#  - ob_interval (int)
#  - obstacle_types (list)
#  - player_damage_to_boss (int)
#  - boss_proj_damage (int)
#  - obstacle_damage (int)
#  - heal_image_path (str) optional
#  - heal_interval (int) frames
#  - heal_amount (int)
#  - heal_spawn_count (int)
#  - puddle_interval (int) frames (for poison puddles)
#  - puddle_damage_per_sec (int)
#  - puddle_near_player_radius (int)
#  - orientation: "vertical","horizontal","both"
#  - tutorial (bool) -> special tutorial behavior
#  - enable_puddles, enable_lasers, enable_enrage (bool)
#  - enrage_cycle, enrage_duration, enrage_factor (for enrage mechanic)

def run_boss_generic(screen, clock, params):
    # Detener música del menú al entrar al boss (si está sonando)
    try:
        pygame.mixer.music.stop()
    except:
        pass

    # Parámetros básicos
    image_path = params.get("image_path")
    proj_image_path = params.get("proj_image_path")
    big_proj_image_path = params.get("big_proj_image_path")
    music_path = params.get("music_path")
    explosion_sound_path = params.get("explosion_sound", getattr(config, "EXPLOSION_SOUND", None))

    boss_size = params.get("boss_size", 160)
    boss_hp = params.get("boss_hp", 800)
    name = params.get("name", "BOSS")

    base_pattern = params.get("base_pattern", "mixed")
    shoot_interval = params.get("shoot_interval", 60)
    projectile_speed = params.get("projectile_speed", 6.0)
    ob_interval = params.get("ob_interval", 220)
    obstacle_types = params.get("obstacle_types", ["falling", "moving"])

    player_damage_to_boss = params.get("player_damage_to_boss", 10)
    boss_proj_damage = params.get("boss_proj_damage", 16)
    obstacle_damage = params.get("obstacle_damage", 18)
    phases = params.get("phases", [])

    laser_interval = params.get("laser_interval", 420)
    laser_duration = params.get("laser_duration", 120)
    laser_color = params.get("laser_color", (255, 40, 40))

    # Nuevas opciones y ajustes por defecto
    heal_image_path = params.get("heal_image_path", getattr(config, "HEAL_PICKUP_IMG", None))
    heal_interval = params.get("heal_interval", 600)
    heal_amount = params.get("heal_amount", 30)
    heal_spawn_count = params.get("heal_spawn_count", 1)

    puddle_interval = params.get("puddle_interval", 300)
    puddle_damage_per_sec = params.get("puddle_damage_per_sec", 6)
    puddle_near_player_radius = params.get("puddle_near_player_radius", 220)

    orientation = params.get("orientation", "vertical")
    tutorial_mode = params.get("tutorial", False)

    # Cargar imágenes
    def load_img(path, size=None):
        if not path:
            return None
        try:
            img = pygame.image.load(path).convert_alpha()
            if size:
                img = pygame.transform.smoothscale(img, size)
            return img
        except:
            return None

    boss_img = load_img(image_path, (boss_size, boss_size))
    proj_img = load_img(proj_image_path, (36, 36))
    big_proj_img = load_img(big_proj_image_path, (72, 72))
    heal_img = load_img(heal_image_path, (28, 28))

    # Precargar sonido de explosión para evitar latencia
    explosion_sound = None
    try:
        if explosion_sound_path and os.path.exists(explosion_sound_path):
            explosion_sound = pygame.mixer.Sound(explosion_sound_path)
            # volumen por defecto; puedes ajustar en params si quieres
            explosion_sound.set_volume(params.get("explosion_volume", 1.0))
    except:
        explosion_sound = None

    # Iniciar música del boss (si existe)
    try:
        if music_path and os.path.exists(music_path):
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(params.get("music_volume", 0.6))
            pygame.mixer.music.play(-1)
    except:
        pass

    # Estado del boss
    boss = {
        "w": boss_size,
        "h": boss_size,
        "x": config.WIDTH - 260,
        "y": config.HEIGHT // 2 - boss_size // 2,
        "img": boss_img,
        "hp": boss_hp,
        "max_hp": boss_hp,
        "projectiles": [],
        "obstacles": [],
        "lasers": [],
        "heals": [],
        "puddles": [],
        "timer_shoot": 0,
        "timer_ob": 0,
        "timer_laser": 0,
        "timer_heal": 0,
        "timer_puddle": 0,
        "enrage_timer": 0,
    }

    player = Player()
    font_small = pygame.font.SysFont("Arial", 20)
    font_big = pygame.font.SysFont("Arial Black", 34)

    def draw_hp_bar(screen, x, y, hp, max_hp, color):
        pygame.draw.rect(screen, (60,60,60), (x, y, 300, 20))
        ratio = max(0, hp / max_hp)
        pygame.draw.rect(screen, color, (x, y, int(300 * ratio), 20))

    # Helpers para proyectiles y entidades
    def spawn_projectile(x, y, vx, vy, life=300, kind="small", size=18):
        rect = pygame.Rect(int(x), int(y), size, size)
        boss["projectiles"].append({"rect":rect,"vx":vx,"vy":vy,"life":life,"kind":kind,"size":size})

    def shoot_fan(center_y, count=7, speed=projectile_speed, big=False):
        angles = [-0.7 + i * (1.4 / max(1, (count - 1))) for i in range(count)]
        for a in angles:
            sx = boss["x"]
            sy = center_y
            vx = -speed * math.cos(a)
            vy = speed * math.sin(a)
            if big:
                spawn_projectile(sx, sy, vx, vy, life=420, kind="big", size=36)
            else:
                spawn_projectile(sx, sy, vx, vy, life=320, kind="small", size=18)

    def shoot_aimed(target_rect, speed=projectile_speed, big=False):
        sx = boss["x"]
        sy = boss["y"] + boss["h"] // 2
        dx = (target_rect.x + target_rect.w // 2) - sx
        dy = (target_rect.y + target_rect.h // 2) - sy
        dist = max(1, math.hypot(dx, dy))
        vx = (dx / dist) * speed
        vy = (dy / dist) * speed
        if big:
            spawn_projectile(sx, sy, vx, vy, life=420, kind="big", size=36)
        else:
            spawn_projectile(sx, sy, vx, vy, life=320, kind="small", size=18)

    def shoot_rotating(center_y, count=12, speed=projectile_speed, offset=0.0, big=False):
        for i in range(count):
            angle = offset + (i / count) * (2 * math.pi)
            sx = boss["x"]
            sy = center_y
            vx = -speed * math.cos(angle)
            vy = speed * math.sin(angle)
            if big:
                spawn_projectile(sx, sy, vx, vy, life=320, kind="big", size=36)
            else:
                spawn_projectile(sx, sy, vx, vy, life=320, kind="small", size=18)

    def spawn_obstacle(kind=None):
        kind = kind or random.choice(obstacle_types)
        if kind == "falling":
            ox = random.randint(200, config.WIDTH - 200)
            rect = pygame.Rect(ox, -40, 40, 40)
            boss["obstacles"].append({"rect": rect, "vx": 0, "vy": random.randint(3, 6), "type": "falling"})
        elif kind == "moving":
            ox = config.WIDTH + 40
            oy = random.randint(80, config.HEIGHT - 120)
            rect = pygame.Rect(ox, oy, 60, 26)
            boss["obstacles"].append({"rect": rect, "vx": -5, "vy": 0, "type": "moving"})
        elif kind == "mine":
            mx = random.randint(260, config.WIDTH - 220)
            rect = pygame.Rect(mx, config.HEIGHT - 30, 20, 20)
            boss["obstacles"].append({"rect": rect, "vx": 0, "vy": 0, "type": "mine"})

    def spawn_heal(count=1):
        for _ in range(count):
            hx = random.randint(200, config.WIDTH - 300)
            hy = random.randint(80, config.HEIGHT - 120)
            rect = pygame.Rect(hx, hy, 28, 28)
            boss["heals"].append({"rect":rect,"amount":heal_amount,"life":600})

    def spawn_puddle_near_player():
        px = max(200, min(config.WIDTH - 200, int(player.x + random.randint(-puddle_near_player_radius, puddle_near_player_radius))))
        pw = random.randint(80, 140)
        py = config.HEIGHT - 40
        rect = pygame.Rect(max(200, min(config.WIDTH - pw - 100, px)), py, pw, 28)
        boss["puddles"].append({"rect":rect,"timer":600})

    def spawn_laser_horizontal(ypos=None):
        y = ypos if ypos is not None else boss["y"] + boss["h"] // 2 - 8
        rect = pygame.Rect(120, y, boss["x"] - 120, 16)
        boss["lasers"].append({"rect":rect,"timer":laser_duration,"dir":"h"})

    def spawn_laser_vertical(xpos=None):
        x = xpos if xpos is not None else boss["x"] - 40
        rect = pygame.Rect(x, 80, 16, config.HEIGHT - 160)
        boss["lasers"].append({"rect":rect,"timer":laser_duration,"dir":"v"})

    def apply_phase_overrides():
        nonlocal shoot_interval, projectile_speed, ob_interval, base_pattern, laser_interval
        if not phases:
            return
        current_hp = boss["hp"]
        chosen = None
        for p in phases:
            if current_hp <= p.get("threshold", -1):
                chosen = p
        if chosen:
            overrides = chosen.get("overrides", {})
            shoot_interval = overrides.get("shoot_interval", shoot_interval)
            projectile_speed = overrides.get("projectile_speed", projectile_speed)
            ob_interval = overrides.get("ob_interval", ob_interval)
            base_pattern = overrides.get("base_pattern", base_pattern)
            laser_interval = overrides.get("laser_interval", laser_interval)

    # Cola de mensajes tutorial
    tutorial_messages = []
    def show_tutorial_message(text, duration=2200):
        tutorial_messages.append({"text":text,"timer":duration})

    # Bloqueo de armas en tutorial
    if tutorial_mode:
        player.allowed_weapons = {"pistol": True, "shotgun": False, "rocket": False}
    else:
        player.allowed_weapons = {"pistol": True, "shotgun": True, "rocket": True}

    running = True
    rotating_offset = 0.0

    # Parámetros de enrage
    enrage_cycle = params.get("enrage_cycle", 900)
    enrage_duration = params.get("enrage_duration", 240)
    enrage_factor = params.get("enrage_factor", 0.6)

    while running:
        clock.tick(config.FPS)
        keys = pygame.key.get_pressed()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                try:
                    pygame.mixer.music.stop()
                except:
                    pass
                pygame.quit()
                raise SystemExit
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    # salida temprana al menú
                    try:
                        pygame.mixer.music.stop()
                    except:
                        pass
                    return "exit"
                if ev.key == pygame.K_SPACE:
                    player.shoot(target_rect=pygame.Rect(int(boss["x"]), int(boss["y"]), boss["w"], boss["h"]))

        player.update(keys)

        # Movimiento del boss según orientación
        t = pygame.time.get_ticks() / 700.0
        if orientation == "vertical":
            boss["y"] = int(config.HEIGHT // 2 + 90 * math.sin(t)) - boss["h"] // 2
        elif orientation == "horizontal":
            x_min = config.WIDTH - 520
            x_max = config.WIDTH - 120
            boss["x"] += int(1.6 * math.sin(t * 1.2))
            boss["x"] = max(x_min, min(x_max, boss["x"]))
        else:
            boss["y"] = int(config.HEIGHT // 2 + 90 * math.sin(t)) - boss["h"] // 2
            boss["x"] = int(config.WIDTH - 260 + 40 * math.sin(t / 1.7))

        # ligera corrección para seguir al jugador
        if player.y + player.h // 2 > boss["y"] + boss["h"] // 2 + 8:
            boss["y"] += 0.8
        elif player.y + player.h // 2 < boss["y"] + boss["h"] // 2 - 8:
            boss["y"] -= 0.8

        boss_rect = pygame.Rect(int(boss["x"]), int(boss["y"]), boss["w"], boss["h"])

        apply_phase_overrides()

        boss["timer_shoot"] += 1
        boss["timer_ob"] += 1
        boss["timer_laser"] += 1
        boss["timer_heal"] += 1
        boss["timer_puddle"] += 1
        boss["enrage_timer"] += 1

        # enrage activo?
        enrage_active = False
        if params.get("enable_enrage", False):
            cycle_pos = boss["enrage_timer"] % enrage_cycle
            if cycle_pos < enrage_duration:
                enrage_active = True
        effective_shoot_interval = int(shoot_interval * (enrage_factor if enrage_active else 1.0))

        # Lógica de disparo
        if boss["timer_shoot"] >= effective_shoot_interval:
            if tutorial_mode:
                # tutorial: alterna proyectiles normales y grandes
                if (boss["timer_shoot"] // effective_shoot_interval) % 2 == 0:
                    shoot_fan(boss["y"] + boss["h"] // 2, count=5, speed=projectile_speed, big=False)
                else:
                    shoot_fan(boss["y"] + boss["h"] // 2, count=5, speed=projectile_speed * 0.7, big=True)
            else:
                if base_pattern == "fan":
                    shoot_fan(boss["y"] + boss["h"] // 2, count=params.get("fan_count", 7), speed=projectile_speed)
                elif base_pattern == "aimed":
                    shoot_aimed(player.rect, speed=projectile_speed)
                elif base_pattern == "rotating":
                    shoot_rotating(boss["y"] + boss["h"] // 2, count=params.get("rot_count", 12), speed=projectile_speed, offset=rotating_offset)
                    rotating_offset += 0.25
                elif base_pattern == "burst":
                    for i in range(4):
                        shoot_aimed(player.rect, speed=projectile_speed * (1.0 + 0.1 * i))
                else:
                    r = random.randint(0, 2)
                    if r == 0:
                        shoot_fan(boss["y"] + boss["h"] // 2, count=5, speed=projectile_speed)
                    elif r == 1:
                        shoot_aimed(player.rect, speed=projectile_speed)
                    else:
                        shoot_rotating(boss["y"] + boss["h"] // 2, count=10, speed=projectile_speed, offset=rotating_offset)
                        rotating_offset += 0.2
                # bola grande ocasional
                if random.random() < 0.28:
                    shoot_aimed(player.rect, speed=projectile_speed * 0.8, big=True)
            boss["timer_shoot"] = 0

        # Obstáculos
        if boss["timer_ob"] >= ob_interval:
            spawn_obstacle()
            boss["timer_ob"] = 0

        # Curativos (más frecuentes si configurado)
        if boss["timer_heal"] >= heal_interval:
            spawn_heal(count=heal_spawn_count)
            boss["timer_heal"] = 0

        # Charcos cerca del jugador (nivel 1)
        if params.get("enable_puddles", False) and boss["timer_puddle"] >= puddle_interval:
            for _ in range(random.randint(1, 2)):
                spawn_puddle_near_player()
            boss["timer_puddle"] = 0

        # Láseres (nivel 2)
        if params.get("enable_lasers", False) and laser_interval > 0 and boss["timer_laser"] >= laser_interval:
            spawn_laser_horizontal()
            if random.random() < 0.5:
                spawn_laser_vertical()
            boss["timer_laser"] = 0

        # Actualizar proyectiles y entidades
        for p in boss["projectiles"]:
            p["rect"].x += int(p["vx"])
            p["rect"].y += int(p["vy"])
            p["life"] -= 1
        boss["projectiles"] = [
            p for p in boss["projectiles"]
            if p["life"] > 0 and -300 < p["rect"].x < config.WIDTH + 300 and -300 < p["rect"].y < config.HEIGHT + 300
        ]

        for o in boss["obstacles"]:
            o["rect"].x += int(o.get("vx", 0))
            o["rect"].y += int(o.get("vy", 0))
        boss["obstacles"] = [
            o for o in boss["obstacles"]
            if -300 < o["rect"].x < config.WIDTH + 300 and -300 < o["rect"].y < config.HEIGHT + 300
        ]

        for h in boss["heals"]:
            h["life"] -= 1
        boss["heals"] = [h for h in boss["heals"] if h["life"] > 0]

        for pd in boss["puddles"]:
            pd["timer"] -= 1
        boss["puddles"] = [pd for pd in boss["puddles"] if pd["timer"] > 0]

        for l in boss["lasers"]:
            l["timer"] -= 1
        boss["lasers"] = [l for l in boss["lasers"] if l["timer"] > 0]

        # Colisiones: disparos del jugador -> boss
        for shot in list(player.shots):
            if boss_rect.colliderect(shot["rect"]):
                boss["hp"] -= shot.get("damage", player_damage_to_boss)
                try:
                    player.shots.remove(shot)
                except:
                    pass

        # Proyectiles del boss -> jugador (grandes hacen doble daño)
        for p in list(boss["projectiles"]):
            if player.rect.colliderect(p["rect"]):
                if p["kind"] == "big":
                    dmg = boss_proj_damage * 2
                else:
                    dmg = boss_proj_damage
                player.hp -= dmg
                try:
                    boss["projectiles"].remove(p)
                except:
                    pass

        # Obstáculos -> jugador
        for o in list(boss["obstacles"]):
            if player.rect.colliderect(o["rect"]):
                player.hp -= obstacle_damage
                try:
                    boss["obstacles"].remove(o)
                except:
                    pass

        # Curativos -> jugador
        for h in list(boss["heals"]):
            if player.rect.colliderect(h["rect"]):
                player.hp = min(PLAYER_MAX_HP, player.hp + h.get("amount", heal_amount))
                try:
                    boss["heals"].remove(h)
                except:
                    pass

        # Puddles -> jugador (daño por segundo)
        for pd in boss["puddles"]:
            if player.rect.colliderect(pd["rect"]):
                per_frame = puddle_damage_per_sec / config.FPS
                player.hp -= per_frame

        # Lasers -> jugador
        for l in boss["lasers"]:
            if player.rect.colliderect(l["rect"]):
                player.hp -= boss_proj_damage + 10

        # Tutorial: desbloqueo por tercios
        if tutorial_mode:
            third = boss["max_hp"] / 3.0
            if boss["hp"] <= 2 * third and not player.allowed_weapons.get("shotgun", False):
                player.unlock_weapon("shotgun")
                show_tutorial_message("Has desbloqueado la Escopeta. Pulsa 2 para seleccionarla.", 3000)
            if boss["hp"] <= third and not player.allowed_weapons.get("rocket", False):
                player.unlock_weapon("rocket")
                show_tutorial_message("Has desbloqueado el Lanzacohetes. Pulsa 3 para usarlo.", 3500)

        # Decrementar timers de mensajes tutorial
        if tutorial_messages:
            for m in tutorial_messages:
                m["timer"] -= 1
            tutorial_messages = [m for m in tutorial_messages if m["timer"] > 0]

        # Condición de derrota del jugador
        if player.hp <= 0:
            try:
                pygame.mixer.music.stop()
            except:
                pass
            return "lose"

        # Condición de victoria del jugador (boss muerto)
        if boss["hp"] <= 0:
            # 1) Fadeout o stop de la música para que solo se oiga la explosión
            try:
                # fadeout suave (300 ms). Si prefieres corte instantáneo, usa pygame.mixer.music.stop()
                pygame.mixer.music.fadeout(300)
            except:
                try:
                    pygame.mixer.music.stop()
                except:
                    pass

            # 2) Reproducir sonido de explosión (preloaded)
            try:
                if explosion_sound:
                    explosion_sound.play()
            except:
                pass

            # 3) Animación vistosa de explosión (4 segundos)
            explosion_duration_sec = 4.0
            explosion_frames = int(explosion_duration_sec * config.FPS)
            particles = []
            cx = int(boss["x"] + boss["w"] // 2)
            cy = int(boss["y"] + boss["h"] // 2)
            # generar partículas
            for i in range(120):
                angle = random.random() * 2 * math.pi
                speed = random.uniform(2.0, 8.0)
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed
                size = random.randint(4, 12)
                life = explosion_frames
                color = (255, random.randint(80, 200), random.randint(20, 80))
                particles.append({"x": cx, "y": cy, "vx": vx, "vy": vy, "size": size, "life": life, "color": color})

            # animar durante explosion_frames frames
            for f in range(explosion_frames):
                clock.tick(config.FPS)
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        pygame.quit(); raise SystemExit

                # actualizar partículas
                for p in particles:
                    p["x"] += p["vx"]
                    p["y"] += p["vy"]
                    p["vx"] *= 0.98
                    p["vy"] *= 0.98
                    p["vy"] += 0.12
                    p["life"] -= 1

                # dibujar frame
                screen.fill(config.C_BG)
                player.draw(screen)

                # dibujar partículas con fade
                for p in particles:
                    alpha = max(0, int(255 * (p["life"] / explosion_frames)))
                    surf = pygame.Surface((p["size"] * 2, p["size"] * 2), pygame.SRCALPHA)
                    pygame.draw.circle(surf, (p["color"][0], p["color"][1], p["color"][2], alpha), (p["size"], p["size"]), p["size"])
                    screen.blit(surf, (p["x"] - p["size"], p["y"] - p["size"]))

                # fragmentos del boss para sensación de destrucción
                for i in range(8):
                    rx = cx + int(math.sin(f * 0.1 + i) * (f * 0.6))
                    ry = cy + int(math.cos(f * 0.1 + i) * (f * 0.4))
                    rsize = max(2, int(6 + (f / (explosion_frames / 6))))
                    pygame.draw.rect(screen, (200, 80, 60), (rx, ry, rsize, rsize))

                # HUD (player hp)
                draw_hp_bar(screen, 20, 20, player.hp, PLAYER_MAX_HP, (0, 255, 0))
                pygame.display.flip()

            # 4) Asegurarse de que la música no vuelva a sonar automáticamente
            try:
                pygame.mixer.music.stop()
            except:
                pass

            return "win"

        # Dibujado normal del bucle
        screen.fill(config.C_BG)
        player.draw(screen)

        # Boss
        if boss["img"]:
            screen.blit(boss["img"], (int(boss["x"]), int(boss["y"])))
        else:
            pygame.draw.rect(screen, (200, 60, 60), (int(boss["x"]), int(boss["y"]), boss["w"], boss["h"]))

        # Dibujar proyectiles del boss
        for p in boss["projectiles"]:
            if p["kind"] == "big" and big_proj_img:
                try:
                    screen.blit(big_proj_img, p["rect"])
                except:
                    pygame.draw.rect(screen, (255, 180, 80), p["rect"])
            elif proj_img:
                try:
                    screen.blit(proj_img, p["rect"])
                except:
                    pygame.draw.rect(screen, (255, 120, 80), p["rect"])
            else:
                color = (255, 200, 80) if p["kind"] == "big" else (255, 120, 80)
                pygame.draw.rect(screen, color, p["rect"])

        # Dibujar obstáculos
        for o in boss["obstacles"]:
            pygame.draw.rect(screen, (200, 160, 0), o["rect"])

        # Dibujar curativos
        for h in boss["heals"]:
            if heal_img:
                screen.blit(heal_img, h["rect"])
            else:
                pygame.draw.rect(screen, (0, 200, 120), h["rect"])

        # Dibujar puddles
        for pd in boss["puddles"]:
            pygame.draw.rect(screen, (40, 120, 40), pd["rect"])

        # Dibujar lasers
        for l in boss["lasers"]:
            pygame.draw.rect(screen, laser_color, l["rect"])

        # Barras de vida
        draw_hp_bar(screen, 20, 20, player.hp, PLAYER_MAX_HP, (0, 255, 0))
        draw_hp_bar(screen, config.WIDTH - 320, 20, boss["hp"], boss["max_hp"], (255, 80, 60))

        # Nombre + hp
        name_surf = font_small.render(f"{name}  HP:{int(boss['hp'])}", True, config.C_TEXT)
        screen.blit(name_surf, (config.WIDTH // 2 - name_surf.get_width() // 2, 20))

        # Mensajes tutorial
        if tutorial_messages:
            y = config.HEIGHT - 120
            for m in tutorial_messages:
                txt = font_big.render(m["text"], True, (255, 255, 200))
                screen.blit(txt, (config.WIDTH // 2 - txt.get_width() // 2, y))
                y -= txt.get_height() + 8

        pygame.display.flip()
