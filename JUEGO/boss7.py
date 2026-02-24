# boss7.py
import os
from boss_template import run_boss_generic
import config

params = {
    "image_path": os.path.join(config.ASSETS_IMG, "boss_7.png"),
    "music_path": os.path.join(config.ASSETS_AUDIO, "boss_7.mp3"),
    "boss_size": 200,
    "boss_hp": 2100,
    "name": "BOSS 7",
    "base_pattern": "mixed",
    "shoot_interval": 30,
    "projectile_speed": 10.0,
    "ob_interval": 90,
    "obstacle_types": ["falling","moving"],
    "player_damage_to_boss": 5,
    "boss_proj_damage": 28,
    "obstacle_damage": 32,
    "phases": [
        {"threshold":1600, "overrides":{"shoot_interval":24,"projectile_speed":11.0}}
    ]
}

def run_boss(screen, clock):
    run_boss_generic(screen, clock, params)
