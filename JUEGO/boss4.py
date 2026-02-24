# boss4.py
import os
from boss_template import run_boss_generic
import config

params = {
    "image_path": os.path.join(config.ASSETS_IMG, "boss_4.png"),
    "music_path": os.path.join(config.ASSETS_AUDIO, "boss_4.mp3"),
    "boss_size": 180,
    "boss_hp": 1500,
    "name": "BOSS 4",
    "base_pattern": "rotating",
    "shoot_interval": 44,
    "projectile_speed": 8.5,
    "ob_interval": 140,
    "obstacle_types": ["falling","moving","mine"],
    "player_damage_to_boss": 7,
    "boss_proj_damage": 22,
    "obstacle_damage": 26,
    "phases": [
        {"threshold":1100, "overrides":{"shoot_interval":36,"projectile_speed":9.5}}
    ]
}

def run_boss(screen, clock):
    run_boss_generic(screen, clock, params)
