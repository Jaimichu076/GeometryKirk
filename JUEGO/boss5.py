# boss5.py
import os
from boss_template import run_boss_generic
import config

params = {
    "image_path": os.path.join(config.ASSETS_IMG, "boss_5.png"),
    "music_path": os.path.join(config.ASSETS_AUDIO, "boss_5.mp3"),
    "boss_size": 180,
    "boss_hp": 1700,
    "name": "BOSS 5",
    "base_pattern": "rotating",
    "shoot_interval": 36,
    "projectile_speed": 9.0,
    "ob_interval": 130,
    "obstacle_types": ["moving","mine"],
    "player_damage_to_boss": 6,
    "boss_proj_damage": 24,
    "obstacle_damage": 28,
    "phases": [
        {"threshold":1200, "overrides":{"shoot_interval":30,"projectile_speed":10.0}}
    ]
}

def run_boss(screen, clock):
    run_boss_generic(screen, clock, params)
