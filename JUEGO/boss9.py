# boss9.py
import os
from boss_template import run_boss_generic
import config

params = {
    "image_path": os.path.join(config.ASSETS_IMG, "boss_9.png"),
    "music_path": os.path.join(config.ASSETS_AUDIO, "boss_9.mp3"),
    "boss_size": 220,
    "boss_hp": 2600,
    "name": "BOSS 9",
    "base_pattern": "mixed",
    "shoot_interval": 22,
    "projectile_speed": 11.0,
    "ob_interval": 90,
    "obstacle_types": ["falling","moving","mine"],
    "player_damage_to_boss": 4,
    "boss_proj_damage": 32,
    "obstacle_damage": 36,
    "phases": [
        {"threshold":2000, "overrides":{"shoot_interval":18,"projectile_speed":12.0}}
    ]
}

def run_boss(screen, clock):
    run_boss_generic(screen, clock, params)
