# boss8.py
import os
from boss_template import run_boss_generic
import config

params = {
    "image_path": os.path.join(config.ASSETS_IMG, "boss_8.png"),
    "music_path": os.path.join(config.ASSETS_AUDIO, "boss_8.mp3"),
    "boss_size": 200,
    "boss_hp": 2300,
    "name": "BOSS 8",
    "base_pattern": "aimed",
    "shoot_interval": 26,
    "projectile_speed": 10.0,
    "ob_interval": 100,
    "obstacle_types": ["falling","moving","mine"],
    "player_damage_to_boss": 5,
    "boss_proj_damage": 30,
    "obstacle_damage": 34,
    "phases": [
        {"threshold":1700, "overrides":{"shoot_interval":20,"projectile_speed":11.5}}
    ]
}

def run_boss(screen, clock):
    run_boss_generic(screen, clock, params)
