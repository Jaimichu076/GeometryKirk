# boss0.py — Tutorial
import os
import pygame
import config
from boss.boss_template import run_boss_generic

# --- SISTEMA DE PAUSAS DEL TUTORIAL ---
# Este boss necesita pausas explicativas. Para eso, usamos un "wrapper"
# que llama a run_boss_generic pero con pausas antes de iniciar el combate.

def run_boss(screen, clock):

    # 1. Mostrar mensaje inicial
    def tutorial_message(text):
        font = pygame.font.SysFont("Arial Black", 38)
        small = pygame.font.SysFont("Arial", 24)
        waiting = True
        while waiting:
            clock.tick(config.FPS)
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit(); raise SystemExit
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE:
                    waiting = False

            screen.fill((10, 10, 25))
            msg = font.render(text, True, (255,255,255))
            hint = small.render("Pulsa ESPACIO para continuar", True, (200,200,200))
            screen.blit(msg, (config.WIDTH//2 - msg.get_width()//2, 200))
            screen.blit(hint, (config.WIDTH//2 - hint.get_width()//2, 300))
            pygame.display.flip()

    tutorial_message("Bienvenido al Boss Tutorial")
    tutorial_message("Muévete con W A S D o Flechas")
    tutorial_message("Dispara con ESPACIO")
    tutorial_message("Esquiva los proyectiles")
    tutorial_message("Golpea al boss para bajarle la vida")
    tutorial_message("Prepárate... ¡Comienza el combate!")

    # --- CONFIGURACIÓN DEL BOSS TUTORIAL ---
    params = {
        "image_path": os.path.join(config.ASSETS_IMG, "Ruth.jpg"),
        "proj_image_path": os.path.join(config.ASSETS_IMG, "obunga.png"),
        "big_proj_image_path": os.path.join(config.ASSETS_IMG, "obunga700.png"),
        "music_path": os.path.join(config.ASSETS_AUDIO, "Estamos perdidas.mp3"),

        "boss_size": 140,
        "boss_hp": 300,
        "name": "BOSS Tutorial",

        "base_pattern": "fan",
        "shoot_interval": 90,
        "projectile_speed": 4.5,
        "ob_interval": 260,
        "obstacle_types": ["falling"],

        "player_damage_to_boss": 14,
        "boss_proj_damage": 6,
        "obstacle_damage": 10,

        "laser_interval": 0,
        "laser_duration": 0,

        "phases": []
    }

    run_boss_generic(screen, clock, params)
