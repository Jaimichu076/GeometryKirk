# boss1.py
import os
import pygame
import config
from boss.boss_template import run_boss_generic

params = {
    "image_path": os.path.join(config.ASSETS_IMG, "boss_1.jpg"),
    "proj_image_path": os.path.join(config.ASSETS_IMG, "boss_1_proj.png"),
    "big_proj_image_path": os.path.join(config.ASSETS_IMG, "boss_1_big.png"),
    "music_path": os.path.join(config.ASSETS_AUDIO, "boss_1.mp3"),
    "boss_size": 150,
    "boss_hp": 800,
    "name": "Netanyahu",
    "base_pattern": "fan",
    "shoot_interval": 60,
    "projectile_speed": 5.5,
    "ob_interval": 220,
    "obstacle_types": ["falling", "moving"],
    "player_damage_to_boss": 12,
    "boss_proj_damage": 12,
    "obstacle_damage": 16,
    "laser_interval": 0,
    "laser_duration": 0,
    "phases": [
        {"threshold": 600, "overrides": {"shoot_interval": 52, "projectile_speed": 6.5}}
    ],
    "heal_image_path": os.path.join(config.ASSETS_IMG, "heal_cube.png"),
    "heal_interval": 500,
    "heal_amount": 25,
    "heal_spawn_count": 2,
    "enable_puddles": True,
    "puddle_interval": 220,
    "puddle_damage_per_sec": 8,
    "puddle_near_player_radius": 260,
    "orientation": "vertical",
    "tutorial": False,
    "enable_lasers": False,
    "enable_enrage": False,
    "explosion_sound": os.path.join(config.ASSETS_AUDIO, "explosion_boss1.wav")
}

def run_boss(screen, clock):
    while True:
        result = run_boss_generic(screen, clock, params)
        if result == "exit":
            return
        if result == "lose":
            font = pygame.font.SysFont("Arial Black", 48)
            small = pygame.font.SysFont("Arial", 22)
            waiting = True
            while waiting:
                clock.tick(config.FPS)
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        pygame.quit(); raise SystemExit
                    if ev.type == pygame.KEYDOWN:
                        if ev.key == pygame.K_RETURN:
                            waiting = False
                        if ev.key == pygame.K_ESCAPE:
                            return
                screen.fill((20,10,10))
                msg = font.render("Has perdido", True, (255, 80, 80))
                hint = small.render("Pulsa ENTER para reintentar o ESC para volver al menú", True, (220,220,220))
                screen.blit(msg, (config.WIDTH//2 - msg.get_width()//2, config.HEIGHT//2 - 40))
                screen.blit(hint, (config.WIDTH//2 - hint.get_width()//2, config.HEIGHT//2 + 40))
                pygame.display.flip()
            continue
        if result == "win":
            font = pygame.font.SysFont("Arial Black", 48)
            small = pygame.font.SysFont("Arial", 22)
            waiting = True
            while waiting:
                clock.tick(config.FPS)
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        pygame.quit(); raise SystemExit
                    if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                        return
                screen.fill((10,20,10))
                msg = font.render("¡Has ganado!", True, (120, 255, 120))
                hint = small.render("Pulsa ESC para volver al menú", True, (220,220,220))
                screen.blit(msg, (config.WIDTH//2 - msg.get_width()//2, config.HEIGHT//2 - 40))
                screen.blit(hint, (config.WIDTH//2 - hint.get_width()//2, config.HEIGHT//2 + 40))
                pygame.display.flip()
