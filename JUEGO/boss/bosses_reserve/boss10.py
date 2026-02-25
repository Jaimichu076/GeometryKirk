# boss10.py — Jefe Final Extremo
import os
import config
from boss.boss_template import run_boss_generic

params = {
    "image_path": os.path.join(config.ASSETS_IMG, "boss_10.png"),
    "proj_image_path": os.path.join(config.ASSETS_IMG, "boss_10_proj.png"),
    "big_proj_image_path": os.path.join(config.ASSETS_IMG, "boss_10_big.png"),
    "music_path": os.path.join(config.ASSETS_AUDIO, "boss_10.mp3"),

    "boss_size": 260,
    "boss_hp": 5000,
    "name": "BOSS FINAL — APOCALIPSIS",

    "base_pattern": "mixed",
    "shoot_interval": 22,
    "projectile_speed": 12.0,
    "ob_interval": 90,
    "obstacle_types": ["falling", "moving", "mine"],

    "player_damage_to_boss": 5,
    "boss_proj_damage": 34,
    "obstacle_damage": 40,

    # Láseres muy frecuentes
    "laser_interval": 260,
    "laser_duration": 160,
    "laser_color": (255, 40, 40),

    # FASES DEL JEFE FINAL
    "phases": [
        # Fase 1 — 5000 → 3800
        {
            "threshold": 3800,
            "overrides": {
                "shoot_interval": 20,
                "projectile_speed": 13.0,
                "laser_interval": 240
            }
        },
        # Fase 2 — 3800 → 2600
        {
            "threshold": 2600,
            "overrides": {
                "shoot_interval": 18,
                "projectile_speed": 14.0,
                "base_pattern": "rotating",
                "laser_interval": 220
            }
        },
        # Fase 3 — 2600 → 1600
        {
            "threshold": 1600,
            "overrides": {
                "shoot_interval": 16,
                "projectile_speed": 15.0,
                "base_pattern": "burst",
                "laser_interval": 200
            }
        },
        # Fase 4 — 1600 → 800
        {
            "threshold": 800,
            "overrides": {
                "shoot_interval": 14,
                "projectile_speed": 16.0,
                "base_pattern": "mixed",
                "laser_interval": 180
            }
        },
        # Fase 5 — 800 → 0 (modo locura)
        {
            "threshold": 0,
            "overrides": {
                "shoot_interval": 10,
                "projectile_speed": 18.0,
                "base_pattern": "rotating",
                "laser_interval": 140
            }
        }
    ]
}

def run_boss(screen, clock):
    run_boss_generic(screen, clock, params)
