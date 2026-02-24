# boss3.py
import os
from boss_template import run_boss_generic
import config

params = {
    "image_path": os.path.join(config.ASSETS_IMG, "boss_3.png"),
    "music_path": os.path.join(config.ASSETS_AUDIO, "boss_3.mp3"),
    "boss_size": 170,
    "boss_hp": 1300,
    "name": "BOSS 3",
    "base_pattern": "aimed",
    "shoot_interval": 46,
    "projectile_speed": 7.0,
    "ob_interval": 160,
    "obstacle_types": ["falling","moving"],
    "player_damage_to_boss": 8,
    "boss_proj_damage": 20,
    "obstacle_damage": 22,
    "phases": [
        {"threshold":900, "overrides":{"shoot_interval":38,"projectile_speed":8.5}}
    ]
}

def run_boss(screen, clock):
    run_boss_generic(screen, clock, params)
