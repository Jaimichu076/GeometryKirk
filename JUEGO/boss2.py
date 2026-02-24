# boss2.py
import os
from boss_template import run_boss_generic
import config

params = {
    "image_path": os.path.join(config.ASSETS_IMG, "boss_2.png"),
    "music_path": os.path.join(config.ASSETS_AUDIO, "boss_2.mp3"),
    "boss_size": 160,
    "boss_hp": 1100,
    "name": "BOSS 2",
    "base_pattern": "mixed",
    "shoot_interval": 48,
    "projectile_speed": 8.0,
    "ob_interval": 180,
    "obstacle_types": ["mine","falling"],
    "player_damage_to_boss": 9,
    "boss_proj_damage": 16,
    "obstacle_damage": 24,
    "phases": [
        {"threshold":800, "overrides":{"shoot_interval":40,"projectile_speed":9.0}}
    ]
}

def run_boss(screen, clock):
    run_boss_generic(screen, clock, params)
