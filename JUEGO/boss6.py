# boss6.py
import os
from boss_template import run_boss_generic
import config

params = {
    "image_path": os.path.join(config.ASSETS_IMG, "boss_6.png"),
    "music_path": os.path.join(config.ASSETS_AUDIO, "boss_6.mp3"),
    "boss_size": 190,
    "boss_hp": 1900,
    "name": "BOSS 6",
    "base_pattern": "mixed",
    "shoot_interval": 34,
    "projectile_speed": 9.0,
    "ob_interval": 110,
    "obstacle_types": ["falling","moving","mine"],
    "player_damage_to_boss": 6,
    "boss_proj_damage": 26,
    "obstacle_damage": 30,
    "phases": [
        {"threshold":1400, "overrides":{"shoot_interval":28,"projectile_speed":10.0}}
    ]
}

def run_boss(screen, clock):
    run_boss_generic(screen, clock, params)
