# boss2.py
import os
import pygame
import config
from boss.boss_template import run_boss_generic

params = {
    "image_path": os.path.join(config.ASSETS_IMG, "falete.jpg"),
    "proj_image_path": os.path.join(config.ASSETS_IMG, "boss_2_proj.png"),
    "big_proj_image_path": os.path.join(config.ASSETS_IMG, "boss_2_big.png"),
    "music_path": os.path.join(config.ASSETS_AUDIO, "faletesong.mp3"),
    "boss_size": 160,
    "boss_hp": 1100,
    "name": "Falete",
    "base_pattern": "mixed",
    "shoot_interval": 52,
    "projectile_speed": 7.0,
    "ob_interval": 200,
    "obstacle_types": ["mine", "falling"],
    "player_damage_to_boss": 11,
    "boss_proj_damage": 14,
    "obstacle_damage": 20,
    "laser_interval": 420,
    "laser_duration": 110,
    "phases": [
        {"threshold": 800, "overrides": {"shoot_interval": 44, "projectile_speed": 8.0}}
    ],
    "heal_image_path": os.path.join(config.ASSETS_IMG, "heal_cube.png"),
    "heal_interval": 450,
    "heal_amount": 28,
    "heal_spawn_count": 2,
    "enable_puddles": False,
    "enable_lasers": True,
    "orientation": "both",
    "tutorial": False,
    "enable_enrage": False,
    "explosion_sound": os.path.join(config.ASSETS_AUDIO, "boss_explosion.wav")
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
