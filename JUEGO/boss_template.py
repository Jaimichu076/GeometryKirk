# boss_template.py
import pygame
import random
import os
import math
import config
from player import Player, PLAYER_MAX_HP
pygame.init()

# run_boss_generic(screen, clock, params)
# params keys:
#  - image_path (str) optional
#  - music_path (str) optional
#  - boss_size (int)
#  - boss_hp (int)
#  - name (str)
#  - phases (list of dict) optional: each phase can override shoot_interval, projectile_speed, patterns, ob_interval, etc.
#  - base_pattern (str): "fan","aimed","mixed","rotating","burst"
#  - shoot_interval (int)
#  - projectile_speed (float)
#  - ob_interval (int)
#  - obstacle_types (list) optional
#  - player_damage_to_boss (int)
#  - boss_proj_damage (int)
#  - obstacle_damage (int)

def run_boss_generic(screen, clock, params):
    # Load resources
    image_path = params.get("image_path")
    music_path = params.get("music_path")
    boss_size = params.get("boss_size", 160)
    boss_hp = params.get("boss_hp", 800)
    name = params.get("name", "BOSS")
    base_pattern = params.get("base_pattern", "mixed")
    shoot_interval = params.get("shoot_interval", 60)
    projectile_speed = params.get("projectile_speed", 6.0)
    ob_interval = params.get("ob_interval", 220)
    obstacle_types = params.get("obstacle_types", ["falling","moving"])
    player_damage_to_boss = params.get("player_damage_to_boss", 10)
    boss_proj_damage = params.get("boss_proj_damage", 16)
    obstacle_damage = params.get("obstacle_damage", 18)
    phases = params.get("phases", [])  # list of dicts with thresholds and overrides

    # safe image loader
    def load_img(path, size):
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, (size, size))
        except Exception:
            surf = pygame.Surface((size, size))
            surf.fill((180, 60, 60))
            return surf

    boss_img = load_img(image_path, boss_size) if image_path else None

    # music
    try:
        if music_path and os.path.exists(music_path):
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.6)
            pygame.mixer.music.play(-1)
    except Exception:
        pass

    # boss state (use dicts, not attributes on Rect)
    boss = {
        "w": boss_size,
        "h": boss_size,
        "x": config.WIDTH - 260,
        "y": config.HEIGHT//2 - boss_size//2,
        "img": boss_img,
        "hp": boss_hp,
        "projectiles": [],   # {"rect":Rect,"vx":float,"vy":float,"life":int}
        "obstacles": [],     # {"rect":Rect,"vx":float,"vy":float,"type":str}
        "timer_shoot": 0,
        "timer_ob": 0,
        "phase_index": 0,
        "phase_timer": 0,
    }

    player = Player()
    font_small = pygame.font.SysFont("Arial", 20)

    def draw_hp_bar(screen, x, y, hp, max_hp, color):
        pygame.draw.rect(screen, (60,60,60), (x, y, 300, 20))
        ratio = max(0, hp/max_hp)
        pygame.draw.rect(screen, color, (x, y, int(300*ratio), 20))

    # helper patterns
    def shoot_fan(center_y, count=7, speed=projectile_speed):
        angles = [ -0.6 + i*(1.2/(count-1)) for i in range(count) ]
        for a in angles:
            rect = pygame.Rect(boss["x"], center_y, 12, 12)
            vx = -speed * math.cos(a)
            vy = speed * math.sin(a)
            boss["projectiles"].append({"rect":rect,"vx":vx,"vy":vy,"life":300})

    def shoot_aimed(target_rect, speed=projectile_speed):
        sx = boss["x"]
        sy = boss["y"] + boss["h"]//2
        rect = pygame.Rect(sx, sy, 12, 12)
        dx = (target_rect.x + target_rect.w//2) - sx
        dy = (target_rect.y + target_rect.h//2) - sy
        dist = max(1, math.hypot(dx, dy))
        vx = (dx/dist) * speed
        vy = (dy/dist) * speed
        boss["projectiles"].append({"rect":rect,"vx":vx,"vy":vy,"life":400})

    def shoot_rotating(center_y, count=12, speed=projectile_speed, offset=0.0):
        for i in range(count):
            angle = offset + (i / count) * (2*math.pi)
            rect = pygame.Rect(boss["x"], center_y, 12, 12)
            vx = -speed * math.cos(angle)
            vy = speed * math.sin(angle)
            boss["projectiles"].append({"rect":rect,"vx":vx,"vy":vy,"life":300})

    def spawn_obstacle(kind=None):
        kind = kind or random.choice(obstacle_types)
        if kind == "falling":
            ox = random.randint(200, config.WIDTH - 200)
            rect = pygame.Rect(ox, -40, 36, 36)
            boss["obstacles"].append({"rect":rect,"vx":0,"vy":random.randint(3,6),"type":"falling"})
        elif kind == "moving":
            ox = config.WIDTH + 40
            oy = random.randint(80, config.HEIGHT - 120)
            rect = pygame.Rect(ox, oy, 48, 24)
            boss["obstacles"].append({"rect":rect,"vx":-5,"vy":0,"type":"moving"})
        elif kind == "mine":
            mx = random.randint(300, config.WIDTH - 200)
            rect = pygame.Rect(mx, config.HEIGHT - 28, 18, 18)
            boss["obstacles"].append({"rect":rect,"vx":0,"vy":0,"type":"mine"})

    # phase helper: check thresholds and apply overrides
    def apply_phase_overrides():
        nonlocal shoot_interval, projectile_speed, ob_interval, base_pattern
        if not phases:
            return
        # phases is list of dicts: {"threshold":hp_value, "overrides":{...}}
        # choose highest threshold <= current hp
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

    # main loop
    running = True
    rotating_offset = 0.0
    while running:
        clock.tick(config.FPS)
        keys = pygame.key.get_pressed()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                try: pygame.mixer.music.stop()
                except: pass
                pygame.quit(); raise SystemExit
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False
                if ev.key == pygame.K_SPACE:
                    player.shoot()

        player.update(keys)

        # movement: sinusoidal + small tracking
        t = pygame.time.get_ticks() / 700.0
        boss["y"] = int(config.HEIGHT//2 + 90 * math.sin(t)) - boss["h"]//2
        # slight tracking to make it feel alive
        if player.y + player.h//2 > boss["y"] + boss["h"]//2 + 8:
            boss["y"] += 0.8
        elif player.y + player.h//2 < boss["y"] + boss["h"]//2 - 8:
            boss["y"] -= 0.8

        boss_rect = pygame.Rect(boss["x"], boss["y"], boss["w"], boss["h"])

        # phases
        apply_phase_overrides()

        # timers
        boss["timer_shoot"] += 1
        boss["timer_ob"] += 1
        boss["phase_timer"] += 1

        # shooting patterns
        if boss["timer_shoot"] >= shoot_interval:
            if base_pattern == "fan":
                shoot_fan(boss["y"] + boss["h"]//2, count=params.get("fan_count",7), speed=projectile_speed)
            elif base_pattern == "aimed":
                shoot_aimed(player.rect, speed=projectile_speed)
            elif base_pattern == "rotating":
                shoot_rotating(boss["y"] + boss["h"]//2, count=params.get("rot_count",12), speed=projectile_speed, offset=rotating_offset)
                rotating_offset += 0.3
            elif base_pattern == "burst":
                # quick burst of aimed shots
                for _ in range(3):
                    shoot_aimed(player.rect, speed=projectile_speed*1.1)
            else:  # mixed
                if (boss["timer_shoot"] // shoot_interval) % 3 == 0:
                    shoot_rotating(boss["y"] + boss["h"]//2, count=10, speed=projectile_speed, offset=rotating_offset)
                    rotating_offset += 0.2
                elif (boss["timer_shoot"] // shoot_interval) % 3 == 1:
                    shoot_fan(boss["y"] + boss["h"]//2, count=5, speed=projectile_speed)
                else:
                    shoot_aimed(player.rect, speed=projectile_speed)
            boss["timer_shoot"] = 0

        # obstacles spawn
        if boss["timer_ob"] >= ob_interval:
            spawn_obstacle()
            boss["timer_ob"] = 0

        # update projectiles and obstacles
        for p in boss["projectiles"]:
            p["rect"].x += int(p["vx"])
            p["rect"].y += int(p["vy"])
            p["life"] -= 1
        boss["projectiles"] = [p for p in boss["projectiles"] if p["life"] > 0 and -200 < p["rect"].x < config.WIDTH + 200 and -200 < p["rect"].y < config.HEIGHT + 200]

        for o in boss["obstacles"]:
            o["rect"].x += int(o.get("vx",0))
            o["rect"].y += int(o.get("vy",0))
        boss["obstacles"] = [o for o in boss["obstacles"] if -200 < o["rect"].x < config.WIDTH + 200 and -200 < o["rect"].y < config.HEIGHT + 200]

        # collisions: player shots -> boss
        for shot in list(player.shots):
            if boss_rect.colliderect(shot):
                boss["hp"] -= player_damage_to_boss
                try: player.shots.remove(shot)
                except: pass

        # boss projectiles -> player
        for p in list(boss["projectiles"]):
            if player.rect.colliderect(p["rect"]):
                player.hp -= boss_proj_damage
                try: boss["projectiles"].remove(p)
                except: pass

        # obstacles -> player
        for o in list(boss["obstacles"]):
            if player.rect.colliderect(o["rect"]):
                player.hp -= obstacle_damage
                try: boss["obstacles"].remove(o)
                except: pass

        # end conditions
        if player.hp <= 0 or boss["hp"] <= 0:
            running = False

        # draw
        screen.fill(config.C_BG)
        player.draw(screen)
        if boss["img"]:
            screen.blit(boss["img"], (boss["x"], boss["y"]))
        else:
            pygame.draw.rect(screen, (200,60,60), (boss["x"], boss["y"], boss["w"], boss["h"]))
        for p in boss["projectiles"]:
            pygame.draw.rect(screen, (255, 120, 80), p["rect"])
        for o in boss["obstacles"]:
            pygame.draw.rect(screen, (200, 160, 0), o["rect"])

        draw_hp_bar(screen, 20, 20, player.hp, PLAYER_MAX_HP, (0,255,0))
        draw_hp_bar(screen, config.WIDTH - 320, 20, boss["hp"], boss_hp, (255,80,60))

        # name + phase
        name_surf = font_small.render(f"{name}  HP:{boss['hp']}", True, config.C_TEXT)
        screen.blit(name_surf, (config.WIDTH//2 - name_surf.get_width()//2, 20))

        pygame.display.flip()

    try:
        pygame.mixer.music.stop()
    except Exception:
        pass
