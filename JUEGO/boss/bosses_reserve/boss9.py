import os
import config
from boss.boss_template import run_boss_generic

params = {
    "image_path": os.path.join(config.ASSETS_IMG, "boss_9.png"),
    "proj_image_path": os.path.join(config.ASSETS_IMG, "boss_9_proj.png"),
    "big_proj_image_path": os.path.join(config.ASSETS_IMG, "boss_9_big.png"),
    "music_path": os.path.join(config.ASSETS_AUDIO, "boss_9.mp3"),
    "boss_size": 230,
    "boss_hp": 2900,
    "name": "BOSS 9",
    "base_pattern": "mixed",
    "shoot_interval": 24,
    "projectile_speed": 11.0,
    "ob_interval": 110,
    "obstacle_types": ["falling", "moving", "mine"],
    "player_damage_to_boss": 5,
    "boss_proj_damage": 30,
    "obstacle_damage": 34,
    "laser_interval": 340,
    "laser_duration": 160,
    "phases": [
        {"threshold": 2200, "overrides": {"shoot_interval": 20, "projectile_speed": 12.0}}
    ]
}

def run_boss(screen, clock):
    run_boss_generic(screen, clock, params)
