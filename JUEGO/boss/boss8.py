import os
import config
from boss.boss_template import run_boss_generic

params = {
    "image_path": os.path.join(config.ASSETS_IMG, "boss_8.png"),
    "proj_image_path": os.path.join(config.ASSETS_IMG, "boss_8_proj.png"),
    "big_proj_image_path": os.path.join(config.ASSETS_IMG, "boss_8_big.png"),
    "music_path": os.path.join(config.ASSETS_AUDIO, "boss_8.mp3"),
    "boss_size": 220,
    "boss_hp": 2500,
    "name": "BOSS 8",
    "base_pattern": "rotating",
    "shoot_interval": 28,
    "projectile_speed": 10.0,
    "ob_interval": 120,
    "obstacle_types": ["falling", "moving", "mine"],
    "player_damage_to_boss": 6,
    "boss_proj_damage": 28,
    "obstacle_damage": 32,
    "laser_interval": 360,
    "laser_duration": 150,
    "phases": [
        {"threshold": 1900, "overrides": {"shoot_interval": 24, "projectile_speed": 11.0}}
    ]
}

def run_boss(screen, clock):
    run_boss_generic(screen, clock, params)
