# boss10.py
import os
from boss_template import run_boss_generic
import config

params = {
    "image_path": os.path.join(config.ASSETS_IMG, "boss_10.png"),
    "music_path": os.path.join(config.ASSETS_AUDIO, "boss_10.mp3"),
    "boss_size": 240,
    "boss_hp": 3600,
    "name": "BOSS 10 - FINAL",
    "base_pattern": "mixed",
    "shoot_interval": 18,
    "projectile_speed": 12.0,
    "ob_interval": 80,
    "obstacle_types": ["falling","moving","mine"],
    "player_damage_to_boss": 4,
    "boss_proj_damage": 36,
    "obstacle_damage": 40,
    "phases": [
        {"threshold":2800, "overrides":{"shoot_interval":16,"projectile_speed":13.0}},
        {"threshold":2000, "overrides":{"shoot_interval":14,"projectile_speed":14.0}},
        {"threshold":1200, "overrides":{"shoot_interval":12,"projectile_speed":15.0}},
        {"threshold":600,  "overrides":{"shoot_interval":10,"projectile_speed":16.0}}
    ]
}

def run_boss(screen, clock):
    run_boss_generic(screen, clock, params)
