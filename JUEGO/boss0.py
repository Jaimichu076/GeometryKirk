# boss1.py
import os
from boss_template import run_boss_generic
import config

params = {
    "image_path": os.path.join(config.ASSETS_IMG, "boss_1.png"),
    "music_path": os.path.join(config.ASSETS_AUDIO, "boss_1.mp3"),
    "boss_size": 150,
    "boss_hp": 900,
    "name": "BOSS 1",
    "base_pattern": "fan",
    "shoot_interval": 55,
    "projectile_speed": 7.0,
    "ob_interval": 160,
    "obstacle_types": ["moving","falling"],
    "player_damage_to_boss": 10,
    "boss_proj_damage": 14,
    "obstacle_damage": 20,
    "phases": [
        {"threshold":600, "overrides":{"shoot_interval":45,"projectile_speed":8.0}}
    ]
}

def run_boss(screen, clock):
    run_boss_generic(screen, clock, params)
