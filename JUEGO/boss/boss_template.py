# boss_template.py
import pygame
import random
import os
import math
import config
from player import Player, PLAYER_MAX_HP

pygame.init()

# params:
#  image_path          -> imagen del boss
#  proj_image_path     -> imagen de las balas normales
#  big_proj_image_path -> imagen de las bolas grandes (opcional)
#  music_path          -> música del nivel
#  boss_size, boss_hp, name
#  base_pattern        -> "fan","aimed","mixed","rotating","burst"
#  shoot_interval, projectile_speed
#  ob_interval, obstacle_types
#  player_damage_to_boss, boss_proj_damage, obstacle_damage
#  phases              -> lista de dicts con "threshold" y "overrides"
#  laser_interval      -> cada cuántos ticks intenta lanzar láser
#  laser_duration      -> duración del láser
#  laser_color         -> color del láser

def run_boss_generic(screen, clock, params):
    image_path = params.get("image_path")
    proj_image_path = params.get("proj_image_path")
    big_proj_image_path = params.get("big_proj_image_path")
    music_path = params.get("music_path")

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

    def load_img(path, size=None):
        if not path:
            return None
        try:
            img = pygame.image.load(path).convert_alpha()
            if size:
                img = pygame.transform.scale(img, size)
            return img
        except:
            return None

    boss_img = load_img(image_path, (boss_size, boss_size))
    proj_img = load_img(proj_image_path, (60, 60))
    big_proj_img = load_img(big_proj_image_path, (32, 32))

    try:
        if music_path and os.path.exists(music_path):
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.6)
            pygame.mixer.music.play(-1)
    except:
        pass

    boss = {
        "w": boss_size,
        "h": boss_size,
        "x": config.WIDTH - 260,
        "y": config.HEIGHT // 2 - boss_size // 2,
        "img": boss_img,
        "hp": boss_hp,
        "projectiles": [],   # {"rect","vx","vy","life","kind"}
        "obstacles": [],     # {"rect","vx","vy","type"}
        "lasers": [],        # {"rect","timer"}
        "timer_shoot": 0,
        "timer_ob": 0,
        "timer_laser": 0,
    }

    player = Player()
    font_small = pygame.font.SysFont("Arial", 20)

    def draw_hp_bar(screen, x, y, hp, max_hp, color):
        pygame.draw.rect(screen, (60, 60, 60), (x, y, 300, 20))
        ratio = max(0, hp / max_hp)
        pygame.draw.rect(screen, color, (x, y, int(300 * ratio), 20))

    def shoot_fan(center_y, count=7, speed=projectile_speed, big=False):
        angles = [-0.7 + i * (1.4 / max(1, (count - 1))) for i in range(count)]
        for a in angles:
            rect = pygame.Rect(boss["x"], center_y, 18, 18)
            vx = -speed * math.cos(a)
            vy = speed * math.sin(a)
            boss["projectiles"].append({
                "rect": rect,
                "vx": vx,
                "vy": vy,
                "life": 320,
                "kind": "big" if big else "small"
            })

    def shoot_aimed(target_rect, speed=projectile_speed, big=False):
        sx = boss["x"]
        sy = boss["y"] + boss["h"] // 2
        rect = pygame.Rect(sx, sy, 18, 18)
        dx = (target_rect.x + target_rect.w // 2) - sx
        dy = (target_rect.y + target_rect.h // 2) - sy
        dist = max(1, math.hypot(dx, dy))
        vx = (dx / dist) * speed
        vy = (dy / dist) * speed
        boss["projectiles"].append({
            "rect": rect,
            "vx": vx,
            "vy": vy,
            "life": 420,
            "kind": "big" if big else "small"
        })

    def shoot_rotating(center_y, count=12, speed=projectile_speed, offset=0.0, big=False):
        for i in range(count):
            angle = offset + (i / count) * (2 * math.pi)
            rect = pygame.Rect(boss["x"], center_y, 18, 18)
            vx = -speed * math.cos(angle)
            vy = speed * math.sin(angle)
            boss["projectiles"].append({
                "rect": rect,
                "vx": vx,
                "vy": vy,
                "life": 320,
                "kind": "big" if big else "small"
            })

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

    def spawn_laser():
        # láser horizontal desde el boss hacia la izquierda
        y = boss["y"] + boss["h"] // 2 - 8
        rect = pygame.Rect(120, y, boss["x"] - 120, 16)
        boss["lasers"].append({"rect": rect, "timer": laser_duration})

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

    running = True
    rotating_offset = 0.0

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
                    running = False
                if ev.key == pygame.K_SPACE:
                    player.shoot()

        player.update(keys)

        t = pygame.time.get_ticks() / 700.0
        boss["y"] = int(config.HEIGHT // 2 + 90 * math.sin(t)) - boss["h"] // 2
        if player.y + player.h // 2 > boss["y"] + boss["h"] // 2 + 8:
            boss["y"] += 0.8
        elif player.y + player.h // 2 < boss["y"] + boss["h"] // 2 - 8:
            boss["y"] -= 0.8

        boss_rect = pygame.Rect(boss["x"], boss["y"], boss["w"], boss["h"])

        apply_phase_overrides()

        boss["timer_shoot"] += 1
        boss["timer_ob"] += 1
        boss["timer_laser"] += 1

        if boss["timer_shoot"] >= shoot_interval:
            if base_pattern == "fan":
                shoot_fan(boss["y"] + boss["h"] // 2, count=7, speed=projectile_speed)
            elif base_pattern == "aimed":
                shoot_aimed(player.rect, speed=projectile_speed)
            elif base_pattern == "rotating":
                shoot_rotating(boss["y"] + boss["h"] // 2, count=12, speed=projectile_speed, offset=rotating_offset)
                rotating_offset += 0.25
            elif base_pattern == "burst":
                for i in range(4):
                    shoot_aimed(player.rect, speed=projectile_speed * (1.0 + 0.1 * i))
            else:  # mixed
                r = random.randint(0, 2)
                if r == 0:
                    shoot_fan(boss["y"] + boss["h"] // 2, count=5, speed=projectile_speed)
                elif r == 1:
                    shoot_aimed(player.rect, speed=projectile_speed)
                else:
                    shoot_rotating(boss["y"] + boss["h"] // 2, count=10, speed=projectile_speed, offset=rotating_offset)
                    rotating_offset += 0.2
            # bola grande cada cierto rato
            if random.random() < 0.35:
                shoot_aimed(player.rect, speed=projectile_speed * 0.8, big=True)
            boss["timer_shoot"] = 0

        if boss["timer_ob"] >= ob_interval:
            spawn_obstacle()
            boss["timer_ob"] = 0

        if laser_interval > 0 and boss["timer_laser"] >= laser_interval:
            spawn_laser()
            boss["timer_laser"] = 0

        for p in boss["projectiles"]:
            p["rect"].x += int(p["vx"])
            p["rect"].y += int(p["vy"])
            p["life"] -= 1
        boss["projectiles"] = [
            p for p in boss["projectiles"]
            if p["life"] > 0 and -200 < p["rect"].x < config.WIDTH + 200 and -200 < p["rect"].y < config.HEIGHT + 200
        ]

        for o in boss["obstacles"]:
            o["rect"].x += int(o.get("vx", 0))
            o["rect"].y += int(o.get("vy", 0))
        boss["obstacles"] = [
            o for o in boss["obstacles"]
            if -200 < o["rect"].x < config.WIDTH + 200 and -200 < o["rect"].y < config.HEIGHT + 200
        ]

        for l in boss["lasers"]:
            l["timer"] -= 1
        boss["lasers"] = [l for l in boss["lasers"] if l["timer"] > 0]

        for shot in list(player.shots):
            if boss_rect.colliderect(shot):
                boss["hp"] -= player_damage_to_boss
                try:
                    player.shots.remove(shot)
                except:
                    pass

        for p in list(boss["projectiles"]):
            if player.rect.colliderect(p["rect"]):
                player.hp -= boss_proj_damage if p["kind"] == "small" else boss_proj_damage + 6
                try:
                    boss["projectiles"].remove(p)
                except:
                    pass

        for o in list(boss["obstacles"]):
            if player.rect.colliderect(o["rect"]):
                player.hp -= obstacle_damage
                try:
                    boss["obstacles"].remove(o)
                except:
                    pass

        for l in boss["lasers"]:
            if player.rect.colliderect(l["rect"]):
                player.hp -= boss_proj_damage + 10

        if player.hp <= 0 or boss["hp"] <= 0:
            running = False

        screen.fill(config.C_BG)
        player.draw(screen)

        if boss["img"]:
            screen.blit(boss["img"], (boss["x"], boss["y"]))
        else:
            pygame.draw.rect(screen, (200, 60, 60), (boss["x"], boss["y"], boss["w"], boss["h"]))

        for p in boss["projectiles"]:
            if p["kind"] == "big" and big_proj_img:
                screen.blit(big_proj_img, p["rect"])
            elif proj_img:
                screen.blit(proj_img, p["rect"])
            else:
                color = (255, 200, 80) if p["kind"] == "big" else (255, 120, 80)
                pygame.draw.rect(screen, color, p["rect"])

        for o in boss["obstacles"]:
            pygame.draw.rect(screen, (200, 160, 0), o["rect"])

        for l in boss["lasers"]:
            pygame.draw.rect(screen, laser_color, l["rect"])

        draw_hp_bar(screen, 20, 20, player.hp, PLAYER_MAX_HP, (0, 255, 0))
        draw_hp_bar(screen, config.WIDTH - 320, 20, boss["hp"], boss_hp, (255, 80, 60))

        name_surf = font_small.render(f"{name}  HP:{boss['hp']}", True, config.C_TEXT)
        screen.blit(name_surf, (config.WIDTH // 2 - name_surf.get_width() // 2, 20))

        pygame.display.flip()

    try:
        pygame.mixer.music.stop()
    except:
        pass
