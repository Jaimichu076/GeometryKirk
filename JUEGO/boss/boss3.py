# boss3.py
import os
import pygame
import config
from boss.boss_template import run_boss_generic

params = {
    "image_path": os.path.join(config.ASSETS_IMG, "boss_3.jpg"),
    "proj_image_path": os.path.join(config.ASSETS_IMG, "boss_3_proj.png"),
    "big_proj_image_path": os.path.join(config.ASSETS_IMG, "boss_3_big.png"),
    "music_path": os.path.join(config.ASSETS_AUDIO, "boss_3.mp3"),
    "boss_size": 170,
    "boss_hp": 1300,
    "name": "Diddy",
    "base_pattern": "aimed",
    "shoot_interval": 48,
    "projectile_speed": 7.5,
    "ob_interval": 190,
    "obstacle_types": ["falling", "moving"],
    "player_damage_to_boss": 10,
    "boss_proj_damage": 18,
    "obstacle_damage": 22,
    "laser_interval": 520,
    "laser_duration": 110,
    "phases": [
        {"threshold": 900, "overrides": {"shoot_interval": 40, "projectile_speed": 8.5}}
    ],
    "heal_image_path": os.path.join(config.ASSETS_IMG, "heal_cube.png"),
    "heal_interval": 500,
    "heal_amount": 30,
    "heal_spawn_count": 2,
    "enable_puddles": False,
    "enable_lasers": True,
    "orientation": "both",
    "tutorial": False,
    "enable_enrage": True,
    "enrage_cycle": 600,
    "enrage_duration": 240,
    "enrage_factor": 0.6,
    "explosion_sound": os.path.join(config.ASSETS_AUDIO, "explosion_boss3.wav")
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
