import os
import config
from boss.boss_template import run_boss_generic

params = {
    "image_path": os.path.join(config.ASSETS_IMG, "boss_7.png"),
    "proj_image_path": os.path.join(config.ASSETS_IMG, "boss_7_proj.png"),
    "big_proj_image_path": os.path.join(config.ASSETS_IMG, "boss_7_big.png"),
    "music_path": os.path.join(config.ASSETS_AUDIO, "boss_7.mp3"),
    "boss_size": 210,
    "boss_hp": 2200,
    "name": "BOSS 7",
    "base_pattern": "aimed",
    "shoot_interval": 32,
    "projectile_speed": 9.5,
    "ob_interval": 130,
    "obstacle_types": ["falling", "moving"],
    "player_damage_to_boss": 6,
    "boss_proj_damage": 26,
    "obstacle_damage": 30,
    "laser_interval": 380,
    "laser_duration": 140,
    "phases": [
        {"threshold": 1700, "overrides": {"shoot_interval": 26, "projectile_speed": 10.5}}
    ]
}

def run_boss(screen, clock):
    run_boss_generic(screen, clock, params)
